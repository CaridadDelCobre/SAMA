from mesh_semantic.text.normalize import normalize_text
from mesh_semantic.text.chunk import chunk_text
from mesh_semantic.embedding.encode import embed
from mesh_semantic.mesh.project import project_to_mesh

def process_source(text, tokenizer, model, mesh_index, mesh_meta, config):
  text = normalize_text(text)
  chunks = chunk_text(
    text,
    tokenizer,
    config.MAX_TOKENS,
    config.CHUNK_OVERLAP
  )

  embeddings = [embed(c, tokenizer, model) for c in chunks]
  source_embedding = sum(embeddings) / len(embeddings)

  mesh_hits = project_to_mesh(
    source_embedding,
    mesh_index,
    mesh_meta,
    config.TOP_K_MESH,
    config.MIN_SIMILARITY
  )

  return source_embedding, mesh_hits
