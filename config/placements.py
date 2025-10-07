#!/usr/bin/env python3
"""
Placements Configuration - Configurazione posizioni ricami/stampe
FOCUS: Facile modifica posizioni cappelli
Valori RELATIVI secondo documentazione Printful
"""

from typing import Dict, Optional


# ============================================================================
# POSIZIONI CAPPELLI - FACILMENTE MODIFICABILI
# ============================================================================

HAT_PLACEMENTS = {
    "embroidery_front": {
        "area_width": 12.0,      # Area frontale cappello
        "area_height": 8.0,      # Altezza area frontale
        "width": 5.0,            # Larghezza logo
        "height": 4.0,           # Altezza logo
        "top": 2.5,              # 🔧 MODIFICA QUI per spostare su/giù
        "left": 1.5,             # 🔧 MODIFICA QUI per spostare sx/dx
        "limit_to_print_area": True
    },
    "embroidery_left": {
        "area_width": 8.0,       # Area laterale più piccola
        "area_height": 6.0,      
        "width": 3.0,            # Logo laterale più piccolo
        "height": 2.5,
        "top": 1.5,              # 🔧 MODIFICA QUI
        "left": 2.5,             # 🔧 MODIFICA QUI
        "limit_to_print_area": True
    },
    "embroidery_right": {
        "area_width": 8.0,
        "area_height": 6.0,
        "width": 3.0,
        "height": 2.5,
        "top": 1.5,              # 🔧 MODIFICA QUI
        "left": 2.5,             # 🔧 MODIFICA QUI
        "limit_to_print_area": True
    }
}


# ============================================================================
# POSIZIONI MANICHE/POLSI - Già ottimizzate (abbassate 70%)
# ============================================================================

SLEEVE_PLACEMENTS = {
    "embroidery_sleeve_left_top": {
        "area_width": 10.0,
        "area_height": 15.0,
        "width": 3.0,
        "height": 3.0,
        "top": 9.5,              # Abbassato 70%
        "left": 3.5,
        "limit_to_print_area": False
    },
    "embroidery_sleeve_right_top": {
        "area_width": 10.0,
        "area_height": 15.0,
        "width": 3.0,
        "height": 3.0,
        "top": 9.5,
        "left": 3.5,
        "limit_to_print_area": False
    },
    "embroidery_wrist_left": {
        "area_width": 8.0,
        "area_height": 12.0,
        "width": 2.4,
        "height": 2.4,
        "top": 7.6,
        "left": 2.8,
        "limit_to_print_area": False
    },
    "embroidery_wrist_right": {
        "area_width": 8.0,
        "area_height": 12.0,
        "width": 2.4,
        "height": 2.4,
        "top": 7.6,
        "left": 2.8,
        "limit_to_print_area": False
    }
}


# ============================================================================
# POSIZIONI PETTO - Standardizzate
# ============================================================================

CHEST_PLACEMENTS = {
    "embroidery_chest_left": {
        "area_width": 18.0,
        "area_height": 24.0,
        "width": 2.0,
        "height": 2.0,
        "top": 3.0,
        "left": 4.0,
        "limit_to_print_area": True
    },
    "embroidery_chest_right": {
        "area_width": 18.0,
        "area_height": 24.0,
        "width": 4.0,
        "height": 4.0,
        "top": 3.0,
        "left": 10.0,
        "limit_to_print_area": True
    },
    "embroidery_chest_center": {
        "area_width": 18.0,
        "area_height": 24.0,
        "width": 5.0,
        "height": 5.0,
        "top": 4.0,
        "left": 6.5,
        "limit_to_print_area": True
    }
}


# ============================================================================
# MAPPER COMPLETO - Unisce tutte le configurazioni
# ============================================================================

ALL_PLACEMENTS = {
    **HAT_PLACEMENTS,
    **SLEEVE_PLACEMENTS,
    **CHEST_PLACEMENTS
}


# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_placement_config(placement_type: str) -> Optional[Dict]:
    """
    Ottiene configurazione posizione per un placement type
    
    Args:
        placement_type: Tipo placement (es: 'embroidery_front')
        
    Returns:
        Configurazione position o None se non trovata
    """
    return ALL_PLACEMENTS.get(placement_type)


def has_custom_position(placement_type: str) -> bool:
    """
    Verifica se un placement ha configurazione custom
    
    Args:
        placement_type: Tipo placement
        
    Returns:
        True se ha configurazione custom
    """
    return placement_type in ALL_PLACEMENTS


def apply_position(placement_type: str, file_config: Dict) -> Dict:
    """
    Applica configurazione posizione a file config
    
    Args:
        placement_type: Tipo placement
        file_config: Configurazione file base
        
    Returns:
        File config con position applicato (se disponibile)
    """
    position = get_placement_config(placement_type)
    
    if position:
        file_config["position"] = position.copy()
    
    return file_config


# ============================================================================
# UTILITY per modifiche rapide cappelli
# ============================================================================

def update_hat_position(placement: str, top: float = None, 
                        left: float = None) -> None:
    """
    Modifica rapida posizione cappello (per testing)
    
    Args:
        placement: 'embroidery_front', 'embroidery_left', 'embroidery_right'
        top: Nuovo valore top (opzionale)
        left: Nuovo valore left (opzionale)
    """
    if placement not in HAT_PLACEMENTS:
        raise ValueError(f"Placement {placement} non è un placement cappello")
    
    if top is not None:
        HAT_PLACEMENTS[placement]["top"] = top
        ALL_PLACEMENTS[placement]["top"] = top
    
    if left is not None:
        HAT_PLACEMENTS[placement]["left"] = left
        ALL_PLACEMENTS[placement]["left"] = left


def get_hat_positions_summary() -> str:
    """
    Ritorna sommario posizioni cappelli per debug
    
    Returns:
        Stringa con sommario posizioni
    """
    lines = ["🧢 POSIZIONI CAPPELLI:"]
    
    for placement, config in HAT_PLACEMENTS.items():
        lines.append(f"\n{placement}:")
        lines.append(f"  Area: {config['area_width']}x{config['area_height']}")
        lines.append(f"  Logo: {config['width']}x{config['height']}")
        lines.append(f"  Posizione: top={config['top']}, left={config['left']}")
    
    return "\n".join(lines)