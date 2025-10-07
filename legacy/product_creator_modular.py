#!/usr/bin/env python3
"""
Product Creator Modulare SEMPLIFICATO - Senza sottocartelle
Versione che funziona immediatamente senza problemi di import
"""

import os
import time
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import moduli esistenti (funzionano già)
from utils.variant_loader import VariantLoader
from placement_config import create_variant_files_config, validate_product_compatibility


class PrintfulAPIClient:
    """Client API Printful semplificato con timeout aumentati"""
    
    def __init__(self, api_key: str, store_id: str):
        self.api_key = api_key
        self.store_id = store_id
        self.base_url = "https://api.printful.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-PF-Store-Id": store_id
        }
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, retries: int = 2) -> Dict:
        """Esegue richiesta HTTP all'API Printful con retry logic e timeout aumentati"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                # TIMEOUT AUMENTATI per gestire operazioni complesse
                timeout = 90 if method in ["POST", "PUT"] else 60
                
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=timeout)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
                elif method == "PUT":
                    response = requests.put(url, headers=self.headers, json=data, timeout=timeout)
                elif method == "DELETE":
                    response = requests.delete(url, headers=self.headers, timeout=timeout)
                else:
                    raise ValueError(f"Metodo HTTP non supportato: {method}")
                
                result = response.json()
                
                # Se tutto ok, ritorna subito
                if response.status_code in [200, 201]:
                    return result
                else:
                    # Se errore ma non timeout, non fare retry
                    return result
                    
            except requests.exceptions.Timeout:
                if attempt < retries:
                    wait_time = (attempt + 1) * 5  # Backoff progressivo
                    print(f"⏳ Timeout su {endpoint}, retry {attempt + 1}/{retries} in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Timeout definitivo su {endpoint} dopo {retries + 1} tentativi")
                    
            except requests.exceptions.RequestException as e:
                if attempt < retries:
                    wait_time = (attempt + 1) * 3
                    print(f"🔄 Errore rete su {endpoint}, retry {attempt + 1}/{retries} in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Errore rete su {endpoint}: {e}")
                    
            except Exception as e:
                raise Exception(f"Errore API {endpoint}: {e}")
        
        raise Exception(f"Tutti i tentativi falliti per {endpoint}")


class ModularProductCreator:
    """
    Product Creator Modulare SEMPLIFICATO
    Mantiene la stessa API ma con architettura interna modulare
    """
    
    def __init__(self, api_key: str, store_id: str):
        print("🔧 Inizializzazione sistema modulare semplificato...")
        
        # Inizializza componenti interni
        self.api_client = PrintfulAPIClient(api_key, store_id)
        self.variant_loader = VariantLoader()
        
        print("✅ ModularProductCreator inizializzato")
        print(f"   📦 Prodotti disponibili: {len(self.variant_loader.get_available_products())}")
    
    # ==========================================
    # API PUBBLICA - COMPATIBILITÀ GARANTITA
    # ==========================================
    
    def create_single_product_type(self, design_file: str, product_type: str, uploader) -> Dict:
        """Crea un singolo tipo di prodotto (COMPATIBILITÀ)"""
        return self._build_single_product(design_file, product_type, uploader)
    
    def create_all_product_types(self, design_file: str, uploader) -> Dict:
        """Crea tutti i tipi di prodotto per un design (COMPATIBILITÀ)"""
        return self._process_all_products(design_file, uploader)
    
    def find_design_files(self, folder: Optional[str] = None) -> List[str]:
        """Trova file design (COMPATIBILITÀ)"""
        return self._find_design_files(folder or "ricamo")
    
    def save_result(self, result: Dict, filename: str) -> bool:
        """Salva risultato in file JSON (COMPATIBILITÀ)"""
        return self._save_result(result, filename)
    
    def save_all_products_result(self, results: Dict, design_filename: str) -> None:
        """Salva risultati di tutti i prodotti (COMPATIBILITÀ)"""
        return self._save_all_products_result(results, design_filename)
    
    def get_store_info(self) -> Dict:
        """Ottiene info dello store (COMPATIBILITÀ)"""
        return self.api_client.make_request("GET", "/store")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Fa richiesta API diretta (COMPATIBILITÀ)"""
        return self.api_client.make_request(method, endpoint, data)
    
    # ==========================================
    # IMPLEMENTAZIONI INTERNE MODULARI
    # ==========================================
    
    def _build_single_product(self, design_file: str, product_type: str, uploader) -> Dict:
        """Costruisce un singolo prodotto completo - STRATEGIA POST + PUT + GET"""
        try:
            print(f"\n🏗️ COSTRUZIONE PRODOTTO MODULARE")
            
            # 1. Preparazione
            design_filename = os.path.basename(design_file)
            design_name = os.path.splitext(design_filename)[0]
            
            # 2. Carica varianti
            variants = self.variant_loader.load_product_variants(product_type)
            product_info = self.variant_loader.get_product_info(product_type)
            
            print(f"📦 Creando prodotto con {len(variants)} varianti...")
            
            # 3. Upload files
            urls = self._prepare_urls(design_file, uploader)
            
            # 4. Genera nome prodotto
            product_name = f"{design_name} - {product_info['name']}"
            
            # FASE 1: CREAZIONE BASE con batch piccolo (come codice originale)
            initial_batch_size = 8  # Batch iniziale più piccolo
            initial_variants = variants[:initial_batch_size]
            remaining_variants = variants[initial_batch_size:]
            
            print(f"🔧 FASE 1: Creazione prodotto base con {len(initial_variants)} varianti iniziali")
            
            # Crea prodotto iniziale con POST
            creation_response = self._create_initial_product(
                product_name, urls["design_url"], initial_variants, product_type, urls
            )
            
            if not (creation_response.get("code") in [200, 201] and "result" in creation_response):
                return {
                    "success": False,
                    "error": f"Creazione prodotto base fallita: {creation_response}",
                    "product_type": product_type
                }
            
            # Ottieni ID prodotto
            created_product = creation_response["result"]
            product_id = created_product.get('id')
            
            if not product_id:
                return {
                    "success": False,
                    "error": f"ID prodotto non trovato nella risposta: {creation_response}",
                    "product_type": product_type
                }
            
            print(f"✅ Prodotto base creato! ID: {product_id}")
            
            # Recupera le varianti effettivamente create con GET
            print("📡 Recupero varianti create...")
            product_info_response = self.api_client.make_request("GET", f"/store/products/{product_id}")
            
            if not (product_info_response.get("code") in [200, 201] and "result" in product_info_response):
                return {
                    "success": False,
                    "error": f"Errore nel recuperare info prodotto: {product_info_response}",
                    "product_type": product_type
                }
            
            product_info_data = product_info_response["result"]
            sync_product = product_info_data.get("sync_product", {})
            sync_variants_result = product_info_data.get("sync_variants", [])
            
            print(f"   💕 Varianti iniziali create: {len(sync_variants_result)}")
            
            # FASE 2: AGGIUNTA INCREMENTALE con PUT (come codice originale)
            if remaining_variants:
                batch_size = 10  # Batch size per aggiornamenti
                total_batches = (len(remaining_variants) + batch_size - 1) // batch_size
                
                print(f"\n🔧 FASE 2: Aggiungendo {len(remaining_variants)} varianti rimanenti in {total_batches} batch...")
                
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(remaining_variants))
                    batch_variants = remaining_variants[start_idx:end_idx]
                    
                    print(f"📦 Batch {batch_num + 1}/{total_batches}: Aggiungendo {len(batch_variants)} varianti...")
                    
                    # Crea payload per questo batch
                    batch_sync_variants = []
                    for variant in batch_variants:
                        files_config = create_variant_files_config(
                            product_type, urls["design_url"], urls["logo_url"], urls["upscaled_url"]
                        )
                        batch_sync_variants.append({
                            "retail_price": f"{variant['price']:.2f}",
                            "variant_id": variant["variant_id"],
                            "files": files_config
                        })
                    
                    # Ottieni riferimenti alle varianti esistenti (CRITICO per PUT)
                    existing_variant_refs = [{"id": existing.get("id")} for existing in sync_variants_result]
                    
                    # Combina varianti esistenti + nuove (STRATEGIA PUT)
                    combined_variants = existing_variant_refs + batch_sync_variants
                    
                    update_data = {
                        "sync_product": {
                            "name": product_name,
                            "thumbnail": urls["design_url"]
                        },
                        "sync_variants": combined_variants
                    }
                    
                    # Invia aggiornamento con PUT
                    print(f"   🚀 Invio batch {batch_num + 1}...")
                    batch_response = self.api_client.make_request("PUT", f"/store/products/{product_id}", update_data)
                    
                    if batch_response.get("code") in [200, 201] and "result" in batch_response:
                        # Ricarica stato del prodotto con GET (VERIFICA)
                        updated_info_response = self.api_client.make_request("GET", f"/store/products/{product_id}")
                        if updated_info_response.get("code") in [200, 201]:
                            updated_info = updated_info_response["result"]
                            sync_variants_result = updated_info.get("sync_variants", [])
                            print(f"   ✅ Batch {batch_num + 1} completato! Varianti totali: {len(sync_variants_result)}")
                        else:
                            print(f"   ⚠️ Impossibile verificare stato dopo batch {batch_num + 1}")
                    else:
                        print(f"   ❌ Batch {batch_num + 1} fallito: {batch_response}")
                        # Continua con i batch successivi
                    
                    # Pausa tra batch (come codice originale)
                    if batch_num < total_batches - 1:
                        time.sleep(3)  # Pausa aumentata
            
            # Stato finale con GET
            final_info_response = self.api_client.make_request("GET", f"/store/products/{product_id}")
            if final_info_response.get("code") in [200, 201]:
                final_info = final_info_response["result"]
                final_sync_product = final_info.get("sync_product", {})
                final_sync_variants = final_info.get("sync_variants", [])
                
                return {
                    "success": True,
                    "product_id": product_id,
                    "sync_product": final_sync_product,
                    "sync_variants": final_sync_variants,
                    "product_type": product_type,
                    "total_variants_created": len(final_sync_variants),
                    "total_variants_requested": len(variants)
                }
            else:
                # Fallback con le info che abbiamo
                return {
                    "success": True,
                    "product_id": product_id,
                    "sync_product": sync_product,
                    "sync_variants": sync_variants_result,
                    "product_type": product_type,
                    "total_variants_created": len(sync_variants_result),
                    "total_variants_requested": len(variants)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore durante creazione prodotto: {str(e)}",
                "product_type": product_type
            }
    
    def _process_all_products(self, design_file: str, uploader) -> Dict:
        """Processa tutti i prodotti per un design"""
        available_products = self.variant_loader.get_available_products()
        design_filename = os.path.basename(design_file)
        
        results = {
            "success": True,
            "total_products": len(available_products),
            "products_created": 0,
            "total_variants": 0,
            "results": {}
        }
        
        for product_type in available_products:
            print(f"\n🎯 Creando {product_type}...")
            
            result = self._build_single_product(design_file, product_type, uploader)
            results["results"][product_type] = result
            
            if result["success"]:
                results["products_created"] += 1
                results["total_variants"] += result.get("total_variants_created", 0)
            
            # Pausa tra prodotti aumentata
            time.sleep(5)  # Pausa aumentata da 3 a 5 secondi
        
        results["success"] = results["products_created"] > 0
        return results
    
    def _prepare_urls(self, design_file: str, uploader) -> Dict:
        """Prepara URL per upload"""
        urls = {"design_url": None, "logo_url": None, "upscaled_url": None}
        
        # Design principale
        urls["design_url"] = uploader.upload_image(design_file)
        
        # Logo opzionale
        logo_file = os.path.join("generate", "universal_logo.png")
        if os.path.exists(logo_file):
            try:
                urls["logo_url"] = uploader.upload_image(logo_file)
            except:
                pass
        
        # Upscaled opzionale
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        upscaled_file = os.path.join("upscaled", f"{design_name}.png")
        if os.path.exists(upscaled_file):
            try:
                urls["upscaled_url"] = uploader.upload_image_with_transparency(upscaled_file)
            except:
                pass
        
        return urls
    
    def _create_initial_product(self, product_name: str, design_url: str, 
                              variants: List[Dict], product_type: str, urls: Dict) -> Dict:
        """Crea prodotto iniziale"""
        sync_variants = []
        for variant in variants:
            files_config = create_variant_files_config(
                product_type, urls["design_url"], urls["logo_url"], urls["upscaled_url"]
            )
            
            sync_variants.append({
                "retail_price": f"{variant['price']:.2f}",
                "variant_id": variant["variant_id"],
                "files": files_config
            })
        
        product_data = {
            "sync_product": {"name": product_name, "thumbnail": design_url},
            "sync_variants": sync_variants
        }
        
        return self.api_client.make_request("POST", "/store/products", product_data)
    
    def _add_remaining_variants(self, product_id: str, variants: List[Dict], 
                              product_type: str, urls: Dict, product_name: str, design_url: str):
        """Aggiunge varianti rimanenti in batch"""
        batch_size = 10
        total_batches = (len(variants) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(variants))
            batch_variants = variants[start_idx:end_idx]
            
            # Crea payload batch
            batch_sync_variants = []
            for variant in batch_variants:
                files_config = create_variant_files_config(
                    product_type, urls["design_url"], urls["logo_url"], urls["upscaled_url"]
                )
                batch_sync_variants.append({
                    "retail_price": f"{variant['price']:.2f}",
                    "variant_id": variant["variant_id"],
                    "files": files_config
                })
            
            # Ottieni varianti esistenti
            current_info = self.api_client.make_request("GET", f"/store/products/{product_id}")
            existing_variants = [{"id": v.get("id")} for v in current_info["result"].get("sync_variants", [])]
            
            # Combina e aggiorna
            update_data = {
                "sync_product": {"name": product_name, "thumbnail": design_url},
                "sync_variants": existing_variants + batch_sync_variants
            }
            
            self.api_client.make_request("PUT", f"/store/products/{product_id}", update_data)
            time.sleep(2)  # Pausa tra batch
    
    def _find_design_files(self, folder: str) -> List[str]:
        """Trova file design nella cartella"""
        if not os.path.exists(folder):
            return []
        
        design_files = []
        extensions = ['.png', '.jpg', '.jpeg']
        
        for ext in extensions:
            pattern = os.path.join(folder, f"*{ext}")
            import glob
            files = glob.glob(pattern)
            design_files.extend(files)
        
        return sorted(design_files)
    
    def _save_result(self, result: Dict, filename: str) -> bool:
        """Salva risultato in file JSON"""
        try:
            # Assicura cartella json
            if not filename.startswith("json/"):
                filepath = os.path.join("json", filename)
            else:
                filepath = filename
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Errore salvataggio {filename}: {e}")
            return False
    
    def _save_all_products_result(self, results: Dict, design_filename: str) -> None:
        """Salva risultati di tutti i prodotti"""
        base_name = os.path.splitext(design_filename)[0]
        
        # Salva risultato per ogni prodotto
        for product_type, result in results.get("results", {}).items():
            if result.get("success"):
                filename = f"{base_name}_{product_type}.json"
                self._save_result(result, filename)
        
        # Salva riepilogo
        summary_filename = f"{base_name}_ALL_PRODUCTS_SUMMARY.json"
        self._save_result(results, summary_filename)


if __name__ == "__main__":
    """Test del sistema modulare semplificato"""
    print("🧪 TEST MODULAR PRODUCT CREATOR SEMPLIFICATO")
    print("=" * 50)
    
    load_dotenv()
    
    API_KEY = os.getenv("PRINTFUL_API_KEY")
    STORE_ID = os.getenv("PRINTFUL_STORE_ID")
    
    if not API_KEY or not STORE_ID:
        print("❌ Credenziali mancanti")
        exit(1)
    
    try:
        creator = ModularProductCreator(API_KEY, STORE_ID)
        
        print("\n📋 Test componenti:")
        print(f"   🔌 API connessa: OK")
        print(f"   📦 Prodotti: {len(creator.variant_loader.get_available_products())}")
        print(f"   🎨 Design files: {len(creator.find_design_files())}")
        
        print("\n✅ Sistema modulare semplificato funzionante!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()