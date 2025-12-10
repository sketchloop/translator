import re

WORD_RE = re.compile(r"[A-Za-z']+|[^\sA-Za-z']")

def tokenize(text: str):
    return WORD_RE.findall(text)
