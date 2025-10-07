#!/usr/bin/env python3
"""
File Manager - Gestione upload e preparazione file
Responsabilità: Upload immagini e preparazione URL
"""

import os
from typing import Dict, Optional


class FileManager:
    """Gestisce upload e preparazione file per prodotti"""
    
    def __init__(self, uploader):
        """
        Args:
            uploader: Istanza CloudinaryUploader
        """
        self.uploader = uploader
        self._cache = {}  # Cache URL per evitare upload duplicati
    
    def prepare_urls(self, design_file: str) -> Dict[str, Optional[str]]:
        """
        Prepara tutte le URL necessarie per un prodotto
        
        Args:
            design_file: Path file design principale
            
        Returns:
            Dict con 'design_url', 'logo_url', 'upscaled_url'
        """
        urls = {
            "design_url": None,
            "logo_url": None,
            "upscaled_url": None
        }
        
        # 1. Upload design principale (obbligatorio)
        urls["design_url"] = self._upload_with_cache(design_file)
        
        # 2. Upload logo (opzionale)
        logo_path = "generate/universal_logo.png"
        if os.path.exists(logo_path):
            urls["logo_url"] = self._upload_with_cache(logo_path)
        
        # 3. Upload design upscaled (opzionale)
        design_name = os.path.splitext(os.path.basename(design_file))[0]
        upscaled_path = f"upscaled/{design_name}.png"
        
        if os.path.exists(upscaled_path):
            urls["upscaled_url"] = self._upload_with_cache(upscaled_path)
        
        return urls
    
    def _upload_with_cache(self, file_path: str) -> str:
        """
        Upload con cache per evitare duplicati
        
        Args:
            file_path: Path del file
            
        Returns:
            URL dell'immagine
        """
        # Controlla cache
        if file_path in self._cache:
            return self._cache[file_path]
        
        # Upload
        url = self.uploader.upload_image(file_path)
        
        # Salva in cache
        self._cache[file_path] = url
        
        return url
    
    def clear_cache(self):
        """Pulisce cache URL"""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Ritorna numero elementi in cache"""
        return len(self._cache)