#!/usr/bin/env python3
"""
🏊 HAVUZ ALANI VALİDATOR
======================
Mevcut havuz alanı tanımlamalarını görsel olarak kontrol et
"""

import cv2
import json
import os
import numpy as np

class PoolAreaValidator:
    """Havuz alanı doğruluğunu kontrol eden araç"""
    
    def __init__(self):
        self.output_dir = "3_OUTPUT"
        self.data_dir = "0_DATA"
        
    def get_pool_files(self):
        """Tüm pool area dosyalarını listele"""
        pool_files = []
        
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.startswith("pool_area_") and file.endswith(".json"):
                    pool_files.append(file)
        
        return sorted(pool_files)
    
    def load_pool_area(self, json_file):
        """Pool area JSON dosyasını yükle"""
        try:
            json_path = os.path.join(self.output_dir, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
            return None
    
    def find_video_file(self, video_name):
        """Video dosyasını bul"""
        # Önce tam isimle ara
        video_path = os.path.join(self.data_dir, video_name)
        if os.path.exists(video_path):
            return video_path
        
        # Video uzantıları dene
        base_name = os.path.splitext(video_name)[0]
        extensions = ['.mp4', '.mov', '.avi', '.MOV', '.MP4']
        
        for ext in extensions:
            video_path = os.path.join(self.data_dir, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # Benzer isimleri ara
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if base_name.lower() in file.lower():
                    return os.path.join(self.data_dir, file)
        
        return None
    
    def validate_pool_area(self, json_file, show_interactive=True):
        """Bir pool area'yı validate et"""
        
        print(f"\n🧪 Validating: {json_file}")
        print("-" * 50)
        
        # Pool data yükle
        pool_data = self.load_pool_area(json_file)
        if not pool_data:
            return False
        
        video_name = pool_data.get('video_name', '')
        polygon_points = pool_data.get('polygon_points', [])
        timestamp = pool_data.get('timestamp', '')
        
        print(f"📹 Video: {video_name}")
        print(f"📅 Created: {timestamp}")
        print(f"🔢 Points: {len(polygon_points)}")
        
        # Video dosyasını bul
        video_path = self.find_video_file(video_name)
        if not video_path:
            print(f"❌ Video not found: {video_name}")
            return False
        
        print(f"✅ Video found: {os.path.basename(video_path)}")
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Cannot open video: {video_path}")
            return False
        
        # İlk frame'i al
        ret, frame = cap.read()
        if not ret:
            print("❌ Cannot read first frame")
            cap.release()
            return False
        
        print(f"📊 Video size: {frame.shape[1]}x{frame.shape[0]}")
        
        # Polygon çiz
        if polygon_points:
            polygon = np.array(polygon_points, dtype=np.int32)
            
            # Pool area'yı çiz
            overlay = frame.copy()
            cv2.fillPoly(overlay, [polygon], (0, 255, 255))  # Sarı transparnt
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
            
            # Polygon çerçevesi
            cv2.polylines(frame, [polygon], True, (0, 255, 255), 3)
            
            # Noktaları çiz
            for i, point in enumerate(polygon_points):
                cv2.circle(frame, tuple(point), 8, (0, 0, 255), -1)
                cv2.putText(frame, str(i+1), (point[0]+10, point[1]+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Merkez point
            center_x = int(np.mean([p[0] for p in polygon_points]))
            center_y = int(np.mean([p[1] for p in polygon_points]))
            cv2.circle(frame, (center_x, center_y), 10, (255, 0, 255), -1)
            cv2.putText(frame, "CENTER", (center_x+15, center_y+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            # Area hesapla
            area = cv2.contourArea(polygon)
            
            # Info text
            info_text = [
                f"Video: {os.path.basename(video_path)}",
                f"Points: {len(polygon_points)}",
                f"Area: {area:,.0f} pixels",
                f"Center: ({center_x}, {center_y})",
                "",
                "ESC: Exit, SPACE: Next, S: Save screenshot"
            ]
            
            for i, text in enumerate(info_text):
                cv2.putText(frame, text, (10, 30 + i*25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cap.release()
        
        if show_interactive:
            # Göster
            window_name = f"Pool Area Validation - {json_file}"
            cv2.imshow(window_name, frame)
            
            print("\n⌨️  Controls:")
            print("   ESC: Continue to next")
            print("   SPACE: Continue to next") 
            print("   S: Save screenshot")
            print("   Q: Quit validation")
            
            while True:
                key = cv2.waitKey(0) & 0xFF
                
                if key == 27 or key == ord(' '):  # ESC or SPACE
                    break
                elif key == ord('s') or key == ord('S'):
                    screenshot_path = f"3_OUTPUT/pool_validation_{os.path.splitext(json_file)[0]}.jpg"
                    cv2.imwrite(screenshot_path, frame)
                    print(f"💾 Screenshot saved: {screenshot_path}")
                elif key == ord('q') or key == ord('Q'):
                    cv2.destroyAllWindows()
                    return False
            
            cv2.destroyAllWindows()
        
        return True
    
    def validate_all_pools(self):
        """Tüm pool area'ları validate et"""
        
        print("🏊 POOL AREA VALIDATION STARTING")
        print("=" * 50)
        
        pool_files = self.get_pool_files()
        
        if not pool_files:
            print("❌ No pool area files found!")
            return
        
        print(f"📊 Found {len(pool_files)} pool area definitions")
        print("\n🎯 Validation will show each pool area overlay on video")
        print("   Use ESC/SPACE to continue, S to save, Q to quit")
        
        input("\nPress ENTER to start validation...")
        
        validated = 0
        for i, pool_file in enumerate(pool_files):
            print(f"\n📍 {i+1}/{len(pool_files)}: {pool_file}")
            
            if self.validate_pool_area(pool_file):
                validated += 1
            else:
                print("⏭️  Skipping to next...")
        
        print(f"\n✅ Validation completed!")
        print(f"📊 Successfully validated: {validated}/{len(pool_files)}")
    
    def quick_check_all(self):
        """Hızlı kontrol - görsel olmayan"""
        
        print("⚡ QUICK POOL AREA CHECK")
        print("=" * 40)
        
        pool_files = self.get_pool_files()
        results = []
        
        for pool_file in pool_files:
            pool_data = self.load_pool_area(pool_file)
            if not pool_data:
                continue
            
            video_name = pool_data.get('video_name', '')
            polygon_points = pool_data.get('polygon_points', [])
            
            video_path = self.find_video_file(video_name)
            video_exists = video_path is not None
            
            result = {
                'json_file': pool_file,
                'video_name': video_name,
                'video_exists': video_exists,
                'point_count': len(polygon_points),
                'valid_polygon': len(polygon_points) >= 3
            }
            
            results.append(result)
        
        # Results table
        print(f"\n📊 POOL AREA SUMMARY:")
        print("-" * 80)
        print(f"{'JSON File':<35} {'Video':<20} {'Points':<8} {'Status'}")
        print("-" * 80)
        
        for result in results:
            json_short = result['json_file'][:34]
            video_short = result['video_name'][:19]
            points = result['point_count']
            
            if result['video_exists'] and result['valid_polygon']:
                status = "✅ OK"
            elif not result['video_exists']:
                status = "❌ No Video"
            elif not result['valid_polygon']:
                status = "⚠️  Few Points"
            else:
                status = "❓ Unknown"
            
            print(f"{json_short:<35} {video_short:<20} {points:<8} {status}")
        
        # Summary stats
        total = len(results)
        ok_count = sum(1 for r in results if r['video_exists'] and r['valid_polygon'])
        no_video = sum(1 for r in results if not r['video_exists'])
        few_points = sum(1 for r in results if not r['valid_polygon'])
        
        print("-" * 80)
        print(f"📈 SUMMARY: {ok_count}/{total} OK, {no_video} missing video, {few_points} insufficient points")
        
        return results

def main():
    """Ana fonksiyon"""
    
    validator = PoolAreaValidator()
    
    print("🏊 POOL AREA VALIDATOR")
    print("=" * 30)
    print("1. Quick check all pools")
    print("2. Visual validation (interactive)")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        validator.quick_check_all()
    elif choice == "2":
        validator.validate_all_pools()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()



