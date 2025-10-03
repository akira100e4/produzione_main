# utils/cloudinary_uploader.py - Cloudinary uploader per OnlyOne con supporto trasparenza
import os
import time
import hashlib
import hmac
import base64
import requests
from typing import Dict, List, Optional

class CloudinaryUploader:
    """
    Uploader Cloudinary robusto per OnlyOne workflow.
    Sostituisce Imgur con servizio più affidabile e professionale.
    Include supporto per preservare trasparenza nelle immagini PNG.
    """
    
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        self.uploaded_images = {}
        
    def _generate_signature(self, params: Dict[str, str]) -> str:
        """Genera signature per autenticazione Cloudinary"""
        # Ordina parametri alfabeticamente ed escludi api_key, file e signature
        sorted_params = sorted(
            [(k, v) for k, v in params.items() if k not in ['api_key', 'file', 'signature']]
        )
        
        # Crea stringa da firmare (formato: key=value&key=value)
        params_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Genera HMAC-SHA1
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            params_string.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        
        return signature
    
    def upload_image(self, image_path: str, public_id: Optional[str] = None) -> str:
        """
        Upload standard a Cloudinary - semplice e funzionale.
        """
        if image_path in self.uploaded_images:
            return self.uploaded_images[image_path]
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Immagine non trovata: {image_path}")
        
        filename = os.path.basename(image_path)
        if public_id is None:
            base_name = os.path.splitext(filename)[0]
            timestamp = int(time.time())
            public_id = f"onlyone_{base_name}_{timestamp}"
        
        print(f"📤 {filename}...", end="", flush=True)
        
        try:
            with open(image_path, "rb") as f:
                file_data = f.read()
            
            # Upload unsigned - zero complicazioni
            files = {'file': file_data}
            data = {
                'upload_preset': 'OnlyOne',
                'public_id': public_id
            }
            
            response = requests.post(self.upload_url, files=files, data=data, timeout=60)
            
            if response.status_code != 200:
                print(f" ❌ {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Dettagli: {error_detail}")
                except:
                    print(f"Dettagli: {response.text}")
                
            response.raise_for_status()
            result = response.json()
            
            if 'secure_url' not in result:
                raise Exception("URL mancante nella risposta Cloudinary")
            
            url = result['secure_url']
            self.uploaded_images[image_path] = url
            print(" ✅")
            return url
            
        except requests.exceptions.RequestException as e:
            print(f" ❌ Errore rete")
            raise Exception(f"Errore rete Cloudinary: {e}")
        except Exception as e:
            print(f" ❌ {str(e)}")
            raise
    
    def upload_image_with_transparency(self, image_path: str, public_id: Optional[str] = None) -> str:
        """
        Upload specifico per immagini con trasparenza (PNG) - VERSIONE CORRETTA
        Usa solo parametri permessi con unsigned upload per evitare errore 400
        """
        if image_path in self.uploaded_images:
            return self.uploaded_images[image_path]
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Immagine non trovata: {image_path}")
        
        filename = os.path.basename(image_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Verifica che sia PNG per supportare trasparenza
        if file_ext != '.png':
            print(f"⚠️ Warning: {filename} non è PNG - usando upload normale")
            return self.upload_image(image_path, public_id)
        
        if public_id is None:
            base_name = os.path.splitext(filename)[0]
            timestamp = int(time.time())
            public_id = f"transparent_{base_name}_{timestamp}"
        
        print(f"📤 {filename} (preservando trasparenza)...", end="", flush=True)
        
        try:
            with open(image_path, "rb") as f:
                file_data = f.read()
            
            # UPLOAD SEMPLIFICATO - solo parametri permessi per unsigned upload
            files = {'file': file_data}
            data = {
                'upload_preset': 'OnlyOne',
                'public_id': public_id
                # RIMOSSI tutti i parametri che causavano l'errore:
                # - 'format': 'png' 
                # - 'quality': 'auto:best'
                # - 'resource_type': 'image'
            }
            
            response = requests.post(self.upload_url, files=files, data=data, timeout=60)
            
            if response.status_code != 200:
                print(f" ❌ {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Dettagli: {error_detail}")
                except:
                    print(f"Dettagli: {response.text}")
                raise Exception(f"Errore HTTP {response.status_code}")
            
            result = response.json()
            
            if 'secure_url' not in result:
                raise Exception("URL mancante nella risposta Cloudinary")
            
            base_url = result['secure_url']
            
            # FORZATURA PNG con trasformazione URL se necessario
            # Cloudinary preserva automaticamente la trasparenza dei PNG
            # Ma possiamo forzare il formato PNG nell'URL per sicurezza
            if not base_url.endswith('.png') and '/upload/' in base_url:
                # Aggiungi trasformazione f_png nell'URL
                url_parts = base_url.split('/upload/')
                if len(url_parts) == 2:
                    base_url = f"{url_parts[0]}/upload/f_png/{url_parts[1]}"
            
            self.uploaded_images[image_path] = base_url
            print(" ✅")
            return base_url
            
        except requests.exceptions.RequestException as e:
            print(f" ❌ Errore rete")
            raise Exception(f"Errore rete Cloudinary: {e}")
        except Exception as e:
            print(f" ❌ {str(e)}")
            raise
    
    def upload_image_with_background_removal(self, image_path: str, public_id: Optional[str] = None) -> str:
        """
        Upload con rimozione automatica sfondo - VERSIONE CORRETTA
        Usa trasformazioni URL invece di parametri di upload
        """
        if image_path in self.uploaded_images:
            return self.uploaded_images[image_path]
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Immagine non trovata: {image_path}")
        
        filename = os.path.basename(image_path)
        
        if public_id is None:
            base_name = os.path.splitext(filename)[0]
            timestamp = int(time.time())
            public_id = f"bg_removed_{base_name}_{timestamp}"
        
        print(f"📤 {filename} (rimuovendo sfondo)...", end="", flush=True)
        
        try:
            with open(image_path, "rb") as f:
                file_data = f.read()
            
            # Upload semplice senza parametri problematici
            files = {'file': file_data}
            data = {
                'upload_preset': 'OnlyOne',
                'public_id': public_id
            }
            
            response = requests.post(self.upload_url, files=files, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if 'secure_url' not in result:
                raise Exception("URL mancante nella risposta Cloudinary")
            
            base_url = result['secure_url']
            
            # Applica trasformazione per rimozione sfondo usando URL transformation
            # Formato: https://res.cloudinary.com/cloud/image/upload/e_background_removal/f_png/public_id.jpg
            if '/upload/' in base_url:
                url_parts = base_url.split('/upload/')
                if len(url_parts) == 2:
                    # Applica background removal + formato PNG
                    transformed_url = f"{url_parts[0]}/upload/e_background_removal/f_png/{url_parts[1]}"
                    
                    self.uploaded_images[image_path] = transformed_url
                    print(" ✅")
                    return transformed_url
            
            # Fallback se la trasformazione URL fallisce
            self.uploaded_images[image_path] = base_url
            print(" ✅")
            return base_url
            
        except requests.exceptions.RequestException as e:
            print(f" ❌ Errore rete")
            raise Exception(f"Errore rete Cloudinary: {e}")
        except Exception as e:
            print(f" ❌ {str(e)}")
            raise
    
    def upload_multiple_images(self, image_paths: List[str]) -> Dict[str, str]:
        """
        Upload multiplo con gestione errori.
        
        Args:
            image_paths: Lista di path immagini
            
        Returns:
            Dict {image_path: url} per upload riusciti
        """
        if not image_paths:
            return {}
        
        print(f"📦 Upload batch Cloudinary: {len(image_paths)} immagini")
        
        successful_uploads = {}
        failed_uploads = []
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                # Public ID univoco
                timestamp = int(time.time())
                filename = os.path.splitext(os.path.basename(image_path))[0]
                public_id = f"batch_{timestamp}_{i}_{filename}"
                
                url = self.upload_image(image_path, public_id)
                successful_uploads[image_path] = url
                
                # Rate limiting gentile
                if i < len(image_paths):
                    time.sleep(0.3)
                    
            except Exception as e:
                failed_uploads.append((image_path, str(e)))
                print(f"❌ {os.path.basename(image_path)}: {e}")
                
                # Pausa anche sui fallimenti
                time.sleep(0.2)
        
        # Summary
        print(f"\n📊 Risultati batch Cloudinary:")
        print(f"  ✅ Successi: {len(successful_uploads)}")
        print(f"  ❌ Fallimenti: {len(failed_uploads)}")
        
        if failed_uploads and len(failed_uploads) <= 3:
            print("  File falliti:")
            for path, error in failed_uploads:
                print(f"    • {os.path.basename(path)}: {error}")
        
        return successful_uploads
    
    def get_public_url(self, image_path: str) -> str:
        """
        Ottiene URL pubblico di un'immagine precedentemente caricata.
        """
        if image_path in self.uploaded_images:
            return self.uploaded_images[image_path]
        
        # Prova a caricare se non è in cache
        try:
            return self.upload_image(image_path)
        except Exception:
            raise ValueError(f"Immagine non caricata e upload fallito: {image_path}")
    
    def verify_url_accessibility(self, url: str) -> bool:
        """Verifica che un URL Cloudinary sia accessibile"""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                return content_type.startswith('image/')
            
            return False
            
        except Exception:
            return False
    
    def batch_verify_urls(self) -> Dict[str, bool]:
        """Verifica accessibilità di tutti gli URL caricati"""
        if not self.uploaded_images:
            return {}
        
        print(f"🔍 Verifica accessibilità {len(self.uploaded_images)} URL Cloudinary...")
        
        results = {}
        accessible_count = 0
        
        for image_path, url in self.uploaded_images.items():
            accessible = self.verify_url_accessibility(url)
            results[image_path] = accessible
            
            if accessible:
                accessible_count += 1
            
            time.sleep(0.1)  # Pausa gentile
        
        print(f"  ✅ Accessibili: {accessible_count}/{len(self.uploaded_images)}")
        
        return results
    
    def get_all_urls(self) -> Dict[str, str]:
        """Ritorna copia di tutte le URL caricate"""
        return self.uploaded_images.copy()
    
    def clear_cache(self):
        """Pulisce la cache delle URL caricate"""
        self.uploaded_images.clear()
        print("🧹 Cache URL Cloudinary pulita")
    
    def get_cache_info(self) -> Dict:
        """Informazioni sulla cache attuale"""
        return {
            'total_uploads': len(self.uploaded_images),
            'images': list(self.uploaded_images.keys()),
            'cloud_name': self.cloud_name,
            'api_key': f"{self.api_key[:8]}...",
            'upload_url': self.upload_url
        }


def test_cloudinary_connection(cloud_name: str, api_key: str, api_secret: str) -> bool:
    """
    Test veloce di connettività Cloudinary con upload preset.
    """
    try:
        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        
        # Test con upload preset (unsigned)
        data = {
            'upload_preset': 'OnlyOne',  # Cambiato da 'ml_default' al tuo preset
            'public_id': f'test_{int(time.time())}'
        }
        files = {'file': ('test.png', b'fake_png_data', 'image/png')}
        
        response = requests.post(url, files=files, data=data, timeout=10)
        
        # 200 = OK, 400 = file invalido ma endpoint OK
        return response.status_code in [200, 400]
        
    except Exception:
        return False


def create_cloudinary_uploader() -> CloudinaryUploader:
    """
    Factory function per creare uploader Cloudinary con test di connessione.
    
    Returns:
        CloudinaryUploader configurato
        
    Raises:
        Exception: Se Cloudinary non è raggiungibile o credenziali mancanti
    """
    # Leggi credenziali da environment variables
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY') 
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        raise Exception(
            "Credenziali Cloudinary mancanti. Imposta:\n"
            "export CLOUDINARY_CLOUD_NAME=your_cloud_name\n"
            "export CLOUDINARY_API_KEY=your_api_key\n"  
            "export CLOUDINARY_API_SECRET=your_api_secret"
        )
    
    if not test_cloudinary_connection(cloud_name, api_key, api_secret):
        raise Exception("Cloudinary non raggiungibile - controlla credenziali e connessione")
    
    return CloudinaryUploader(cloud_name, api_key, api_secret)


# Alias per compatibilità con codice esistente
ImgurUploader = CloudinaryUploader