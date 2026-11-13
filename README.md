# Module 2 Project: Data Processing Pipeline

## Your mission

You are given a messy employee survey dataset (`data/messy_employee_survey.csv`).
Implement the `DataPipeline` class in `pipeline.py` so that running `main.py`
produces a clean dataset, summary statistics, and visualizations.

## Setup

```bash
pip install -r requirements.txt
```

## Run (once pipeline.py is implemented)

```bash
python main.py
```

## Files

| File | Your task |
|------|-----------|
| `pipeline.py` | Implement all 6 methods in `DataPipeline` |
| `main.py` | Uncomment the pipeline calls and add a summary printout |
| `data/messy_employee_survey.csv` | The raw messy input — do not modify |
| `output/` | Pipeline will save charts and cleaned CSV here |

## Expected output

When complete, your pipeline should produce:
- Console output with a cleaning summary and analysis results
- `output/charts.png` — at least 2 visualizations
- `output/clean_employees.csv` — the cleaned dataset

## Data issues to handle

| Column | Issues |
|--------|--------|
| `employee_id` | Some duplicate IDs |
| `name` | Inconsistent casing, extra whitespace |
| `department` | Variants: `"Eng"`, `"ENGINEERING"`, `"engineering"` |
| `office_location` | Variants: `"NYC"`, `" New York "`, `"new york"` |
| `salary` | Stored as `"$75,000.00"` strings, some negative, some missing |
| `years_experience` | Some missing, one value > 50 (outlier) |
| `satisfaction_score` | Should be 1–10; some outside range, some missing |
| `survey_date` | Three different date formats mixed together |

## Tips

- Work through `clean()` one step at a time — print the DataFrame shape after each
- `df.isnull().sum()` shows you how many missing values each column has
- `pd.to_numeric(..., errors='coerce')` converts strings to numbers safely
- `df["col"].str.strip().str.lower().map(mapping_dict)` is the cleanest normalization pattern
