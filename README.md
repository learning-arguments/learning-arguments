# Explainable AI: Learning Arguments

Master's student project at Maastricht University, Spring 2021

Authors: Jonas Bei, David Pomerenke, Lukas Schreiner, Sepideh Sharbaf

Supervisors: Nico Roos, Pieter Collins

This is the code for the project, also known as _Appendix C_.

## Installation

For reproducibility, best use a virtual environment. For this, execute the following steps on the command line, from the folder where this file is also located.

1. Create an empty virtual environment in the `.venv` directory:

```
python3.8 -m venv .venv
```

2. Open the environment in your command line instance:

```
source .venv/bin/activate
```

3. Install the project dependencies at the correct versions into the virtual environment:

```
pip -r requirements.txt
```

4. Finished! Now you can run, for example, `python main.py`. When you come back after closing your command line window, you will need to repeat step 3 to load the virtual environment again.

## Running

Inside the virtual environment (see above) execute the following in the console:

```
python main.py
```

## Testing

Inside the virtual environment (see above) execute the following in the console:

```
pytest
```

There are some more tests inside `Appendix B.ipynb`, which can be run by opening the notebook within a [Jupyter Notebook](https://jupyter.org/) environment.

![](dke-logo.png)