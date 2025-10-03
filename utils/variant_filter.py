#!/usr/bin/env python3
"""
Variant Filter - Script per filtrare e limitare le varianti dei prodotti
Risolve il problema del limite di 100 varianti per prodotto Printful
"""

import os
import json
import glob
from typing import List, Dict, Set, Optional
from collections import Counter


class VariantFilter:
    """Classe per filtrare le varianti dei prodotti"""
    
    def __init__(self, variants_folder: str = "variants", max_variants: int = 100):
        self.variants_folder = variants_folder
        self.max_variants = max_variants
        self.backup_folder = os.path.join(variants_folder, "backup")
        
        # Assicurati che la cartella backup esista
        os.makedirs(self.backup_folder, exist_ok=True)
    
    def analyze_product_variants(self, product_file: str) -> Dict:
        """
        Analizza le varianti di un prodotto
        
        Args:
            product_file: Path al file JSON del prodotto
            
        Returns:
            Dizionario con statistiche delle varianti
        """
        with open(product_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Estrai varianti (gestisce diversi formati JSON)
        variants = []
        if isinstance(data, list):
            variants = data
        elif 'variants' in data:
            variants = data['variants']
        elif 'data' in data:
            variants = data['data']
        elif 'result' in data:
            variants = data['result']
        else:
            raise ValueError(f"Formato JSON non riconosciuto in {product_file}")
        
        # Analizza colori e taglie
        colors = Counter()
        sizes = Counter()
        color_size_combinations = []
        
        for variant in variants:
            color = variant.get('color', 'Unknown')
            size = variant.get('size', 'Unknown')
            
            colors[color] += 1
            sizes[size] += 1
            color_size_combinations.append((color, size))
        
        return {
            'total_variants': len(variants),
            'colors': dict(colors),
            'sizes': dict(sizes),
            'color_count': len(colors),
            'size_count': len(sizes),
            'combinations': color_size_combinations,
            'variants': variants
        }
    
    def get_popular_colors(self, variants_stats: Dict, limit: int = 20) -> List[str]:
        """
        Ottieni i colori più popolari (ordinati per frequenza)
        
        Args:
            variants_stats: Statistiche dalle analisi
            limit: Numero massimo di colori
            
        Returns:
            Lista colori ordinata per popolarità
        """
        colors_by_popularity = sorted(
            variants_stats['colors'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [color for color, count in colors_by_popularity[:limit]]
    
    def get_standard_sizes(self, variants_stats: Dict) -> List[str]:
        """
        Ottieni taglie standard ordinate logicamente
        
        Args:
            variants_stats: Statistiche dalle analisi
            
        Returns:
            Lista taglie ordinate
        """
        available_sizes = list(variants_stats['sizes'].keys())
        
        # Ordine logico delle taglie
        size_order = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', 'One size', 'None']
        
        ordered_sizes = []
        for size in size_order:
            if size in available_sizes:
                ordered_sizes.append(size)
        
        # Aggiungi eventuali taglie non standard alla fine
        for size in available_sizes:
            if size not in ordered_sizes:
                ordered_sizes.append(size)
        
        return ordered_sizes
    
    def create_filtered_variants(self, 
                               variants_stats: Dict, 
                               selected_colors: List[str], 
                               selected_sizes: List[str]) -> List[Dict]:
        """
        Crea lista filtrata delle varianti
        
        Args:
            variants_stats: Statistiche varianti originali
            selected_colors: Colori da includere
            selected_sizes: Taglie da includere
            
        Returns:
            Lista varianti filtrate
        """
        filtered_variants = []
        
        for variant in variants_stats['variants']:
            color = variant.get('color', '')
            size = variant.get('size', '')
            
            if color in selected_colors and size in selected_sizes:
                filtered_variants.append(variant)
        
        return filtered_variants
    
    def suggest_optimal_selection(self, variants_stats: Dict) -> Dict:
        """
        Suggerisci selezione ottimale per rispettare il limite di 100 varianti
        
        Args:
            variants_stats: Statistiche varianti
            
        Returns:
            Dizionario con suggerimenti
        """
        total_variants = variants_stats['total_variants']
        
        if total_variants <= self.max_variants:
            return {
                'needs_filtering': False,
                'message': f"Il prodotto ha {total_variants} varianti, sotto il limite di {self.max_variants}"
            }
        
        # Calcola combinazioni ottimali
        available_colors = len(variants_stats['colors'])
        available_sizes = len(variants_stats['sizes'])
        
        # Trova la combinazione che si avvicina di più a 100
        best_combination = None
        best_total = 0
        
        for colors in range(1, available_colors + 1):
            for sizes in range(1, available_sizes + 1):
                total = colors * sizes
                if total <= self.max_variants and total > best_total:
                    best_total = total
                    best_combination = (colors, sizes)
        
        if not best_combination:
            best_combination = (10, 4)  # Fallback sicuro
            best_total = 40
        
        colors_to_keep, sizes_to_keep = best_combination
        
        # Ottieni colori e taglie più popolari
        popular_colors = self.get_popular_colors(variants_stats, colors_to_keep)
        standard_sizes = self.get_standard_sizes(variants_stats)[:sizes_to_keep]
        
        return {
            'needs_filtering': True,
            'original_total': total_variants,
            'suggested_total': best_total,
            'colors_to_keep': colors_to_keep,
            'sizes_to_keep': sizes_to_keep,
            'suggested_colors': popular_colors,
            'suggested_sizes': standard_sizes,
            'reduction_percentage': ((total_variants - best_total) / total_variants) * 100
        }
    
    def backup_original(self, product_file: str) -> str:
        """
        Crea backup del file originale
        
        Args:
            product_file: Path al file da backuppare
            
        Returns:
            Path del file di backup
        """
        filename = os.path.basename(product_file)
        backup_path = os.path.join(self.backup_folder, f"original_{filename}")
        
        # Copia solo se il backup non esiste già
        if not os.path.exists(backup_path):
            with open(product_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Backup salvato: {backup_path}")
        
        return backup_path
    
    def save_filtered_variants(self, 
                             product_file: str, 
                             filtered_variants: List[Dict], 
                             original_data: Dict = None) -> bool:
        """
        Salva le varianti filtrate nel file originale
        
        Args:
            product_file: Path al file da sovrascrivere
            filtered_variants: Varianti filtrate
            original_data: Dati originali (per mantenere struttura)
            
        Returns:
            True se salvato con successo
        """
        try:
            if original_data:
                # Mantieni la struttura originale
                new_data = original_data.copy()
                
                if isinstance(original_data, list):
                    new_data = filtered_variants
                elif 'variants' in original_data:
                    new_data['variants'] = filtered_variants
                elif 'data' in original_data:
                    new_data['data'] = filtered_variants
                elif 'result' in original_data:
                    new_data['result'] = filtered_variants
            else:
                # Struttura semplice
                new_data = filtered_variants
            
            with open(product_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ File filtrato salvato: {product_file}")
            print(f"   📊 Varianti: {len(filtered_variants)}")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel salvare {product_file}: {e}")
            return False
    
    def filter_product_interactive(self, product_file: str) -> bool:
        """
        Filtra un prodotto in modalità interattiva
        
        Args:
            product_file: Path al file del prodotto
            
        Returns:
            True se filtrato con successo
        """
        print(f"\n🔍 ANALISI: {os.path.basename(product_file)}")
        print("-" * 50)
        
        try:
            # Analizza varianti esistenti
            stats = self.analyze_product_variants(product_file)
            print(f"📊 Varianti totali: {stats['total_variants']}")
            print(f"🎨 Colori disponibili: {stats['color_count']}")
            print(f"📏 Taglie disponibili: {stats['size_count']}")
            
            # Ottieni suggerimenti
            suggestion = self.suggest_optimal_selection(stats)
            
            if not suggestion['needs_filtering']:
                print(f"✅ {suggestion['message']}")
                return True
            
            print(f"\n⚠️ LIMITE SUPERATO!")
            print(f"   📈 Varianti attuali: {suggestion['original_total']}")
            print(f"   🎯 Limite Printful: {self.max_variants}")
            print(f"   📉 Riduzione necessaria: {suggestion['reduction_percentage']:.1f}%")
            
            print(f"\n💡 SUGGERIMENTO OTTIMALE:")
            print(f"   🎨 Colori: {suggestion['colors_to_keep']} (da {stats['color_count']})")
            print(f"   📏 Taglie: {suggestion['sizes_to_keep']} (da {stats['size_count']})")
            print(f"   👕 Varianti risultanti: {suggestion['suggested_total']}")
            
            print(f"\n🎨 Colori suggeriti:")
            for i, color in enumerate(suggestion['suggested_colors'], 1):
                count = stats['colors'][color]
                print(f"   {i}. {color} ({count} varianti)")
            
            print(f"\n📏 Taglie suggerite:")
            for i, size in enumerate(suggestion['suggested_sizes'], 1):
                count = stats['sizes'][size]
                print(f"   {i}. {size} ({count} varianti)")
            
            # Chiedi conferma
            print(f"\n🤔 Vuoi applicare questa selezione ottimale?")
            confirm = input("   Digita 's' per confermare, 'n' per annullare: ").strip().lower()
            
            if confirm != 's':
                print("🚫 Filtro annullato")
                return False
            
            # Crea backup
            with open(product_file, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            self.backup_original(product_file)
            
            # Crea varianti filtrate
            filtered_variants = self.create_filtered_variants(
                stats, 
                suggestion['suggested_colors'], 
                suggestion['suggested_sizes']
            )
            
            # Salva file filtrato
            success = self.save_filtered_variants(product_file, filtered_variants, original_data)
            
            if success:
                print(f"\n🎉 FILTRO APPLICATO CON SUCCESSO!")
                print(f"   📉 {stats['total_variants']} → {len(filtered_variants)} varianti")
                print(f"   💾 Backup originale in: {self.backup_folder}/")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Errore nell'elaborazione di {product_file}: {e}")
            return False
    
    def restore_from_backup(self, product_file: str) -> bool:
        """
        Ripristina un file dal backup
        
        Args:
            product_file: Path al file da ripristinare
            
        Returns:
            True se ripristinato con successo
        """
        filename = os.path.basename(product_file)
        backup_path = os.path.join(self.backup_folder, f"original_{filename}")
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup non trovato: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            with open(product_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ File ripristinato da backup: {product_file}")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel ripristino: {e}")
            return False


def main():
    """Funzione principale per l'utilizzo interattivo"""
    print("🔧 VARIANT FILTER - Limitatore Varianti Printful")
    print("=" * 60)
    print("📋 Risolve il problema del limite di 100 varianti per prodotto")
    print("=" * 60)
    
    filter_tool = VariantFilter()
    
    # Trova tutti i file JSON nella cartella variants
    variants_pattern = os.path.join("variants", "*_data.json")
    json_files = glob.glob(variants_pattern)
    
    if not json_files:
        print("❌ Nessun file JSON trovato nella cartella variants/")
        return
    
    print(f"\n📁 Trovati {len(json_files)} file prodotto:")
    for i, file_path in enumerate(json_files, 1):
        filename = os.path.basename(file_path)
        try:
            stats = filter_tool.analyze_product_variants(file_path)
            status = "⚠️" if stats['total_variants'] > 100 else "✅"
            print(f"   {i}. {status} {filename} ({stats['total_variants']} varianti)")
        except Exception as e:
            print(f"   {i}. ❌ {filename} (errore: {e})")
    
    print(f"\n📋 OPZIONI:")
    print(f"   1-{len(json_files)}. Filtra prodotto specifico")
    print(f"   a. Filtra tutti i prodotti che superano 100 varianti")
    print(f"   r. Ripristina prodotto dal backup")
    print(f"   q. Esci")
    
    while True:
        try:
            choice = input(f"\nSeleziona opzione: ").strip().lower()
            
            if choice == 'q':
                print("👋 Arrivederci!")
                break
            elif choice == 'a':
                print(f"\n🚀 FILTRO AUTOMATICO DI TUTTI I PRODOTTI")
                filtered_count = 0
                
                for file_path in json_files:
                    try:
                        stats = filter_tool.analyze_product_variants(file_path)
                        if stats['total_variants'] > 100:
                            print(f"\n🔄 Elaborando {os.path.basename(file_path)}...")
                            if filter_tool.filter_product_interactive(file_path):
                                filtered_count += 1
                    except Exception as e:
                        print(f"❌ Errore con {file_path}: {e}")
                
                print(f"\n📊 RIEPILOGO: {filtered_count} prodotti filtrati")
                
            elif choice == 'r':
                print(f"\n🔄 RIPRISTINO DAL BACKUP")
                print("Seleziona il file da ripristinare:")
                for i, file_path in enumerate(json_files, 1):
                    filename = os.path.basename(file_path)
                    print(f"   {i}. {filename}")
                
                try:
                    restore_choice = int(input("Numero file da ripristinare: "))
                    if 1 <= restore_choice <= len(json_files):
                        selected_file = json_files[restore_choice - 1]
                        filter_tool.restore_from_backup(selected_file)
                    else:
                        print("❌ Numero non valido")
                except ValueError:
                    print("❌ Inserisci un numero valido")
                    
            elif choice.isdigit():
                file_index = int(choice)
                if 1 <= file_index <= len(json_files):
                    selected_file = json_files[file_index - 1]
                    filter_tool.filter_product_interactive(selected_file)
                else:
                    print(f"❌ Inserisci un numero tra 1-{len(json_files)}")
            else:
                print("❌ Opzione non valida")
                
        except KeyboardInterrupt:
            print("\n👋 Arrivederci!")
            break
        except Exception as e:
            print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()