#!/usr/bin/env python3
"""
API Client - Gestione pura delle chiamate API Printful
Estratto da product_creator.py per separare responsabilità
"""

import requests
import time
from typing import Dict, Optional


class PrintfulAPIClient:
    """
    Client dedicato alle chiamate API Printful.
    Gestisce autenticazione, rate limiting, retry logic.
    """
    
    def __init__(self, api_key: str, store_id: str):
        self.api_key = api_key
        self.store_id = store_id
        self.base_url = "https://api.printful.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-PF-Store-Id": store_id
        }
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limiting: max 1 req/sec
    
    def _wait_for_rate_limit(self) -> None:
        """Implementa rate limiting per evitare errori API"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            time.sleep(wait_time)
    
    def _validate_response(self, response: requests.Response, endpoint: str) -> Dict:
        """
        Valida e processa la risposta API
        
        Args:
            response: Oggetto Response di requests
            endpoint: Endpoint chiamato (per debug)
            
        Returns:
            Dizionario JSON della risposta
            
        Raises:
            Exception: Se la risposta non è valida
        """
        try:
            result = response.json()
        except ValueError:
            raise Exception(f"Risposta non JSON da {endpoint}: {response.text}")
        
        # Log per debug (solo codici di errore)
        if response.status_code not in [200, 201]:
            print(f"⚠️ API Warning {response.status_code} su {endpoint}")
        
        return result
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, retries: int = 3) -> Dict:
        """
        Esegue richiesta HTTP all'API Printful con retry logic
        
        Args:
            method: Metodo HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint API relativo
            data: Dati da inviare (per POST/PUT)
            retries: Numero tentativi in caso di errore
            
        Returns:
            Risposta JSON dell'API
            
        Raises:
            Exception: Se tutti i tentativi falliscono
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                # Rate limiting
                self._wait_for_rate_limit()
                
                # Esegui richiesta
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data, timeout=30)
                elif method == "PUT":
                    response = requests.put(url, headers=self.headers, json=data, timeout=30)
                elif method == "DELETE":
                    response = requests.delete(url, headers=self.headers, timeout=30)
                else:
                    raise ValueError(f"Metodo HTTP non supportato: {method}")
                
                self.last_request_time = time.time()
                
                # Valida e ritorna risposta
                return self._validate_response(response, endpoint)
                
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2  # Backoff esponenziale
                    print(f"⏳ Timeout su {endpoint}, retry in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Timeout definitivo su {endpoint}")
                
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"🔄 Errore rete su {endpoint}, retry in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Errore rete su {endpoint}: {e}")
                
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠️ Errore generico su {endpoint}: {e}")
                    time.sleep(1)
                    continue
                raise
        
        raise Exception(f"Tutti i tentativi falliti per {endpoint}")
    
    def test_connection(self) -> bool:
        """
        Testa la connessione API con una chiamata leggera
        
        Returns:
            True se la connessione funziona
        """
        try:
            response = self.make_request("GET", "/store")
            return response.get("code") in [200, 201]
        except:
            return False
    
    def get_api_info(self) -> Dict:
        """Ottiene informazioni sul client API"""
        return {
            "base_url": self.base_url,
            "store_id": self.store_id,
            "api_key_preview": f"{self.api_key[:8]}..." if self.api_key else "Non configurato",
            "rate_limit": f"{self.min_request_interval}s tra richieste"
        }