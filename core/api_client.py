#!/usr/bin/env python3
"""
API Client - Client HTTP pulito per Printful API
Responsabilità: SOLO chiamate HTTP, nessuna logica business
"""

import requests
import time
from typing import Dict, Optional


class PrintfulAPIClient:
    """Client API Printful minimale e veloce"""
    
    BASE_URL = "https://api.printful.com"
    
    def __init__(self, api_key: str, store_id: str):
        """
        Inizializza client API
        
        Args:
            api_key: Token API Printful
            store_id: ID dello store Printful
        """
        self.api_key = api_key
        self.store_id = store_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            #!/ "X-PF-Store-Id": store_id
        }
    
    def request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                retries: int = 3) -> Dict:
        """
        Esegue richiesta HTTP con retry automatico
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Endpoint API (es: /store/products)
            data: Payload JSON (opzionale)
            retries: Numero tentativi in caso errore
            
        Returns:
            Risposta JSON da Printful
            
        Raises:
            Exception: Se tutti i tentativi falliscono
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, 
                                           json=data, timeout=30)
                elif method == "PUT":
                    response = requests.put(url, headers=self.headers, 
                                          json=data, timeout=30)
                elif method == "DELETE":
                    response = requests.delete(url, headers=self.headers, timeout=30)
                else:
                    raise ValueError(f"Metodo HTTP non supportato: {method}")
                
                # Rate limit handling
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 60))
                    if attempt < retries - 1:
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise Exception(f"Timeout su {endpoint}")
                
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"Errore richiesta {method} {endpoint}: {e}")
        
        raise Exception(f"Tutti i {retries} tentativi falliti per {endpoint}")
    
    # Metodi helper per readability
    def get(self, endpoint: str) -> Dict:
        """GET request"""
        return self.request("GET", endpoint)
    
    def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request"""
        return self.request("POST", endpoint, data)
    
    def put(self, endpoint: str, data: Dict) -> Dict:
        """PUT request"""
        return self.request("PUT", endpoint, data)
    
    def delete(self, endpoint: str) -> Dict:
        """DELETE request"""
        return self.request("DELETE", endpoint)