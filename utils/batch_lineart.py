#!/usr/bin/env python3
import os, base64, pathlib, sys, time, csv, io
from typing import Iterable
from openai import OpenAI

# Carica le variabili d'ambiente dal file .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Installare python-dotenv: pip install python-dotenv", file=sys.stderr)
    # Se non hai dotenv, puoi comunque usare le variabili d'ambiente del sistema

# === Config principali ===
INPUT_DIR  = pathlib.Path("upscaled")
OUTPUT_DIR = pathlib.Path("ricamo")
MODEL      = "gpt-image-1"
SIZE       = "auto"  # Supportato: '1024x1024', '1024x1536', '1536x1024', 'auto'
QUALITY    = "high" # 'low', 'medium', 'high'
FORMAT     = "png"
BACKGROUND = "transparent"   # mantieni trasparenza
EXTS       = ("*.png",)       # solo PNG, come da tua conferma

# Prompt mirato per RICAMO/LINEART
PROMPT_IT = (
    "Crea un'illustrazione vettoriale pulita basata su questa immagine."
    "Usa solo aree piatte e uniformi di colore (massimo 6 tinte)."
    "I colori devono essere campionati dall'immagine originale e semplificati, senza inventare nuove palette."
    "Applica contorni spessi e uniformi per dare contrasto."
    "Rimuovi texture, gradienti e ombreggiature."
    "Mantieni le proporzioni e i dettagli principali del soggetto, semplificando soltanto gli elementi troppo piccoli o complessi."
    "Lo sfondo deve essere trasparente."
    "Lo stile finale deve essere adatto a ricami o serigrafie: colori piatti, contorni netti, bordi ben definiti."
)

# Variante inglese (se mai volessi alternare)
PROMPT_EN = (
    "Crea un'illustrazione vettoriale pulita basata su questa immagine."
    "Usa solo aree piatte e uniformi di colore (massimo 6 tinte)."
    "I colori devono essere campionati dall'immagine originale e semplificati, senza inventare nuove palette."
    "Applica contorni spessi e uniformi per dare contrasto."
    "Rimuovi texture, gradienti e ombreggiature."
    "Mantieni le proporzioni e i dettagli principali del soggetto, semplificando soltanto gli elementi troppo piccoli o complessi."
    "Lo sfondo deve essere trasparente."
    "Lo stile finale deve essere adatto a ricami o serigrafie: colori piatti, contorni netti, bordi ben definiti."
)

PROMPT = PROMPT_IT

# === Helpers ===
def iter_pngs(root: pathlib.Path) -> Iterable[pathlib.Path]:
    for ext in EXTS:
        yield from root.rglob(ext)

def out_path_for(in_path: pathlib.Path) -> pathlib.Path:
    rel = in_path.relative_to(INPUT_DIR)
    out = (OUTPUT_DIR / rel).with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    return out

def ensure_dirs():
    if not INPUT_DIR.exists():
        print(f"ERRORE: cartella input non trovata: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_png_b64(b64: str, path: pathlib.Path):
    path.write_bytes(base64.b64decode(b64))

def image_edit(client: OpenAI, png_path: pathlib.Path) -> str:
    # Ritorna base64 dell'immagine generata
    with open(png_path, "rb") as f:
        image_bytes = f.read()
    
    # Crea un oggetto file-like con il nome corretto per il MIME type
    image_file = io.BytesIO(image_bytes)
    image_file.name = png_path.name  # Importante: questo aiuta l'API a riconoscere il formato
    
    res = client.images.edit(
        model=MODEL,
        image=image_file,
        prompt=PROMPT,
        size=SIZE,
        quality=QUALITY,
        output_format=FORMAT,
        background=BACKGROUND,
    )
    return res.data[0].b64_json

def convert_one(client: OpenAI, in_path: pathlib.Path, out_path: pathlib.Path, retries=3, delay=0.8) -> bool:
    for attempt in range(1, retries+1):
        try:
            b64 = image_edit(client, in_path)
            save_png_b64(b64, out_path)
            return True
        except Exception as e:
            print(f"  Tentativo {attempt}/{retries} fallito: {e}", file=sys.stderr)
            if attempt < retries:
                time.sleep(delay * attempt)
    return False

def main():
    ensure_dirs()
    
    # Verifica che la chiave API sia presente
    if not os.getenv("OPENAI_API_KEY"):
        print("ERRORE: OPENAI_API_KEY non trovata nelle variabili d'ambiente", file=sys.stderr)
        print("Assicurati che il file .env contenga: OPENAI_API_KEY=la_tua_chiave", file=sys.stderr)
        sys.exit(1)
    
    client = OpenAI()  # ora dovrebbe funzionare

    files = sorted(iter_pngs(INPUT_DIR))
    if not files:
        print("Nessun PNG trovato in 'upscaled/'.")
        return

    # Tracking CSV minimale
    report_path = OUTPUT_DIR / "report.csv"
    write_header = not report_path.exists()
    with open(report_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["input", "output", "status"])

        total = len(files)
        print(f"Trovati {total} PNG. Converto in '{OUTPUT_DIR}/' (size {SIZE}) ...")
        for i, in_path in enumerate(files, 1):
            out_path = out_path_for(in_path)
            if out_path.exists():
                print(f"[{i}/{total}] Skip (già presente): {out_path}")
                writer.writerow([str(in_path), str(out_path), "skip_exists"])
                continue

            print(f"[{i}/{total}] {in_path.name} → {out_path}")
            ok = convert_one(client, in_path, out_path)
            writer.writerow([str(in_path), str(out_path), "ok" if ok else "error"])
            # throttling leggero
            time.sleep(0.25)

    print("Completato.")

if __name__ == "__main__":
    main()