#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏊 HAVUZ GÜVENLİK SİSTEMİ - KONFIGURASYON
==========================================
Tüm proje ayarlarını merkezi olarak yönetir.
"""

import os
from datetime import datetime

# 📁 KLASÖR YAPILARI
class Paths:
    """Dosya yolları yönetimi"""
    # CODES klasöründen ana dizine çık
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CODES_DIR = os.path.join(BASE_DIR, "CODES")
    
    # Ana proje klasörleri
    DATA_DIR = os.path.join(BASE_DIR, "DATA")
    MODELS_DIR = os.path.join(BASE_DIR, "MODELS") 
    OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUT")
    
    @staticmethod
    def ensure_dirs():
        """Gerekli klasörleri oluştur"""
        os.makedirs(Paths.OUTPUT_DIR, exist_ok=True)
    
    @staticmethod
    def get_available_videos():
        """DATA klasöründeki mevcut videoları listele"""
        videos = []
        if os.path.exists(Paths.DATA_DIR):
            for file in os.listdir(Paths.DATA_DIR):
                if file.lower().endswith(('.mp4', '.mov', '.avi')):
                    videos.append(os.path.join(Paths.DATA_DIR, file))
        return videos
    
    @staticmethod
    def get_available_models():
        """MODELS klasöründeki mevcut modelleri listele"""
        models = []
        if os.path.exists(Paths.MODELS_DIR):
            for file in os.listdir(Paths.MODELS_DIR):
                if file.lower().endswith('.pt'):
                    models.append(os.path.join(Paths.MODELS_DIR, file))
        return models

# 🤖 DETECTION AYARLARI
class Detection:
    """Tespit konfigürasyonu"""
    # Tercih edilen modeller
    PREFERRED_MODELS = [
        "yolov12m_drowning_best.pt",  # 🎯 Özel eğitilmiş!
        "yolov8m.pt",                 # Genel amaçlı
        "yolo11l.pt",                 # Alternatif
    ]
    
    # Tespit eşikleri
    CONFIDENCE_THRESHOLD = 0.3
    IOU_THRESHOLD = 0.3
    MIN_AREA = 500
    
    @staticmethod
    def get_best_model():
        """En iyi modeli seç"""
        available_models = Paths.get_available_models()
        available_names = [os.path.basename(m) for m in available_models]
        
        for preferred in Detection.PREFERRED_MODELS:
            if preferred in available_names:
                return os.path.join(Paths.MODELS_DIR, preferred)
        
        return available_models[0] if available_models else None

# 🔧 SİSTEM AYARLARI
class System:
    """Sistem geneli ayarlar"""
    VERSION = "2.0.0"
    PROJECT_NAME = "Havuz Güvenlik Sistemi - Modüler"
    DEBUG_MODE = True

def initialize():
    """Sistemi başlat"""
    Paths.ensure_dirs()
    
    videos = Paths.get_available_videos()
    models = Paths.get_available_models()
    best_model = Detection.get_best_model()
    
    print(f"🚀 {System.PROJECT_NAME} v{System.VERSION}")
    print(f"📁 Ana dizin: {Paths.BASE_DIR}")
    print(f"📊 Mevcut videolar: {len(videos)}")
    print(f"🤖 Mevcut modeller: {len(models)}")
    print(f"🎯 En iyi model: {os.path.basename(best_model) if best_model else 'Yok'}")

def get_project_info():
    """Proje bilgilerini döndür"""
    return {
        'videos': Paths.get_available_videos(),
        'models': Paths.get_available_models(),
        'best_model': Detection.get_best_model(),
    }

if __name__ == "__main__":
    initialize()
    info = get_project_info()
    
    print("\n📋 DETAYLAR:")
    print("📹 Videolar:")
    for video in info['videos']:
        print(f"   - {os.path.basename(video)}")
    
    print("\n🤖 Modeller:")
    for model in info['models']:
        name = os.path.basename(model)
        if model == info['best_model']:
            print(f"   🎯 {name} (tercih edilen)")
        else:
            print(f"   - {name}")

# 🏊 HAVUZ AYARLARI  
class Pool:
    """Havuz alanı konfigürasyonu"""
    DEFAULT_AREA = None           # Kullanıcı tanımlayacak
    
    # Havuz alanı tanımlama renkleri (BGR formatında)
    POLYGON_COLOR = (0, 0, 255)  # Kırmızı
    POINT_COLOR = (0, 255, 0)    # Yeşil
    LINE_THICKNESS = 2
