#!/usr/bin/env python3
"""
Batch Processor - Gestione operazioni batch e processamento multiplo
Estratto da product_creator.py
"""

import time
from typing import Dict, List
from .product_builder import ProductBuilder


class BatchProcessor:
    """
    Processore per operazioni batch.
    Gestisce creazione multipla prodotti, timing, errori batch.
    """
    
    def __init__(self, product_builder: ProductBuilder):
        self.product_builder = product_builder
        self.default_batch_delay = 3  # Secondi tra operazioni batch
    
    def process_all_products(self, design_file: str, uploader, variant_loader) -> Dict:
        """
        Processa tutti i prodotti disponibili per un singolo design
        
        Args:
            design_file: Path del file design
            uploader: Istanza CloudinaryUploader
            variant_loader: Istanza VariantLoader
            
        Returns:
            Dizionario con risultati di tutti i prodotti
        """
        available_products = variant_loader.get_available_products()
        design_filename = os.path.basename(design_file)
        design_name = os.path.splitext(design_filename)[0]
        
        print(f"\n🚀 BATCH: TUTTI I PRODOTTI per {design_name}")
        print(f"📦 Prodotti da creare: {len(available_products)}")
        print("=" * 60)
        
        results = {
            "success": True,
            "design_file": design_file,
            "design_name": design_name,
            "total_products": len(available_products),
            "products_created": 0,
            "total_variants": 0,
            "results": {},
            "errors": [],
            "start_time": time.time()
        }
        
        for i, product_type in enumerate(available_products, 1):
            print(f"\n{'='*60}")
            print(f"🎯 PRODOTTO {i}/{len(available_products)}: {product_type}")
            print(f"{'='*60}")
            
            try:
                # Ottieni info prodotto per il log
                product_info = variant_loader.get_product_info(product_type)
                print(f"📋 {product_info['name']}")
                
                # Crea singolo prodotto
                result = self.product_builder.build_single_product(
                    design_file, product_type, uploader, variant_loader
                )
                
                # Salva risultato
                results["results"][product_type] = result
                
                if result["success"]:
                    results["products_created"] += 1
                    variants_created = result.get("total_variants_created", 0)
                    results["total_variants"] += variants_created
                    
                    print(f"✅ COMPLETATO: {product_info['name']}")
                    print(f"   💕 Varianti create: {variants_created}")
                else:
                    error_msg = result.get("error", "Errore sconosciuto")
                    results["errors"].append({
                        "product_type": product_type,
                        "error": error_msg
                    })
                    print(f"❌ FALLITO: {error_msg}")
                
            except Exception as e:
                error_msg = f"Errore imprevisto: {e}"
                results["results"][product_type] = {
                    "success": False,
                    "error": error_msg,
                    "product_type": product_type
                }
                results["errors"].append({
                    "product_type": product_type,
                    "error": error_msg
                })
                print(f"❌ ERRORE: {error_msg}")
            
            # Pausa tra prodotti (tranne l'ultimo)
            if i < len(available_products):
                print(f"⏳ Pausa di {self.default_batch_delay} secondi...")
                time.sleep(self.default_batch_delay)
        
        # Statistiche finali
        results["end_time"] = time.time()
        results["duration_seconds"] = results["end_time"] - results["start_time"]
        results["success"] = results["products_created"] > 0
        
        return results
    
    def process_single_product_batch(self, design_files: List[str], product_type: str, 
                                   uploader, variant_loader) -> Dict:
        """
        Processa un singolo tipo di prodotto per tutti i design files
        
        Args:
            design_files: Lista path dei file design
            product_type: Tipo di prodotto da creare
            uploader: Istanza CloudinaryUploader
            variant_loader: Istanza VariantLoader
            
        Returns:
            Dizionario con risultati del batch
        """
        product_info = variant_loader.get_product_info(product_type)
        
        print(f"\n📦 BATCH: SINGOLO PRODOTTO")
        print(f"🎯 Prodotto: {product_info['name']} ({product_type})")
        print(f"🎨 Design files: {len(design_files)}")
        print("=" * 60)
        
        results = {
            "success": True,
            "product_type": product_type,
            "product_name": product_info['name'],
            "total_designs": len(design_files),
            "products_created": 0,
            "total_variants": 0,
            "results": {},
            "errors": [],
            "start_time": time.time()
        }
        
        for i, design_file in enumerate(design_files, 1):
            design_filename = os.path.basename(design_file)
            design_name = os.path.splitext(design_filename)[0]
            
            print(f"\n{'='*60}")
            print(f"🎨 DESIGN {i}/{len(design_files)}: {design_filename}")
            print(f"{'='*60}")
            
            try:
                # Crea prodotto per questo design
                result = self.product_builder.build_single_product(
                    design_file, product_type, uploader, variant_loader
                )
                
                # Salva risultato
                results["results"][design_name] = result
                
                if result["success"]:
                    results["products_created"] += 1
                    variants_created = result.get("total_variants_created", 0)
                    results["total_variants"] += variants_created
                    
                    print(f"✅ COMPLETATO: {design_filename}")
                    print(f"   💕 Varianti: {variants_created}")
                else:
                    error_msg = result.get("error", "Errore sconosciuto")
                    results["errors"].append({
                        "design_file": design_filename,
                        "error": error_msg
                    })
                    print(f"❌ FALLITO: {error_msg}")
                
            except Exception as e:
                error_msg = f"Errore imprevisto: {e}"
                results["results"][design_name] = {
                    "success": False,
                    "error": error_msg,
                    "design_file": design_file
                }
                results["errors"].append({
                    "design_file": design_filename,
                    "error": error_msg
                })
                print(f"❌ ERRORE: {error_msg}")
            
            # Pausa tra design (tranne l'ultimo)
            if i < len(design_files):
                print(f"⏳ Pausa di {self.default_batch_delay} secondi...")
                time.sleep(self.default_batch_delay)
        
        # Statistiche finali
        results["end_time"] = time.time()
        results["duration_seconds"] = results["end_time"] - results["start_time"]
        results["success"] = results["products_created"] > 0
        
        return results
    
    def process_massive_batch(self, design_files: List[str], uploader, variant_loader) -> Dict:
        """
        Processa TUTTI i prodotti per TUTTI i design files (operazione massiva)
        
        Args:
            design_files: Lista path dei file design
            uploader: Istanza CloudinaryUploader
            variant_loader: Istanza VariantLoader
            
        Returns:
            Dizionario con risultati dell'operazione massiva
        """
        available_products = variant_loader.get_available_products()
        total_operations = len(design_files) * len(available_products)
        
        print(f"\n🎆 BATCH MASSIVO")
        print(f"🎨 Design files: {len(design_files)}")
        print(f"📦 Prodotti: {len(available_products)}")
        print(f"🚀 Operazioni totali: {total_operations}")
        print("=" * 60)
        
        results = {
            "success": True,
            "total_designs": len(design_files),
            "total_products": len(available_products),
            "total_operations": total_operations,
            "successful_operations": 0,
            "total_variants": 0,
            "design_results": {},
            "errors": [],
            "start_time": time.time()
        }
        
        for design_i, design_file in enumerate(design_files, 1):
            design_filename = os.path.basename(design_file)
            design_name = os.path.splitext(design_filename)[0]
            
            print(f"\n{'█'*60}")
            print(f"🎨 DESIGN {design_i}/{len(design_files)}: {design_filename}")
            print(f"{'█'*60}")
            
            # Processa tutti i prodotti per questo design
            design_batch_result = self.process_all_products(design_file, uploader, variant_loader)
            
            # Salva risultati di questo design
            results["design_results"][design_name] = design_batch_result
            
            # Aggiorna statistiche globali
            results["successful_operations"] += design_batch_result["products_created"]
            results["total_variants"] += design_batch_result["total_variants"]
            results["errors"].extend(design_batch_result["errors"])
            
            # Pausa tra design (tranne l'ultimo)
            if design_i < len(design_files):
                pause_time = self.default_batch_delay * 2  # Pausa più lunga per batch massivi
                print(f"⏳ Pausa di {pause_time} secondi tra design...")
                time.sleep(pause_time)
        
        # Statistiche finali
        results["end_time"] = time.time()
        results["duration_seconds"] = results["end_time"] - results["start_time"]
        results["success"] = results["successful_operations"] > 0
        results["success_rate"] = (results["successful_operations"] / total_operations) * 100
        
        return results
    
    def estimate_batch_time(self, num_designs: int, num_products: int) -> Dict:
        """
        Stima il tempo necessario per un'operazione batch
        
        Args:
            num_designs: Numero di design
            num_products: Numero di prodotti
            
        Returns:
            Dizionario con stime temporali
        """
        # Tempi stimati (basati su esperienza)
        time_per_product = 120  # 2 minuti per prodotto
        batch_overhead = 3     # 3 secondi di pausa tra operazioni
        
        total_operations = num_designs * num_products
        estimated_seconds = (total_operations * time_per_product) + (total_operations * batch_overhead)
        
        return {
            "total_operations": total_operations,
            "estimated_seconds": estimated_seconds,
            "estimated_minutes": round(estimated_seconds / 60, 1),
            "estimated_hours": round(estimated_seconds / 3600, 2),
            "time_per_operation": time_per_product + batch_overhead
        }