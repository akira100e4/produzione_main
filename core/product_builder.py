#!/usr/bin/env python3
"""
Product Builder - Costruzione prodotti Printful
Responsabilità: Logica creazione prodotti (POST + PUT + GET pattern)
🔧 MODIFICATO: Logica speciale per cappelli Yupoong 6089M e AS Colour 1120
"""

import os
import time
from typing import Dict, List
from PIL import Image

from core.image_processor import create_left_aligned_image
from config.products import get_product_placements, get_product_name
from config.placements import apply_position


class ProductBuilder:
    """Costruisce prodotti Printful con logica POST + PUT + GET"""
    
    def __init__(self, api_client, variant_loader, file_manager, verbose: bool = False):
        """
        Args:
            api_client: Istanza PrintfulAPIClient
            variant_loader: Istanza VariantLoader
            file_manager: Istanza FileManager
            verbose: Se True, stampa log dettagliati
        """
        self.api = api_client
        self.variants = variant_loader
        self.files = file_manager
        self.verbose = verbose
    
    def build(self, design_file: str, product_type: str) -> Dict:
        """
        Costruisce un prodotto completo
        
        Args:
            design_file: Path file design
            product_type: Tipo prodotto (es: 'gildan_5000')
            
        Returns:
            Dict con risultato creazione
        """
        try:
            # Preparazione
            design_name = os.path.splitext(os.path.basename(design_file))[0]
            product_name = f"{design_name} - {get_product_name(product_type)}"
            
            # Carica varianti
            variant_list = self.variants.load_product_variants(product_type)
            
            if self.verbose:
                print(f"\n🏗️  Costruzione: {product_name}")
                print(f"   Varianti: {len(variant_list)}")
            
            # Upload file (con logica speciale per cappelli)
            urls = self._prepare_urls_for_product(design_file, product_type)
            
            # Creazione prodotto
            product_id = self._create_product(
                product_name, product_type, variant_list, urls
            )
            
            # Verifica finale
            final_product = self.api.get(f"/store/products/{product_id}")
            
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product_name,
                "product_type": product_type,
                "variants_count": len(final_product["result"]["sync_variants"]),
                "result": final_product["result"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "product_type": product_type
            }
    
    def _prepare_urls_for_product(self, design_file: str, product_type: str) -> Dict:
        """
        Prepara URL con logica speciale per cappelli
        
        Args:
            design_file: Path file design principale
            product_type: Tipo prodotto
            
        Returns:
            Dict con URL (design_url, logo_url, upscaled_url, logo_black_url)
        """
        # Upload standard
        urls = self.files.prepare_urls(design_file)
        
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        
        # 🧢 LOGICA SPECIALE CAPPELLO YUPOONG 6089M
        if product_type == "yupoong_6089m":
            # Cerca versione ottimizzata in ricami/
            hat_optimized_path = f"ricami/{design_name}.png"
            
            if os.path.exists(hat_optimized_path):
                source_file = hat_optimized_path
                if self.verbose:
                    print(f"   🧢 Usando versione ottimizzata da ricami/")
            else:
                source_file = design_file
                if self.verbose:
                    print(f"   ⚠️  Versione ottimizzata non trovata, uso ricamo/")
            
            # Crea versione logo spostato a sinistra e ingrandito per front
            try:
                left_aligned_path = create_left_aligned_image(
                    source_file,
                    canvas_multiplier=2.5,
                    margin_percent=0.05,
                    scale_factor=1.5
                )
                
                # Upload versione modificata e sovrascrive design_url
                urls["design_url"] = self.files._upload_with_cache(left_aligned_path)
                
                if self.verbose:
                    print(f"   🧢 Yupoong: Immagine modificata (allineata sinistra, +50%)")
                
                # Pulizia file temporaneo
                os.remove(left_aligned_path)
                
            except Exception as e:
                if self.verbose:
                    print(f"   ❌ Errore modifica immagine: {e}")
            
            # Upload logo_black per lato sinistro
            logo_black_path = "generate/logo_black.png"
            if os.path.exists(logo_black_path):
                urls["logo_black_url"] = self.files._upload_with_cache(logo_black_path)
                if self.verbose:
                    print(f"   🧢 Logo laterale: logo_black.png caricato")
        
        # 🧢 LOGICA SPECIALE CAPPELLO AS COLOUR 1120 (BEANIE) - SOLO LOGO
        elif product_type == "as_colour_1120":
            ricami_path = f"ricami/{design_name}.png"
            
            # SOLO ricami/, nessun fallback
            if not os.path.exists(ricami_path):
                raise Exception(
                    f"File ottimizzato per beanie non trovato: {ricami_path}\n"
                    f"Crea il file in ricami/ prima di procedere."
                )
            
            source_file = ricami_path
            
            # Ingrandisci il logo senza aggiungere testo
            try:
                img = Image.open(source_file).convert('RGBA')
                
                # Ingrandimento del 50%
                scale_factor = 1.5
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img_scaled = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Salva temporaneamente
                temp_path = f"ricami/{design_name}_beanie_scaled.png"
                img_scaled.save(temp_path)
                
                # Upload immagine ingrandita
                urls["design_url"] = self.files._upload_with_cache(temp_path)
                
                if self.verbose:
                    print(f"   🧢 AS Colour 1120: Logo ingrandito +50% (solo logo)")
                
                # Pulizia file temporaneo
                os.remove(temp_path)
                
            except Exception as e:
                if self.verbose:
                    print(f"   ❌ Errore ingrandimento: {e}")
                raise
        
        return urls
    
    def _create_product(self, product_name: str, product_type: str,
                       variants: List[Dict], urls: Dict) -> int:
        """
        Crea prodotto usando pattern POST + PUT + GET
        
        Args:
            product_name: Nome prodotto
            product_type: Tipo prodotto
            variants: Lista varianti
            urls: Dict con URL file
            
        Returns:
            ID prodotto creato
        """
        # FASE 1: Creazione base (POST con batch iniziale piccolo)
        initial_batch = variants[:8]
        remaining = variants[8:]
        
        if self.verbose:
            print(f"   📦 Fase 1: Creazione base ({len(initial_batch)} varianti)")
        
        # Crea payload iniziale
        initial_payload = {
            "sync_product": {
                "name": product_name,
                "thumbnail": urls["design_url"]
            },
            "sync_variants": self._build_variants_payload(
                product_type, initial_batch, urls
            )
        }
        
        # POST iniziale
        response = self.api.post("/store/products", initial_payload)
        
        if response.get("code") not in [200, 201]:
            raise Exception(f"Creazione fallita: {response}")
        
        product_id = response["result"]["id"]
        
        if self.verbose:
            print(f"   ✅ Prodotto creato: ID {product_id}")
        
        # FASE 2: Aggiunta varianti rimanenti (PUT in batch)
        if remaining:
            if self.verbose:
                print(f"   📦 Fase 2: Aggiunta {len(remaining)} varianti")
            
            batch_size = 10
            for i in range(0, len(remaining), batch_size):
                batch = remaining[i:i + batch_size]
                self._add_variants_batch(product_id, product_name, product_type, 
                                        batch, urls)
                time.sleep(2)
        
        return product_id
    
    def _add_variants_batch(self, product_id: int, product_name: str,
                           product_type: str, batch: List[Dict], 
                           urls: Dict) -> None:
        """Aggiunge batch di varianti con PUT"""
        
        # GET varianti esistenti
        current = self.api.get(f"/store/products/{product_id}")
        existing = [{"id": v["id"]} for v in current["result"]["sync_variants"]]
        
        # Crea payload batch
        new_variants = self._build_variants_payload(product_type, batch, urls)
        
        # PUT con varianti esistenti + nuove
        update_payload = {
            "sync_product": {
                "name": product_name,
                "thumbnail": urls["design_url"]
            },
            "sync_variants": existing + new_variants
        }
        
        self.api.put(f"/store/products/{product_id}", update_payload)
    
    def _build_variants_payload(self, product_type: str, variants: List[Dict],
                                urls: Dict) -> List[Dict]:
        """
        Costruisce payload varianti con file configs
        
        Args:
            product_type: Tipo prodotto
            variants: Lista varianti da processare
            urls: Dict con URL file
            
        Returns:
            Lista payload varianti
        """
        payload_variants = []
        
        for variant in variants:
            files_config = self._build_files_config(product_type, urls)
            
            payload_variants.append({
                "retail_price": f"{variant['price']:.2f}",
                "variant_id": variant["variant_id"],
                "files": files_config
            })
        
        return payload_variants
    
    def _build_files_config(self, product_type: str, urls: Dict) -> List[Dict]:
        """
        Costruisce configurazione files per un prodotto
        🧢 MODIFICATO: Logica speciale per cappelli
        
        Args:
            product_type: Tipo prodotto
            urls: Dict con URL file
            
        Returns:
            Lista configurazioni file
        """
        placements = get_product_placements(product_type)
        files_config = []
        
        for i, placement in enumerate(placements):
            placement_type = placement["type"]
            design_type = placement["design_type"]
            
            # 🧢 LOGICA SPECIALE CAPPELLO YUPOONG 6089M
            if product_type == "yupoong_6089m":
                if placement_type == "embroidery_front":
                    # Front: usa design modificato (spostato sinistra)
                    url = urls["design_url"]
                    
                elif placement_type == "embroidery_left":
                    # Lato sinistro: usa logo_black.png (alta qualità)
                    url = urls.get("logo_black_url") or urls.get("logo_url")
                    
                    if not url:
                        continue
                else:
                    continue
            
            # 🧢 LOGICA SPECIALE CAPPELLO AS COLOUR 1120 (BEANIE) - SOLO LOGO
            elif product_type == "as_colour_1120":
                if placement_type == "embroidery_front":
                    # Front: usa solo logo ingrandito (senza testo)
                    url = urls["design_url"]
                else:
                    # Solo front per AS Colour 1120
                    continue
            
            # LOGICA STANDARD ALTRI PRODOTTI
            else:
                if i == 0:
                    url = urls["design_url"]
                elif i == 1 and urls.get("logo_url"):
                    url = urls["logo_url"]
                elif placement_type == "back" and urls.get("upscaled_url"):
                    url = urls["upscaled_url"]
                else:
                    continue
            
            # Crea config base
            file_config = {
                "type": placement_type,
                "url": url
            }
            
            # Aggiungi opzioni ricamo
            if design_type == "embroidery":
                file_config["options"] = [
                    {"id": "auto_thread_color", "value": True}
                ]
            
            # Applica posizionamento custom (se configurato)
            file_config = apply_position(placement_type, file_config)
            
            files_config.append(file_config)
        
        return files_config