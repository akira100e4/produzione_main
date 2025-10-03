#!/usr/bin/env python3
"""
🔥 CONFIGURAZIONE POSIZIONAMENTI - VERSIONE CON VALORI RELATIVI CORRETTI 🔥

IMPORTANTE: Basato sulla documentazione Printful che specifica che i valori sono RELATIVI, 
non assoluti! Esempio documentazione: area_width: 12, area_height: 16, top: 1, left: 4.5

QUESTO È IL FILE CHE VIENE EFFETTIVAMENTE IMPORTATO dal main_single_variant.py
"""

from typing import Dict, List


# 🔥 CONFIGURAZIONE UNIVERSALE OFFSET MANICA - VALORI RELATIVI CORRETTI 🔥
# Basata su documentazione Printful: valori piccoli e relativi, non grandi e assoluti
UNIVERSAL_SLEEVE_OFFSET = {
    "embroidery_sleeve_left_top": {
        "area_width": 10.0,          # Area sleeve relativamente piccola
        "area_height": 15.0,         # Area sleeve più alta per permettere movimento
        "width": 3.0,                # Logo piccolo
        "height": 3.0,               # Logo quadrato
        "top": 9.5,                  # 🔥 ABBASSATO! (70% più in basso nell'area)
        "left": 3.5,                 # Centrato nell'area
        "limit_to_print_area": False # Permetti posizionamento flessibile
    },
    "embroidery_sleeve_right_top": {
        "area_width": 10.0,
        "area_height": 15.0,
        "width": 3.0,
        "height": 3.0,
        "top": 9.5,                  # 🔥 ABBASSATO! Stesso offset per uniformità
        "left": 3.5,
        "limit_to_print_area": False
    },
    "embroidery_wrist_left": {
        "area_width": 8.0,           # Area polso più piccola della manica
        "area_height": 12.0,         # Proporzionalmente più piccola
        "width": 2.4,                # Logo più piccolo per polso
        "height": 2.4,
        "top": 7.6,                  # 🔥 ABBASSATO! Proporzionale all'area polso
        "left": 2.8,                 # Centrato nell'area polso
        "limit_to_print_area": False
    },
    "embroidery_wrist_right": {
        "area_width": 8.0,
        "area_height": 12.0,
        "width": 2.4,
        "height": 2.4,
        "top": 7.6,                  # 🔥 ABBASSATO! Stesso offset per uniformità
        "left": 2.8,
        "limit_to_print_area": False
    }
}

# 🎯 CONFIGURAZIONE UNIVERSALE RICAMO PETTO - VALORI RELATIVI CORRETTI
UNIVERSAL_CHEST_OFFSET = {
    "embroidery_chest_left": {
        "area_width": 18.0,          # Area petto standard
        "area_height": 24.0,         # Area petto più alta
        "width": 2.0,                # Logo petto dimensione media
        "height": 2.0,
        "top": 3.0,                  # Posizione standard petto
        "left": 4.0,                 # Verso sinistra per effetto "pocket"
        "limit_to_print_area": True  # Mantieni dentro area petto
    },
    "embroidery_chest_right": {
        "area_width": 18.0,
        "area_height": 24.0,
        "width": 4.0,
        "height": 4.0,
        "top": 3.0,
        "left": 10.0,                # Simmetrico a sinistra
        "limit_to_print_area": True
    },
    "embroidery_chest_center": {
        "area_width": 18.0,
        "area_height": 24.0,
        "width": 5.0,                # Logo centrale leggermente più grande
        "height": 5.0,
        "top": 4.0,
        "left": 6.5,                 # Centrato (18/2 - 5/2 = 6.5)
        "limit_to_print_area": True
    }
}


# Configurazione posizionamenti per prodotto (invariata)
PRODUCT_PLACEMENTS = {
    "gildan_5000": {
        "name": "Gildan 5000 - T-shirt",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery"
            },
            {
                "type": "embroidery_sleeve_left_top", 
                "description": "Ricamo manica sinistra",
                "design_type": "embroidery"
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg"
            }
        ]
    },
    
    "gildan_18000": {
        "name": "Gildan 18000 - Felpa",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro", 
                "design_type": "embroidery"
            },
            {
                "type": "embroidery_wrist_left",
                "description": "Ricamo polso sinistro",
                "design_type": "embroidery"
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg"
            }
        ]
    },
    
    "gildan_18500": {
        "name": "Gildan 18500 - Felpa con Cappuccio",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery"  
            },
            {
                "type": "embroidery_wrist_left",
                "description": "Ricamo polso sinistro",
                "design_type": "embroidery"
            },
            {
                "type": "back",
                "description": "Stampa DTG retro", 
                "design_type": "dtg"
            }
        ]
    },
    
    "as_colour_1120": {
        "name": "AS Colour 1120 - T-shirt",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery"
            },
            {
                "type": "embroidery_sleeve_left_top",
                "description": "Ricamo manica sinistra",
                "design_type": "embroidery"
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg"
            }
        ]
    },
    
    "yupoong_6089m": {
        "name": "Yupoong 6089M - Cappello",
        "placements": [
            {
                "type": "embroidery_front",
                "description": "Ricamo frontale",
                "design_type": "embroidery"
            },
            {
                "type": "embroidery_left",
                "description": "Ricamo lato sinistro", 
                "design_type": "embroidery"
            }
        ]
    }
}


