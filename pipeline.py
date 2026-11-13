"""
pipeline.py — Module 2 Project Starter
Your job: implement each method in the DataPipeline class below.
The docstrings describe exactly what each method should do.
"""

import os
import pandas as pd
import re
import matplotlib
matplotlib.use("Agg")  # Prevent errors when no display is available
import matplotlib.pyplot as plt


class DataPipeline:
    """
    A data processing pipeline for employee survey data.

    Usage (once implemented):
        pipeline = DataPipeline("data/messy_employee_survey.csv")
        results = pipeline.run()
    """

    # Canonical spellings for normalization — use these dicts in your clean() method.
    DEPT_MAP = {
        "engineering": "Engineering",
        "eng":         "Engineering",
        "marketing":   "Marketing",
        "mktg":        "Marketing",
        "sales":       "Sales",
        "hr":          "HR",
        "human resources": "HR",
        "h.r.":        "HR",
        "finance":     "Finance",
        "fin":         "Finance",
    }

    LOC_MAP = {
        "new york":        "New York",
        "nyc":             "New York",
        "chicago":         "Chicago",
        "chi":             "Chicago",
        "austin":          "Austin",
        "austin, tx":      "Austin",
        "atx":             "Austin",
        "seattle":         "Seattle",
        "sea":             "Seattle",
        "remote":          "Remote",
        "work from home":  "Remote",
    }

    def __init__(self, filepath):
        """Load the CSV at `filepath` into self.df (a pandas DataFrame).
        Print how many rows and columns were loaded.

        Hint: use pd.read_csv()
        Wrap the load in try/except to catch FileNotFoundError.

        Args:
            filepath: path to the messy CSV file
        """
        try:
            df = pd.read_csv(filepath)
        except FileNotFoundError:
            print("Invalid filepath")
            df = pd.DataFrame() # Loads empty dataframe if csv file not found

        print(df.shape) # Print number of rows and columns loaded
        self.df = df

    def clean(self):
        """Clean the DataFrame stored in self.df and print a summary.

        Steps (in order):
        1. Remove rows with duplicate employee_id (keep first occurrence).
           Hint: df.drop_duplicates(subset=["employee_id"], keep="first")

        2. Standardize 'name' — strip whitespace, title case.
           Hint: df["name"].str.strip().str.title()

        3. Normalize 'department' — map messy variants to canonical names.
           Hint: df["department"].str.strip().str.lower().map(self.DEPT_MAP)

        4. Normalize 'office_location' — same pattern as department.
           Hint: use self.LOC_MAP

        5. Convert 'salary' to float — strip "$" and "," first, flip signs of negatives.
           Hint: write a helper function and use df["salary"].apply(helper)
                 import re; re.sub(r"[$,]", "", str(val)) strips the symbols

        6. Convert 'years_experience' to numeric; set values > 50 to None (outliers).
           Hint: pd.to_numeric(..., errors="coerce")

        7. Convert 'satisfaction_score' to numeric; clamp values outside 1-10.

        8. Parse 'survey_date' — multiple formats exist (MM/DD/YYYY, YYYY-MM-DD, DD-MM-YYYY).
           Hint: write a helper that tries pd.to_datetime(val, format=fmt) for each format.
                 Formats to try: "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"

        After all steps, reassign self.df = df and print a missing-values summary.

        Returns self so calls can be chained: pipeline.clean().analyze()
        """
        df = self.df.copy() # Create a copy of the original dataframe to avoid modifying it directly

        duplicate_count = df.duplicated(subset=["employee_id"]).sum() # Count duplicate employee ids
        df = df.drop_duplicates(subset=["employee_id"], keep="first") # Drop rows with duplicate employee ids
        print(f"Removed {duplicate_count} duplicate rows based on employee_id.") # Print number of duplicates removed

        df["name"] = df["name"].str.strip().str.title()               # Normalize names to title case

        df["department"] = df["department"].str.strip().str.lower().map(self.DEPT_MAP)          # Normalize department and map according to canonical names

        df["office_location"] = df["office_location"].str.strip().str.lower().map(self.LOC_MAP) # Normalize office location and map according to canonical names

        strip_symbols = lambda x : re.sub(r"[$,]", "", str(x))        # Helper lambda function for cleaning '$' and ',' characters
        df["salary"] = df["salary"].apply(strip_symbols)              # Apply helper function to salary column
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce")   # Convert salary to numeric values
        negative_salaries = df[df["salary"] < 0].shape[0]             # Count negative salaries
        df["salary"] = df["salary"].abs()                             # Flip signs of negative salaries
        print(f"Flipped signs of {negative_salaries} negative salary values.") # Print number of negative salaries flipped
        print(f"Removed {df['salary'].isnull().sum()} invalid salary values.") # Print number of missing/invalid values in salary column

        df["years_experience"] = pd.to_numeric(df["years_experience"], errors="coerce")                 # Convert years_experience to numeric values
        df.loc[(df["years_experience"] < 0) | (df["years_experience"] > 50), "years_experience"] = None # Set negative or excessive values to None
        print(f"Removed {df['years_experience'].isnull().sum()} invalid years_experience values.") # Print number of missing/invalid values in years_experience column

        df["satisfaction_score"] = pd.to_numeric(df["satisfaction_score"], errors="coerce")            # Convert satisfaction_score to numeric values
        invalid_satisfaction = df[(df["satisfaction_score"] < 1) | (df["satisfaction_score"] > 10)].shape[0] # Count invalid satisfaction scores
        df.loc[df["satisfaction_score"] < 1, "satisfaction_score"] = 1                                 # Set values below 1 to 1
        df.loc[df["satisfaction_score"] > 10, "satisfaction_score"] = 10                               # Set values above 10 to 10
        print(f"Clamped {invalid_satisfaction} invalid satisfaction_score values.")                    # Print number of invalid satisfaction scores clamped
        print(f"Removed {df['satisfaction_score'].isnull().sum()} missing satisfaction_score values.") # Print number of missing satisfaction scores

        df["survey_date"] = df["survey_date"].apply(self._parse_survey_date) # Parse survey_date column with multiple formats

        self.df = df
        return self # Return self to allow method chaining

    def _parse_survey_date(self, value):
        """Helper function to parse survey_date with multiple formats.

        Try each format in order: "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y".
        If all fail, return None.

        Args:
            value: a single survey_date value (string)
        Returns:
            A pandas Timestamp if parsing succeeds, else None.
        """
        formats = ["%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return pd.to_datetime(value, format=fmt)
            except (ValueError, TypeError):
                continue
        return None

    def analyze(self):
        """Compute summary statistics from the cleaned self.df.

        Compute and print:
        1. Average salary by department
           Hint: df.groupby("department")["salary"].mean().round(0)

        2. Average satisfaction score by department

        3. Headcount by office location
           Hint: df["office_location"].value_counts()

        4. Pearson correlation between years_experience and salary
           Hint: drop rows where either is NaN, then Series.corr()

        5. One additional insight of your choice (e.g., satisfaction by location)

        Return a dict with all results so main.py can use them.
        Keys to use: "avg_salary_by_dept", "avg_satisfaction_by_dept",
                     "headcount_by_location", "experience_salary_correlation",
                     "avg_satisfaction_by_location"
        """
        df = self.df.copy() # Create a copy of the cleaned dataframe to avoid modifying it directly

        avg_salary_by_dept = df.groupby("department")["salary"].mean().round(0)                   # Average salary by department
        avg_satisfaction_by_dept = df.groupby("department")["satisfaction_score"].mean().round(2) # Average satisfaction score by department
        headcount_by_location = df["office_location"].value_counts()                              # Headcount by office location

        # Pearson correlation between years_experience and salary
        experience_salary_correlation = df[["years_experience", "salary"]].dropna().corr().loc["years_experience", "salary"]

        avg_satisfaction_by_location = df.groupby("office_location")["satisfaction_score"].mean().round(2) # Average satisfaction score by location

        results = {
            "avg_salary_by_dept": avg_salary_by_dept,
            "avg_satisfaction_by_dept": avg_satisfaction_by_dept,
            "headcount_by_location": headcount_by_location,
            "experience_salary_correlation": experience_salary_correlation,
            "avg_satisfaction_by_location": avg_satisfaction_by_location
        }

        # print(f"Analysis results:\n{results}") # Print analysis results
        return results

    def visualize(self, output_path="output/charts.png"):
        """Create and save visualizations to `output_path`.

        Required charts:
        - Bar chart: average salary by department
        - Histogram: satisfaction score distribution (bins 1–10)
        Bonus:
        - Horizontal bar: headcount by office location

        Use matplotlib with plt.subplots() for a multi-chart layout.
        Save with plt.savefig(output_path, dpi=120, bbox_inches="tight").
        Call plt.close() after saving.

        Hint: import matplotlib; matplotlib.use("Agg") at top of file
              prevents errors when no display is available.

        Args:
            output_path: where to save the PNG file
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6)) # Create a figure with 1 row and 3 columns of subplots
        axes[0].bar(self.df.groupby("department")["salary"].mean().index, self.df.groupby("department")["salary"].mean().round(0)) # Bar chart for average salary by department
        axes[0].set_title("Average Salary by Department")
        axes[0].set_ylabel("Average Salary")

        axes[1].hist(self.df["satisfaction_score"].dropna(), bins=10, range=(1, 10), edgecolor='black') # Histogram for satisfaction score distribution
        axes[1].set_title("Satisfaction Score Distribution")
        axes[1].set_xlabel("Satisfaction Score")
        axes[1].set_ylabel("Frequency")

        axes[2].barh(self.df["office_location"].value_counts().index, self.df["office_location"].value_counts()) # Horizontal bar chart for headcount by office location
        axes[2].set_title("Headcount by Office Location")
        axes[2].set_xlabel("Headcount")

        plt.tight_layout() # Adjust layout to prevent overlap

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True) # Create output directory if it doesn't exist
        except Exception as e:
            print(f"Error creating output directory: {e}") # Print error message if directory creation fails    
        plt.savefig(output_path, dpi=120, bbox_inches="tight") # Save the figure
        print(f"Charts saved to {output_path}") # Print success message
        plt.close() # Close the figure to free memory

    def export(self, output_path="output/clean_employees.csv"):
        """Save the cleaned self.df to a CSV at `output_path`.

        Create the output directory if it doesn't exist.
        Wrap in try/except.

        Hint: df.to_csv(output_path, index=False)

        Args:
            output_path: path for the exported CSV
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True) # Create output directory if it doesn't exist
            self.df.to_csv(output_path, index=False) # Save the cleaned dataframe to CSV
            print(f"Cleaned data exported to {output_path}") # Print success message
        except Exception as e:
            print(f"Error exporting cleaned data: {e}") # Print error message if export fails

    def run(self):
        """Execute the full pipeline: clean → analyze → visualize → export.

        Build output paths using os.path.join(os.path.dirname(__file__), "output", ...).
        Return the results dict from analyze().
        """
        
        self.clean()
        result = self.analyze()
        self.visualize(os.path.join(os.path.dirname(__file__), "output", "charts.png"))
        self.export(os.path.join(os.path.dirname(__file__), "output", "clean_employees.csv"))
        return result