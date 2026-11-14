"""CLI entry point to execute EarthScope Data Ingestion & Preprocessing Pipeline."""

import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.data_pipeline.pipeline import EarthScopePipeline


def main():
    pipeline = EarthScopePipeline()
    res = pipeline.run_all()
    print("\n✓ Pipeline execution completed successfully.")
    print(f"Processed variables: {res['variables_processed']}")
    print(f"Aligned multi-variable months: {res['multi_variable_aligned_months']}")


if __name__ == "__main__":
    main()
