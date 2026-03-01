"""
build_index.py

Builds a FAISS index from the SAMA MeSH descriptor bank and persists both
the index and metadata to disk for fast loading at query time.

Replaces the original in-memory build_mesh_index function with:
  - Entry term enrichment in text construction
  - FAISS index serialization to disk
  - A companion load_mesh_index function for query-time loading

Usage (from scripts/build_faiss_index.py):
    from mesh_semantic.mesh.build_index import build_and_save_mesh_index
    build_and_save_mesh_index(mesh_records, embed_fn, index_path, metadata_path)

At query time:
    from mesh_semantic.mesh.build_index import load_mesh_index
    index, metadata = load_mesh_index(index_path, metadata_path)
"""

import faiss
import numpy as np
import pickle
import logging
from pathlib import Path

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Text construction
# ---------------------------------------------------------------------------

def build_term_text(mesh: dict, max_entry_terms: int = 10) -> str:
    """
    Construct enriched text representation of a MeSH descriptor for embedding.

    Combines:
      - Preferred name
      - Scope note (if present)
      - Entry terms / synonyms (up to max_entry_terms)

    This richer text gives SPECTER2 more signal to position the term
    accurately in semantic space, improving recall for sources that use
    non-canonical terminology.
    """
    parts = [f"{mesh['name']}."]

    if mesh.get("scope"):
        parts.append(mesh["scope"])

    entry_terms = mesh.get("entry_terms", [])[:max_entry_terms]
    if entry_terms:
        parts.append(f"Also known as: {', '.join(entry_terms)}.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Build and save
# ---------------------------------------------------------------------------

def build_and_save_mesh_index(
    mesh_records: list[dict],
    embed_fn,
    index_path: str = "data/mesh/mesh.index",
    metadata_path: str = "data/mesh/mesh_metadata.pkl",
    max_entry_terms: int = 10,
) -> tuple:
    """
    Embed all MeSH descriptors, build a FAISS flat inner product index,
    and persist both index and metadata to disk.

    Args:
        mesh_records:    List of descriptor dicts from descriptors.json
        embed_fn:        Callable that takes a text string and returns a
                         normalized numpy vector
        index_path:      Output path for the FAISS binary index file
        metadata_path:   Output path for the pickled metadata list
        max_entry_terms: Maximum entry terms to include in embedded text

    Returns:
        (index, metadata) tuple — same interface as the original build_mesh_index
    """
    log.info(f"Building FAISS index for {len(mesh_records)} descriptors...")

    vectors = []
    metadata = []

    for i, mesh in enumerate(mesh_records):
        text = build_term_text(mesh, max_entry_terms)
        vec = embed_fn(text)
        vectors.append(vec)
        metadata.append(mesh)

        if (i + 1) % 500 == 0:
            log.info(f"  Embedded {i + 1} / {len(mesh_records)} descriptors")

    log.info("All descriptors embedded. Building FAISS index...")

    dimension = len(vectors[0])
    index = faiss.IndexFlatIP(dimension)
    index.add(np.vstack(vectors).astype(np.float32))

    # Persist index
    index_out = Path(index_path)
    index_out.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_out))
    log.info(f"FAISS index saved to {index_path}")

    # Persist metadata
    metadata_out = Path(metadata_path)
    with open(metadata_out, "wb") as f:
        pickle.dump(metadata, f)
    log.info(f"Metadata saved to {metadata_path}")

    return index, metadata


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_mesh_index(
    index_path: str = "data/mesh/mesh.index",
    metadata_path: str = "data/mesh/mesh_metadata.pkl",
) -> tuple:
    """
    Load a persisted FAISS index and metadata from disk.

    This replaces the build step at query time — call this instead of
    build_and_save_mesh_index for all normal pipeline runs.

    Args:
        index_path:    Path to the saved FAISS binary index file
        metadata_path: Path to the saved pickled metadata list

    Returns:
        (index, metadata) tuple — same interface as build_and_save_mesh_index
    """
    log.info(f"Loading FAISS index from {index_path}...")
    index = faiss.read_index(index_path)

    log.info(f"Loading metadata from {metadata_path}...")
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    log.info(f"Index loaded: {index.ntotal} descriptors, dimension {index.d}")
    return index, metadata


# ---------------------------------------------------------------------------
# Legacy compatibility
# ---------------------------------------------------------------------------

def build_mesh_index(mesh_records: list[dict], embed_fn) -> tuple:
    """
    Original in-memory build function retained for compatibility.
    For production use, prefer build_and_save_mesh_index + load_mesh_index.
    """
    vectors = []
    metadata = []

    for mesh in mesh_records:
        text = build_term_text(mesh)
        vec = embed_fn(text)
        vectors.append(vec)
        metadata.append(mesh)

    index = faiss.IndexFlatIP(len(vectors[0]))
    index.add(np.vstack(vectors).astype(np.float32))

    return index, metadata
