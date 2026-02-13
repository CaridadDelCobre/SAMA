def chunk_text(text, tokenizer, max_tokens, overlap):
  tokens = tokenizer.tokenize(text) # turns the text into tokens
  if len(tokens) <= max_tokens: # checks condition for not chunking
    return [text]

  chunks = []
  step = max_tokens - overlap
  for i in range(0, len(tokens), step):
    chunk_tokens = tokens[i:i + max_tokens]
    chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
    chunks.append(chunk_text)

  return chunks
