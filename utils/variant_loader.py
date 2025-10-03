#!/usr/bin/env python3
"""
Variant Loader - Sistema di caricamento dinamico delle varianti prodotto.
Carica automaticamente le varianti dai file JSON nella cartella variants/
"""

import os
import json
import glob
from typing import List, Dict, Optional


class VariantLoader:
    """Classe per caricare dinamicamente le varianti dai file JSON"""
    
    def __init__(self, variants_folder: str = "variants"):
        self.variants_folder = variants_folder
        self._variants_cache = {}  # Cache per evitare riletture
        self._product_configs = self._load_product_configs()
    
    def _load_product_configs(self) -> Dict[str, Dict]:
        """Mappa automatica dei prodotti basata sui file JSON trovati"""
        configs = {}
        
        if not os.path.exists(self.variants_folder):
            print(f"⚠️ Cartella {self.variants_folder} non trovata!")
            return configs
        
        # Trova tutti i file JSON
        pattern = os.path.join(self.variants_folder, "*_data.json")
        json_files = glob.glob(pattern)
        
        for json_file in json_files:
            filename = os.path.basename(json_file)
            # Estrai il nome prodotto dal filename (es: gildan_5000_data.json -> gildan_5000)
            product_key = filename.replace("_data.json", "")
            
            # Genera nome display leggibile
            display_name = self._generate_display_name(product_key)
            
            configs[product_key] = {
                "name": display_name,
                "variant_file": filename,
                "json_path": json_file,
                "description": f"Prodotto {display_name}"
            }
        
        return configs
    
    def _generate_display_name(self, product_key: str) -> str:
        """Genera nome display leggibile dal product_key"""
        # Mapping per nomi speciali
        name_mappings = {
            "gildan_5000": "Gildan 5000",
            "gildan_18000": "Gildan 18000", 
            "gildan_18500": "Gildan 18500",
            "as_colour_1120": "AS Colour 1120",
            "yupoong_6089m": "Yupoong 6089M"
        }
        
        return name_mappings.get(product_key, product_key.replace("_", " ").title())
    
    def get_available_products(self) -> List[str]:
        """
        Restituisce lista dei prodotti disponibili
        
        Returns:
            Lista delle chiavi prodotto disponibili
        """
        return list(self._product_configs.keys())
    
    def get_product_info(self, product_type: str) -> Optional[Dict]:
        """
        Ottieni informazioni su un prodotto specifico
        
        Args:
            product_type: Chiave del prodotto (es: 'gildan_5000')
            
        Returns:
            Dizionario con info prodotto o None se non trovato
        """
        return self._product_configs.get(product_type)
    
    def list_products(self) -> None:
        """Stampa lista formattata dei prodotti disponibili"""
        if not self._product_configs:
            print("❌ Nessun prodotto trovato!")
            return
        
        print(f"\n📋 Prodotti disponibili ({len(self._product_configs)}):")
        print("-" * 50)
        
        for i, (key, config) in enumerate(self._product_configs.items(), 1):
            print(f"   {i}. {config['name']} ({key})")
            print(f"      File: {config['variant_file']}")
        
        print("-" * 50)
    
    def load_product_variants(self, product_type: str) -> List[Dict]:
        """
        Carica le varianti per un prodotto specifico
        
        Args:
            product_type: Tipo di prodotto (es: 'gildan_5000')
            
        Returns:
            Lista delle varianti del prodotto
            
        Raises:
            FileNotFoundError: Se il file JSON non esiste
            ValueError: Se il prodotto non è supportato
        """
        # Controlla cache
        if product_type in self._variants_cache:
            return self._variants_cache[product_type]
        
        # Verifica che il prodotto esista
        if product_type not in self._product_configs:
            available = ", ".join(self.get_available_products())
            raise ValueError(f"Prodotto '{product_type}' non trovato. Disponibili: {available}")
        
        # Percorso file JSON
        json_path = self._product_configs[product_type]["json_path"]
        
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"File varianti non trovato: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Il formato può variare - gestiamo i casi più comuni
            variants = self._extract_variants_from_json(data, product_type)
            
            # Cache il risultato
            self._variants_cache[product_type] = variants
            
            print(f"✅ Caricate {len(variants)} varianti per {self._product_configs[product_type]['name']}")
            return variants
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore parsing JSON per {product_type}: {e}")
        except Exception as e:
            raise RuntimeError(f"Errore caricamento varianti per {product_type}: {e}")
    
    def _extract_variants_from_json(self, data: Dict, product_type: str) -> List[Dict]:
        """
        Estrae le varianti dal JSON, gestendo diversi formati
        
        Args:
            data: Dati JSON caricati
            product_type: Tipo di prodotto
            
        Returns:
            Lista standardizzata delle varianti
        """
        # Se il JSON contiene direttamente una lista di varianti
        if isinstance(data, list):
            return self._standardize_variants(data)
        
        # Se ha una chiave 'variants' o 'data'
        for key in ['variants', 'data', 'result']:
            if key in data and isinstance(data[key], list):
                return self._standardize_variants(data[key])
        
        # Se non troviamo un formato riconosciuto
        raise ValueError(f"Formato JSON non riconosciuto per {product_type}. Chiavi disponibili: {list(data.keys())}")
    
    def _standardize_variants(self, variants: List[Dict]) -> List[Dict]:
        """
        Standardizza le varianti in un formato consistente
        
        Args:
            variants: Lista varianti dal JSON
            
        Returns:
            Lista varianti standardizzata
        """
        standardized = []
        
        for variant in variants:
            # Standardizza i campi principali
            standardized_variant = {
                "variant_id": variant.get("variant_id") or variant.get("id"),
                "size": variant.get("size", ""),
                "color": variant.get("color", ""),
                "price": float(variant.get("price", 25.00))  # Default €25.00
            }
            
            # Aggiungi campi extra se presenti
            for key, value in variant.items():
                if key not in standardized_variant:
                    standardized_variant[key] = value
            
            standardized.append(standardized_variant)
        
        return standardized
    
    def load_all_variants(self) -> Dict[str, List[Dict]]:
        """
        Carica le varianti di TUTTI i prodotti disponibili
        
        Returns:
            Dizionario {product_type: [varianti]}
        """
        all_variants = {}
        failed_products = []
        
        print(f"\n🔄 Caricamento di tutti i prodotti...")
        
        for product_type in self.get_available_products():
            try:
                variants = self.load_product_variants(product_type)
                all_variants[product_type] = variants
            except Exception as e:
                print(f"❌ Errore caricamento {product_type}: {e}")
                failed_products.append(product_type)
        
        print(f"\n✅ Caricamento completato:")
        print(f"   📦 Prodotti caricati: {len(all_variants)}")
        print(f"   ❌ Prodotti falliti: {len(failed_products)}")
        
        if failed_products:
            print(f"   ⚠️ Falliti: {', '.join(failed_products)}")
        
        # Calcola statistiche totali
        total_variants = sum(len(variants) for variants in all_variants.values())
        print(f"   👕 Varianti totali: {total_variants}")
        
        return all_variants
    
    def get_variants_summary(self, product_type: str = None) -> None:
        """
        Stampa riepilogo delle varianti
        
        Args:
            product_type: Se specificato, mostra solo quel prodotto. Altrimenti tutti.
        """
        if product_type:
            # Riepilogo singolo prodotto
            try:
                variants = self.load_product_variants(product_type)
                info = self.get_product_info(product_type)
                
                print(f"\n📊 Riepilogo {info['name']}:")
                print(f"   👕 Totale varianti: {len(variants)}")
                
                # Raggruppa per colore
                colors = {}
                sizes = set()
                
                for variant in variants:
                    color = variant['color']
                    size = variant['size']
                    
                    if color not in colors:
                        colors[color] = 0
                    colors[color] += 1
                    sizes.add(size)
                
                print(f"   🎨 Colori disponibili: {len(colors)}")
                print(f"   📏 Taglie disponibili: {sorted(sizes)}")
                print(f"   💰 Prezzo: €{variants[0]['price']:.2f}")
                
                # Top 5 colori
                top_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"   🔝 Top colori: {', '.join([f'{color} ({count})' for color, count in top_colors])}")
                
            except Exception as e:
                print(f"❌ Errore nel riepilogo di {product_type}: {e}")
        else:
            # Riepilogo tutti i prodotti
            all_variants = self.load_all_variants()
            
            print(f"\n📊 Riepilogo Generale:")
            for product_type, variants in all_variants.items():
                info = self.get_product_info(product_type)
                print(f"   • {info['name']}: {len(variants)} varianti")


