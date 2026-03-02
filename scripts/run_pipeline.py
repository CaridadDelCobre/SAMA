"""
run_pipeline.py

Dynamic SAMA pipeline script. Accepts a CSV of source materials and prints
MeSH assignments for each source to the console.

Input CSV format (required columns):
    id      - Unique identifier for the source (e.g. PI name, grant number)
    label   - Human-readable label for the source
    text    - Plain text content to embed and assign MeSH terms to

Usage:
    python scripts/run_pipeline.py --input path/to/sources.csv

Optional arguments:
    --index       Path to FAISS index (default: data/mesh/mesh.index)
    --metadata    Path to metadata pickle (default: data/mesh/mesh_metadata.pkl)
"""

import sys
import os
import csv
import argparse
import logging

sys.path.append(os.path.abspath("."))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

from mesh_semantic.embedding.model import load_model
from mesh_semantic.mesh.build_index import load_mesh_index
from mesh_semantic.pipeline.process import process_source
import config.settings as config


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = {"id", "label", "text"}

def load_input_csv(input_path: str) -> list[dict]:
    """
    Load and validate the input CSV. Returns a list of row dicts.
    Exits with a helpful error if required columns are missing.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            log.error(
                f"Input CSV is missing required columns: {missing}\n"
                f"Required columns are: {REQUIRED_COLUMNS}\n"
                f"Found columns: {columns}"
            )
            sys.exit(1)
        rows = [row for row in reader if row["text"].strip()]

    log.info(f"Loaded {len(rows)} sources from {input_path}")
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Run SAMA MeSH assignment pipeline.")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV with columns: id, label, text"
    )
    parser.add_argument(
        "--index",
        default="data/mesh/mesh.index",
        help="Path to FAISS index (default: data/mesh/mesh.index)"
    )
    parser.add_argument(
        "--metadata",
        default="data/mesh/mesh_metadata.pkl",
        help="Path to metadata pickle (default: data/mesh/mesh_metadata.pkl)"
    )
    args = parser.parse_args()

    # Validate index files exist
    if not os.path.exists(args.index) or not os.path.exists(args.metadata):
        log.error(
            "FAISS index not found. Please run the following first:\n"
            "    python scripts/build_faiss_index.py"
        )
        sys.exit(1)

    # Load model
    log.info(f"Loading model: {config.MODEL_NAME}")
    tokenizer, model = load_model(config.MODEL_NAME)

    # Load index
    mesh_index, mesh_meta = load_mesh_index(args.index, args.metadata)

    # Load input
    sources = load_input_csv(args.input)

    # Run pipeline and print results
    for i, source in enumerate(sources):
        print(f"\n{'='*60}")
        print(f"Source {i + 1}: {source['label']} (ID: {source['id']})")
        print(f"{'='*60}")

        try:
            _, mesh_hits = process_source(
                source["text"],
                tokenizer,
                model,
                mesh_index,
                mesh_meta,
                config
            )

            if mesh_hits:
                print(f"MeSH assignments ({len(mesh_hits)} terms above threshold {config.MIN_SIMILARITY}):")
                for hit in mesh_hits:
                    print(f"  [{hit['score']:.4f}] {hit['mesh_term']}")
            else:
                print(
                    f"No MeSH terms met the similarity threshold ({config.MIN_SIMILARITY}). "
                    f"Consider lowering MIN_SIMILARITY in config/settings.py."
                )

        except Exception as e:
            log.error(f"Failed to process source {source['id']}: {e}")

    print(f"\n{'='*60}")
    print(f"Pipeline complete. {len(sources)} sources processed.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
