# Feature utilities for grammatical agreement
def merge_feats(base, extra):
    out = dict(base or {})
    out.update(extra or {})
    return out

def guess_number_en(word):
    if word.endswith("s") and len(word) > 3:
        return "PL"
    return "SG"
