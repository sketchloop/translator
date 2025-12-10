# Quenya-inspired module (non-canonical; structured for completeness)
# Supports: noun plural, genitive, allative; verb present/past/future; person-number agreement.
from dataclasses import dataclass
from typing import Dict
from engine import Wordform

meta = {
    "name": "Quenya-inspired",
    "key": "quenya",
    "order": "SOV",  # Subject-Object-Verb tendency
}

# Lexicon format:
# en_word -> { lemma_en, pos, lemma_lang, gloss }
lexicon_en: Dict[str, Dict] = {
    "friend": {"lemma_en": "friend", "pos": "NOUN", "lemma_lang": "meldo", "gloss": "friend"},
    "king": {"lemma_en": "king", "pos": "NOUN", "lemma_lang": "aran", "gloss": "king"},
    "queen": {"lemma_en": "queen", "pos": "NOUN", "lemma_lang": "tári", "gloss": "queen"},
    "light": {"lemma_en": "light", "pos": "NOUN", "lemma_lang": "calë", "gloss": "light"},
    "darkness": {"lemma_en": "darkness", "pos": "NOUN", "lemma_lang": "mórë", "gloss": "darkness"},
    "water": {"lemma_en": "water", "pos": "NOUN", "lemma_lang": "nen", "gloss": "water"},
    "ring": {"lemma_en": "ring", "pos": "NOUN", "lemma_lang": "corma", "gloss": "ring"},
    "bring": {"lemma_en": "bring", "pos": "VERB", "lemma_lang": "tulya", "gloss": "bring"},
    "bind": {"lemma_en": "bind", "pos": "VERB", "lemma_lang": "notya", "gloss": "bind"},
    "see": {"lemma_en": "see", "pos": "VERB", "lemma_lang": "cenda", "gloss": "see"},
    "love": {"lemma_en": "love", "pos": "VERB", "lemma_lang": "melë", "gloss": "love"},
    "the": {"lemma_en": "the", "pos": "DET", "lemma_lang": "i", "gloss": "the"},
    "to": {"lemma_en": "to", "pos": "ADP", "lemma_lang": "na", "gloss": "to"},
    "of": {"lemma_en": "of", "pos": "ADP", "lemma_lang": "o", "gloss": "of"},
    "and": {"lemma_en": "and", "pos": "CONJ", "lemma_lang": "ar", "gloss": "and"},
    "I": {"lemma_en": "I", "pos": "PRON", "lemma_lang": "ni", "gloss": "I"},
    "you": {"lemma_en": "you", "pos": "PRON", "lemma_lang": "le", "gloss": "you"},
}

# Reverse mapping (lang lemma -> English lemma)
lexicon_lang_to_en = {v["lemma_lang"]: k for k, v in lexicon_en.items()}

# Morphology rules (simplified, stylized)
def noun_plural(stem: str) -> str:
    # e.g., "corma" -> "cormar"
    if stem.endswith(("a", "o")):
        return stem + "r"
    if stem.endswith("ë"):
        return stem[:-1] + "i"
    return stem + "i"

def noun_genitive(stem: str) -> str:
    # add -o or -on depending on ending
    if stem.endswith("a"):
        return stem[:-1] + "o"
    return stem + "o"

def noun_allative(stem: str) -> str:
    # to/towards: -nna
    return stem + "nna"

def verb_present(stem: str, person: str, number: str) -> str:
    # stem + -a/-ë plus agreement suffix
    base = stem if stem.endswith("a") else stem + "a"
    suf = _verb_agreement_suffix(person, number)
    return base + suf

def verb_past(stem: str, person: str, number: str) -> str:
    base = stem + "në"
    suf = _verb_agreement_suffix(person, number)
    return base + suf

def verb_future(stem: str, person: str, number: str) -> str:
    base = stem + "uva"
    suf = _verb_agreement_suffix(person, number)
    return base + suf

def _verb_agreement_suffix(person: str, number: str) -> str:
    # stylized endings
    table = {
        ("1", "SG"): "n",
        ("2", "SG"): "l",
        ("3", "SG"): "",
        ("1", "PL"): "lmë",
        ("2", "PL"): "lvë",
        ("3", "PL"): "r",
    }
    return table.get((person, number), "")

