#!/usr/bin/env python3
"""
Entry Point Principale - Sistema Modularizzato Printful Creator
Supporta creazione dinamica di prodotti con menu interattivo
"""

import os
import time
from dotenv import load_dotenv
from typing import List, Tuple, Optional

# Import moduli personalizzati
# CAMBIATA QUESTA RIGA: ora importa dal nuovo file modulare
from product_creator_modular import ModularProductCreator
from utils.cloudinary_uploader import create_cloudinary_uploader


def print_banner():
    """Stampa banner di benvenuto"""
    print("🚀 PRINTFUL PRODUCT CREATOR - VERSIONE MODULARE")
    print("=" * 60)
    print("✨ Funzionalità:")
    print("   • Creazione singolo prodotto con selezione dinamica")
    print("   • Creazione di TUTTI i prodotti contemporaneamente")
    print("   • Supporto per 5 tipi di prodotto (Gildan, AS Colour, Yupoong)")  
    print("   • Caricamento automatico varianti dai file JSON")
    print("=" * 60)


def show_creation_modes() -> int:
    """
    Mostra menu modalità di creazione e restituisce la scelta
    
    Returns:
        Numero modalità scelta (1-4)
    """
    print("\n📋 MODALITÀ DI CREAZIONE DISPONIBILI:")
    print("-" * 40)
    print("1. 🎯 Singolo Prodotto")
    print("   └─ Scegli prodotto + design → Crea 1 prodotto")
    print()
    print("2. 🚀 Tutti i Prodotti (NUOVO!)")
    print("   └─ Scegli design → Crea TUTTI e 5 i prodotti")
    print()
    print("3. 📦 Batch Singolo Prodotto")
    print("   └─ Scegli prodotto → Crea con tutti i design")
    print()
    print("4. 🎆 Batch Tutti i Prodotti (MASSIVO!)")
    print("   └─ Tutti i design × Tutti i prodotti")
    print()
    print("q. 🚫 Esci")
    print("-" * 40)
    
    while True:
        try:
            choice = input("Seleziona modalità (1-4 o q): ").strip().lower()
            
            if choice == 'q':
                print("👋 Arrivederci!")
                return 0
            
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                return choice_num
            else:
                print("⚠️ Inserisci un numero tra 1-4 o 'q'")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido o 'q'")
        except KeyboardInterrupt:
            print("\n👋 Arrivederci!")
            return 0


def select_product_type(creator: ModularProductCreator) -> Optional[str]:
    """
    Permette di selezionare un tipo di prodotto
    
    Returns:
        Chiave del prodotto selezionato o None
    """
    available_products = creator.variant_loader.get_available_products()
    
    print(f"\n📦 Seleziona tipo di prodotto:")
    print("-" * 40)
    
    for i, product_type in enumerate(available_products, 1):
        product_info = creator.variant_loader.get_product_info(product_type)
        print(f"{i}. {product_info['name']} ({product_type})")
    
    print("q. Torna al menu principale")
    print("-" * 40)
    
    while True:
        try:
            choice = input(f"Seleziona prodotto (1-{len(available_products)} o q): ").strip().lower()
            
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_products):
                selected_product = available_products[choice_num - 1]
                product_info = creator.variant_loader.get_product_info(selected_product)
                print(f"✅ Selezionato: {product_info['name']}")
                return selected_product
            else:
                print(f"⚠️ Inserisci un numero tra 1-{len(available_products)} o 'q'")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido o 'q'")
        except KeyboardInterrupt:
            print("\n🚫 Operazione annullata")
            return None


def select_design_files(creator: ModularProductCreator, mode: str = "single") -> Optional[List[str]]:
    """
    Seleziona file design basato sulla modalità
    
    Args:
        creator: Istanza ModularProductCreator
        mode: "single" per singolo file, "all" per tutti
        
    Returns:
        Lista file selezionati o None
    """
    files = creator.find_design_files()
    if not files:
        print("❌ Nessun design file trovato nella cartella ricamo/")
        return None
    
    if mode == "all":
        print(f"✅ Modalità batch: tutti i {len(files)} file selezionati")
        return files
    
    # Modalità singolo file
    print(f"\n🎨 Seleziona design file:")
    print("-" * 40)
    
    for i, file in enumerate(files, 1):
        file_size = os.path.getsize(file) / 1024
        filename = os.path.basename(file)
        print(f"{i}. {filename} ({file_size:.1f} KB)")
    
    print("q. Torna al menu principale")
    print("-" * 40)
    
    while True:
        try:
            choice = input(f"Seleziona design (1-{len(files)} o q): ").strip().lower()
            
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num - 1]
                filename = os.path.basename(selected_file)
                print(f"✅ Selezionato: {filename}")
                return [selected_file]
            else:
                print(f"⚠️ Inserisci un numero tra 1-{len(files)} o 'q'")
                
        except ValueError:
            print("⚠️ Inserisci un numero valido o 'q'")
        except KeyboardInterrupt:
            print("\n🚫 Operazione annullata")
            return None


