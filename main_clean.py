#!/usr/bin/env python3
"""
Main - Entry point pulito per Product Creator
Versione refactorata con architettura modulare
"""

import os
import sys
from dotenv import load_dotenv

from product_creator_clean import create_product_creator
from utils.cloudinary_uploader import CloudinaryUploader
from config.products import get_all_products, get_product_name, print_products_summary
from config.placements import get_hat_positions_summary


def print_menu():
    """Stampa menu principale"""
    print("\n" + "=" * 60)
    print("🚀 PRINTFUL PRODUCT CREATOR - VERSIONE MODULARE")
    print("=" * 60)
    print("\n📋 OPZIONI:")
    print("  1. Crea singolo prodotto")
    print("  2. Crea tutti i prodotti per un design")
    print("  3. Batch - Tutti design × Tutti prodotti")
    print("  4. Info prodotti disponibili")
    print("  5. Info posizioni cappelli")
    print("  q. Esci")
    print("-" * 60)


def select_product(creator) -> str:
    """Seleziona tipo prodotto"""
    products = creator.get_available_products()
    
    print("\n📦 SELEZIONA PRODOTTO:")
    for i, product_type in enumerate(products, 1):
        print(f"  {i}. {get_product_name(product_type)} ({product_type})")
    
    while True:
        try:
            choice = input(f"\nProdotto (1-{len(products)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(products):
                return products[idx]
            print(f"❌ Scegli tra 1-{len(products)}")
        except (ValueError, KeyboardInterrupt):
            return None


def select_design(creator) -> str:
    """Seleziona file design"""
    files = creator.find_design_files()
    
    if not files:
        print("❌ Nessun design trovato in ricamo/")
        return None
    
    print("\n🎨 SELEZIONA DESIGN:")
    for i, file in enumerate(files, 1):
        filename = os.path.basename(file)
        size_kb = os.path.getsize(file) / 1024
        print(f"  {i}. {filename} ({size_kb:.1f} KB)")
    
    while True:
        try:
            choice = input(f"\nDesign (1-{len(files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
            print(f"❌ Scegli tra 1-{len(files)}")
        except (ValueError, KeyboardInterrupt):
            return None


def mode_single_product(creator):
    """Modalità: Singolo prodotto"""
    print("\n🎯 MODALITÀ: SINGOLO PRODOTTO")
    
    # Seleziona prodotto
    product_type = select_product(creator)
    if not product_type:
        return
    
    # Seleziona design
    design_file = select_design(creator)
    if not design_file:
        return
    
    # Conferma
    print(f"\n📋 RIEPILOGO:")
    print(f"   Prodotto: {get_product_name(product_type)}")
    print(f"   Design: {os.path.basename(design_file)}")
    
    confirm = input("\n🚀 Procedere? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Annullato")
        return
    
    # Creazione
    print("\n⏳ Creazione in corso...")
    result = creator.create_product(design_file, product_type)
    
    # Salvataggio
    if result["success"]:
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        filename = f"{design_name}_{product_type}.json"
        creator.save_result(result, filename)
        
        print(f"\n✅ SUCCESSO!")
        print(f"   ID Prodotto: {result['product_id']}")
        print(f"   Varianti: {result['variants_count']}")
    else:
        print(f"\n❌ ERRORE: {result.get('error', 'Unknown')}")


def mode_all_products(creator):
    """Modalità: Tutti prodotti per un design"""
    print("\n🎯 MODALITÀ: TUTTI I PRODOTTI")
    
    # Seleziona design
    design_file = select_design(creator)
    if not design_file:
        return
    
    # Conferma
    products_count = len(get_all_products())
    print(f"\n📋 RIEPILOGO:")
    print(f"   Design: {os.path.basename(design_file)}")
    print(f"   Prodotti da creare: {products_count}")
    
    confirm = input("\n🚀 Procedere? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Annullato")
        return
    
    # Creazione batch
    print("\n⏳ Creazione batch in corso...")
    results = creator.create_all_products(design_file)
    
    # Salvataggio
    creator.save_batch_results(results, os.path.basename(design_file))
    
    # Risultati
    print(f"\n📊 RISULTATI:")
    print(f"   ✅ Successi: {results['success_count']}")
    print(f"   ❌ Fallimenti: {results['failure_count']}")


def mode_batch_all(creator):
    """Modalità: Tutti design × Tutti prodotti"""
    print("\n🎯 MODALITÀ: BATCH COMPLETO")
    
    files = creator.find_design_files()
    
    if not files:
        print("❌ Nessun design trovato")
        return
    
    # Conferma
    products_count = len(get_all_products())
    total_operations = len(files) * products_count
    
    print(f"\n📋 RIEPILOGO:")
    print(f"   Design files: {len(files)}")
    print(f"   Prodotti per design: {products_count}")
    print(f"   Totale operazioni: {total_operations}")
    
    confirm = input("\n🚀 Procedere? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Annullato")
        return
    
    # Batch completo
    print("\n⏳ Batch completo in corso...")
    
    total_success = 0
    total_failure = 0
    
    for i, design_file in enumerate(files, 1):
        design_name = os.path.basename(design_file)
        print(f"\n[{i}/{len(files)}] 🎨 {design_name}")
        
        results = creator.create_all_products(design_file)
        creator.save_batch_results(results, design_name)
        
        total_success += results['success_count']
        total_failure += results['failure_count']
    
    # Risultati finali
    print(f"\n{'=' * 60}")
    print(f"📊 RISULTATI FINALI:")
    print(f"   Design processati: {len(files)}")
    print(f"   ✅ Prodotti creati: {total_success}")
    print(f"   ❌ Fallimenti: {total_failure}")
    print(f"{'=' * 60}")


def show_products_info():
    """Mostra info prodotti"""
    print()
    print_products_summary()


def show_hat_positions():
    """Mostra info posizioni cappelli"""
    print()
    print(get_hat_positions_summary())
    print("\n💡 Per modificare le posizioni, edita config/placements.py")
    print("   Cerca la sezione HAT_PLACEMENTS")


def main():
    """Entry point principale"""
    load_dotenv()
    
    # Credenziali
    api_key = os.getenv("PRINTFUL_API_KEY")
    store_id = os.getenv("PRINTFUL_STORE_ID")
    
    if not api_key or not store_id:
        print("❌ Credenziali mancanti!")
        print("   Imposta PRINTFUL_API_KEY e PRINTFUL_STORE_ID in .env")
        sys.exit(1)
    
    # Setup
    try:
        uploader = CloudinaryUploader(
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        )
        
        creator = create_product_creator(
            api_key, store_id, uploader, verbose=True
        )
        
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        sys.exit(1)
    
    # Menu loop
    while True:
        try:
            print_menu()
            choice = input("Scegli opzione: ").strip().lower()
            
            if choice == '1':
                mode_single_product(creator)
            elif choice == '2':
                mode_all_products(creator)
            elif choice == '3':
                mode_batch_all(creator)
            elif choice == '4':
                show_products_info()
            elif choice == '5':
                show_hat_positions()
            elif choice == 'q':
                print("\n👋 Arrivederci!")
                break
            else:
                print("❌ Opzione non valida")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrotto")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}")


if __name__ == "__main__":
    main()