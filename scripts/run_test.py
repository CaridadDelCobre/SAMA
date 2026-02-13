import json
from mesh_semantic.embedding.model import load_model
from mesh_semantic.embedding.encode import embed
from mesh_semantic.mesh.build_index import build_mesh_index
from mesh_semantic.pipeline.process import process_source
import config.settings as config

# Load Model
tokenizer, model = load_model(config.MODEL_NAME)

# Load MeSH
with open("scripts/test_mesh.json") as f:
  mesh_records = json.load(f)

# Build MeSH index
mesh_index, mesh_meta = build_mesh_index(
  mesh_records,
  lambda txt: embed(txt, tokenizer, model)
)

# Test Input
profile_text = """
My research focuses on obesity and metabolic disease, with a particular interest in insulin resitance and lifestyle-based interventions such as physical activity.
"""

# Run pipeline
embedding, mesh_hits = process_source(
  profile_text,
  tokenizer,
  model,
  mesh_index,
  mesh_meta,
  config
)

print("Top MeSH matches:")
for hit in mesh_hits:
  print(hit)