def get_product_placements(product_type: str) -> List[Dict]:
    """Ottieni configurazione posizionamenti per un prodotto"""
    if product_type not in PRODUCT_PLACEMENTS:
        available = ", ".join(PRODUCT_PLACEMENTS.keys())
        raise ValueError(f"Prodotto '{product_type}' non configurato. Disponibili: {available}")
    
    return PRODUCT_PLACEMENTS[product_type]["placements"]


def get_product_placement_info(product_type: str) -> Dict:
    """Ottieni info complete sui posizionamenti di un prodotto"""
    if product_type not in PRODUCT_PLACEMENTS:
        return None
    
    return PRODUCT_PLACEMENTS[product_type]


def apply_universal_positioning(placement_type: str, file_config: Dict) -> Dict:
    """
    🔥 APPLICA POSIZIONAMENTO UNIVERSALE CON VALORI RELATIVI CORRETTI 🔥
    
    Args:
        placement_type: Tipo di posizionamento (es. embroidery_sleeve_left_top)
        file_config: Configurazione file base
    
    Returns:
        Configurazione file con posizionamento universale applicato
    """
    
    # Controlla se è un posizionamento manica/polso da modificare
    if placement_type in UNIVERSAL_SLEEVE_OFFSET:
        position_config = UNIVERSAL_SLEEVE_OFFSET[placement_type].copy()
        file_config["position"] = position_config
        
        print(f"   🔥 POSIZIONAMENTO UNIVERSALE SLEEVE applicato per {placement_type}:")
        print(f"      📐 Area RELATIVA: {position_config['area_width']}x{position_config['area_height']}")
        print(f"      📍 Posizione RELATIVA: left={position_config['left']}, top={position_config['top']} (ABBASSATO!)")
        print(f"      📏 Dimensione RELATIVA: {position_config['width']}x{position_config['height']}")
        print(f"      🚫 Limiti: {position_config['limit_to_print_area']}")
        
        return file_config
    
    # Controlla se è un posizionamento petto da standardizzare
    elif placement_type in UNIVERSAL_CHEST_OFFSET:
        position_config = UNIVERSAL_CHEST_OFFSET[placement_type].copy()
        file_config["position"] = position_config
        
        print(f"   🎯 POSIZIONAMENTO PETTO STANDARDIZZATO per {placement_type}:")
        print(f"      📍 Posizione RELATIVA: left={position_config['left']}, top={position_config['top']}")
        print(f"      📏 Dimensione RELATIVA: {position_config['width']}x{position_config['height']}")
        
        return file_config
    
    else:
        # Per altri tipi di posizionamento, mantieni configurazione standard
        print(f"   ℹ️  Posizionamento standard mantenuto per {placement_type}")
        return file_config


