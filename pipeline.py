import argparse
from engine import TranslatorEngine
from languages import quenya, sindarin

LANGS = {
    "quenya": quenya,
    "sindarin": sindarin,
}

def main():
    parser = argparse.ArgumentParser(description="Full fantasy translator (lemma + morphology + syntax)")
    parser.add_argument("language", choices=list(LANGS.keys()))
    parser.add_argument("direction", choices=["encode", "decode"], help="encode: EN->lang, decode: lang->EN")
    parser.add_argument("text", help="Text to translate")
    args = parser.parse_args()

    engine = TranslatorEngine(LANGS[args.language])
    print(engine.translate(args.text, direction=args.direction))

if __name__ == "__main__":
    main()
