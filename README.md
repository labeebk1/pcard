# Toronto PCard Expenditures

<img src="https://img.shields.io/badge/python-3.7.7-blue"/>
<img src="https://img.shields.io/badge/documentation-no-red" />

The following repository runs a HDBSCAN clustering algorithm on the City of Toronto Division's based on their purchases from 2011 to 2019.

## Requirements

Please install the following libraries in requirements.txt

```bash
pip install -r requirements.txt
```

please download and extract the pcard-expenditures data from [here](https://open.toronto.ca/dataset/pcard-expenditures/) into the /data/raw_data/ folder.

## Pipeline

### Commands
------------------------

1. Run the cleaning script

```bash
python clean_data.py
```

2. Create Profiles

```bash
python profiles.py
```

3. Run the Model

```bash
python clustering.py
```