#!/usr/bin/env python3
"""
Test Script - Creazione immagine composita beanie
Per testare dimensioni e layout prima di integrare
"""

from PIL import Image
import os


def create_beanie_composite(logo_path: str, 
                            text_path: str,
                            output_path: str = "test_beanie_output.png",
                            spacing: int = -10,
                            logo_scale: float = 1.5,
                            final_scale: float = 1.0):
    """
    Crea immagine composita per test
    
    Args:
        logo_path: Path logo principale
        text_path: Path testo "The Only One"
        output_path: Dove salvare output
        spacing: Pixel tra logo e testo
        logo_scale: Quanto ingrandire il logo (1.5 = +50%)
        final_scale: Quanto ingrandire immagine finale (1.5 = +50%)
    """
    print(f"\n📸 CREAZIONE IMMAGINE COMPOSITA BEANIE")
    print("=" * 60)
    
    # Carica immagini
    print(f"📂 Caricamento immagini...")
    print(f"   Logo: {logo_path}")
    print(f"   Testo: {text_path}")
    
    logo = Image.open(logo_path).convert('RGBA')
    text = Image.open(text_path).convert('RGBA')
    
    print(f"\n📏 Dimensioni originali:")
    print(f"   Logo: {logo.width}x{logo.height} px")
    print(f"   Testo: {text.width}x{text.height} px")
    
    # Ingrandisci logo SE richiesto
    if logo_scale != 1.0:
        new_logo_size = (
            int(logo.width * logo_scale),
            int(logo.height * logo_scale)
        )
        logo = logo.resize(new_logo_size, Image.Resampling.LANCZOS)
        print(f"\n🔍 Logo ingrandito {logo_scale}x: {logo.width}x{logo.height} px")
    
    # Calcola dimensioni canvas
    max_width = max(logo.width, text.width)
    total_height = logo.height + spacing + text.height
    
    print(f"\n📐 Canvas composito:")
    print(f"   Larghezza: {max_width} px")
    print(f"   Altezza: {total_height} px")
    print(f"   Spacing: {spacing} px")
    
    # Crea canvas trasparente
    canvas = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))
    
    # Centra logo in alto
    logo_x = (max_width - logo.width) // 2
    canvas.paste(logo, (logo_x, 0), logo)
    
    # Centra testo sotto
    text_x = (max_width - text.width) // 2
    text_y = logo.height + spacing
    canvas.paste(text, (text_x, text_y), text)
    
    # Ingrandisci canvas finale SE richiesto
    if final_scale != 1.0:
        final_size = (
            int(canvas.width * final_scale),
            int(canvas.height * final_scale)
        )
        canvas = canvas.resize(final_size, Image.Resampling.LANCZOS)
        print(f"\n🔍 Canvas finale ingrandito {final_scale}x: {canvas.width}x{canvas.height} px")
    
    # Salva
    canvas.save(output_path)
    print(f"\n✅ Immagine salvata: {output_path}")
    print(f"   Dimensioni finali: {canvas.width}x{canvas.height} px")
    
    return output_path


def test_multiple_configs():
    """Test con diverse configurazioni"""
    
    logo_path = "ricami/Farfalla Cosmica.png"
    text_path = "generate/the_only_one_text_darkgray.png"
    
    # Verifica file esistono
    if not os.path.exists(logo_path):
        print(f"❌ Logo non trovato: {logo_path}")
        return
    
    if not os.path.exists(text_path):
        print(f"❌ Testo non trovato: {text_path}")
        return
    
    # Test diverse configurazioni - SPACING 0
    configs = [
        {
            "name": "Test 1: Spacing 0px, logo +80%",
            "spacing": -10,
            "logo_scale": 1.8,
            "final_scale": 1.0,
            "output": "test_beanie_1.png"
        },
        {
            "name": "Test 2: Spacing 0px, logo +85%",
            "spacing": -10,
            "logo_scale": 1.85,
            "final_scale": 1.0,
            "output": "test_beanie_2.png"
        },
        {
            "name": "Test 3: Spacing 0px, logo +90%",
            "spacing": -10,
            "logo_scale": 1.9,
            "final_scale": 1.0,
            "output": "test_beanie_3.png"
        },
        {
            "name": "Test 4: Spacing 0px, logo +100%",
            "spacing": -10,
            "logo_scale": 2.0,
            "final_scale": 1.0,
            "output": "test_beanie_4.png"
        }
    ]
    
    print("\n🧪 TEST MULTIPLI CONFIGURAZIONI")
    print("=" * 60)
    
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}] {config['name']}")
        print("-" * 60)
        
        create_beanie_composite(
            logo_path=logo_path,
            text_path=text_path,
            output_path=config["output"],
            spacing=config["spacing"],
            logo_scale=config["logo_scale"],
            final_scale=config["final_scale"]
        )
    
    print(f"\n\n🎉 COMPLETATO!")
    print("Controlla i file generati:")
    for config in configs:
        print(f"   - {config['output']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Modalità test multipli
        test_multiple_configs()
    
    elif len(sys.argv) >= 3:
        # Modalità singola personalizzata
        logo = sys.argv[1]
        text = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "output.png"
        spacing = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        logo_scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1.5
        
        create_beanie_composite(logo, text, output, spacing, logo_scale)
    
    else:
        print("Uso:")
        print("  python test_beanie_composite.py")
        print("    → Genera 4 test con configurazioni diverse")
        print()
        print("  python test_beanie_composite.py <logo> <text> [output] [spacing] [logo_scale]")
        print("    → Configurazione manuale")