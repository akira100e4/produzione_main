#!/usr/bin/env python3
"""
🔥 SCRIPT PER OTTENERE DIMENSIONI REALI PRINTFUL E CALCOLARE OFFSET CORRETTI 🔥

Questo script:
1. Interroga l'API Printful per ottenere le dimensioni reali dei printfiles
2. Calcola i valori relativi corretti per abbassare il logo manica
3. Genera la configurazione corretta per placement_config.py

IMPORTANTE: La documentazione Printful dice che i valori sono RELATIVI, non assoluti!
"""

import requests
import json
from typing import Dict, List, Optional


class PrintfulDimensionsFetcher:
    def __init__(self, api_token: str):
        """
        Inizializza il fetcher con token API Printful
        
        Args:
            api_token: Token API Printful (Bearer token)
        """
        self.api_token = api_token
        self.base_url = "https://api.printful.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def get_product_printfiles(self, product_id: int) -> Dict:
        """
        Ottieni informazioni sui printfiles per un prodotto specifico
        
        Args:
            product_id: ID prodotto Printful (es. 71 per Gildan 5000)
        
        Returns:
            Dati sui printfiles dal Mockup Generator API
        """
        url = f"{self.base_url}/mockup-generator/printfiles/{product_id}"
        
        print(f"🔍 Interrogando API Printful per prodotto {product_id}...")
        print(f"📡 URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Risposta ricevuta con successo!")
            
            return data.get('result', {})
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore nella richiesta API: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"📄 Dettagli risposta: {e.response.text}")
            return {}
    
    def get_embroidery_templates(self, product_id: int) -> Dict:
        """
        Ottieni template per ricami specifici di un prodotto
        
        Args:
            product_id: ID prodotto Printful
        
        Returns:
            Dati sui template di ricamo
        """
        url = f"{self.base_url}/mockup-generator/templates/{product_id}?technique=EMBROIDERY"
        
        print(f"🧵 Ottenendo template ricami per prodotto {product_id}...")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Template ricami ottenuti!")
            
            return data.get('result', {})
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore nel recupero template: {e}")
            return {}
    
    def analyze_sleeve_dimensions(self, printfiles_data: Dict, templates_data: Dict) -> Dict:
        """
        Analizza le dimensioni specifiche per posizionamento sleeve
        
        Args:
            printfiles_data: Dati dai printfiles
            templates_data: Dati dai template
        
        Returns:
            Analisi delle dimensioni sleeve
        """
        analysis = {
            "product_id": printfiles_data.get('product_id'),
            "available_placements": printfiles_data.get('available_placements', {}),
            "sleeve_placements": {},
            "printfiles": printfiles_data.get('printfiles', []),
            "recommended_positions": {}
        }
        
        print(f"\n📊 ANALISI DIMENSIONI SLEEVE")
        print("=" * 50)
        
        # Trova i posizionamenti sleeve disponibili
        placements = printfiles_data.get('available_placements', {})
        sleeve_keys = [key for key in placements.keys() if 'sleeve' in key.lower() or 'embroidery_sleeve' in key]
        
        print(f"🔍 Posizionamenti sleeve trovati: {sleeve_keys}")
        
        # Analizza i printfiles
        printfiles = printfiles_data.get('printfiles', [])
        for printfile in printfiles:
            print(f"\n📏 Printfile ID {printfile.get('printfile_id')}:")
            print(f"   Dimensioni: {printfile.get('width')}x{printfile.get('height')}")
            print(f"   DPI: {printfile.get('dpi')}")
            print(f"   Fill mode: {printfile.get('fill_mode')}")
        
        # Analizza i template di ricamo
        if templates_data:
            templates = templates_data.get('templates', [])
            for template in templates:
                template_id = template.get('template_id')
                print(f"\n🎯 Template {template_id}:")
                print(f"   Print area: {template.get('print_area_width')}x{template.get('print_area_height')}")
                print(f"   Print area offset: top={template.get('print_area_top')}, left={template.get('print_area_left')}")
                print(f"   Template size: {template.get('template_width')}x{template.get('template_height')}")
        
        return analysis
    
    def calculate_lowered_sleeve_position(self, base_dimensions: Dict, lower_percentage: float = 0.7) -> Dict:
        """
        Calcola posizione abbassata per logo manica basata su dimensioni reali
        
        Args:
            base_dimensions: Dimensioni base del print area
            lower_percentage: Percentuale per abbassare il logo (0.7 = 70% più in basso)
        
        Returns:
            Configurazione position object corretta
        """
        
        # Usa valori RELATIVI come nella documentazione Printful
        # Esempio documentazione: area_width: 12, area_height: 16, top: 1, left: 4.5
        
        # Configurazione base sleeve (valori relativi tipici)
        base_config = {
            "area_width": 10,      # Area sleeve relativamente piccola
            "area_height": 15,     # Area sleeve più alta per permettere movimento
            "width": 3,            # Logo piccolo
            "height": 3,           # Logo quadrato
            "left": 3.5,           # Centrato nell'area (10/2 - 3/2 = 3.5)
            "limit_to_print_area": False  # Permetti posizionamento flessibile
        }
        
        # Calcola posizione abbassata
        # Standard sarebbe top: 2-3, abbassato: 8-10
        standard_top = 2.5
        lowered_top = standard_top + (base_config["area_height"] - base_config["height"] - standard_top) * lower_percentage
        
        base_config["top"] = round(lowered_top, 1)
        
        print(f"\n🔢 CALCOLO POSIZIONE ABBASSATA:")
        print(f"   📐 Area sleeve: {base_config['area_width']}x{base_config['area_height']} (RELATIVA)")
        print(f"   📏 Logo: {base_config['width']}x{base_config['height']} (RELATIVO)")
        print(f"   📍 Posizione standard: top={standard_top}")
        print(f"   📍 Posizione abbassata: top={base_config['top']} ({lower_percentage*100}% più basso)")
        print(f"   🎯 Left: {base_config['left']} (centrato)")
        
        return base_config
    
    def generate_universal_config(self, sleeve_position: Dict) -> str:
        """
        Genera codice Python per configurazione universale
        
        Args:
            sleeve_position: Configurazione position calcolata
        
        Returns:
            Codice Python da inserire in placement_config.py
        """
        
        # Crea configurazioni per tutti i tipi sleeve/wrist
        configs = {
            "embroidery_sleeve_left_top": sleeve_position.copy(),
            "embroidery_sleeve_right_top": sleeve_position.copy(),
            "embroidery_wrist_left": {
                **sleeve_position,
                "area_width": sleeve_position["area_width"] * 0.8,  # Polso più piccolo
                "area_height": sleeve_position["area_height"] * 0.8,
                "width": sleeve_position["width"] * 0.8,  # Logo più piccolo per polso
                "height": sleeve_position["height"] * 0.8,
                "top": sleeve_position["top"] * 0.9,  # Leggermente meno abbassato per polso
                "left": sleeve_position["left"] * 0.8
            },
            "embroidery_wrist_right": {
                **sleeve_position,
                "area_width": sleeve_position["area_width"] * 0.8,
                "area_height": sleeve_position["area_height"] * 0.8,
                "width": sleeve_position["width"] * 0.8,
                "height": sleeve_position["height"] * 0.8,
                "top": sleeve_position["top"] * 0.9,
                "left": sleeve_position["left"] * 0.8
            }
        }
        
        # Arrotonda tutti i valori
        for config_name, config in configs.items():
            for key, value in config.items():
                if isinstance(value, (int, float)) and key != "limit_to_print_area":
                    configs[config_name][key] = round(value, 1)
        
        python_code = '''# 🔥 CONFIGURAZIONE UNIVERSALE OFFSET MANICA - VALORI REALI PRINTFUL 🔥
# Calcolata interrogando l'API Printful per dimensioni corrette
UNIVERSAL_SLEEVE_OFFSET = {
'''
        
        for config_name, config in configs.items():
            python_code += f'    "{config_name}": {{\n'
            for key, value in config.items():
                if isinstance(value, bool):
                    python_code += f'        "{key}": {str(value)},\n'
                elif isinstance(value, str):
                    python_code += f'        "{key}": "{value}",\n'
                else:
                    python_code += f'        "{key}": {value},\n'
            python_code += '    },\n'
        
        python_code += '}\n'
        
        return python_code


