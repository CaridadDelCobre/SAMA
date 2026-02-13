import torch
import numpy as np
def mean_pool(hidden_states):
  return hidden_states.mean(dim=1).squeeze()

def embed(text, tokenizer, model):
  inputs = tokenizer(
    text,
    return_tensors='pt',
    truncation=True,
    max_length=512
  )

  with torch.no_grad():
    outputs = model(**inputs)

  emb = mean_pool(outputs.last_hidden_state)
  emb = emb / emb.norm()
  return emb.numpy()
