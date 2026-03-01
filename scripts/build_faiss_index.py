
"""
build_faiss_index.py

One-time script to build and persist the SAMA FAISS index from the
MeSH descriptor bank in data/mesh/descriptors.json.

Run this whenever descriptors.json is updated (e.g. after a new MeSH
annual release or changes to branch filtering in build_mesh_bank.py).

The output files (mesh.index and mesh_metadata.pkl) are gitignored --
they are build artifacts regenerated from descriptors.json as needed.

Usage:
    python scripts/build_faiss_index.py

Optional arguments:
    --descriptors  Path to descriptors JSON (default: data/mesh/descriptors.json)
    --index        Path for output FAISS index (default: data/mesh/mesh.index)
    --metadata     Path for output metadata pickle (default: data/mesh/mesh_metadata.pkl)
"""

import sys
import os
import json
import argparse
import logging

sys.path.append(os.path.abspath("."))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

from mesh_semantic.embedding.model import load_model
from mesh_semantic.embedding.encode import embed
from mesh_semantic.mesh.build_index import build_and_save_mesh_index
import config.settings as config


def main():
    parser = argparse.ArgumentParser(description="Build and persist SAMA FAISS index.")
    parser.add_argument(
        "--descriptors",
        default="data/mesh/descriptors.json",
        help="Path to MeSH descriptors JSON (default: data/mesh/descriptors.json)"
    )
    parser.add_argument(
        "--index",
        default="data/mesh/mesh.index",
        help="Output path for FAISS index (default: data/mesh/mesh.index)"
    )
    parser.add_argument(
        "--metadata",
        default="data/mesh/mesh_metadata.pkl",
        help="Output path for metadata pickle (default: data/mesh/mesh_metadata.pkl)"
    )
    args = parser.parse_args()

    # Load model
    log.info(f"Loading model: {config.MODEL_NAME}")
    tokenizer, model = load_model(config.MODEL_NAME)

    # Load descriptors
    log.info(f"Loading descriptors from: {args.descriptors}")
    with open(args.descriptors) as f:
        mesh_records = json.load(f)
    log.info(f"Loaded {len(mesh_records)} descriptors")

    # Build and save
    embed_fn = lambda text: embed(text, tokenizer, model)
    build_and_save_mesh_index(
        mesh_records,
        embed_fn,
        index_path=args.index,
        metadata_path=args.metadata,
    )

    log.info("Done. Index is ready for use.")


if __name__ == "__main__":
    main()