def create_variant_files_config(product_type: str, 
                               design_url: str, 
                               logo_url: str = None, 
                               upscaled_url: str = None) -> List[Dict]:
    """
    🔥 VERSIONE CON VALORI RELATIVI CORRETTI 🔥
    Crea configurazione files per una variante basata sul prodotto
    APPLICA OFFSET ABBASSATO PER TUTTE LE MANICHE DI TUTTI I PRODOTTI
    """
    print(f"🔧 DEBUG: create_variant_files_config RELATIVI CORRETTI per {product_type}")
    
    placements = get_product_placements(product_type)
    files_config = []
    
    for i, placement in enumerate(placements):
        placement_type = placement["type"]
        design_type = placement["design_type"]
        
        print(f"   📋 Processando placement: {placement_type}")
        
        # Assegna URL basandosi sulla posizione e tipo
        if i == 0:  # Prima posizione = design principale
            url = design_url
        elif i == 1 and logo_url:  # Seconda posizione = logo
            url = logo_url
        elif placement_type == "back" and upscaled_url:  # Retro = upscaled
            url = upscaled_url
        else:
            print(f"   ⏭️  Saltando {placement_type} - nessun URL disponibile")
            continue
        
        # Crea configurazione file base
        file_config = {
            "type": placement_type,
            "url": url
        }
        
        # Aggiungi opzioni per ricamo
        if design_type == "embroidery":
            file_config["options"] = [
                {"id": "auto_thread_color", "value": True}
            ]
        
        # 🔥🔥🔥 APPLICA POSIZIONAMENTO UNIVERSALE CON VALORI RELATIVI 🔥🔥🔥
        file_config = apply_universal_positioning(placement_type, file_config)
        
        files_config.append(file_config)
        print(f"   ✅ Configurazione aggiunta per {placement_type}")
    
    print(f"🔥 DEBUG: Ritorno {len(files_config)} configurazioni con VALORI RELATIVI")
    
    # Debug finale - verifica configurazioni
    sleeve_types = ["embroidery_sleeve_left_top", "embroidery_sleeve_right_top", 
                   "embroidery_wrist_left", "embroidery_wrist_right"]
    
    for config in files_config:
        if config['type'] in sleeve_types:
            if 'position' in config:
                top_value = config['position']['top']
                area_height = config['position']['area_height']
                print(f"🎯 CONFERMA RELATIVA: {config['type']} con top={top_value}/{area_height} (ABBASSATO!)")
            else:
                print(f"❌ ERRORE: {config['type']} SENZA position universale!")
    
    return files_config


def validate_product_compatibility(product_type: str, 
                                 has_logo: bool = True,
                                 has_dtg: bool = True) -> Dict:
    """Valida se un prodotto è compatibile con le risorse disponibili"""
    try:
        placements = get_product_placements(product_type)
        info = get_product_placement_info(product_type)
        
        # Controlla compatibilità  
        embroidery_positions = [p for p in placements if p["design_type"] == "embroidery"]
        dtg_positions = [p for p in placements if p["design_type"] == "dtg"]
        
        warnings = []
        
        # Verifica logo per seconda posizione ricamo
        if len(embroidery_positions) > 1 and not has_logo:
            warnings.append(f"Prodotto richiede logo per {embroidery_positions[1]['description']}")
        
        # Verifica DTG
        if dtg_positions and not has_dtg:
            warnings.append(f"Prodotto supporta {dtg_positions[0]['description']} ma manca design DTG")
        
        return {
            "compatible": True,
            "product_name": info["name"],
            "embroidery_positions": len(embroidery_positions),
            "dtg_positions": len(dtg_positions),
            "warnings": warnings,
            "placements": placements
        }
        
    except ValueError as e:
        return {
            "compatible": False,
            "error": str(e),
            "warnings": [],
            "placements": []
        }


def list_all_placements():
    """Stampa tutti i posizionamenti per tutti i prodotti"""
    print("🎯 POSIZIONAMENTI SUPPORTATI - VERSIONE VALORI RELATIVI CORRETTI")
    print("=" * 70)
    
    for product_type, config in PRODUCT_PLACEMENTS.items():
        print(f"\n📦 {config['name']} ({product_type}):")
        
        for i, placement in enumerate(config['placements'], 1):
            icon = "🧵" if placement['design_type'] == 'embroidery' else "🖨️"
            universal_indicator = ""
            
            # Indica se questo placement ha posizionamento universale
            if placement['type'] in UNIVERSAL_SLEEVE_OFFSET:
                universal_indicator = " 🔥 (OFFSET UNIVERSALE ABBASSATO - VALORI RELATIVI)"
            elif placement['type'] in UNIVERSAL_CHEST_OFFSET:
                universal_indicator = " 🎯 (STANDARDIZZATO - VALORI RELATIVI)"
            
            print(f"   {i}. {icon} {placement['description']} ({placement['type']}){universal_indicator}")


def get_universal_offset_summary():
    """Stampa riepilogo degli offset universali con valori relativi"""
    print("\n🔥🔥🔥 RIEPILOGO OFFSET UNIVERSALI - VALORI RELATIVI CORRETTI 🔥🔥🔥")
    print("=" * 70)
    print("📖 NOTA: Valori sono RELATIVI secondo documentazione Printful")
    print("   Esempio doc: area_width: 12, area_height: 16, top: 1, left: 4.5")
    print()
    
    print("📍 OFFSET MANICA/POLSO (ABBASSATI - VALORI RELATIVI):")
    for placement_type, config in UNIVERSAL_SLEEVE_OFFSET.items():
        percentage = (config['top'] / config['area_height']) * 100
        print(f"   🧵 {placement_type}:")
        print(f"      📐 Area RELATIVA: {config['area_width']}x{config['area_height']}")
        print(f"      📍 Posizione RELATIVA: left={config['left']}, top={config['top']} ({percentage:.1f}% dall'alto)")
        print(f"      📏 Dimensione RELATIVA: {config['width']}x{config['height']}")
        print(f"      🚫 Limiti: {config['limit_to_print_area']}")
        print()
    
    print("📍 OFFSET PETTO (STANDARDIZZATI - VALORI RELATIVI):")
    for placement_type, config in UNIVERSAL_CHEST_OFFSET.items():
        print(f"   🧵 {placement_type}:")
        print(f"      📍 Posizione RELATIVA: left={config['left']}, top={config['top']}")
        print(f"      📏 Dimensione RELATIVA: {config['width']}x{config['height']}")
        print()