def mode_1_single_product(creator: ModularProductCreator, uploader) -> None:
    """Modalità 1: Singolo Prodotto"""
    print("\n🎯 MODALITÀ: SINGOLO PRODOTTO")
    print("=" * 40)
    
    # 1. Seleziona tipo prodotto
    product_type = select_product_type(creator)
    if not product_type:
        return
    
    # 2. Seleziona design
    design_files = select_design_files(creator, mode="single")
    if not design_files:
        return
    
    design_file = design_files[0]
    
    # 3. Conferma creazione
    product_info = creator.variant_loader.get_product_info(product_type)
    design_filename = os.path.basename(design_file)
    
    print(f"\n📋 RIEPILOGO CREAZIONE:")
    print(f"   🏭 Prodotto: {product_info['name']}")
    print(f"   🎨 Design: {design_filename}")
    
    try:
        variants = creator.variant_loader.load_product_variants(product_type)
        print(f"   💕 Varianti: {len(variants)}")
        estimated_value = len(variants) * 25.00
        print(f"   💰 Valore stimato: €{estimated_value:,.2f}")
    except Exception as e:
        print(f"   ⚠️ Errore caricamento varianti: {e}")
        return
    
    confirm = input("\n🚀 Procedere con la creazione? (s/N): ").strip().lower()
    if confirm != 's':
        print("🚫 Creazione annullata")
        return
    
    # 4. Creazione prodotto
    print(f"\n🗂️ Avvio creazione...")
    result = creator.create_single_product_type(design_file, product_type, uploader)
    
    # 5. Salvataggio risultati
    if result["success"]:
        base_name = os.path.splitext(design_filename)[0]
        filename = f"json/{base_name}_{product_type}.json"
        creator.save_result(result, filename)
        
        print(f"\n🎉 CREAZIONE COMPLETATA CON SUCCESSO!")
        sync_product = result.get("sync_product", {})
        sync_variants = result.get("sync_variants", [])
        print(f"   🆔 Product ID: {sync_product.get('id')}")
        print(f"   📝 Nome: {sync_product.get('name')}")
        print(f"   💕 Varianti create: {len(sync_variants)}")
        print(f"   📄 Risultato salvato: {filename}")
    else:
        print(f"\n❌ CREAZIONE FALLITA")
        print(f"   🛠️ Errore: {result.get('error', 'Errore sconosciuto')}")


def mode_2_all_products(creator: ModularProductCreator, uploader) -> None:
    """Modalità 2: Tutti i Prodotti (NUOVA!)"""
    print("\n🚀 MODALITÀ: TUTTI I PRODOTTI")
    print("=" * 40)
    
    # 1. Seleziona design
    design_files = select_design_files(creator, mode="single")
    if not design_files:
        return
    
    design_file = design_files[0]
    design_filename = os.path.basename(design_file)
    
    # 2. Mostra riepilogo
    available_products = creator.variant_loader.get_available_products()
    total_variants = 0
    
    print(f"\n📋 RIEPILOGO CREAZIONE:")
    print(f"   🎨 Design: {design_filename}")
    print(f"   🏭 Prodotti da creare: {len(available_products)}")
    print(f"\n   📦 Lista prodotti:")
    
    for product_type in available_products:
        try:
            product_info = creator.variant_loader.get_product_info(product_type)
            variants = creator.variant_loader.load_product_variants(product_type)
            total_variants += len(variants)
            print(f"      • {product_info['name']}: {len(variants)} varianti")
        except Exception as e:
            print(f"      • {product_type}: Errore caricamento - {e}")
    
    estimated_value = total_variants * 25.00
    print(f"\n   💕 Varianti totali: {total_variants}")
    print(f"   💰 Valore catalogo stimato: €{estimated_value:,.2f}")
    print(f"   ⏱️ Tempo stimato: ~{len(available_products) * 2} minuti")
    
    confirm = input(f"\n🚀 Procedere con la creazione di TUTTI i {len(available_products)} prodotti? (s/N): ").strip().lower()
    if confirm != 's':
        print("🚫 Creazione annullata")
        return
    
    # 3. Creazione di tutti i prodotti
    print(f"\n🗂️ Avvio creazione di tutti i prodotti...")
    results = creator.create_all_product_types(design_file, uploader)
    
    # 4. Salvataggio risultati
    creator.save_all_products_result(results, design_filename)
    
    # 5. Riepilogo finale
    if results["success"]:
        print(f"\n🎉 CREAZIONE COMPLETATA!")
        print(f"   ✅ Prodotti creati: {results['products_created']}/{results['total_products']}")
        print(f"   💕 Varianti totali: {results['total_variants']}")
        print(f"   📝 Risultati salvati nella cartella json/")
        
        if results['products_created'] < results['total_products']:
            failed_count = results['total_products'] - results['products_created']
            print(f"   ⚠️ Prodotti falliti: {failed_count}")
    else:
        print(f"\n❌ CREAZIONE FALLITA COMPLETAMENTE")
        print(f"   🛠️ Nessun prodotto è stato creato con successo")