def translate_lemma_en_to_lang(lemma_en: str, pos: str) -> str:
    entry = lexicon_en.get(lemma_en)
    return entry["lemma_lang"] if entry else lemma_en

def translate_lemma_lang_to_en(lemma_lang: str, pos: str) -> str:
    return lexicon_lang_to_en.get(lemma_lang, lemma_lang)

def syntax_map(tokens):
    # Convert approximate English SVO into Quenya-like SOV + postpositions where helpful
    # We’ll mark features for case to drive morphology.
    out = []
    subject_idx, verb_idx, object_idx = None, None, None
    for i, t in enumerate(tokens):
        if t.pos == "PRON" or (t.pos == "NOUN" and subject_idx is None):
            subject_idx = i
        if t.pos == "VERB":
            verb_idx = i
        if t.pos == "NOUN" and i != subject_idx:
            object_idx = i

    for i, t in enumerate(tokens):
        t.feats = dict(t.feats or {})
        if i == object_idx:
            t.feats["case"] = "ACC"
        if i == subject_idx:
            t.feats["case"] = "NOM"
            # crude person-number from pronouns
            if t.text.lower() in ("i", "I"):
                t.feats["person"] = "1"; t.feats["number"] = "SG"
            elif t.text.lower() == "you":
                t.feats["person"] = "2"; t.feats["number"] = "SG"
            else:
                t.feats.setdefault("person", "3"); t.feats.setdefault("number", "SG")
        out.append(t)

    # Reorder: Subject, Object, Verb
    if subject_idx is not None and verb_idx is not None and object_idx is not None:
        ordered = [out[subject_idx], out[object_idx], out[verb_idx]]
        # plus remaining tokens in original order
        extras = [out[i] for i in range(len(out)) if i not in (subject_idx, object_idx, verb_idx)]
        return ordered + extras
    return out

def inflect_from_lemma(lemma: str, pos: str, feats: Dict[str, str]) -> Wordform:
    if pos == "NOUN":
        case = feats.get("case", "NOM")
        num = feats.get("number", "SG")
        stem = lemma
        if case == "GEN":
            stem = noun_genitive(stem)
        elif case == "ALL":
            stem = noun_allative(stem)
        if num == "PL":
            stem = noun_plural(stem)
        return Wordform(surface=stem, lemma=lemma, pos=pos, feats=feats)
    elif pos == "PRON" or pos == "DET" or pos == "ADP" or pos == "CONJ":
        return Wordform(surface=lemma, lemma=lemma, pos=pos, feats=feats)
    elif pos == "VERB":
        tense = feats.get("tense", "PRS")
        person = feats.get("person", "3")
        number = feats.get("number", "SG")
        if tense == "PRS":
            form = verb_present(lemma, person, number)
        elif tense == "PST":
            form = verb_past(lemma, person, number)
        elif tense == "FUT":
            form = verb_future(lemma, person, number)
        else:
            form = verb_present(lemma, person, number)
        return Wordform(surface=form, lemma=lemma, pos=pos, feats=feats)
    else:
        return Wordform(surface=lemma, lemma=lemma, pos=pos, feats=feats)

def decode_surface_to_en(surface: str, pos: str, feats: Dict[str, str]) -> Wordform:
    # Minimal reverse mapping: use lexicon_lang_to_en and strip common suffixes
    lemma_guess = surface
    for suf in ("nna", "o", "r", "në", "uva", "lmë", "lvë"):
        if surface.endswith(suf):
            lemma_guess = surface.replace(suf, "")
            break
    en_lemma = translate_lemma_lang_to_en(lemma_guess, pos)
    return Wordform(surface=en_lemma, lemma=en_lemma, pos=pos, feats=feats)

def assemble_sentence(wordforms):
    # Join with spaces, capitalize first, keep punctuation from original if present
    words = [wf.surface for wf in wordforms]
    s = " ".join(words)
    return s[:1].upper() + s[1:]
