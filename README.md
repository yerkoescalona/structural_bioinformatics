![logo](imgs/logo.png)

# Structural Bioinformatics

Teaching materials for the course "Structural Bioinformatics" at [FHWN](https://tulln.fhwn.ac.at/studiengang/bio-data-science).

## Installation

After some minor research, google colab is the best option.
I have downgraded the notebooks to the GoogleColab versions for compatibility.

Despite of it, you are free to use the notebooks in your local machine.

### google colab

Google colab is a free service that allows you to run jupyter notebooks in the cloud.

| Link                                                                                                                               | Description                          |
|------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| [crash_course](https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex00/crash_course.ipynb) | Crash course for Bio Data Scientists |
| [ex01](https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex01/ex01.ipynb)                 | Exercise 01                          |
| [ex02](https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex02/ex02.ipynb)                 | Exercise 02                          |
| [ex03](https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex03/ex03.ipynb)                 | Exercise 03                          |
| [ex04](https://colab.research.google.com/github/yerkoescalona/structural_bioinformatics/blob/main/ex04/ex04.ipynb)                 | Exercise 04                          |


### conda

Create a new environment with conda:

    conda env create -f environment.yml

This will create an environment called structbioinfo. Activate it using:

    conda activate structbioinfo

For upcoming modifications of the environment execute:

    conda activate structbioinfo
    conda env update --file environment.yml --prune

### pip

Using pip:

    pip install -r requirements.txt


### License
[![BY-NC-SA](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)


This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).
