#!/usr/bin/env python3
"""
Main per creazione singola variante - Test specifico
"""

import os
import time
from dotenv import load_dotenv
from typing import List, Optional, Dict

# Import moduli personalizzati
from product_creator_modular import ModularProductCreator
from utils.cloudinary_uploader import create_cloudinary_uploader


def print_banner():
    """Stampa banner"""
    print("🎯 CREATORE SINGOLA VARIANTE")
    print("=" * 40)
    print("   Crea un prodotto con una sola variante specifica")
    print("=" * 40)


def select_design_file(creator: ModularProductCreator) -> Optional[str]:
    """Seleziona design file"""
    files = creator.find_design_files()
    if not files:
        print("❌ Nessun design file trovato nella cartella ricamo/")
        return None
    
    print(f"\n🎨 Design files:")
    print("-" * 30)
    
    for i, file in enumerate(files, 1):
        filename = os.path.basename(file)
        print(f"{i}. {filename}")
    
    print("q. Esci")
    print("-" * 30)
    
    while True:
        try:
            choice = input(f"Seleziona (1-{len(files)} o q): ").strip().lower()
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(files):
                return files[choice_num - 1]
            else:
                print(f"⚠️ Numero non valido")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido")
        except KeyboardInterrupt:
            return None


def select_product_type(creator: ModularProductCreator) -> Optional[str]:
    """Seleziona tipo prodotto"""
    products = creator.variant_loader.get_available_products()
    
    print(f"\n📦 Prodotti:")
    print("-" * 30)
    
    for i, product_type in enumerate(products, 1):
        info = creator.variant_loader.get_product_info(product_type)
        print(f"{i}. {info['name']}")
    
    print("q. Esci")
    print("-" * 30)
    
    while True:
        try:
            choice = input(f"Seleziona (1-{len(products)} o q): ").strip().lower()
            if choice == 'q':
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(products):
                return products[choice_num - 1]
            else:
                print(f"⚠️ Numero non valido")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido")
        except KeyboardInterrupt:
            return None


def select_variant(creator: ModularProductCreator, product_type: str) -> Optional[Dict]:
    """Seleziona una singola variante"""
    try:
        variants = creator.variant_loader.load_product_variants(product_type)
    except Exception as e:
        print(f"❌ Errore caricamento varianti: {e}")
        return None
    
    print(f"\n💕 Varianti disponibili ({len(variants)}):")
    print("-" * 50)
    
    # Mostra prime 20 varianti per evitare overflow
    display_variants = variants[:20]
    
    for i, variant in enumerate(display_variants, 1):
        color = variant.get('color', 'N/A')
        size = variant.get('size', 'N/A')
        price = variant.get('price', 0)
        print(f"{i:2d}. {color:<15} {size:<8} €{price:.2f}")
    
    if len(variants) > 20:
        print(f"... e altre {len(variants) - 20} varianti")
    
    print("q. Esci")
    print("-" * 50)
    
    while True:
        try:
            choice = input(f"Seleziona variante (1-{len(display_variants)} o q): ").strip().lower()
            if choice == 'q':
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(display_variants):
                selected = display_variants[choice_num - 1]
                color = selected.get('color', 'N/A')
                size = selected.get('size', 'N/A')
                print(f"✅ Selezionata: {color} {size}")
                return selected
            else:
                print(f"⚠️ Numero non valido")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido")
        except KeyboardInterrupt:
            return None


def create_single_variant_product(creator: ModularProductCreator, design_file: str, 
                                product_type: str, variant: Dict, uploader) -> Dict:
    """Crea un prodotto con una singola variante"""
    
    design_filename = os.path.basename(design_file)
    design_name = os.path.splitext(design_filename)[0]
    
    # Prepara URLs
    urls = creator._prepare_urls(design_file, uploader)
    
    # Nome prodotto con info variante
    product_info = creator.variant_loader.get_product_info(product_type)
    color = variant.get('color', 'N/A')
    size = variant.get('size', 'N/A')
    product_name = f"{design_name} - {product_info['name']} - {color} {size}"
    
    print(f"\n🏗️ Creazione prodotto singola variante:")
    print(f"   📝 Nome: {product_name}")
    print(f"   🎨 Design: {design_filename}")
    print(f"   📦 Prodotto: {product_info['name']}")
    print(f"   💕 Variante: {color} {size}")
    
    try:
        # Crea configurazione per la singola variante
        from placement_config import create_variant_files_config
        
        files_config = create_variant_files_config(
            product_type, urls["design_url"], urls["logo_url"], urls["upscaled_url"]
        )
        
        sync_variant = {
            "retail_price": f"{variant['price']:.2f}",
            "variant_id": variant["variant_id"],
            "files": files_config
        }
        
        # Payload per creazione prodotto
        product_data = {
            "sync_product": {
                "name": product_name,
                "thumbnail": urls["design_url"]
            },
            "sync_variants": [sync_variant]  # Solo una variante
        }
        
        print("🚀 Invio richiesta a Printful...")
        
        # Crea prodotto
        response = creator.api_client.make_request("POST", "/store/products", product_data)
        
        if response.get("code") in [200, 201] and "result" in response:
            result = response["result"]
            sync_product = result.get("sync_product", {})
            
            return {
                "success": True,
                "product_id": sync_product.get("id"),
                "sync_product": sync_product,
                "sync_variants": result.get("sync_variants", []),
                "variant_created": variant,
                "urls": urls
            }
        else:
            return {
                "success": False,
                "error": f"Errore API: {response}",
                "response": response
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Funzione principale"""
    print_banner()
    
    load_dotenv()
    
    API_KEY = os.getenv("PRINTFUL_API_KEY")
    STORE_ID = os.getenv("PRINTFUL_STORE_ID")
    
    if not API_KEY or not STORE_ID:
        print("❌ Credenziali Printful mancanti")
        return
    
    try:
        # Inizializza sistema
        print("\n🔧 Inizializzazione...")
        creator = ModularProductCreator(API_KEY, STORE_ID)
        uploader = create_cloudinary_uploader()
        
        # Selezione parametri
        design_file = select_design_file(creator)
        if not design_file:
            return
        
        product_type = select_product_type(creator)
        if not product_type:
            return
        
        variant = select_variant(creator, product_type)
        if not variant:
            return
        
        # Crea prodotto
        result = create_single_variant_product(creator, design_file, product_type, variant, uploader)
        
        # Mostra risultato
        if result["success"]:
            print(f"\n🎉 PRODOTTO CREATO!")
            print(f"   🆔 ID: {result['product_id']}")
            print(f"   📝 Nome: {result['sync_product'].get('name')}")
            
            # Salva risultato
            base_name = os.path.splitext(os.path.basename(design_file))[0]
            filename = f"json/{base_name}_{product_type}_SINGLE_VARIANT.json"
            creator.save_result(result, filename)
            print(f"   📄 Salvato: {filename}")
            
        else:
            print(f"\n❌ CREAZIONE FALLITA")
            print(f"   Errore: {result.get('error')}")
    
    except KeyboardInterrupt:
        print("\n👋 Operazione annullata")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()