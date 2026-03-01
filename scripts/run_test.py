"""
run_test.py

Test script for the SAMA pipeline using the persistent FAISS index.

Workflow:
  1. Load SPECTER2 model
  2. Load persistent FAISS index and metadata from disk
     (run scripts/build_faiss_index.py first if index does not exist)
  3. Run one or more test source profiles through the pipeline
  4. Print MeSH assignments and similarity scores

Usage:
    python scripts/run_test.py
"""

import sys
import os

sys.path.append(os.path.abspath("."))

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

from mesh_semantic.embedding.model import load_model
from mesh_semantic.mesh.build_index import load_mesh_index
from mesh_semantic.pipeline.process import process_source
import config.settings as config

# ---
# Index paths
# ---

INDEX_PATH = "data/mesh/mesh.index"
METADATA_PATH = "data/mesh/mesh_metadata.pkl"

# ---
# Load model
# ---

log.info(f"Loading model: {config.MODEL_NAME}")
tokenizer, model = load_model(config.MODEL_NAME)

# ---
# Load persistent FAISS index
# ---

if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
  log.error(
    "FAISS index not found. Please run the following first:\n"
    "    python scripts/build_faiss_index.py"

  )
  sys.exit(1)

mesh_index, mesh_meta = load_mesh_index(INDEX_PATH, METADATA_PATH)

# ---
# Test sources
# ---

test_sources = [
  {
    "id": "test_001",
    "label": "Obesity and Metabolic Disease Researcher",
    "text": """
      My research focuses on obesity and metabolic disease, with a particular
      interest in insulin resistance and lifestyle-based interventions such as
      physical activity and dietary modification. I use epidemiological methods
      alongside clinical trials to evaluate the effectiveness of behavioral
      interventions in high-risk populations.
    """
  },
  {
    "id": "test_002",
    "label": "Sample Donor Interest Profile",
    "text": """
      Our foundation prioritizes funding initiatives at the intersection of
      mental health and technology. We are especially interested in digital
      therapeutics, mobile health interventions, and efforts to improve access
      to mental health care in underserved communities.
    """
  },
  {
    "id": "test_003",
    "label": "Genomics and Bioinformatics Researcher",
    "text": """
      Our lab applies machine learning and bioinformatics tools to large-scale
      genomic and proteomic datasets. We are particularly interested in identifying
      biomarkers for early cancer detection and understanding the role of gene
      expression in tumor microenvironments.
    """
  },
]

# ---
# Run pipeline
# ---

for source in test_sources:
  print(f"\n{'='*60}")
  print(f"Source: {source['label']} (ID: {source['id']})")
  print(f"{'='*60}")

  embedding, mesh_hits = process_source(
    source["text"],
    tokenizer,
    model,
    mesh_index,
    mesh_meta,
    config
  )

  if mesh_hits:
    print(f"Top MeSH assignments ({len(mesh_hits)} terms above threshold {config.MIN_SIMILARITY}):")
    for hit in mesh_hits:
      print(f" [{hit['score']:.4f}] {hit['mesh_term']}")

  else:
    print(
      f"No MeSH terms met the similarity threshold ({config.MIN_SIMILARITY})."
      f" Consider lowering MIN_SIMILARITY in config/settings.py."
    )















