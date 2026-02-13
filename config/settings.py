MODEL_NAME = "allenai/specter2_base" #opensource embedding model

MAX_TOKENS = 512 #fundamental unit of text is 1 token (~4 characters)
CHUNK_SIZE = 400 
CHUNK_OVERLAP = 50 #Overlap token range to help with context flow

TOP_K_MESH = 15 # Number of MeSH terms assigned
MIN_SIMILARITY = 0.85 # Minimum cosine similarity for assignment

EXCLUDED_MESH_TERMS = {
  "Humans", "Animals", "Male", "Female"
}
