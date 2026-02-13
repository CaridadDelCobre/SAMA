from transformers import AutoTokenizer, AutoModel

def load_model(model_name):
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModel.from_pretrained(model_name)
  model.eval()
  return tokenizer, model