def mode_3_batch_single_product(creator: ModularProductCreator, uploader) -> None:
    """Modalità 3: Batch Singolo Prodotto"""
    print("\n📦 MODALITÀ: BATCH SINGOLO PRODOTTO")
    print("=" * 40)
    
    # 1. Seleziona tipo prodotto
    product_type = select_product_type(creator)
    if not product_type:
        return
    
    # 2. Ottieni tutti i design files
    design_files = select_design_files(creator, mode="all")
    if not design_files:
        return
    
    # 3. Mostra riepilogo
    product_info = creator.variant_loader.get_product_info(product_type)
    
    try:
        variants = creator.variant_loader.load_product_variants(product_type)
        variants_per_product = len(variants)
        total_variants = len(design_files) * variants_per_product
        estimated_value = total_variants * 25.00
        
        print(f"\n📋 RIEPILOGO BATCH:")
        print(f"   🏭 Prodotto: {product_info['name']}")
        print(f"   🎨 Design files: {len(design_files)}")
        print(f"   💕 Varianti per prodotto: {variants_per_product}")
        print(f"   💕 Varianti totali: {total_variants}")
        print(f"   💰 Valore stimato: €{estimated_value:,.2f}")
        print(f"   ⏱️ Tempo stimato: ~{len(design_files) * 3} minuti")
    except Exception as e:
        print(f"   ⚠️ Errore caricamento varianti: {e}")
        return
    
    confirm = input(f"\n🚀 Procedere con il batch di {len(design_files)} prodotti? (s/N): ").strip().lower()
    if confirm != 's':
        print("🚫 Batch annullato")
        return
    
    # 4. Creazione batch
    successful_creations = 0
    total_variants_created = 0
    
    for i, design_file in enumerate(design_files, 1):
        design_filename = os.path.basename(design_file)
        print(f"\n{'='*60}")
        print(f"🎨 DESIGN {i}/{len(design_files)}: {design_filename}")
        print(f"{'='*60}")
        
        result = creator.create_single_product_type(design_file, product_type, uploader)
        
        # Salva risultato
        if result["success"]:
            successful_creations += 1
            sync_variants = result.get("sync_variants", [])
            total_variants_created += len(sync_variants)
            
            base_name = os.path.splitext(design_filename)[0]
            filename = f"json/{base_name}_{product_type}.json"
            creator.save_result(result, filename)
            
            print(f"✅ COMPLETATO: {design_filename}")
        else:
            print(f"❌ FALLITO: {design_filename}")
            print(f"   🛠️ Errore: {result.get('error', 'Errore sconosciuto')}")
        
        # Pausa tra le creazioni
        if i < len(design_files):
            print("⏳ Pausa di 3 secondi...")
            time.sleep(3)
    
    # 5. Riepilogo finale
    print(f"\n📊 RIEPILOGO BATCH FINALE:")
    print(f"   ✅ Prodotti creati: {successful_creations}/{len(design_files)}")
    print(f"   💕 Varianti totali: {total_variants_created}")
    
    if successful_creations > 0:
        success_rate = (successful_creations / len(design_files)) * 100
        print(f"   📈 Tasso successo: {success_rate:.1f}%")


