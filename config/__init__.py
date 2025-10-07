"""
Config package - Configurazioni prodotti e posizioni
"""

from .products import (
    get_product,
    get_product_name,
    get_product_placements,
    get_all_products,
    is_hat,
    requires_logo,
    requires_upscaled
)

from .placements import (
    get_placement_config,
    has_custom_position,
    apply_position,
    update_hat_position,
    get_hat_positions_summary
)

__all__ = [
    # Products
    'get_product',
    'get_product_name',
    'get_product_placements',
    'get_all_products',
    'is_hat',
    'requires_logo',
    'requires_upscaled',
    # Placements
    'get_placement_config',
    'has_custom_position',
    'apply_position',
    'update_hat_position',
    'get_hat_positions_summary'
]