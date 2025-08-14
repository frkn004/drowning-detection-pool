#!/usr/bin/env python3
"""
🤖 DROWNING DETECTION MODEL TRAINING SCRIPT
===========================================
YOLOv12 tabanlı özel boğulma tespit modeli eğitimi
"""

import os
import sys
import yaml
import torch
import logging
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

class DrowningModelTrainer:
    def __init__(self, config_path="configs/training.yaml", dataset_path="configs/dataset.yaml"):
        """
        Drowning Detection Model Trainer
        
        Args:
            config_path: Training configuration file
            dataset_path: Dataset configuration file
        """
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configurations
        self.training_config = self.load_config(config_path)
        self.dataset_config = self.load_config(dataset_path)
        
        # Setup paths
        self.project_root = Path.cwd()
        self.models_dir = self.project_root / "models"
        self.logs_dir = self.project_root / "logs"
        
        # Create directories
        self.models_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.logger.info("🏊 Drowning Detection Trainer başlatıldı")
        self.logger.info(f"📁 Proje dizini: {self.project_root}")
        
    def setup_logging(self):
        """Logging sistemini ayarla"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/training_{timestamp}.log"
        
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def load_config(self, config_path):
        """YAML konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"✅ Konfigürasyon yüklendi: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"❌ Konfigürasyon yüklenemedi {config_path}: {e}")
            raise
            
    def check_environment(self):
        """Eğitim ortamını kontrol et"""
        self.logger.info("🔍 Ortam kontrolü...")
        
        # CUDA kontrolü
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            self.logger.info(f"🔥 CUDA mevcut: {gpu_count} GPU")
            self.logger.info(f"🎮 GPU: {gpu_name}")
        else:
            self.logger.warning("⚠️ CUDA bulunamadı, CPU kullanılacak")
            
        # Dataset kontrolü
        dataset_path = Path(self.dataset_config['path'])
        if not dataset_path.exists():
            self.logger.error(f"❌ Dataset bulunamadı: {dataset_path}")
            return False
            
        train_path = dataset_path / self.dataset_config['train']
        val_path = dataset_path / self.dataset_config['val']
        
        if train_path.exists():
            train_images = len(list(train_path.glob("*.jpg")))
            self.logger.info(f"📸 Train görüntüleri: {train_images}")
        else:
            self.logger.error(f"❌ Train klasörü bulunamadı: {train_path}")
            return False
            
        if val_path.exists():
            val_images = len(list(val_path.glob("*.jpg")))
            self.logger.info(f"📸 Validation görüntüleri: {val_images}")
        else:
            self.logger.warning(f"⚠️ Validation klasörü bulunamadı: {val_path}")
            
        return True
        
    def train_model(self, phase="phase1"):
        """
        Modeli eğit
        
        Args:
            phase: Eğitim fazı (phase1, phase2, phase3, phase4)
        """
        self.logger.info(f"🚀 {phase.upper()} eğitimi başlıyor...")
        
        if not self.check_environment():
            self.logger.error("❌ Ortam kontrolü başarısız!")
            return False
            
        try:
            # Phase-specific parameters
            phase_config = self.training_config.get(phase, {})
            
            # Model yükle
            model_name = self.training_config.get('model', 'yolov8m.pt')
            self.logger.info(f"📦 Model yükleniyor: {model_name}")
            model = YOLO(model_name)
            
            # Training parameters
            train_params = {
                'data': 'configs/dataset.yaml',
                'epochs': phase_config.get('epochs', self.training_config.get('epochs', 100)),
                'batch': phase_config.get('batch', self.training_config.get('batch', 16)),
                'imgsz': self.training_config.get('imgsz', 640),
                'device': self.training_config.get('device', '0'),
                'patience': phase_config.get('patience', self.training_config.get('patience', 20)),
                'lr0': phase_config.get('lr0', self.training_config.get('lr0', 0.01)),
                'lrf': self.training_config.get('lrf', 0.01),
                'momentum': self.training_config.get('momentum', 0.937),
                'weight_decay': self.training_config.get('weight_decay', 0.0005),
                'amp': self.training_config.get('amp', True),
                'project': f"runs/train",
                'name': f"drowning_{phase}",
                'exist_ok': True,
                'save': True,
                'plots': True,
                'verbose': True
            }
            
            self.logger.info(f"⚙️ Eğitim parametreleri:")
            for key, value in train_params.items():
                self.logger.info(f"   {key}: {value}")
                
            # Eğitimi başlat
            self.logger.info("🎯 Eğitim başlıyor...")
            results = model.train(**train_params)
            
            # Model kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_save_path = self.models_dir / f"drowning_{phase}_{timestamp}.pt"
            model.save(model_save_path)
            
            self.logger.info(f"✅ Eğitim tamamlandı!")
            self.logger.info(f"💾 Model kaydedildi: {model_save_path}")
            
            # En iyi modeli kopyala
            best_model_path = self.models_dir / f"best_{phase}.pt"
            if hasattr(results, 'save_dir'):
                source_best = Path(results.save_dir) / "weights" / "best.pt"
                if source_best.exists():
                    import shutil
                    shutil.copy2(source_best, best_model_path)
                    self.logger.info(f"💎 En iyi model: {best_model_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Eğitim hatası: {e}")
            raise
            
    def validate_model(self, model_path, data_path="configs/dataset.yaml"):
        """Modeli doğrula"""
        self.logger.info(f"🔍 Model doğrulaması: {model_path}")
        
        try:
            model = YOLO(model_path)
            results = model.val(data=data_path, verbose=True)
            
            self.logger.info("📊 Doğrulama sonuçları:")
            if hasattr(results, 'box'):
                metrics = results.box
                self.logger.info(f"   mAP50: {metrics.map50:.4f}")
                self.logger.info(f"   mAP50-95: {metrics.map:.4f}")
                
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Doğrulama hatası: {e}")
            return None

def main():
    """Ana eğitim fonksiyonu"""
    print("🏊 DROWNING DETECTION MODEL TRAINING")
    print("====================================")
    
    # Phase seçimi
    phases = {
        '1': 'phase1',  # 200 frame mini dataset
        '2': 'phase2',  # 500 frame extended dataset  
        '3': 'phase3',  # 1000 frame production dataset
        '4': 'phase4'   # 1500 frame final dataset
    }
    
    print("📊 Eğitim fazları:")
    print("   1. Phase 1: Mini Dataset (200 frame)")
    print("   2. Phase 2: Extended Dataset (500 frame)")
    print("   3. Phase 3: Production Dataset (1000 frame)")
    print("   4. Phase 4: Final Dataset (1500 frame)")
    
    try:
        choice = input("\nHangi fazı eğitmek istiyorsunuz? (1-4): ").strip()
        phase = phases.get(choice)
        
        if not phase:
            print("❌ Geçersiz seçim!")
            return
            
        # Trainer oluştur ve eğit
        trainer = DrowningModelTrainer()
        success = trainer.train_model(phase)
        
        if success:
            print(f"\n✅ {phase.upper()} eğitimi başarılı!")
            
            # Doğrulama
            best_model = f"models/best_{phase}.pt"
            if os.path.exists(best_model):
                print(f"🔍 Model doğrulaması başlıyor...")
                trainer.validate_model(best_model)
        else:
            print(f"\n❌ {phase.upper()} eğitimi başarısız!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Eğitim kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()