def mode_4_batch_all_products(creator: ModularProductCreator, uploader) -> None:
    """Modalità 4: Batch Tutti i Prodotti (MASSIVA!)"""
    print("\n🎆 MODALITÀ: BATCH TUTTI I PRODOTTI")
    print("=" * 40)
    print("⚠️ ATTENZIONE: Questa modalità creerà MOLTI prodotti!")
    
    # 1. Ottieni tutti i design files
    design_files = select_design_files(creator, mode="all")
    if not design_files:
        return
    
    # 2. Calcola statistiche
    available_products = creator.variant_loader.get_available_products()
    total_products_to_create = len(design_files) * len(available_products)
    
    # Calcola varianti totali stimulate
    total_variants_estimate = 0
    for product_type in available_products:
        try:
            variants = creator.variant_loader.load_product_variants(product_type)
            total_variants_estimate += len(variants) * len(design_files)
        except:
            total_variants_estimate += 50 * len(design_files)  # Stima fallback
    
    estimated_value = total_variants_estimate * 25.00
    estimated_time_hours = (total_products_to_create * 2) / 60  # 2 min per prodotto
    
    print(f"\n📋 RIEPILOGO OPERAZIONE MASSIVA:")
    print(f"   🎨 Design files: {len(design_files)}")
    print(f"   📦 Tipi prodotto: {len(available_products)}")
    print(f"   🚀 Prodotti da creare: {total_products_to_create}")
    print(f"   💕 Varianti stimate: {total_variants_estimate:,}")
    print(f"   💰 Valore stimato: €{estimated_value:,.2f}")
    print(f"   ⏱️ Tempo stimato: ~{estimated_time_hours:.1f} ore")
    
    print(f"\n⚠️ QUESTA È UN'OPERAZIONE MOLTO IMPEGNATIVA!")
    confirm = input(f"\n🚀 Sei SICURO di voler procedere? Digita 'CONFERMA' per continuare: ").strip()
    if confirm != 'CONFERMA':
        print("🚫 Operazione annullata")
        return
    
    # 3. Esecuzione massiva
    start_time = time.time()
    successful_creations = 0
    total_variants_created = 0
    
    for design_i, design_file in enumerate(design_files, 1):
        design_filename = os.path.basename(design_file)
        print(f"\n{'█'*60}")
        print(f"🎨 DESIGN {design_i}/{len(design_files)}: {design_filename}")
        print(f"{'█'*60}")
        
        # Crea tutti i prodotti per questo design
        results = creator.create_all_product_types(design_file, uploader)
        
        # Salva risultati
        creator.save_all_products_result(results, design_filename)
        
        # Aggiorna statistiche
        if results["success"]:
            successful_creations += results["products_created"]
            total_variants_created += results["total_variants"]
        
        # Pausa tra design
        if design_i < len(design_files):
            print("⏳ Pausa di 5 secondi tra design...")
            time.sleep(5)
    
    # 4. Riepilogo finale massivo
    total_time = time.time() - start_time
    print(f"\n🎆 OPERAZIONE MASSIVA COMPLETATA!")
    print(f"   ✅ Prodotti creati: {successful_creations}/{total_products_to_create}")
    print(f"   💕 Varianti totali: {total_variants_created}")
    print(f"   ⏱️ Tempo totale: {int(total_time/60)} minuti")
    
    if successful_creations > 0:
        success_rate = (successful_creations / total_products_to_create) * 100
        print(f"   📈 Tasso successo: {success_rate:.1f}%")


def main():
    """Funzione principale"""
    print_banner()
    
    # Carica variabili d'ambiente
    load_dotenv()
    
    API_KEY = os.getenv("PRINTFUL_API_KEY")
    STORE_ID = os.getenv("PRINTFUL_STORE_ID")
    
    if not API_KEY or not STORE_ID:
        print("❌ Credenziali Printful mancanti in .env")
        print("💡 Assicurati di aver configurato:")
        print("   PRINTFUL_API_KEY=your_api_key")
        print("   PRINTFUL_STORE_ID=your_store_id")
        return
    
    try:
        # Inizializza componenti
        print("\n🔧 Inizializzazione sistema...")
        creator = ModularProductCreator(API_KEY, STORE_ID)
        
        print("☁️ Inizializzazione Cloudinary...")
        uploader = create_cloudinary_uploader()
        
        # Verifica connessione store (opzionale)
        print("🏭 Verifica connessione Printful...")
        try:
            store_info = creator.get_store_info()
            if store_info.get("code") == 200:
                store_name = store_info.get("result", {}).get("name", "Sconosciuto")
                print(f"✅ Connesso al store: {store_name}")
            else:
                print("⚠️ Connessione store non verificabile (permessi limitati)")
        except Exception:
            print("⚠️ Salto verifica store")
        
        # Loop menu principale
        while True:
            mode = show_creation_modes()
            
            if mode == 0:  # Uscita
                break
            elif mode == 1:
                mode_1_single_product(creator, uploader)
            elif mode == 2:
                mode_2_all_products(creator, uploader)
            elif mode == 3:
                mode_3_batch_single_product(creator, uploader)
            elif mode == 4:
                mode_4_batch_all_products(creator, uploader)
            
            # Pausa prima di tornare al menu
            if mode > 0:
                input("\n⏸️ Premi INVIO per tornare al menu principale...")
    
    except KeyboardInterrupt:
        print("\n\n👋 Operazione interrotta dall'utente")
    except Exception as e:
        print(f"\n❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Grazie per aver usato Printful Product Creator!")


if __name__ == "__main__":
    main()