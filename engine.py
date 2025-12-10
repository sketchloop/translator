from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class Token:
    text: str
    lemma: Optional[str] = None
    pos: Optional[str] = None
    feats: Dict[str, str] = None  # grammatical features
    lang: str = "en"

@dataclass
class Wordform:
    surface: str
    lemma: str
    pos: str
    feats: Dict[str, str]

class TranslatorEngine:
    def __init__(self, language_module):
        self.lang_mod = language_module

    def pos_tag(self, tokens: List[Token]) -> List[Token]:
        # POS via lexicon; fallback simple heuristics
        for tok in tokens:
            entry = self.lang_mod.lexicon_en.get(tok.text.lower())
            if entry:
                tok.lemma = entry["lemma_en"]
                tok.pos = entry["pos"]
            else:
                tok.lemma = tok.text.lower()
                tok.pos = self._guess_pos(tok.text)
            tok.feats = tok.feats or {}
        return tokens

    def _guess_pos(self, word: str) -> str:
        # Very naive heuristic to keep pipeline running
        if word.endswith("ing"):
            return "VERB"
        if word.endswith("ly"):
            return "ADV"
        if word.endswith("ed"):
            return "VERB"
        return "NOUN"

    def syntax_map(self, tokens: List[Token]) -> List[Token]:
        # Map English syntax to target language syntax (e.g., SVO -> SOV)
        return self.lang_mod.syntax_map(tokens)

    def translate_lemmas(self, tokens: List[Token], direction: str = "encode") -> List[Token]:
        # English -> target language lemma mapping (or reverse)
        out = []
        for tok in tokens:
            mapped = Token(text=tok.text, lemma=tok.lemma, pos=tok.pos, feats=dict(tok.feats or {}))
            if direction == "encode":
                mapped.lemma = self.lang_mod.translate_lemma_en_to_lang(tok.lemma, tok.pos)
                mapped.lang = self.lang_mod.meta["key"]
            else:
                mapped.lemma = self.lang_mod.translate_lemma_lang_to_en(tok.lemma or tok.text.lower(), tok.pos)
                mapped.lang = "en"
            out.append(mapped)
        return out

    def morph_generate(self, tokens: List[Token], direction: str = "encode") -> List[Wordform]:
        wordforms = []
        for tok in tokens:
            feats = dict(tok.feats or {})
            if tok.pos == "VERB":
                # propagate subject-person features if present
                pass
            if direction == "encode":
                wf = self.lang_mod.inflect_from_lemma(tok.lemma, tok.pos, feats)
            else:
                # Decode path: try to decompose surface to lemma first
                wf = self.lang_mod.decode_surface_to_en(tok.text, tok.pos, feats)
            wordforms.append(wf)
        return wordforms

    def assemble(self, wordforms: List[Wordform]) -> str:
        return self.lang_mod.assemble_sentence(wordforms)

    def translate(self, text: str, direction: str = "encode") -> str:
        from tokenizer import tokenize
        tokens = [Token(t) for t in tokenize(text)]
        tokens = self.pos_tag(tokens)
        tokens = self.syntax_map(tokens)
        tokens = self.translate_lemmas(tokens, direction=direction)
        wordforms = self.morph_generate(tokens, direction=direction)
        return self.assemble(wordforms)
