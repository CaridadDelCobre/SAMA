def project_to_mesh(embedding, index, metadata, top_k, threshold):
  scores, idxs = index.search(embedding.reshape(1, -1), top_k)

  results = []
  for score, idx in zip(scores[0], idxs[0]):
    mesh = metadata[idx]
    if score < threshold:
      continue
    results.append({
      "mesh_term": mesh["name"],
      "score": float(score)
    })
  return results
