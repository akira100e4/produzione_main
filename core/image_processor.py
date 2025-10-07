from PIL import Image
import os

def create_left_aligned_image(image_path: str, 
                              canvas_multiplier: float = 3.0, 
                              margin_percent: float = 0.1,
                              scale_factor: float = 1.0) -> str:
    """
    Args:
        scale_factor: Fattore ingrandimento logo (1.5 = +50%, 2.0 = +100%)
    """
    img = Image.open(image_path).convert('RGBA')
    
    # INGRANDISCI logo
    if scale_factor != 1.0:
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Crea canvas (basato su dimensione INGRANDITA)
    new_width = int(img.width * canvas_multiplier)
    canvas = Image.new('RGBA', (new_width, img.height), (0, 0, 0, 0))
    
    # Posiziona a sinistra
    left_margin = int(img.width * margin_percent)
    canvas.paste(img, (left_margin, 0), img)
    
    # Salva
    base, ext = os.path.splitext(image_path)
    temp_path = f"{base}_hat_left{ext}"
    canvas.save(temp_path)
    
    return temp_path

def create_beanie_image_with_text(logo_path: str, 
                                   text_path: str,
                                   output_folder: str = "1120",
                                   spacing: int = 20,
                                   scale_factor: float = 1.5) -> str:
    """
    Args aggiunto:
        scale_factor: Ingrandimento immagine finale (1.5 = +50%)
    """
    # Apri immagini
    logo = Image.open(logo_path).convert('RGBA')
    text = Image.open(text_path).convert('RGBA')
    
    # Calcola dimensioni canvas
    max_width = max(logo.width, text.width)
    total_height = logo.height + spacing + text.height
    
    # Crea canvas
    canvas = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))
    
    # Centra logo in alto
    logo_x = (max_width - logo.width) // 2
    canvas.paste(logo, (logo_x, 0), logo)
    
    # Centra testo sotto
    text_x = (max_width - text.width) // 2
    text_y = logo.height + spacing
    canvas.paste(text, (text_x, text_y), text)
    
    # INGRANDISCI l'immagine composita
    if scale_factor != 1.0:
        new_size = (
            int(canvas.width * scale_factor),
            int(canvas.height * scale_factor)
        )
        canvas = canvas.resize(new_size, Image.Resampling.LANCZOS)
    
    # Salva
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.basename(logo_path)
    output_path = os.path.join(output_folder, filename)
    canvas.save(output_path)
    
    return output_path