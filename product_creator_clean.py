#!/usr/bin/env python3
"""
Product Creator - Interfaccia principale pulita e modulare
Orchestrazione creazione prodotti Printful
"""

import os
import json
from typing import Dict, List, Optional

from core.api_client import PrintfulAPIClient
from core.product_builder import ProductBuilder
from core.file_manager import FileManager
from utils.variant_loader import VariantLoader
from utils.cloudinary_uploader import CloudinaryUploader
from config.products import get_all_products, get_product_name


class ProductCreator:
    """
    Interfaccia principale per creazione prodotti Printful
    Architettura modulare e pulita
    """
    
    def __init__(self, api_key: str, store_id: str, uploader: CloudinaryUploader,
                 verbose: bool = False):
        """
        Args:
            api_key: Token API Printful
            store_id: ID store Printful
            uploader: Istanza CloudinaryUploader
            verbose: Se True, abilita log dettagliati
        """
        # Componenti core
        self.api = PrintfulAPIClient(api_key, store_id)
        self.variants = VariantLoader()
        self.files = FileManager(uploader)
        self.builder = ProductBuilder(self.api, self.variants, self.files, verbose)
        
        self.verbose = verbose
    
    # ========================================================================
    # API PUBBLICA - Creazione Prodotti
    # ========================================================================
    
    def create_product(self, design_file: str, product_type: str) -> Dict:
        """
        Crea un singolo prodotto
        
        Args:
            design_file: Path file design
            product_type: Tipo prodotto (es: 'gildan_5000')
            
        Returns:
            Dict con risultato creazione
        """
        if self.verbose:
            print(f"🚀 Creazione {product_type}")
        
        result = self.builder.build(design_file, product_type)
        
        if result["success"] and self.verbose:
            print(f"✅ Prodotto creato: {result['product_id']}")
        elif not result["success"]:
            print(f"❌ Errore: {result.get('error', 'Unknown')}")
        
        return result
    
    def create_all_products(self, design_file: str) -> Dict:
        """
        Crea tutti i tipi di prodotto per un design
        
        Args:
            design_file: Path file design
            
        Returns:
            Dict con risultati di tutti i prodotti
        """
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        
        if self.verbose:
            print(f"\n🚀 Creazione batch: {design_name}")
            print(f"   Prodotti: {len(get_all_products())}")
        
        results = {
            "design_file": design_file,
            "design_name": design_name,
            "total_products": len(get_all_products()),
            "results": {}
        }
        
        for product_type in get_all_products():
            if self.verbose:
                print(f"\n📦 {get_product_name(product_type)}")
            
            result = self.create_product(design_file, product_type)
            results["results"][product_type] = result
        
        # Statistiche finali
        success_count = sum(1 for r in results["results"].values() if r["success"])
        results["success_count"] = success_count
        results["failure_count"] = results["total_products"] - success_count
        
        if self.verbose:
            print(f"\n📊 Risultati: {success_count}/{results['total_products']} OK")
        
        return results
    
    # ========================================================================
    # UTILITY - File e Salvataggio
    # ========================================================================
    
    def find_design_files(self, folder: str = "ricamo") -> List[str]:
        """
        Trova file design nella cartella
        
        Args:
            folder: Cartella con design files
            
        Returns:
            Lista path file trovati
        """
        if not os.path.exists(folder):
            return []
        
        files = []
        extensions = ['.png', '.jpg', '.jpeg']
        
        for ext in extensions:
            import glob
            pattern = os.path.join(folder, f"*{ext}")
            files.extend(glob.glob(pattern))
        
        return sorted(files)
    
    def save_result(self, result: Dict, filename: str) -> bool:
        """
        Salva risultato in JSON
        
        Args:
            result: Dict risultato
            filename: Nome file (sarà salvato in json/)
            
        Returns:
            True se salvato con successo
        """
        try:
            # Assicura folder json/
            if not filename.startswith("json/"):
                filepath = os.path.join("json", filename)
            else:
                filepath = filename
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"💾 Salvato: {filepath}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore salvataggio {filename}: {e}")
            return False
    
    def save_batch_results(self, results: Dict, design_filename: str) -> None:
        """
        Salva risultati batch (singoli + sommario)
        
        Args:
            results: Dict con risultati batch
            design_filename: Nome file design originale
        """
        base_name = os.path.splitext(design_filename)[0]
        
        # Salva risultato per ogni prodotto
        for product_type, result in results.get("results", {}).items():
            if result.get("success"):
                filename = f"{base_name}_{product_type}.json"
                self.save_result(result, filename)
        
        # Salva sommario
        summary_filename = f"{base_name}_ALL_PRODUCTS_SUMMARY.json"
        self.save_result(results, summary_filename)
    
    # ========================================================================
    # INFO
    # ========================================================================
    
    def get_available_products(self) -> List[str]:
        """Ottiene lista prodotti disponibili"""
        return get_all_products()
    
    def get_store_info(self) -> Dict:
        """Ottiene info dello store"""
        return self.api.get("/store")
    
    def clear_cache(self):
        """Pulisce cache file manager"""
        self.files.clear_cache()


# ============================================================================
# FUNZIONI HELPER per retrocompatibilità
# ============================================================================

def create_product_creator(api_key: str, store_id: str, 
                          uploader: CloudinaryUploader,
                          verbose: bool = False) -> ProductCreator:
    """
    Factory function per creare ProductCreator
    
    Args:
        api_key: Token API Printful
        store_id: ID store Printful
        uploader: Istanza CloudinaryUploader
        verbose: Log dettagliati
        
    Returns:
        ProductCreator configurato
    """
    return ProductCreator(api_key, store_id, uploader, verbose)