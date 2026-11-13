"""
main.py — Module 2 Project entry point
Run this file to execute your pipeline.

Once you've implemented DataPipeline in pipeline.py, running:
    python main.py
should load, clean, analyze, visualize, and export the data — all without errors.
"""

import os
from pipeline import DataPipeline

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "messy_employee_survey.csv")


def main():
    print("=" * 60)
    print("Employee Survey Data Pipeline")
    print("=" * 60)

    pipeline = DataPipeline(DATA_PATH)
    results = pipeline.run()

    print("=" * 60)
    print("Analysis Results:")
    for key, value in results.items():
        print(f"{key}: {value}")
    print("=" * 60)

if __name__ == "__main__":
    main()
