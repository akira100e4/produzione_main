from PIL import Image
import os

def compose_right_center(
    src_path: str,
    dst_path: str,
    area_width: int = 1031,
    area_height: int = 1375,
    scale: float = 0.8,
    right_offset: int = 0
) -> None:
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    src_img = Image.open(src_path)
    if src_img.mode != 'RGBA':
        src_img = src_img.convert('RGBA')
    
    src_w, src_h = src_img.size
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    
    resized_img = src_img.resize((new_w, new_h), Image.LANCZOS)
    
    canvas = Image.new('RGBA', (area_width, area_height), (0, 0, 0, 0))
    
    top = round((area_height - new_h) / 2)
    left = area_width - new_w - right_offset
    
    canvas.paste(resized_img, (left, top), resized_img)
    
    canvas.save(dst_path, 'PNG')

def compose_center(
    src_path: str,
    dst_path: str,
    area_width: int = 1031,
    area_height: int = 1375,
    scale: float = 0.7
) -> None:
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    src_img = Image.open(src_path)
    if src_img.mode != 'RGBA':
        src_img = src_img.convert('RGBA')
    
    src_w, src_h = src_img.size
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    
    resized_img = src_img.resize((new_w, new_h), Image.LANCZOS)
    
    canvas = Image.new('RGBA', (area_width, area_height), (0, 0, 0, 0))
    
    top = round((area_height - new_h) / 2)
    left = round((area_width - new_w) / 2)
    
    canvas.paste(resized_img, (left, top), resized_img)
    
    canvas.save(dst_path, 'PNG')

if __name__ == "__main__":
    choice = input("Vuoi l'immagine all'estrema destra (r) o centrale (c)? ").lower()
    
    if choice == 'r':
        compose_right_center("ricami/Farfalla Cosmica.png", "ricamo/Farfalla Cosmica.png")
    elif choice == 'c':
        compose_center("ricami/Farfalla Cosmica.png", "ricamo/Farfalla Cosmica.png")
    else:
        print("Scelta non valida")