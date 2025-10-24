![logo](imgs/logo.png)

# Structural Bioinformatics (W2025)

Teaching materials for the course "Structural Bioinformatics" at [FHWN](https://tulln.fhwn.ac.at/studiengang/bio-data-science).

## Getting started

After some research, Google Colab is the best option.

### Google Colab

Google colab is a free service that allows you to run jupyter notebooks in the cloud.

| Link                                                                                                                               | Description                          |
|------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex00/scientific_python_crash_course.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Exercise 00: Scientific Python Crash Course for Structural Bioinformatics |
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex01/ex01.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Exercise 01: Exploring and Analyzing Protein Structures in the PDB Database |
<!-- 
TODO: Exercises for W2025 - Coming Soon!
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex02/ex02.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Exercise 02: Protein Structure and Modeling |
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex03/ex03.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Exercise 03: Protein Dynamics |
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex04/ex04.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Exercise 04: Protein Docking |
-->


### Conda

You are free to use the files

For Linux, Mac or Windows (via WSL).

1. **Create a new environment with conda:**

    ```bash
    conda env create -f environment.yml
    ```

    This will create an environment called `structbioinfo`.

2. **Activate the environment:**

    ```bash
    conda activate structbioinfo
    ```

3. **Update the environment for upcoming modifications:**

    ```bash
    conda activate structbioinfo
    conda env update --file environment.yml --prune
    ```

4. In VSCode, select the interpreter to the one you just created.


## Protein-Ligand Complexes for Study

A curated list of small protein-ligand complexes suitable for molecular dynamics simulations on laptop computers is available in the `scripts/` directory. These structures were identified using UniProt enzyme classification and RCSB PDB searches, filtered for:

- Small size (< 50,000 atoms)
- Presence of organic ligands (no simple ions/solvents)
- High-quality structures (X-ray or cryo-EM)
- Soluble proteins (avoiding membrane-embedded proteins)
- No complex interactions (excluding RNA/DNA binding complexes)

📊 **[View the curated summary table](scripts/simple_table.md)**

The complete dataset with all details is also available as a [CSV file](scripts/suitable_protein_ligand_complexes.csv) including protein names, PDB IDs, ligands, resolution, organism, and other relevant data for structural analysis and MD simulations.

**Note:** This list is provided as a starting point for project work. Students are **not limited** to these proteins and are encouraged to explore and select other suitable protein-ligand systems for their projects based on their research interests.


### License
[![BY-NC-SA](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)


This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).