def compare_old_vs_new_values():
    """Confronta i valori vecchi (assoluti sbagliati) con quelli nuovi (relativi corretti)"""
    print("\n📊 CONFRONTO VALORI VECCHI vs NUOVI")
    print("=" * 50)
    
    old_values = {
        "area_width": 1200,
        "area_height": 1800,
        "top": 1350,
        "left": 500,
        "width": 200,
        "height": 200
    }
    
    new_values = UNIVERSAL_SLEEVE_OFFSET["embroidery_sleeve_left_top"]
    
    print("❌ VALORI VECCHI (ASSOLUTI - SBAGLIATI):")
    for key, value in old_values.items():
        print(f"   {key}: {value}")
    
    print("\n✅ VALORI NUOVI (RELATIVI - CORRETTI):")
    for key, value in new_values.items():
        if key != "limit_to_print_area":
            print(f"   {key}: {value}")
    
    print(f"\n🔍 ANALISI:")
    print(f"   📏 Riduzione scala area: {old_values['area_width']/new_values['area_width']:.1f}x più piccola")
    print(f"   📍 Posizione top: da {old_values['top']} a {new_values['top']} (scala corretta)")
    print(f"   💡 I nuovi valori seguono la documentazione Printful!")


if __name__ == "__main__":
    # Test delle configurazioni CON VALORI RELATIVI CORRETTI
    print("🧪 TEST PLACEMENT CONFIGURATION - VALORI RELATIVI CORRETTI")
    print("=" * 70)
    
    # Test 1: Lista tutti i posizionamenti
    list_all_placements()
    
    # Test 2: Riepilogo offset universali
    get_universal_offset_summary()
    
    # Test 3: Confronto valori vecchi vs nuovi
    compare_old_vs_new_values()
    
    # Test 4: Validazione compatibilità 
    print(f"\n🔍 TEST COMPATIBILITÀ:")
    for product_type in PRODUCT_PLACEMENTS.keys():
        compat = validate_product_compatibility(product_type, has_logo=True, has_dtg=True)
        status = "✅" if compat["compatible"] else "❌"
        print(f"   {status} {compat.get('product_name', product_type)}")
        
        if compat.get("warnings"):
            for warning in compat["warnings"]:
                print(f"      ⚠️ {warning}")
    
    # Test 5: Test configurazione files per OGNI prodotto
    print(f"\n🛠️ TEST CONFIGURAZIONE FILES CON VALORI RELATIVI:")
    
    for product_type in PRODUCT_PLACEMENTS.keys():
        print(f"\n📦 Testing {product_type}:")
        
        try:
            files_config = create_variant_files_config(
                product_type,
                design_url="https://example.com/design.png",
                logo_url="https://example.com/logo.png", 
                upscaled_url="https://example.com/upscaled.png"
            )
            
            print(f"   📋 Configurazioni generate: {len(files_config)}")
            
            # Verifica offset applicati
            for file_config in files_config:
                if 'position' in file_config:
                    pos = file_config['position']
                    if file_config['type'] in UNIVERSAL_SLEEVE_OFFSET:
                        percentage = (pos['top'] / pos['area_height']) * 100
                        print(f"   🔥 {file_config['type']}: top={pos['top']}/{pos['area_height']} ({percentage:.1f}% - ABBASSATO!)")
                    elif file_config['type'] in UNIVERSAL_CHEST_OFFSET:
                        print(f"   🎯 {file_config['type']}: top={pos['top']}/{pos['area_height']} (STANDARDIZZATO)")
                        
        except Exception as e:
            print(f"   ❌ ERRORE per {product_type}: {e}")
    
    print(f"\n🎉 TEST CON VALORI RELATIVI COMPLETATO!")
    print("🔥 Tutti i prodotti ora hanno offset ABBASSATO con valori RELATIVI corretti!")
    print("📖 Basato su documentazione Printful: valori piccoli e relativi, non grandi e assoluti!")