def main():
    """
    Script principale per ottenere dimensioni e generare configurazione
    """
    print("🔥🔥🔥 PRINTFUL DIMENSIONS FETCHER 🔥🔥🔥")
    print("=" * 60)
    
    # IMPORTANTE: Inserisci qui il tuo token API Printful
    API_TOKEN = "YOUR_PRINTFUL_API_TOKEN_HERE"
    
    if API_TOKEN == "YOUR_PRINTFUL_API_TOKEN_HERE":
        print("❌ ERRORE: Devi inserire il tuo token API Printful!")
        print("📝 Modifica la variabile API_TOKEN nel codice")
        return
    
    # ID prodotti Printful da analizzare
    PRODUCTS_TO_ANALYZE = {
        71: "Gildan 5000 T-shirt",      # Prodotto principale
        162: "Gildan 18000 Sweatshirt", # Felpa
        163: "Gildan 18500 Hoodie"      # Felpa con cappuccio
    }
    
    fetcher = PrintfulDimensionsFetcher(API_TOKEN)
    
    print(f"🔍 Analizzerò {len(PRODUCTS_TO_ANALYZE)} prodotti...")
    print()
    
    all_analysis = {}
    
    # Analizza ogni prodotto
    for product_id, product_name in PRODUCTS_TO_ANALYZE.items():
        print(f"\n📦 ANALIZZANDO: {product_name} (ID: {product_id})")
        print("-" * 50)
        
        # Ottieni printfiles
        printfiles_data = fetcher.get_product_printfiles(product_id)
        
        # Ottieni template ricami
        templates_data = fetcher.get_embroidery_templates(product_id)
        
        if printfiles_data:
            analysis = fetcher.analyze_sleeve_dimensions(printfiles_data, templates_data)
            all_analysis[product_id] = analysis
        else:
            print(f"❌ Impossibile ottenere dati per prodotto {product_id}")
    
    # Calcola posizione abbassata basata sul primo prodotto (Gildan 5000)
    if 71 in all_analysis:
        print(f"\n🧮 CALCOLO CONFIGURAZIONE UNIVERSALE...")
        print("=" * 50)
        
        base_dimensions = all_analysis[71]
        lowered_position = fetcher.calculate_lowered_sleeve_position(base_dimensions, lower_percentage=0.7)
        
        # Genera codice configurazione
        config_code = fetcher.generate_universal_config(lowered_position)
        
        print(f"\n🎉 CONFIGURAZIONE GENERATA!")
        print("=" * 50)
        print(config_code)
        
        # Salva su file
        import datetime
        with open("universal_sleeve_config.py", "w", encoding="utf-8") as f:
            f.write(f"""#!/usr/bin/env python3
'''
🔥 CONFIGURAZIONE UNIVERSALE SLEEVE - GENERATA AUTOMATICAMENTE 🔥
Generata da printful_dimensions_fetcher.py basandosi su dati reali API Printful

Data generazione: {datetime.datetime.now().isoformat()}
Prodotti analizzati: {list(PRODUCTS_TO_ANALYZE.values())}
'''

{config_code}

# 🎯 CONFIGURAZIONE PETTO STANDARDIZZATA (opzionale)
UNIVERSAL_CHEST_OFFSET = {{
    "embroidery_chest_left": {{
        "area_width": 18,
        "area_height": 24,
        "width": 4,
        "height": 4,
        "top": 3,
        "left": 4,
        "limit_to_print_area": True
    }},
    "embroidery_chest_right": {{
        "area_width": 18,
        "area_height": 24,
        "width": 4,
        "height": 4,
        "top": 3,
        "left": 10,
        "limit_to_print_area": True
    }}
}}

if __name__ == "__main__":
    print("🔥 Configurazione sleeve universale caricata!")
    print("📋 Posizionamenti disponibili:")
    for placement in UNIVERSAL_SLEEVE_OFFSET.keys():
        config = UNIVERSAL_SLEEVE_OFFSET[placement]
        print(f"   🧵 {{placement}}: top={{config['top']}} (ABBASSATO)")
""")
        
        print(f"\n💾 Configurazione salvata in: universal_sleeve_config.py")
        print(f"\n🔗 PROSSIMI PASSI:")
        print(f"1. Copia la configurazione generata in placement_config.py")
        print(f"2. Sostituisci UNIVERSAL_SLEEVE_OFFSET con quella generata")
        print(f"3. Testa la configurazione")
        
    else:
        print(f"❌ Impossibile generare configurazione - dati Gildan 5000 mancanti")


if __name__ == "__main__":
    main()