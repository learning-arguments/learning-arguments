# Explainable AI: Learning Arguments

Master's student project at Maastricht University, Spring 2021

Authors: Jonas Bei, David Pomerenke, Lukas Schreiner, Sepideh Sharbaf

Supervisors: Nico Roos, Pieter Collins

[Report [PDF]](https://github.com/learning-arguments/learning-arguments/raw/main/Report.pdf)

[Appendix A - Extended related work [PDF]](https://github.com/learning-arguments/learning-arguments/raw/main/Appendix-A.pdf)

[Appendix B - Notebook with examples [iPython]](https://github.com/learning-arguments/learning-arguments/blob/main/Appendix-B.ipynb)

This is the code repository for the project, also known as _Appendix C_.

## Description

Lawyers, doctors, and other experts rely more and more on machine learning systems that make predictions. The predictions may be about important issues such as: "What is the likelihood that this criminal commits another crime if I release them on probation?" In such a case the expert wants to be absolutely sure that the prediction of the machine learning system is correct and ethically sound. The best way would be if the system could explain the decision to the expert in the way that another human expert would explain it. It would say things like: "In general, criminals on probation do not commit crimes. But when they have already committed more than 10 heavy crimes, like criminal K. has, they usually do commit another crime when on probation." This is the human way of justifying things: Giving arguments, considering exceptions to these arguments, and putting multiple small arguments together to build big, convincing arguments.

### The problem

Traditional machine learning systems do not give explanations like humans do. Some systems cannot give explanations at all, some systems can only give more or less cryptic statistical values to support their conclusion. Yet there are also systems that base their predictions on rules -- these systems are already relatively well comprehensible for humans. The most well-known of these rule-based systems are decision trees and association rules. But the rules that they give often work like this: The system has a set of rules and whenever it has to make a prediction, it chooses exactly one suitable rule that it applies. The consequence is that each rule tends to be long and complicated, and that the set of rules is not structured in a meaningful way. Moreover, these rules require that all the possibly relevant information is known, and when we know only a part of the information, we may not be able to use any rule at all.


### The solution

In our project, we build and evaluate a machine learning system that does better, by using not numbers or rules, but simple arguments that can have exceptions and that can be composed together. Multiple researchers have precisely formalized the idea of argumentation. We want to use the definition by Bart Verheij. Their definition has been applied to reasoning about legal cases, so we know that it is really usable by humans. Bart Verheij has proposed that their definitions are also useful for making explainable machine learning systems, and this idea is what we are investigating in this project.

### The approach

Our project involves multiple steps: 

- First, we make a survey of existing machine learning systems that are related to rules or arguments, to see whether they are helpful for our project. 

- Second, we implement different systems: One of them uses decision trees. Another one is based on systematic searching for good rules, and subsequently removing rules that are less relevant. Yet another one is from the literature (the "HeRo" algorithm, see Johnston and Governatori 2003) and follows the idea of iteratively generating the most useful argument given the set of already found arguments. 

- Third, after implementing these algorithms, we try them out on existing data sets of various sizes, trying to predict, for example, housing prices, or the weather. We also generate some artificial data sets to demonstrate the weaknesses and strengths of the different systems. 

- One important issue for all systems is: How do we convert numerical data to simple categories such as "low price", "medium price", "high price"? We put some focus on this question by considering different techniques for binning and clustering numbers into categories. 

In the end, we have a machine learning system that is even more human-understandable than existing systems and works by putting arguments together and considering exceptions.


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
cd src
python main.py
```

## Testing

Inside the virtual environment (see above) execute the following in the console:

```
cd src
pytest
```

There are some more tests inside `Appendix B.ipynb`, which can be run by opening the notebook within a [Jupyter Notebook](https://jupyter.org/) environment.

## Mini bibliography

[Bart Verheij.](https://www.ai.rug.nl/~verheij/) [‘Proof with and without Probabilities’.](https://core.ac.uk/download/pdf/232520479.pdf) Artificial Intelligence and Law 25, no. 1 (2017): 127–54.

Bart Verheij. [‘Arguments for Good Artificial Intelligence’.](http://www.ai.rug.nl/~verheij/publications/oratie/oratie_Bart_Verheij.pdf) Inaugural lecture. Groningen: University of Groningen, 2018.

[Benjamin Johnston](https://www.benjaminjohnston.com.au/) ([@bjau](https://github.com/bjau)) and [Guido Governatori](http://www.governatori.net/). [‘An Algorithm for the Induction of Defeasible Logic Theories from Databases’.](https://core.ac.uk/download/pdf/14982404.pdf) In Proceedings of the 14th Australasian Database Conference-Volume 17, 75–83, 2003.






![Logo of the Department of Data Science and Knowledge Engineering, Uni Maastricht](dke-logo.png)
