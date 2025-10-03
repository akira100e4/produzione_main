#!/usr/bin/env python3
"""
Product Builder - Costruzione e creazione singoli prodotti
Estratto da product_creator.py - logica core di creazione prodotti
"""

import os
import time
from typing import Dict, List, Optional
from .api_client import PrintfulAPIClient
from ...placement_config import create_variant_files_config, validate_product_compatibility


class ProductBuilder:
    """
    Builder dedicato alla creazione di singoli prodotti Printful.
    Gestisce upload, configurazione varianti, creazione sync products.
    """
    
    def __init__(self, api_client: PrintfulAPIClient):
        self.api_client = api_client
    
    def _prepare_product_urls(self, design_file: str, uploader) -> Dict[str, Optional[str]]:
        """
        Prepara e carica le URL necessarie per il prodotto
        
        Args:
            design_file: Path del file design principale
            uploader: Istanza CloudinaryUploader
            
        Returns:
            Dizionario con le URL caricate
        """
        urls = {
            "design_url": None,
            "logo_url": None, 
            "upscaled_url": None
        }
        
        # 1. Upload design principale (sempre necessario)
        print("📤 Upload design principale...")
        try:
            urls["design_url"] = uploader.upload_image(design_file)
            print(f"   ✅ Design: {urls['design_url']}")
        except Exception as e:
            raise Exception(f"Errore upload design: {e}")
        
        # 2. Cerca e carica logo (opzionale)
        design_filename = os.path.basename(design_file)
        design_name = os.path.splitext(design_filename)[0]
        logo_file = os.path.join("generate", "universal_logo.png")
        
        if os.path.exists(logo_file):
            print("📤 Upload logo...")
            try:
                urls["logo_url"] = uploader.upload_image(logo_file)
                print(f"   ✅ Logo: {urls['logo_url']}")
            except Exception as e:
                print(f"   ⚠️ Errore upload logo: {e}")
        
        # 3. Cerca e carica design upscaled per DTG (opzionale)
        upscaled_file = os.path.join("upscaled", f"{design_name}.png")
        
        if os.path.exists(upscaled_file):
            print("📤 Upload design upscaled...")
            try:
                urls["upscaled_url"] = uploader.upload_image_with_transparency(upscaled_file)
                print(f"   ✅ Upscaled: {urls['upscaled_url']}")
            except Exception as e:
                print(f"   ⚠️ Errore upload upscaled: {e}")
        
        return urls
    
    def _create_variant_payload(self, variant: Dict, product_type: str, urls: Dict) -> Dict:
        """
        Crea payload per una singola variante
        
        Args:
            variant: Dati variante dal VariantLoader
            product_type: Tipo di prodotto
            urls: Dizionario con URL caricate
            
        Returns:
            Dizionario con payload variante per Printful API
        """
        # Usa configurazione dinamica dei posizionamenti
        files_config = create_variant_files_config(
            product_type=product_type,
            design_url=urls["design_url"],
            logo_url=urls["logo_url"],
            upscaled_url=urls["upscaled_url"]
        )
        
        return {
            "retail_price": f"{variant['price']:.2f}",
            "variant_id": variant["variant_id"],
            "files": files_config
        }
    
    def _create_initial_product(self, product_name: str, design_url: str, 
                              initial_variants: List[Dict], product_type: str, urls: Dict) -> Dict:
        """
        Crea prodotto iniziale con prime varianti (max 20)
        
        Args:
            product_name: Nome del prodotto
            design_url: URL design principale  
            initial_variants: Prime varianti da creare
            product_type: Tipo di prodotto
            urls: Dizionario con URL caricate
            
        Returns:
            Risposta API Printful
        """
        print(f"🏗️ Creazione prodotto iniziale con {len(initial_variants)} varianti...")
        
        # Crea payload per varianti iniziali
        sync_variants = []
        for variant in initial_variants:
            variant_payload = self._create_variant_payload(variant, product_type, urls)
            sync_variants.append(variant_payload)
        
        # Payload completo per creazione prodotto
        product_data = {
            "sync_product": {
                "name": product_name,
                "thumbnail": design_url
            },
            "sync_variants": sync_variants
        }
        
        # Invia richiesta di creazione
        response = self.api_client.make_request("POST", "/store/products", product_data)
        
        if response.get("code") not in [200, 201]:
            raise Exception(f"Errore creazione prodotto: {response}")
        
        return response
    
    def _add_remaining_variants_batch(self, product_id: str, remaining_variants: List[Dict], 
                                    product_type: str, urls: Dict, product_name: str, 
                                    design_url: str) -> List[Dict]:
        """
        Aggiunge varianti rimanenti in batch
        
        Args:
            product_id: ID del prodotto già creato
            remaining_variants: Varianti da aggiungere
            product_type: Tipo di prodotto
            urls: URL caricate
            product_name: Nome prodotto
            design_url: URL design principale
            
        Returns:
            Lista varianti finali
        """
        if not remaining_variants:
            return []
        
        batch_size = 10  # Batch size ottimale
        total_batches = (len(remaining_variants) + batch_size - 1) // batch_size
        
        print(f"🔧 FASE 2: Aggiungendo {len(remaining_variants)} varianti in {total_batches} batch...")
        
        # Recupera stato attuale del prodotto
        current_info = self.api_client.make_request("GET", f"/store/products/{product_id}")
        if current_info.get("code") not in [200, 201]:
            raise Exception(f"Errore recupero prodotto: {current_info}")
        
        current_variants = current_info["result"].get("sync_variants", [])
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(remaining_variants))
            batch_variants = remaining_variants[start_idx:end_idx]
            
            print(f"📦 Batch {batch_num + 1}/{total_batches}: {len(batch_variants)} varianti...")
            
            # Crea payload per questo batch
            batch_sync_variants = []
            for variant in batch_variants:
                variant_payload = self._create_variant_payload(variant, product_type, urls)
                batch_sync_variants.append(variant_payload)
            
            # Mantieni riferimenti alle varianti esistenti
            existing_refs = [{"id": v.get("id")} for v in current_variants]
            combined_variants = existing_refs + batch_sync_variants
            
            # Payload di aggiornamento
            update_data = {
                "sync_product": {
                    "name": product_name,
                    "thumbnail": design_url
                },
                "sync_variants": combined_variants
            }
            
            # Invia aggiornamento
            batch_response = self.api_client.make_request("PUT", f"/store/products/{product_id}", update_data)
            
            if batch_response.get("code") not in [200, 201]:
                print(f"⚠️ Batch {batch_num + 1} parzialmente fallito")
                continue
            
            # Aggiorna stato varianti correnti
            updated_info = self.api_client.make_request("GET", f"/store/products/{product_id}")
            if updated_info.get("code") in [200, 201]:
                current_variants = updated_info["result"].get("sync_variants", [])
            
            print(f"   ✅ Batch {batch_num + 1} completato")
            
            # Pausa tra batch
            if batch_num < total_batches - 1:
                time.sleep(2)
        
        return current_variants
    
    def build_single_product(self, design_file: str, product_type: str, uploader, variant_loader) -> Dict:
        """
        Costruisce un singolo prodotto completo
        
        Args:
            design_file: Path del file design
            product_type: Tipo di prodotto da creare
            uploader: Istanza CloudinaryUploader
            variant_loader: Istanza VariantLoader
            
        Returns:
            Dizionario con risultato della creazione
        """
        try:
            # 1. Validazione iniziale
            design_filename = os.path.basename(design_file)
            design_name = os.path.splitext(design_filename)[0]
            
            print(f"\n🏗️ COSTRUZIONE PRODOTTO: {design_name}")
            print(f"   📦 Tipo: {product_type}")
            
            # 2. Carica varianti del prodotto
            variants = variant_loader.load_product_variants(product_type)
            product_info = variant_loader.get_product_info(product_type)
            
            # 3. Validazione compatibilità
            compatibility = validate_product_compatibility(product_type, has_logo=True, has_dtg=True)
            if not compatibility["compatible"]:
                return {
                    "success": False,
                    "error": f"Prodotto non compatibile: {compatibility.get('error')}"
                }
            
            # 4. Prepara URL
            urls = self._prepare_product_urls(design_file, uploader)
            
            # 5. Divide varianti per gestione batch
            max_initial = 20  # Prime varianti nella creazione iniziale
            initial_variants = variants[:max_initial]
            remaining_variants = variants[max_initial:]
            
            product_name = f"{design_name} - {product_info['name']}"
            
            # 6. Crea prodotto iniziale
            creation_response = self._create_initial_product(
                product_name, urls["design_url"], initial_variants, product_type, urls
            )
            
            product_id = creation_response["result"]["sync_product"]["id"]
            print(f"   🆔 Product ID: {product_id}")
            
            # 7. Aggiungi varianti rimanenti se necessario
            final_variants = initial_variants
            if remaining_variants:
                batch_variants = self._add_remaining_variants_batch(
                    product_id, remaining_variants, product_type, urls, 
                    product_name, urls["design_url"]
                )
                final_variants = initial_variants + remaining_variants
            
            # 8. Recupera stato finale
            final_info = self.api_client.make_request("GET", f"/store/products/{product_id}")
            
            if final_info.get("code") not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Errore recupero stato finale: {final_info}",
                    "product_type": product_type
                }
            
            final_product_info = final_info["result"]
            sync_product = final_product_info.get("sync_product", {})
            sync_variants = final_product_info.get("sync_variants", [])
            
            print(f"✅ PRODOTTO CREATO CON SUCCESSO!")
            print(f"   🎯 Varianti create: {len(sync_variants)}/{len(variants)}")
            
            return {
                "success": True,
                "product_id": product_id,
                "sync_product": sync_product,
                "sync_variants": sync_variants,
                "product_type": product_type,
                "design_file": design_file,
                "total_variants_requested": len(variants),
                "total_variants_created": len(sync_variants),
                "urls": urls
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "product_type": product_type,
                "design_file": design_file
            }
    
    def validate_product_requirements(self, product_type: str, design_file: str) -> Dict:
        """
        Valida i requisiti per la creazione di un prodotto
        
        Args:
            product_type: Tipo di prodotto
            design_file: Path del file design
            
        Returns:
            Dizionario con risultato validazione
        """
        issues = []
        warnings = []
        
        # Verifica esistenza file design
        if not os.path.exists(design_file):
            issues.append(f"File design non trovato: {design_file}")
        
        # Verifica dimensione file (max 10MB per Printful)
        if os.path.exists(design_file):
            file_size = os.path.getsize(design_file)
            if file_size > 10 * 1024 * 1024:  # 10MB
                issues.append(f"File troppo grande: {file_size/1024/1024:.1f}MB (max 10MB)")
        
        # Verifica compatibilità prodotto
        compatibility = validate_product_compatibility(product_type, has_logo=True, has_dtg=True)
        if not compatibility["compatible"]:
            issues.append(f"Prodotto non compatibile: {compatibility.get('error')}")
        
        if compatibility.get("warnings"):
            warnings.extend(compatibility["warnings"])
        
        # Verifica file opzionali
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        
        logo_file = os.path.join("generate", "universal_logo.png")
        if not os.path.exists(logo_file):
            warnings.append("Logo universale non trovato - alcune posizioni potrebbero essere vuote")
        
        upscaled_file = os.path.join("upscaled", f"{design_name}.png")
        if not os.path.exists(upscaled_file):
            warnings.append("Design upscaled non trovato - stampa DTG non disponibile")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "compatibility": compatibility
        }