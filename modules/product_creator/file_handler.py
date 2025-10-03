#!/usr/bin/env python3
"""
File Handler - Gestione file, cartelle e salvataggio risultati
Estratto da product_creator.py
"""

import os
import json
import glob
import time
from typing import List, Dict, Optional
from pathlib import Path


class FileHandler:
    """
    Gestore dedicato alle operazioni sui file.
    Gestisce ricerca design, salvataggio risultati, gestione cartelle.
    """
    
    def __init__(self, design_folder: str = "ricamo", output_folder: str = "json"):
        self.design_folder = design_folder
        self.output_folder = output_folder
        self.supported_extensions = ['.png', '.jpg', '.jpeg']
        
        # Crea cartelle se non esistono
        self._ensure_folders_exist()
    
    def _ensure_folders_exist(self) -> None:
        """Crea le cartelle necessarie se non esistono"""
        for folder in [self.design_folder, self.output_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"📁 Creata cartella: {folder}")
    
    def find_design_files(self, folder: Optional[str] = None) -> List[str]:
        """
        Trova tutti i file design nella cartella specificata
        
        Args:
            folder: Cartella dove cercare (default: self.design_folder)
            
        Returns:
            Lista ordinata dei file design trovati
        """
        search_folder = folder or self.design_folder
        
        if not os.path.exists(search_folder):
            print(f"⚠️ Cartella design non trovata: {search_folder}")
            return []
        
        design_files = []
        
        # Cerca file con estensioni supportate
        for ext in self.supported_extensions:
            pattern = os.path.join(search_folder, f"*{ext}")
            files = glob.glob(pattern)
            design_files.extend(files)
        
        # Ordina alfabeticamente
        design_files.sort()
        
        print(f"🎨 Trovati {len(design_files)} design files in '{search_folder}'")
        return design_files
    
    def get_design_file_info(self, file_path: str) -> Dict:
        """
        Ottiene informazioni dettagliate su un file design
        
        Args:
            file_path: Path del file
            
        Returns:
            Dizionario con info del file
        """
        if not os.path.exists(file_path):
            return {"exists": False, "error": "File non trovato"}
        
        stat = os.stat(file_path)
        
        return {
            "exists": True,
            "name": os.path.basename(file_path),
            "path": file_path,
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "extension": os.path.splitext(file_path)[1],
            "modified": time.ctime(stat.st_mtime)
        }
    
    def save_result(self, result: Dict, filename: str) -> bool:
        """
        Salva risultato in file JSON
        
        Args:
            result: Dizionario da salvare
            filename: Nome del file (relativo a output_folder)
            
        Returns:
            True se salvato con successo
        """
        try:
            # Assicura che il filename sia nella cartella output
            if not filename.startswith(self.output_folder):
                filepath = os.path.join(self.output_folder, filename)
            else:
                filepath = filename
            
            # Crea cartelle intermedie se necessario
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Salva con formattazione leggibile
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filepath)
            print(f"💾 Salvato: {filepath} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Errore salvataggio {filename}: {e}")
            return False
    
    def save_all_products_result(self, results: Dict, design_filename: str) -> Dict:
        """
        Salva risultati della creazione di tutti i prodotti
        
        Args:
            results: Dizionario con tutti i risultati
            design_filename: Nome del file design usato
            
        Returns:
            Dizionario con info sui salvataggi
        """
        base_name = os.path.splitext(design_filename)[0]
        saved_files = []
        failed_saves = []
        
        # Salva risultato individuale per ogni prodotto
        individual_results = results.get("results", {})
        for product_type, result in individual_results.items():
            if result.get("success"):
                filename = f"{base_name}_{product_type}.json"
                if self.save_result(result, filename):
                    saved_files.append(filename)
                else:
                    failed_saves.append(filename)
        
        # Salva riepilogo generale
        summary_filename = f"{base_name}_ALL_PRODUCTS_SUMMARY.json"
        if self.save_result(results, summary_filename):
            saved_files.append(summary_filename)
        else:
            failed_saves.append(summary_filename)
        
        print(f"📂 Salvataggio completato:")
        print(f"   ✅ File salvati: {len(saved_files)}")
        if failed_saves:
            print(f"   ❌ File falliti: {len(failed_saves)}")
        
        return {
            "saved_files": saved_files,
            "failed_saves": failed_saves,
            "total_attempts": len(saved_files) + len(failed_saves)
        }
    
    def cleanup_old_results(self, days_old: int = 30) -> Dict:
        """
        Pulisce risultati vecchi dalla cartella output
        
        Args:
            days_old: Giorni di anzianità per considerare un file vecchio
            
        Returns:
            Dizionario con statistiche pulizia
        """
        if not os.path.exists(self.output_folder):
            return {"deleted": 0, "error": "Cartella output non esiste"}
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_files = []
        
        for filename in os.listdir(self.output_folder):
            filepath = os.path.join(self.output_folder, filename)
            
            if os.path.isfile(filepath) and filename.endswith('.json'):
                if os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_files.append(filename)
                    except OSError as e:
                        print(f"⚠️ Errore eliminazione {filename}: {e}")
        
        return {
            "deleted": len(deleted_files),
            "deleted_files": deleted_files,
            "days_old": days_old
        }
    
    def get_folder_stats(self) -> Dict:
        """
        Ottiene statistiche delle cartelle gestite
        
        Returns:
            Dizionario con statistiche
        """
        stats = {}
        
        for folder_name, folder_path in [("design", self.design_folder), ("output", self.output_folder)]:
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                total_size = sum(
                    os.path.getsize(os.path.join(folder_path, f)) 
                    for f in files 
                    if os.path.isfile(os.path.join(folder_path, f))
                )
                
                stats[folder_name] = {
                    "path": folder_path,
                    "exists": True,
                    "files_count": len(files),
                    "total_size_mb": round(total_size / (1024 * 1024), 2)
                }
            else:
                stats[folder_name] = {
                    "path": folder_path,
                    "exists": False,
                    "files_count": 0,
                    "total_size_mb": 0
                }
        
        return stats