def main():
    """Test function per verificare il funzionamento"""
    print("🧪 TEST VARIANT LOADER")
    print("=" * 40)
    
    # Inizializza loader
    loader = VariantLoader()
    
    # Test 1: Lista prodotti disponibili
    print("\n1️⃣ Test: Lista prodotti disponibili")
    loader.list_products()
    
    # Test 2: Carica singolo prodotto
    products = loader.get_available_products()
    if products:
        test_product = products[0]
        print(f"\n2️⃣ Test: Caricamento {test_product}")
        try:
            variants = loader.load_product_variants(test_product)
            print(f"   ✅ Caricate {len(variants)} varianti")
            
            # Mostra prime 3 varianti
            print("   🔍 Prime 3 varianti:")
            for i, variant in enumerate(variants[:3]):
                print(f"      {i+1}. ID:{variant['variant_id']} - {variant['color']} {variant['size']} - €{variant['price']}")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    # Test 3: Carica tutti i prodotti
    print(f"\n3️⃣ Test: Caricamento di tutti i prodotti")
    try:
        all_variants = loader.load_all_variants()
        print(f"   ✅ Test completato con successo!")
    except Exception as e:
        print(f"   ❌ Errore nel test: {e}")
    
    # Test 4: Riepilogo
    if products:
        print(f"\n4️⃣ Test: Riepilogo dettagliato")
        loader.get_variants_summary(products[0])


if __name__ == "__main__":
    main()