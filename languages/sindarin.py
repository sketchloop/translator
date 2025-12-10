# Sindarin-inspired module (non-canonical; structured rules)
from typing import Dict
from engine import Wordform

meta = {
    "name": "Sindarin-inspired",
    "key": "sindarin",
    "order": "SVO",  # tendency toward SVO; lenition rules applied
}

lexicon_en: Dict[str, Dict] = {
    "friend": {"lemma_en": "friend", "pos": "NOUN", "lemma_lang": "mellon", "gloss": "friend"},
    "king": {"lemma_en": "king", "pos": "NOUN", "lemma_lang": "aran", "gloss": "king"},
    "light": {"lemma_en": "light", "pos": "NOUN", "lemma_lang": "galad", "gloss": "light"},
    "darkness": {"lemma_en": "darkness", "pos": "NOUN", "lemma_lang": "morn", "gloss": "darkness"},
    "water": {"lemma_en": "water", "pos": "NOUN", "lemma_lang": "nen", "gloss": "water"},
    "ring": {"lemma_en": "ring", "pos": "NOUN", "lemma_lang": "ereg", "gloss": "ring"},
    "bring": {"lemma_en": "bring", "pos": "VERB", "lemma_lang": "togo", "gloss": "bring"},
    "bind": {"lemma_en": "bind", "pos": "VERB", "lemma_lang": "gorn", "gloss": "bind"},
    "see": {"lemma_en": "see", "pos": "VERB", "lemma_lang": "círa", "gloss": "see"},
    "love": {"lemma_en": "love", "pos": "VERB", "lemma_lang": "meleth", "gloss": "love"},
    "the": {"lemma_en": "the", "pos": "DET", "lemma_lang": "i", "gloss": "the"},
    "to": {"lemma_en": "to", "pos": "ADP", "lemma_lang": "na", "gloss": "to"},
    "of": {"lemma_en": "of", "pos": "ADP", "lemma_lang": "o", "gloss": "of"},
    "and": {"lemma_en": "and", "pos": "CONJ", "lemma_lang": "a", "gloss": "and"},
    "I": {"lemma_en": "I", "pos": "PRON", "lemma_lang": "im", "gloss": "I"},
    "you": {"lemma_en": "you", "pos": "PRON", "lemma_lang": "le", "gloss": "you"},
}

lexicon_lang_to_en = {v["lemma_lang"]: k for k, v in lexicon_en.items()}

def apply_lenition(noun: str) -> str:
    # Initial consonant mutation after certain particles (stylized)
    rules = {
        "p": "b",
        "t": "d",
        "c": "g",
        "m": "v",
        "s": "h",
        "h": "",
        "gw": "w",
    }
    for k, v in rules.items():
        if noun.startswith(k):
            return v + noun[len(k):]
    return noun

def pluralize_noun(stem: str) -> str:
    # Very simplified pluralization
    if stem.endswith("on"):
        return stem[:-2] + "in"
    if stem.endswith("eg"):
        return stem[:-2] + "ig"
    return stem + "in"

def verb_present(stem: str, person: str, number: str) -> str:
    # Simple present, add agreement when needed
    if person == "3" and number == "SG":
        return stem
    if number == "PL":
        return stem + "ir"
    return stem + "a"

def verb_past(stem: str) -> str:
    return stem + "nt"

def verb_future(stem: str) -> str:
    return stem + "tha"

def translate_lemma_en_to_lang(lemma_en: str, pos: str) -> str:
    entry = lexicon_en.get(lemma_en)
    return entry["lemma_lang"] if entry else lemma_en

def translate_lemma_lang_to_en(lemma_lang: str, pos: str) -> str:
    return lexicon_lang_to_en.get(lemma_lang, lemma_lang)

def syntax_map(tokens):
    # Keep SVO; add lenition triggers for 'i' (the) before nouns
    out = []
    prev_det = False
    for t in tokens:
        t.feats = dict(t.feats or {})
        if t.pos == "DET":
            t.feats["det"] = "i"
            prev_det = True
        elif t.pos == "NOUN":
            t.feats["lenite"] = "yes" if prev_det else "no"
            prev_det = False
        elif t.pos == "VERB":
            # infer tense from English surface (placeholder)
            t.feats.setdefault("tense", "PRS")
            prev_det = False
        else:
            prev_det = False
        out.append(t)
    return out

def inflect_from_lemma(lemma: str, pos: str, feats: Dict[str, str]) -> Wordform:
    if pos == "NOUN":
        stem = lemma
        if feats.get("lenite") == "yes":
            stem = apply_lenition(stem)
        if feats.get("number") == "PL":
            stem = pluralize_noun(stem)
        return Wordform(surface=stem, lemma=lemma, pos=pos, feats=feats)
    elif pos == "DET":
        return Wordform(surface="i", lemma=lemma, pos=pos, feats=feats)
    elif pos == "PRON" or pos == "ADP" or pos == "CONJ":
        return Wordform(surface=lemma, lemma=lemma, pos=pos, feats=feats)
    elif pos == "VERB":
        tense = feats.get("tense", "PRS")
        person = feats.get("person", "3")
        number = feats.get("number", "SG")
        if tense == "PRS":
            form = verb_present(lemma, person, number)
        elif tense == "PST":
            form = verb_past(lemma)
        elif tense == "FUT":
            form = verb_future(lemma)
        else:
            form = verb_present(lemma, person, number)
        return Wordform(surface=form, lemma=lemma, pos=pos, feats=feats)
    return Wordform(surface=lemma, lemma=lemma, pos=pos, feats=feats)

def decode_surface_to_en(surface: str, pos: str, feats: Dict[str, str]) -> Wordform:
    # Basic reverse: de-lenite common patterns, strip suffixes
    s = surface
    for pre, base in [("b", "p"), ("d", "t"), ("g", "c"), ("v", "m")]:
        if s.startswith(pre):
            s = base + s[1:]
            break
    for suf in ("in", "ir", "a", "nt", "tha"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    en_lemma = translate_lemma_lang_to_en(s, pos)
    return Wordform(surface=en_lemma, lemma=en_lemma, pos=pos, feats=feats)

def assemble_sentence(wordforms):
    words = [wf.surface for wf in wordforms]
    s = " ".join(words)
    return s[:1].upper() + s[1:]
