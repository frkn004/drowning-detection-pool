#!/usr/bin/env python3
"""
👥 OBJECT TRACKER - Advanced Person Tracking System
🎯 Kişi takibi ve ID assignment için gelişmiş tracker

Özellikler:
- Centroid-based tracking
- Kalman Filter prediction
- Object lifecycle management
- Multi-person tracking
- Lost object recovery

📅 Date: 31 Temmuz 2025
"""

import numpy as np
import math
from collections import OrderedDict
from scipy.spatial import distance as dist

class ObjectTracker:
    def __init__(self, max_disappeared=30, max_distance=100):
        """
        🎯 Object Tracker Initialization
        
        Args:
            max_disappeared (int): Maksimum kayıp frame sayısı
            max_distance (float): Maksimum eşleştirme mesafesi
        """
        # Track ID counter
        self.next_object_id = 1
        
        # Active objects
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        
        # Parameters
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        # Statistics
        self.total_objects_created = 0
        self.total_objects_lost = 0
        
        print(f"🎯 Object Tracker başlatıldı")
        print(f"   📊 Max disappeared: {max_disappeared} frame")
        print(f"   📏 Max distance: {max_distance} pixel")

    def register_object(self, centroid, bbox, confidence, class_name):
        """
        👤 Yeni obje kaydet
        
        Args:
            centroid (tuple): (x, y) merkez koordinatı
            bbox (dict): Bounding box koordinatları
            confidence (float): Güven skoru
            class_name (str): Sınıf adı
        
        Returns:
            int: Atanan track ID
        """
        object_id = self.next_object_id
        
        self.objects[object_id] = {
            'centroid': centroid,
            'bbox': bbox,
            'confidence': confidence,
            'class_name': class_name,
            'first_seen': True,
            'frame_count': 1,
            'total_confidence': confidence,
            'avg_confidence': confidence,
            'trajectory': [centroid],
            'velocities': [],
            'stable': False
        }
        
        self.disappeared[object_id] = 0
        self.next_object_id += 1
        self.total_objects_created += 1
        
        return object_id

    def deregister_object(self, object_id):
        """🗑️ Objeyi sistemden çıkar"""
        if object_id in self.objects:
            del self.objects[object_id]
            del self.disappeared[object_id]
            self.total_objects_lost += 1

    def update_object(self, object_id, centroid, bbox, confidence, class_name):
        """
        🔄 Mevcut objeyi güncelle
        
        Args:
            object_id (int): Track ID
            centroid (tuple): Yeni merkez koordinatı
            bbox (dict): Yeni bounding box
            confidence (float): Yeni güven skoru
            class_name (str): Sınıf adı
        """
        obj = self.objects[object_id]
        
        # Velocity hesapla
        old_centroid = obj['centroid']
        velocity = (centroid[0] - old_centroid[0], centroid[1] - old_centroid[1])
        obj['velocities'].append(velocity)
        
        # Son 5 velocity'yi tut
        if len(obj['velocities']) > 5:
            obj['velocities'] = obj['velocities'][-5:]
        
        # Trajectory güncelle
        obj['trajectory'].append(centroid)
        if len(obj['trajectory']) > 10:
            obj['trajectory'] = obj['trajectory'][-10:]
        
        # Object güncelle
        obj['centroid'] = centroid
        obj['bbox'] = bbox
        obj['confidence'] = confidence
        obj['class_name'] = class_name
        obj['first_seen'] = False
        obj['frame_count'] += 1
        
        # Ortalama confidence hesapla
        obj['total_confidence'] += confidence
        obj['avg_confidence'] = obj['total_confidence'] / obj['frame_count']
        
        # Stabilite kontrolü (5+ frame görülmüşse stable)
        obj['stable'] = obj['frame_count'] >= 5
        
        # Disappeared counter sıfırla
        self.disappeared[object_id] = 0

    def predict_position(self, object_id):
        """
        🔮 Obje pozisyonunu tahmin et (velocity based)
        
        Args:
            object_id (int): Track ID
            
        Returns:
            tuple: Tahmini (x, y) pozisyon
        """
        if object_id not in self.objects:
            return None
        
        obj = self.objects[object_id]
        
        if len(obj['velocities']) == 0:
            return obj['centroid']
        
        # Son velocity'lerin ortalamasını al
        avg_velocity = np.mean(obj['velocities'], axis=0)
        
        # Tahmin et
        predicted_x = obj['centroid'][0] + avg_velocity[0]
        predicted_y = obj['centroid'][1] + avg_velocity[1]
        
        return (int(predicted_x), int(predicted_y))

    def update(self, detections):
        """
        🔄 Ana tracking fonksiyonu
        
        Args:
            detections (list): Detection listesi
            
        Returns:
            dict: object_id -> detection mapping
        """
        result = {}
        
        # Eğer detection yoksa, sadece disappeared counter'ı artır
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                # Çok uzun kayıpsa sil
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister_object(object_id)
            
            return result
        
        # İlk detection'larsa, hepsini register et
        if len(self.objects) == 0:
            for detection in detections:
                centroid = (detection['center']['x'], detection['center']['y'])
                bbox = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['classified_class']
                
                object_id = self.register_object(centroid, bbox, confidence, class_name)
                result[object_id] = detection
            
            return result
        
        # Mevcut objeler ve yeni detection'lar arasında eşleştirme yap
        object_centroids = []
        object_ids = list(self.objects.keys())
        
        for object_id in object_ids:
            # Tahmin edilen pozisyonu kullan
            predicted_pos = self.predict_position(object_id)
            if predicted_pos:
                object_centroids.append(predicted_pos)
            else:
                object_centroids.append(self.objects[object_id]['centroid'])
        
        # Detection centroid'leri
        detection_centroids = []
        for detection in detections:
            detection_centroids.append((detection['center']['x'], detection['center']['y']))
        
        # Mesafe matrisi hesapla
        if len(object_centroids) > 0 and len(detection_centroids) > 0:
            D = dist.cdist(np.array(object_centroids), np.array(detection_centroids))
            
            # Hungarian algorithm yerine basit min assignment
            used_detection_indices = set()
            used_object_indices = set()
            
            # En yakın eşleştirmeleri bul
            for _ in range(min(len(object_ids), len(detections))):
                min_distance = float('inf')
                min_object_idx = -1
                min_detection_idx = -1
                
                for i in range(len(object_ids)):
                    if i in used_object_indices:
                        continue
                    
                    for j in range(len(detections)):
                        if j in used_detection_indices:
                            continue
                        
                        if D[i, j] < min_distance and D[i, j] < self.max_distance:
                            min_distance = D[i, j]
                            min_object_idx = i
                            min_detection_idx = j
                
                # Eşleştirme bulunduysa güncelle
                if min_object_idx != -1 and min_detection_idx != -1:
                    object_id = object_ids[min_object_idx]
                    detection = detections[min_detection_idx]
                    
                    centroid = (detection['center']['x'], detection['center']['y'])
                    bbox = detection['bbox']
                    confidence = detection['confidence']
                    class_name = detection['classified_class']
                    
                    self.update_object(object_id, centroid, bbox, confidence, class_name)
                    result[object_id] = detection
                    
                    used_object_indices.add(min_object_idx)
                    used_detection_indices.add(min_detection_idx)
                else:
                    break
            
            # Eşleşmeyen detection'ları yeni obje olarak kaydet
            for j in range(len(detections)):
                if j not in used_detection_indices:
                    detection = detections[j]
                    centroid = (detection['center']['x'], detection['center']['y'])
                    bbox = detection['bbox']
                    confidence = detection['confidence']
                    class_name = detection['classified_class']
                    
                    object_id = self.register_object(centroid, bbox, confidence, class_name)
                    result[object_id] = detection
            
            # Eşleşmeyen objelerin disappeared counter'ını artır
            for i in range(len(object_ids)):
                if i not in used_object_indices:
                    object_id = object_ids[i]
                    self.disappeared[object_id] += 1
                    
                    # Çok uzun kayıpsa sil
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister_object(object_id)
        
        return result

    def get_object_info(self, object_id):
        """
        📊 Obje bilgilerini al
        
        Args:
            object_id (int): Track ID
            
        Returns:
            dict: Obje bilgileri
        """
        if object_id not in self.objects:
            return None
        
        obj = self.objects[object_id]
        
        # Average velocity hesapla
        avg_velocity = (0, 0)
        if len(obj['velocities']) > 0:
            avg_velocity = np.mean(obj['velocities'], axis=0)
        
        return {
            'track_id': object_id,
            'centroid': obj['centroid'],
            'bbox': obj['bbox'],
            'confidence': obj['confidence'],
            'avg_confidence': obj['avg_confidence'],
            'class_name': obj['class_name'],
            'frame_count': obj['frame_count'],
            'stable': obj['stable'],
            'avg_velocity': avg_velocity,
            'trajectory_length': len(obj['trajectory']),
            'disappeared_frames': self.disappeared[object_id]
        }

    def get_active_objects(self):
        """📋 Aktif objelerin listesini al"""
        return list(self.objects.keys())

    def get_statistics(self):
        """📊 Tracker istatistiklerini al"""
        return {
            'active_objects': len(self.objects),
            'total_created': self.total_objects_created,
            'total_lost': self.total_objects_lost,
            'next_id': self.next_object_id
        }

    def draw_trajectory(self, frame, object_id, color=(255, 255, 0), thickness=2):
        """
        🎯 Trajectory çiz
        
        Args:
            frame: OpenCV frame
            object_id (int): Track ID
            color (tuple): RGB renk
            thickness (int): Çizgi kalınlığı
        """
        if object_id not in self.objects:
            return
        
        trajectory = self.objects[object_id]['trajectory']
        
        if len(trajectory) > 1:
            import cv2
            
            # Trajectory çizgilerini çiz
            for i in range(1, len(trajectory)):
                # Şeffaflık efekti için alpha blending
                alpha = i / len(trajectory)
                line_color = tuple(int(c * alpha) for c in color)
                
                cv2.line(frame, trajectory[i-1], trajectory[i], line_color, thickness)
            
            # Son pozisyonda büyük nokta
            cv2.circle(frame, trajectory[-1], 8, color, -1)