def normalize_text(text: str) -> str:
  text = text.lower()
  text = " ".join(text.split())
  return text
