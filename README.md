# Explainable AI: Learning Arguments

## Usage

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

## Testing

```
pytest
```

(This requires [pytest](https://docs.pytest.org/en/stable/getting-started.html), which can be installed with `pip install -U pytest`.)
