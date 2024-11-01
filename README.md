![logo](imgs/logo.png)

# Structural Bioinformatics (W2024)

Teaching materials for the course "Structural Bioinformatics" at [FHWN](https://tulln.fhwn.ac.at/studiengang/bio-data-science).

## Installation

After some minor research, google colab is the best option.
I have downgraded the notebooks to the GoogleColab versions for compatibility.

Despite of it, you are free to use the notebooks in your local machine.

### google colab

Google colab is a free service that allows you to run jupyter notebooks in the cloud.

| Link                                                                                                                               | Description                          |
|------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex00/crash_course.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> | Crash course for Bio Data Scientists |
| <a href="https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex01/ex01.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>                 | Exercise 01                          |
|


### Conda Installation

1. Install Miniconda from [here](https://docs.conda.io/en/latest/miniconda.html) or Anaconda from [here](https://www.anaconda.com/products/distribution#download-section) (Note: **Miniconda is recommended for this course**).


#### Conda (via VSCode)

To select the Conda interpreter in your editor, follow these steps:

1. **Install the Python extension:**
    - Install the extensions by going to `File` > `Preferences` > `Profile` > `Profiles` > Click on `∨` (next to `New profile`) > `Import Profile` > Select the file `structbioinfo.code-profile`.
    - Alternatively, you can install it via the Extensions view:
      - Open the extensions view by pressing `Ctrl + Shift + X`.
      - Search for `Python` and install the extension.

1. **Open Command Palette:**
    - Press `Ctrl + Shift + P` to open the command palette.

2. **Select Interpreter:**
    - Type `Select Interpreter` and select the option from the list.
    - Choose the Miniconda Python 3 executable from the available interpreters.
      - **Note:** This step is crucial if you have multiple Python versions installed on your computer.

      Example path: `~\miniconda3\python3.exe`

3. **Create Environment:**
    - Press `Ctrl + Shift + P` again to open the command palette.
    - Type `Create Environment` and select the option from the list.
    - Choose `Conda` as the environment type.
    - Select the `Python 3.10` version for the new environment.

Following these steps ensures that your editor uses the correct Conda environment and Python version for your projects.


#### Conda (via Terminal)

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


### License
[![BY-NC-SA](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)


This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).
