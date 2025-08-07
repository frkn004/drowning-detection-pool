#!/usr/bin/env python3

"""
🎬 VIDEO İŞLEME MODÜLÜ
====================
Video dosyalarını işleyerek kişi tespiti yapar.
"""

import cv2
import sys
import os
import time
from datetime import datetime

# Config'i import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Paths, System, Camera

class VideoProcessor:
    """
    🎬 Video işleme sınıfı
    """
    
    def __init__(self):
        self.current_video = None
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        
        print("🎬 VideoProcessor başlatıldı")
    
    def load_video(self, video_path):
        """
        Video dosyasını yükle
        
        Args:
            video_path (str): Video dosyası yolu
            
        Returns:
            bool: Başarılı mı
        """
        try:
            if not os.path.exists(video_path):
                print(f"❌ Video dosyası bulunamadı: {video_path}")
                return False
            
            self.current_video = cv2.VideoCapture(video_path)
            
            if not self.current_video.isOpened():
                print(f"❌ Video açılamadı: {video_path}")
                return False
            
            # Video özelliklerini al
            self.total_frames = int(self.current_video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.current_video.get(cv2.CAP_PROP_FPS)
            self.width = int(self.current_video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.current_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Video yüklendi: {os.path.basename(video_path)}")
            print(f"📊 Özellikler: {self.width}x{self.height} @ {self.fps:.1f} FPS")
            print(f"🎬 Toplam kare: {self.total_frames}")
            print(f"⏱️  Süre: {self.total_frames/self.fps:.1f} saniye")
            
            return True
            
        except Exception as e:
            print(f"❌ Video yükleme hatası: {e}")
            return False
    
    def get_frame(self):
        """
        Sonraki kareyi al
        
        Returns:
            tuple: (success, frame)
        """
        if self.current_video is None:
            return False, None
            
        ret, frame = self.current_video.read()
        if ret:
            self.current_frame += 1
            
        return ret, frame
    
    def get_progress(self):
        """
        İşleme ilerlemesini al
        
        Returns:
            dict: İlerleme bilgileri
        """
        if self.total_frames == 0:
            return {"percent": 0, "current": 0, "total": 0}
            
        percent = (self.current_frame / self.total_frames) * 100
        return {
            "percent": percent,
            "current": self.current_frame,
            "total": self.total_frames
        }
    
    def seek_to_time(self, seconds):
        """
        Belirli bir zamana git
        
        Args:
            seconds (float): Zaman (saniye)
        """
        if self.current_video is None:
            return False
            
        frame_number = int(seconds * self.fps)
        self.current_video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number
        return True
    
    def close(self):
        """Video'yu kapat"""
        if self.current_video is not None:
            self.current_video.release()
            self.current_video = None

def test_video_processing():
    """Video işleme testini yap"""
    print("="*60)
    print("🧪 VIDEO İŞLEME TESTİ")
    print("="*60)
    
    # Test videoları kontrol et
    test_videos = Camera.TEST_VIDEOS
    
    for video_path in test_videos:
        print(f"\n📁 Test ediliyor: {video_path}")
        
        if not os.path.exists(video_path):
            print(f"⚠️  Video bulunamadı: {video_path}")
            continue
        
        # Video processor oluştur
        processor = VideoProcessor()
        
        if not processor.load_video(video_path):
            continue
        
        print(f"🔄 İlk 100 kareyi test ediyorum...")
        
        # İlk 100 kareyi test et
        frame_count = 0
        start_time = time.time()
        
        try:
            while frame_count < 100:
                ret, frame = processor.get_frame()
                if not ret:
                    print("📹 Video sonu")
                    break
                
                frame_count += 1
                
                # Her 25 karede bir bilgi göster
                if frame_count % 25 == 0:
                    progress = processor.get_progress()
                    print(f"   📊 İşlenen: {frame_count} kare ({progress['percent']:.1f}%)")
        
        except KeyboardInterrupt:
            print("⏹️  Test durduruldu")
        
        finally:
            processor.close()
            
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        print(f"✅ Test tamamlandı: {frame_count} kare, {fps:.1f} FPS")
        print("-" * 40)
    
    print("🎉 Tüm video testleri tamamlandı!")

if __name__ == "__main__":
    test_video_processing()
