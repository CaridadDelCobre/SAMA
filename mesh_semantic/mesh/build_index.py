import faiss
import numpy as np

def build_mesh_index(mesh_records, embed_fn):
  vectors = []
  metadata = []

  for mesh in mesh_records:
    text = f"{mesh['name']}. {mesh['scope']}."
    vec = embed_fn(text)
    vectors.append(vec)
    metadata.append(mesh)

  index = faiss.IndexFlatIP(len(vectors[0]))
  index.add(np.vstack(vectors))

  return index, metadata
