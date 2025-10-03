#!/usr/bin/env python3
"""
Store Manager - Gestione store Printful e validazioni
Estratto da product_creator.py
"""

from typing import Dict, Optional
# IMPORT FISSO: uso import assoluto invece di relativo
from modules.product_creator.api_client import PrintfulAPIClient


class StoreManager:
    """
    Gestore dedicato alle operazioni di store Printful.
    Gestisce info store, limiti, validazioni.
    """
    
    def __init__(self, api_client: PrintfulAPIClient):
        self.api_client = api_client
        self._store_info_cache = None
    
    def get_store_info(self, use_cache: bool = True) -> Dict:
        """
        Ottiene informazioni dello store Printful
        
        Args:
            use_cache: Se utilizzare la cache per evitare chiamate multiple
            
        Returns:
            Dizionario con informazioni store
        """
        if use_cache and self._store_info_cache:
            return self._store_info_cache
        
        try:
            response = self.api_client.make_request("GET", "/store")
            self._store_info_cache = response
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Impossibile recuperare info store: {e}",
                "code": 0,
                "result": None
            }
    
    def validate_store_connection(self) -> Dict:
        """
        Valida la connessione allo store
        
        Returns:
            Dizionario con risultato validazione
        """
        store_info = self.get_store_info(use_cache=False)
        
        if store_info.get("code") in [200, 201]:
            store_data = store_info.get("result", {})
            return {
                "valid": True,
                "store_id": store_data.get("id"),
                "store_name": store_data.get("name", "Nome non disponibile"),
                "store_type": store_data.get("type", "Tipo non disponibile"),
                "message": "✅ Connessione store validata"
            }
        else:
            return {
                "valid": False,
                "error": store_info.get("error", "Errore sconosciuto"),
                "code": store_info.get("code", 0),
                "message": "❌ Connessione store non valida"
            }
    
    def check_store_limits(self) -> Dict:
        """
        Controlla i limiti dello store (se disponibili via API)
        
        Returns:
            Dizionario con info sui limiti
        """
        # Nota: Printful non espone sempre i limiti via API
        # Implementiamo controlli di base
        
        return {
            "max_products": "Illimitati (presumo)",
            "max_variants_per_product": 100,
            "api_rate_limit": "120 req/min",
            "concurrent_requests": 10,
            "note": "Limiti basati su documentazione Printful standard"
        }
    
    def get_store_summary(self) -> Dict:
        """
        Ottiene riepilogo completo dello store
        
        Returns:
            Riepilogo con tutte le info disponibili
        """
        validation = self.validate_store_connection()
        limits = self.check_store_limits()
        api_info = self.api_client.get_api_info()
        
        return {
            "connection": validation,
            "limits": limits,
            "api_client": api_info,
            "timestamp": __import__('time').time()
        }
    
    def clear_cache(self) -> None:
        """Pulisce la cache delle informazioni store"""
        self._store_info_cache = None