"""Populate PostgreSQL with SAXS data from CSV files."""

import os
from pathlib import Path

import pandas as pd
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://saxs@localhost:5432/saxs",
)

DATA_DIR = Path(__file__).parent.parent / "assets" / "samples"


def load_csv(filepath: Path) -> pd.DataFrame:
    """Load SAXS CSV file (q, intensity, error)."""
    df = pd.read_csv(
        filepath,
        names=["q", "intensity", "error"],
        header=None,
    )
    return df.dropna()


def populate_bulk(filepath: Path, conn) -> int:
    """Bulk insert using COPY (faster)."""
    from io import StringIO

    df = load_csv(filepath)
    cur = conn.cursor()

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cur.copy_from(
        buffer, "saxs_data", sep=",", columns=("q", "intensity", "error")
    )
    conn.commit()
    cur.close()

    return len(df)


def populate_all():
    """Populate database with all CSV files from test data directory."""
    conn = psycopg2.connect(DATABASE_URL)
    total = 0

    for csv_file in DATA_DIR.glob("*.csv"):
        count = populate_bulk(csv_file, conn)
        print(f"Inserted {count} rows from {csv_file.name}")
        total += count

    conn.close()
    print(f"Total: {total} rows inserted")
    return total


if __name__ == "__main__":
    populate_all()
