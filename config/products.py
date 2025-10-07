#!/usr/bin/env python3
"""
Products Configuration - Definizione prodotti e placements
Configurazione pulita e leggibile di tutti i prodotti supportati
"""

from typing import Dict, List


# ============================================================================
# DEFINIZIONE PRODOTTI
# ============================================================================

PRODUCTS = {
    "gildan_5000": {
        "name": "Gildan 5000 - T-shirt",
        "category": "tshirt",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery",
                "order": 1  # Design principale
            },
            {
                "type": "embroidery_sleeve_left_top",
                "description": "Ricamo manica sinistra",
                "design_type": "embroidery",
                "order": 2  # Logo
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg",
                "order": 3  # Upscaled
            }
        ]
    },
    
    "gildan_18000": {
        "name": "Gildan 18000 - Felpa",
        "category": "sweatshirt",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery",
                "order": 1
            },
            {
                "type": "embroidery_wrist_left",
                "description": "Ricamo polso sinistro",
                "design_type": "embroidery",
                "order": 2
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg",
                "order": 3
            }
        ]
    },
    
    "gildan_18500": {
        "name": "Gildan 18500 - Felpa con Cappuccio",
        "category": "hoodie",
        "placements": [
            {
                "type": "embroidery_chest_left",
                "description": "Ricamo petto sinistro",
                "design_type": "embroidery",
                "order": 1
            },
            {
                "type": "embroidery_wrist_left",
                "description": "Ricamo polso sinistro",
                "design_type": "embroidery",
                "order": 2
            },
            {
                "type": "back",
                "description": "Stampa DTG retro",
                "design_type": "dtg",
                "order": 3
            }
        ]
    },
    
    "as_colour_1120": {
        "name": "AS Colour 1120 - Beanie",  # ← Era "T-shirt"
        "category": "hat",                   # ← Aggiungi categoria
        "placements": [
            {
                "type": "embroidery_front",  # ← Solo front per beanie
                "description": "Ricamo frontale",
                "design_type": "embroidery",
                "order": 1
            }
        ]
    },
    
    "yupoong_6089m": {
        "name": "Yupoong 6089M - Cappello",
        "category": "hat",
        "placements": [
            {
                "type": "embroidery_front",
                "description": "Ricamo frontale",
                "design_type": "embroidery",
                "order": 1  # Design principale
            },
            {
                "type": "embroidery_left",
                "description": "Ricamo lato sinistro",
                "design_type": "embroidery",
                "order": 2  # Logo
            }
        ]
    }
}


# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_product(product_type: str) -> Dict:
    """
    Ottiene configurazione completa prodotto
    
    Args:
        product_type: Chiave prodotto (es: 'gildan_5000')
        
    Returns:
        Configurazione prodotto
        
    Raises:
        ValueError: Se prodotto non esiste
    """
    if product_type not in PRODUCTS:
        available = ", ".join(PRODUCTS.keys())
        raise ValueError(
            f"Prodotto '{product_type}' non configurato.\n"
            f"Disponibili: {available}"
        )
    
    return PRODUCTS[product_type]


def get_product_name(product_type: str) -> str:
    """Ottiene nome prodotto"""
    return get_product(product_type)["name"]


def get_product_placements(product_type: str) -> List[Dict]:
    """Ottiene lista placements per prodotto"""
    return get_product(product_type)["placements"]


def get_all_products() -> List[str]:
    """Ottiene lista di tutti i prodotti disponibili"""
    return list(PRODUCTS.keys())


def get_products_by_category(category: str) -> List[str]:
    """
    Filtra prodotti per categoria
    
    Args:
        category: 'tshirt', 'sweatshirt', 'hoodie', 'hat'
        
    Returns:
        Lista chiavi prodotti della categoria
    """
    return [
        key for key, config in PRODUCTS.items()
        if config["category"] == category
    ]


def is_hat(product_type: str) -> bool:
    """Verifica se prodotto è un cappello"""
    return get_product(product_type)["category"] == "hat"


def get_embroidery_placements(product_type: str) -> List[Dict]:
    """Ottiene solo placements ricamo per prodotto"""
    placements = get_product_placements(product_type)
    return [p for p in placements if p["design_type"] == "embroidery"]


def get_dtg_placements(product_type: str) -> List[Dict]:
    """Ottiene solo placements DTG per prodotto"""
    placements = get_product_placements(product_type)
    return [p for p in placements if p["design_type"] == "dtg"]


def requires_logo(product_type: str) -> bool:
    """Verifica se prodotto richiede logo (ha più di 1 placement ricamo)"""
    embroidery = get_embroidery_placements(product_type)
    return len(embroidery) > 1


def requires_upscaled(product_type: str) -> bool:
    """Verifica se prodotto richiede design upscaled (ha DTG)"""
    dtg = get_dtg_placements(product_type)
    return len(dtg) > 0


# ============================================================================
# INFO UTILITY
# ============================================================================

def print_products_summary():
    """Stampa sommario di tutti i prodotti configurati"""
    print("📦 PRODOTTI CONFIGURATI")
    print("=" * 60)
    
    for product_type, config in PRODUCTS.items():
        print(f"\n{config['name']} ({product_type})")
        print(f"  Categoria: {config['category']}")
        print(f"  Placements: {len(config['placements'])}")
        
        for placement in config['placements']:
            icon = "🧵" if placement['design_type'] == 'embroidery' else "🖨️"
            print(f"    {icon} {placement['description']} ({placement['type']})")


def get_product_info(product_type: str) -> str:
    """
    Ottiene info formattate su un prodotto
    
    Returns:
        Stringa con info prodotto
    """
    config = get_product(product_type)
    
    lines = [
        f"📦 {config['name']}",
        f"Categoria: {config['category']}",
        f"Placements: {len(config['placements'])}",
        ""
    ]
    
    for i, placement in enumerate(config['placements'], 1):
        icon = "🧵" if placement['design_type'] == 'embroidery' else "🖨️"
        lines.append(
            f"{i}. {icon} {placement['description']} "
            f"({placement['type']}) - Order {placement['order']}"
        )
    
    return "\n".join(lines)