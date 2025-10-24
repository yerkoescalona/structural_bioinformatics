#!/usr/bin/env python3
"""RCSB PDB Small Protein-Ligand Finder via UniProt.

This script searches for small protein structures by first finding UniProt entries
with known ligands, then finding their PDB structures suitable for molecular
dynamics simulations on a laptop computer.

Requirements:
    pip install requests biopython pandas --break-system-packages
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
import requests


@dataclass
class ProteinLigandComplex:
    """Data class to store protein-ligand complex information."""

    pdb_id: str
    title: str
    resolution: Optional[float]
    method: str
    num_residues: int
    num_atoms: int
    uniprot_ids: List[str]
    ligands: List[str]
    organism: str

    def is_laptop_suitable(self, max_atoms: int = 50000) -> bool:
        """Check if structure is small enough for laptop simulation."""
        return self.num_atoms <= max_atoms


class UniProtLigandFinder:
    """Class to search UniProt for proteins with known ligands."""

    UNIPROT_API = "https://rest.uniprot.org/uniprotkb/search"
    UNIPROT_ENTRY = "https://rest.uniprot.org/uniprotkb"

    # Common ions and simple inorganic molecules to exclude
    EXCLUDED_LIGANDS = {
        # Metal ions
        "Zn(2+)",
        "Mg(2+)",
        "Ca(2+)",
        "Fe(2+)",
        "Fe(3+)",
        "Mn(2+)",
        "Cu(2+)",
        "Na(+)",
        "K(+)",
        "Ni(2+)",
        "Co(2+)",
        "Zn",
        "Mg",
        "Ca",
        "Fe",
        "Mn",
        "Cu",
        "Na",
        "K",
        "Ni",
        "Co",
        "Cd",
        "Hg",
        "Pb",
        # Simple inorganic
        "Cl(-)",
        "PO4(3-)",
        "SO4(2-)",
        "H2O",
        "water",
        "chloride",
        "sulfate",
        "phosphate",
        "hydroxide",
        "oxide",
    }

    def __init__(self, max_length: int = 300):
        """Initialize the finder.

        Args:
            max_length: Maximum protein length in amino acids
        """
        self.max_length = max_length

    def is_organic_ligand(self, ligand_name: str) -> bool:
        """Check if a ligand is an organic molecule (not just an ion or water).

        Args:
            ligand_name: Name of the ligand/cofactor

        Returns:
            True if organic, False if ion/inorganic
        """
        ligand_lower = ligand_name.lower()

        # Check against excluded list
        for excluded in self.EXCLUDED_LIGANDS:
            if excluded.lower() in ligand_lower:
                return False

        # Simple heuristic: organic ligands typically have longer names
        # and don't end with charge notation like (+) or (2+)
        if len(ligand_name) < 4:  # Very short names are usually ions
            return False

        # Check for charge notation at the end (indicates ion)
        if ligand_name.endswith(("+)", "-)", "+")):
            return False

        return True

    def search_proteins_with_ligands(self, limit: int = 100) -> List[Dict]:
        """Search UniProt for small proteins with known ligands.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of dictionaries with UniProt ID and protein info
        """
        # Search for reviewed enzymes with 3D structure
        # Enzymes typically bind substrates and cofactors
        query = (
            f"(reviewed:true) AND "
            f"(length:[50 TO {self.max_length}]) AND "
            f"(structure_3d:true) AND "
            f"(ec:*)"  # Has EC number (enzyme classification)
        )

        params = {
            "query": query,
            "format": "json",
            "size": min(limit * 2, 500),  # Get extra results to filter
            "fields": "accession,id,protein_name,length,organism_name,ec,cc_cofactor,cc_catalytic_activity,xref_pdb",
        }

        try:
            print("Searching UniProt for small enzymes with 3D structures...")
            response = requests.get(self.UNIPROT_API, params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            print(f"Got {len(results)} enzyme entries, filtering...")

            proteins = []
            for entry in results:
                uniprot_id = entry.get("primaryAccession", "")
                protein_name = (
                    entry.get("proteinDescription", {})
                    .get("recommendedName", {})
                    .get("fullName", {})
                    .get("value", "Unknown")
                )
                length = entry.get("sequence", {}).get("length", 0)
                organism = entry.get("organism", {}).get("scientificName", "Unknown")

                # Extract PDB references
                pdb_refs = []
                for xref in entry.get("uniProtKBCrossReferences", []):
                    if xref.get("database") == "PDB":
                        pdb_refs.append(xref.get("id"))

                # Extract cofactor/ligand information if available
                ligands = []
                for comment in entry.get("comments", []):
                    if comment.get("commentType") == "COFACTOR":
                        for cofactor in comment.get("cofactors", []):
                            ligand_name = cofactor.get("name", "")
                            if ligand_name and self.is_organic_ligand(ligand_name):
                                ligands.append(ligand_name)

                # Include enzymes with PDB structures
                # We'll check for actual ligands when processing the PDB files
                if pdb_refs:
                    proteins.append(
                        {
                            "uniprot_id": uniprot_id,
                            "protein_name": protein_name,
                            "length": length,
                            "organism": organism,
                            "pdb_ids": pdb_refs,
                            "known_ligands": ligands
                            if ligands
                            else ["Unknown - will check PDB"],
                        }
                    )

                    # Stop if we have enough proteins
                    if len(proteins) >= limit:
                        break

            print(f"Found {len(proteins)} enzyme entries with PDB structures")
            return proteins

        except requests.exceptions.RequestException as e:
            print(f"Error searching UniProt: {e}")
            return []


class RCSBLigandFinder:
    """Class to search RCSB PDB for small protein-ligand complexes."""

    BASE_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
    DATA_API = "https://data.rcsb.org/rest/v1/core/entry"

    def __init__(self, max_residues: int = 300, max_atoms: int = 50000):
        """Initialize the finder with size constraints.

        Args:
            max_residues: Maximum number of protein residues (default: 300)
            max_atoms: Maximum total atoms for laptop simulation (default: 50000)
        """
        self.max_residues = max_residues
        self.max_atoms = max_atoms

    def search_small_proteins_with_ligands(self, limit: int = 100) -> List[str]:
        """Search for small protein structures with bound ligands.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of PDB IDs
        """
        query = {
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": [
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entry_info.polymer_entity_count_protein",
                            "operator": "greater",
                            "value": 0,
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entry_info.deposited_nonpolymer_entity_instance_count",
                            "operator": "greater",
                            "value": 0,
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entry_info.deposited_atom_count",
                            "operator": "less_or_equal",
                            "value": self.max_atoms,
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "exptl.method",
                            "operator": "exact_match",
                            "value": "X-RAY DIFFRACTION",
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entry_info.resolution_combined",
                            "operator": "less_or_equal",
                            "value": 3.0,
                        },
                    },
                ],
            },
            "request_options": {
                "return_all_hits": False,
                "results_content_type": ["experimental"],
                "sort": [
                    {"sort_by": "rcsb_accession_info.deposit_date", "direction": "asc"}
                ],
                "scoring_strategy": "combined",
            },
            "return_type": "entry",
            "request_info": {"query_id": "search_query", "src": "ui"},
        }

        all_pdb_ids = []
        rows_per_request = 10  # RCSB API default/maximum per request

        try:
            # Calculate how many requests we need
            num_requests = (limit + rows_per_request - 1) // rows_per_request

            print(f"Making {num_requests} API requests to fetch {limit} results...")

            for request_num in range(num_requests):
                start = request_num * rows_per_request
                rows = min(rows_per_request, limit - len(all_pdb_ids))

                print(
                    f"  Request {request_num + 1}/{num_requests}: start={start}, rows={rows}"
                )

                # Modify pagination in request_options for this request
                current_query = query.copy()
                current_query["request_options"] = query["request_options"].copy()
                current_query["request_options"]["paginate"] = {
                    "start": start,
                    "rows": rows,
                }

                response = requests.post(
                    self.BASE_URL,
                    json=current_query,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

                results = response.json()
                result_set = results.get("result_set", [])

                if not result_set:
                    print(f"  No more results at start={start}")
                    break  # No more results

                pdb_ids = [hit["identifier"] for hit in result_set]
                print(f"  Got {len(pdb_ids)} unique results")
                all_pdb_ids.extend(pdb_ids)

                if len(all_pdb_ids) >= limit:
                    all_pdb_ids = all_pdb_ids[:limit]
                    break

                # Be nice to the API
                time.sleep(0.3)

            total_count = results.get("total_count", 0)
            print(
                f"Found {len(all_pdb_ids)} structures matching criteria (total available: {total_count})"
            )
            return all_pdb_ids

        except requests.exceptions.RequestException as e:
            print(f"Error searching RCSB: {e}")
            return []

    def get_ligands(self, pdb_id: str) -> List[str]:
        """Get list of non-polymer ligands for a PDB structure.

        Args:
            pdb_id: PDB identifier

        Returns:
            List of ligand IDs
        """
        ligands = []

        # Common solvents and ions to filter out
        common_solvents = {
            "HOH",
            "WAT",
            "H2O",
            "DOD",
            "D2O",  # Water
            "SO4",
            "PO4",
            "PO3",
            "NO3",  # Ions
            "GOL",
            "EDO",
            "PEG",
            "PGE",
            "1PE",
            "P6G",  # Glycols/PEGs
            "ACT",
            "DMS",
            "BME",
            "TRS",  # Buffers
            "CL",
            "NA",
            "MG",
            "CA",
            "K",
            "ZN",
            "MN",
            "FE",
            "CU",  # Metal ions
            "BR",
            "I",
            "CD",
            "CO",
            "NI",  # More metals
            "ACE",
            "NH2",
            "EOH",
            "MEO",
            "MES",
            "CS",  # More solvents
        }

        try:
            # First, get the entry to find nonpolymer entity IDs
            url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                # Get the list of nonpolymer entity IDs
                entity_ids = data.get("rcsb_entry_container_identifiers", {}).get(
                    "non_polymer_entity_ids", []
                )

                # For each entity, get its comp_id
                for entity_id in entity_ids:
                    entity_url = f"https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb_id}/{entity_id}"
                    entity_response = requests.get(entity_url)

                    if entity_response.status_code == 200:
                        entity_data = entity_response.json()
                        comp_id = entity_data.get(
                            "rcsb_nonpolymer_entity_container_identifiers", {}
                        ).get("nonpolymer_comp_id", "")

                        # Filter out solvents and ions
                        if comp_id and comp_id not in common_solvents:
                            ligands.append(comp_id)

                    time.sleep(0.05)  # Be nice to the API

            # Remove duplicates
            ligands = list(set(ligands))

        except Exception:
            pass  # Silently fail and return empty list

        return ligands

    def get_structure_details(self, pdb_id: str) -> Optional[ProteinLigandComplex]:
        """Get detailed information about a PDB structure.

        Args:
            pdb_id: PDB identifier

        Returns:
            ProteinLigandComplex object or None
        """
        try:
            url = f"{self.DATA_API}/{pdb_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract basic information
            title = data.get("struct", {}).get("title", "N/A")

            # Get resolution
            resolution = None
            if "refine" in data and len(data["refine"]) > 0:
                resolution = data["refine"][0].get("ls_d_res_high")
            elif "em_3d_reconstruction" in data:
                resolution = data["em_3d_reconstruction"].get("resolution")

            # Get experimental method
            method = data.get("exptl", [{}])[0].get("method", "Unknown")

            # Get entity counts
            entry_info = data.get("rcsb_entry_info", {})
            num_atoms = entry_info.get("deposited_atom_count", 0)

            # Get polymer entity info for residue count
            num_residues = 0
            uniprot_ids = []

            if "rcsb_entry_container_identifiers" in data:
                uniprot_ids = data["rcsb_entry_container_identifiers"].get(
                    "uniprot_ids", []
                )

            # Get polymer entities for residue count
            polymer_url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}"
            try:
                poly_response = requests.get(polymer_url)
                if poly_response.status_code == 200:
                    poly_data = poly_response.json()
                    # Count total residues from all protein entities
                    if isinstance(poly_data, dict):
                        poly_entities = poly_data.get("rcsb_polymer_entity", [])
                        for entity in poly_entities:
                            entity_type = entity.get("type", "")
                            if "Protein" in entity_type or "protein" in entity_type:
                                num_residues += entity.get(
                                    "pdbx_number_of_molecules", 1
                                ) * entity.get("mon_polymer_entity_count_deposited", 0)
            except Exception:
                pass

            # Get ligand information using dedicated method
            ligands = self.get_ligands(pdb_id)

            # Get organism
            organism = "Unknown"
            if (
                "rcsb_entity_source_organism" in data
                and len(data["rcsb_entity_source_organism"]) > 0
            ):
                organism = data["rcsb_entity_source_organism"][0].get(
                    "ncbi_scientific_name", "Unknown"
                )

            return ProteinLigandComplex(
                pdb_id=pdb_id,
                title=title,
                resolution=resolution,
                method=method,
                num_residues=num_residues,
                num_atoms=num_atoms,
                uniprot_ids=uniprot_ids,
                ligands=ligands,
                organism=organism,
            )

        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for {pdb_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing {pdb_id}: {e}")
            return None

    def find_suitable_complexes(self, num_results: int = 50) -> pd.DataFrame:
        """Find protein-ligand complexes suitable for laptop simulation.

        Args:
            num_results: Number of results to search through

        Returns:
            pandas DataFrame with suitable complexes
        """
        print("Searching for protein-ligand complexes...")
        print(
            f"Constraints: max {self.max_residues} residues, max {self.max_atoms} atoms"
        )
        print("-" * 70)

        pdb_ids = self.search_small_proteins_with_ligands(limit=num_results)

        suitable_complexes = []

        for i, pdb_id in enumerate(pdb_ids, 1):
            print(f"Processing {i}/{len(pdb_ids)}: {pdb_id}...", end=" ")

            complex_info = self.get_structure_details(pdb_id)

            if complex_info and complex_info.ligands:
                if complex_info.is_laptop_suitable(self.max_atoms):
                    suitable_complexes.append(
                        {
                            "PDB_ID": complex_info.pdb_id,
                            "Title": complex_info.title[:80] + "..."
                            if len(complex_info.title) > 80
                            else complex_info.title,
                            "Resolution_Å": complex_info.resolution,
                            "Method": complex_info.method,
                            "Num_Atoms": complex_info.num_atoms,
                            "Num_Residues": complex_info.num_residues,
                            "Ligands": ", ".join(complex_info.ligands[:5]),
                            "UniProt_IDs": ", ".join(complex_info.uniprot_ids[:3])
                            if complex_info.uniprot_ids
                            else "N/A",
                            "Organism": complex_info.organism[:50],
                        }
                    )
                    print("✓ Suitable!")
                else:
                    print(f"✗ Too large ({complex_info.num_atoms} atoms)")
            else:
                print("✗ No ligands or data unavailable")

            # Be nice to the API
            time.sleep(0.2)

        df = pd.DataFrame(suitable_complexes)

        if not df.empty:
            df = df.sort_values("Num_Atoms")

        return df


def main():
    """Main execution function."""
    print("=" * 70)
    print("RCSB PDB Small Protein-Ligand Complex Finder (via UniProt)")
    print("=" * 70)
    print()

    # Configuration
    MAX_LENGTH = 300  # Small proteins suitable for MD
    MAX_ATOMS = 50000  # Reasonable for laptop simulations
    NUM_PROTEINS = 100  # Number of UniProt entries to search

    # Step 1: Search UniProt for proteins with known ligands
    uniprot_finder = UniProtLigandFinder(max_length=MAX_LENGTH)
    proteins = uniprot_finder.search_proteins_with_ligands(limit=NUM_PROTEINS)

    if not proteins:
        print("No proteins found in UniProt. Exiting.")
        return

    print()
    print("-" * 70)

    # Step 2: For each protein, get PDB structures and check suitability
    pdb_finder = RCSBLigandFinder(max_residues=MAX_LENGTH, max_atoms=MAX_ATOMS)
    suitable_complexes = []

    for i, protein_info in enumerate(proteins, 1):
        uniprot_id = protein_info["uniprot_id"]
        protein_name = protein_info["protein_name"]
        pdb_ids = protein_info["pdb_ids"][
            :5
        ]  # Check up to 5 PDB structures per protein
        known_ligands = protein_info["known_ligands"]

        print(f"\n[{i}/{len(proteins)}] {uniprot_id}: {protein_name[:60]}")
        print(f"  Known ligands: {', '.join(known_ligands[:3])}")
        print(f"  PDB structures: {', '.join(pdb_ids)}")

        for pdb_id in pdb_ids:
            print(f"    Checking {pdb_id}...", end=" ")

            complex_info = pdb_finder.get_structure_details(pdb_id)

            if complex_info:
                if complex_info.is_laptop_suitable(MAX_ATOMS):
                    # Check if structure has ligands
                    if complex_info.ligands:
                        suitable_complexes.append(
                            {
                                "PDB_ID": complex_info.pdb_id,
                                "UniProt_ID": uniprot_id,
                                "Protein_Name": protein_name[:60],
                                "Title": complex_info.title[:60] + "..."
                                if len(complex_info.title) > 60
                                else complex_info.title,
                                "Resolution_Å": complex_info.resolution,
                                "Method": complex_info.method,
                                "Num_Atoms": complex_info.num_atoms,
                                "Num_Residues": complex_info.num_residues,
                                "Ligands": ", ".join(complex_info.ligands[:5]),
                                "Known_Cofactors": ", ".join(known_ligands[:3]),
                                "Organism": complex_info.organism[:40],
                            }
                        )
                        print(
                            f"✓ Suitable! ({complex_info.num_atoms} atoms, ligands: {', '.join(complex_info.ligands[:3])})"
                        )
                    else:
                        print("✗ No ligands detected")
                else:
                    print(f"✗ Too large ({complex_info.num_atoms} atoms)")
            else:
                print("✗ Data unavailable")

            # Be nice to the APIs
            time.sleep(0.3)

        # Stop if we have enough suitable structures
        if len(suitable_complexes) >= 50:
            print(
                f"\nFound {len(suitable_complexes)} suitable structures. Stopping search."
            )
            break

    # Display results
    print()
    print("=" * 70)
    print(f"Found {len(suitable_complexes)} suitable protein-ligand complexes")
    print("=" * 70)
    print()

    if suitable_complexes:
        df = pd.DataFrame(suitable_complexes)
        df = df.sort_values("Num_Atoms")

        # Display summary
        print(df.to_string(index=False))

        # Save to CSV
        output_file = "suitable_protein_ligand_complexes.csv"
        df.to_csv(output_file, index=False)
        print()
        print(f"Results saved to: {output_file}")

        # Print some statistics
        print()
        print("Statistics:")
        print(f"  Average atoms: {df['Num_Atoms'].mean():.0f}")
        print(
            f"  Smallest structure: {df['PDB_ID'].iloc[0]} ({df['Num_Atoms'].iloc[0]} atoms)"
        )
        print(
            f"  Largest structure: {df['PDB_ID'].iloc[-1]} ({df['Num_Atoms'].iloc[-1]} atoms)"
        )
        print(f"  Unique proteins: {df['UniProt_ID'].nunique()}")

        # Print download instructions
        print()
        print("To download a structure:")
        print("  wget https://files.rcsb.org/download/[PDB_ID].pdb")
        print("  Example: wget https://files.rcsb.org/download/1ABC.pdb")

    else:
        print("No suitable complexes found. Try adjusting the search parameters.")


if __name__ == "__main__":
    main()
