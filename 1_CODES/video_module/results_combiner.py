#!/usr/bin/env python3
"""
📊📊 RESULTS COMBINER - Multi-Camera Results Fusion
🎯 Tekli kamera sonuçlarını birleştir ve analiz et

Özellikler:
- Existing single camera results combination
- Zone-based coverage analysis
- Cross-camera correlation
- Unified timeline creation
- Performance comparison

📅 Date: 4 Ağustos 2025
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import os

class ResultsCombiner:
    def __init__(self, cam1_output_dir, cam2_output_dir):
        """
        📊 Results Combiner Initialization
        
        Args:
            cam1_output_dir (str): Camera 1 output directory
            cam2_output_dir (str): Camera 2 output directory
        """
        self.cam1_dir = Path(cam1_output_dir)
        self.cam2_dir = Path(cam2_output_dir)
        
        # Output directory
        self.output_dir = self._create_output_directory()
        
        # Load data
        self.cam1_data = None
        self.cam2_data = None
        self.cam1_metrics = None
        self.cam2_metrics = None
        
        print(f"📊📊 Results Combiner başlatıldı")
        print(f"📹 Camera 1: {self.cam1_dir.name}")
        print(f"📹 Camera 2: {self.cam2_dir.name}")
        print(f"📂 Combined Output: {self.output_dir}")

    def _create_output_directory(self):
        """📁 OUTPUT klasörü oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_output = Path(__file__).parent.parent.parent / "3_OUTPUT"
        base_output.mkdir(exist_ok=True)
        
        output_name = f"COMBINED_RESULTS_{timestamp}"
        output_dir = base_output / output_name
        output_dir.mkdir(exist_ok=True)
        
        return str(output_dir)

    def load_data(self):
        """📥 Kamera verilerini yükle"""
        try:
            # Camera 1 data
            cam1_csv = self.cam1_dir / "coordinates_log.csv"
            cam1_json = self.cam1_dir / "performance_metrics.json"
            
            if cam1_csv.exists() and cam1_json.exists():
                self.cam1_data = pd.read_csv(cam1_csv)
                with open(cam1_json, 'r') as f:
                    self.cam1_metrics = json.load(f)
                print(f"✅ Camera 1 data yüklendi: {len(self.cam1_data)} records")
            else:
                print(f"❌ Camera 1 data bulunamadı: {self.cam1_dir}")
                return False
            
            # Camera 2 data  
            cam2_csv = self.cam2_dir / "coordinates_log.csv"
            cam2_json = self.cam2_dir / "performance_metrics.json"
            
            if cam2_csv.exists() and cam2_json.exists():
                self.cam2_data = pd.read_csv(cam2_csv)
                with open(cam2_json, 'r') as f:
                    self.cam2_metrics = json.load(f)
                print(f"✅ Camera 2 data yüklendi: {len(self.cam2_data)} records")
            else:
                print(f"❌ Camera 2 data bulunamadı: {self.cam2_dir}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Data loading hatası: {e}")
            return False

    def analyze_coverage(self):
        """🎯 Coverage analizi yap"""
        if self.cam1_data is None or self.cam2_data is None:
            return {}
        
        # Basic stats
        cam1_total = len(self.cam1_data)
        cam2_total = len(self.cam2_data)
        
        cam1_swimming = len(self.cam1_data[self.cam1_data['classified_class'] == 'person_swimming'])
        cam1_poolside = len(self.cam1_data[self.cam1_data['classified_class'] == 'person_poolside'])
        
        cam2_swimming = len(self.cam2_data[self.cam2_data['classified_class'] == 'person_swimming'])
        cam2_poolside = len(self.cam2_data[self.cam2_data['classified_class'] == 'person_poolside'])
        
        # Tracking stats
        cam1_tracks = self.cam1_metrics['tracking_metrics']
        cam2_tracks = self.cam2_metrics['tracking_metrics']
        
        coverage_analysis = {
            'camera_comparison': {
                'camera1': {
                    'total_detections': cam1_total,
                    'swimming_detections': cam1_swimming,
                    'poolside_detections': cam1_poolside,
                    'swimming_ratio': round(cam1_swimming / cam1_total * 100, 2) if cam1_total > 0 else 0,
                    'unique_tracks': cam1_tracks['total_tracks_created'],
                    'stable_tracks': cam1_tracks.get('stable_track_detections', 0),
                    'avg_confidence': round(self.cam1_data['confidence'].mean(), 3),
                    'coverage_focus': 'Poolside dominant' if cam1_poolside > cam1_swimming * 2 else 'Balanced'
                },
                'camera2': {
                    'total_detections': cam2_total,
                    'swimming_detections': cam2_swimming,
                    'poolside_detections': cam2_poolside,
                    'swimming_ratio': round(cam2_swimming / cam2_total * 100, 2) if cam2_total > 0 else 0,
                    'unique_tracks': cam2_tracks['total_tracks_created'],
                    'stable_tracks': cam2_tracks.get('stable_track_detections', 0),
                    'avg_confidence': round(self.cam2_data['confidence'].mean(), 3),
                    'coverage_focus': 'Swimming focused' if cam2_swimming > cam2_poolside else 'Poolside focused'
                }
            },
            'combined_stats': {
                'total_detections': cam1_total + cam2_total,
                'total_swimming': cam1_swimming + cam2_swimming,
                'total_poolside': cam1_poolside + cam2_poolside,
                'overall_swimming_ratio': round((cam1_swimming + cam2_swimming) / (cam1_total + cam2_total) * 100, 2),
                'total_unique_tracks': cam1_tracks['total_tracks_created'] + cam2_tracks['total_tracks_created'],
                'coverage_complementarity': self._calculate_complementarity(cam1_swimming, cam1_poolside, cam2_swimming, cam2_poolside)
            },
            'time_analysis': self._analyze_temporal_patterns()
        }
        
        return coverage_analysis

    def _calculate_complementarity(self, c1_swim, c1_pool, c2_swim, c2_pool):
        """📊 Kameraların birbirini tamamlama derecesi"""
        c1_total = c1_swim + c1_pool
        c2_total = c2_swim + c2_pool
        
        if c1_total == 0 or c2_total == 0:
            return 0
        
        c1_swim_ratio = c1_swim / c1_total
        c2_swim_ratio = c2_swim / c2_total
        
        # Fark ne kadar büyükse o kadar complementary
        complementarity = abs(c1_swim_ratio - c2_swim_ratio) * 100
        
        if complementarity > 30:
            return "High complementarity"
        elif complementarity > 15:
            return "Medium complementarity" 
        else:
            return "Low complementarity"

    def _analyze_temporal_patterns(self):
        """⏰ Temporal pattern analizi"""
        if self.cam1_data is None or self.cam2_data is None:
            return {}
        
        # Frame-based analysis (her 50 frame'de bir)
        frame_bins = 50
        
        cam1_frames = self.cam1_data['frame_number'].max()
        cam2_frames = self.cam2_data['frame_number'].max()
        
        max_frames = min(cam1_frames, cam2_frames)
        
        temporal_data = []
        
        for frame_start in range(0, max_frames, frame_bins):
            frame_end = min(frame_start + frame_bins, max_frames)
            
            # Camera 1 data for this time window
            c1_window = self.cam1_data[
                (self.cam1_data['frame_number'] >= frame_start) & 
                (self.cam1_data['frame_number'] < frame_end)
            ]
            
            # Camera 2 data for this time window
            c2_window = self.cam2_data[
                (self.cam2_data['frame_number'] >= frame_start) & 
                (self.cam2_data['frame_number'] < frame_end)
            ]
            
            temporal_data.append({
                'time_window': f"{frame_start}-{frame_end}",
                'cam1_detections': len(c1_window),
                'cam2_detections': len(c2_window),
                'cam1_swimming': len(c1_window[c1_window['classified_class'] == 'person_swimming']),
                'cam2_swimming': len(c2_window[c2_window['classified_class'] == 'person_swimming']),
                'combined_activity': len(c1_window) + len(c2_window)
            })
        
        return {
            'temporal_windows': temporal_data,
            'peak_activity_window': max(temporal_data, key=lambda x: x['combined_activity'])['time_window'],
            'total_analyzed_frames': max_frames
        }

    def create_combined_dataset(self):
        """🔄 Kombine dataset oluştur"""
        if self.cam1_data is None or self.cam2_data is None:
            return None
        
        # Camera ID ekle
        cam1_copy = self.cam1_data.copy()
        cam2_copy = self.cam2_data.copy()
        
        cam1_copy['camera_id'] = 1
        cam2_copy['camera_id'] = 2
        
        # Global track ID oluştur (basit)
        cam1_copy['global_track_id'] = cam1_copy['track_id'].apply(lambda x: f"C1_{x}" if pd.notna(x) else "N/A")
        cam2_copy['global_track_id'] = cam2_copy['track_id'].apply(lambda x: f"C2_{x}" if pd.notna(x) else "N/A")
        
        # Birleştir
        combined_df = pd.concat([cam1_copy, cam2_copy], ignore_index=True)
        
        # Timestamp sıralama
        combined_df = combined_df.sort_values(['frame_number', 'camera_id'])
        
        # CSV olarak kaydet
        output_csv = os.path.join(self.output_dir, "combined_coordinates.csv")
        combined_df.to_csv(output_csv, index=False)
        
        print(f"📊 Combined dataset oluşturuldu: {len(combined_df)} records")
        print(f"📁 Saved: {output_csv}")
        
        return combined_df

    def generate_visualizations(self, coverage_analysis):
        """📈 Visualizasyonlar oluştur"""
        try:
            plt.style.use('default')
            
            # 1. Detection Comparison
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Detection counts
            cameras = ['Camera 1', 'Camera 2']
            swimming_counts = [
                coverage_analysis['camera_comparison']['camera1']['swimming_detections'],
                coverage_analysis['camera_comparison']['camera2']['swimming_detections']
            ]
            poolside_counts = [
                coverage_analysis['camera_comparison']['camera1']['poolside_detections'],
                coverage_analysis['camera_comparison']['camera2']['poolside_detections']
            ]
            
            x = np.arange(len(cameras))
            width = 0.35
            
            ax1.bar(x - width/2, swimming_counts, width, label='Swimming', color='green', alpha=0.7)
            ax1.bar(x + width/2, poolside_counts, width, label='Poolside', color='blue', alpha=0.7)
            ax1.set_xlabel('Camera')
            ax1.set_ylabel('Detection Count')
            ax1.set_title('Detection Distribution by Camera')
            ax1.set_xticks(x)
            ax1.set_xticklabels(cameras)
            ax1.legend()
            
            # Swimming ratios
            swimming_ratios = [
                coverage_analysis['camera_comparison']['camera1']['swimming_ratio'],
                coverage_analysis['camera_comparison']['camera2']['swimming_ratio']
            ]
            
            ax2.bar(cameras, swimming_ratios, color=['red', 'orange'], alpha=0.7)
            ax2.set_ylabel('Swimming Ratio (%)')
            ax2.set_title('Swimming Activity Ratio by Camera')
            ax2.set_ylim(0, max(swimming_ratios) * 1.2)
            
            # Track counts
            track_counts = [
                coverage_analysis['camera_comparison']['camera1']['unique_tracks'],
                coverage_analysis['camera_comparison']['camera2']['unique_tracks']
            ]
            
            ax3.bar(cameras, track_counts, color=['purple', 'cyan'], alpha=0.7)
            ax3.set_ylabel('Unique Tracks')
            ax3.set_title('Tracking Performance by Camera')
            
            # Confidence comparison
            confidences = [
                coverage_analysis['camera_comparison']['camera1']['avg_confidence'],
                coverage_analysis['camera_comparison']['camera2']['avg_confidence']
            ]
            
            ax4.bar(cameras, confidences, color=['gold', 'silver'], alpha=0.7)
            ax4.set_ylabel('Average Confidence')
            ax4.set_title('Detection Confidence by Camera')
            ax4.set_ylim(0, 1)
            
            plt.tight_layout()
            plot_path = os.path.join(self.output_dir, "camera_comparison.png")
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Visualization saved: {plot_path}")
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")

    def generate_report(self):
        """📋 Comprehensive report oluştur"""
        if not self.load_data():
            return False
        
        # Analysis yap
        coverage_analysis = self.analyze_coverage()
        
        # Combined dataset oluştur
        combined_df = self.create_combined_dataset()
        
        # Visualizations
        self.generate_visualizations(coverage_analysis)
        
        # JSON report
        report = {
            'generation_info': {
                'timestamp': datetime.now().isoformat(),
                'camera1_source': str(self.cam1_dir),
                'camera2_source': str(self.cam2_dir),
                'combined_output': self.output_dir
            },
            'coverage_analysis': coverage_analysis,
            'recommendations': self._generate_recommendations(coverage_analysis)
        }
        
        # Save JSON report
        report_path = os.path.join(self.output_dir, "combined_analysis_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self._print_summary(coverage_analysis)
        
        print(f"\n📁 COMBINED ANALYSIS COMPLETED!")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"📊 Files generated:")
        print(f"   📈 combined_coordinates.csv")
        print(f"   📋 combined_analysis_report.json") 
        print(f"   📊 camera_comparison.png")
        
        return True

    def _generate_recommendations(self, analysis):
        """💡 Öneriler oluştur"""
        cam1 = analysis['camera_comparison']['camera1']
        cam2 = analysis['camera_comparison']['camera2']
        combined = analysis['combined_stats']
        
        recommendations = []
        
        # Coverage recommendations
        if cam1['swimming_ratio'] < 10 and cam2['swimming_ratio'] > 15:
            recommendations.append("Camera 1'in havuz coverage'ı düşük - pozisyon ayarlanmalı")
        
        if cam2['swimming_ratio'] > cam1['swimming_ratio'] * 3:
            recommendations.append("Camera 2 havuz aktivitesini daha iyi yakalıyor - ana camera olarak kullanılabilir")
        
        # Tracking recommendations
        if cam1['unique_tracks'] > cam2['unique_tracks'] * 2:
            recommendations.append("Camera 1'de çok fazla track fragmentation var - tracker parametreleri ayarlanmalı")
        
        # Confidence recommendations
        if abs(cam1['avg_confidence'] - cam2['avg_confidence']) > 0.1:
            recommendations.append("Kameralar arası confidence farkı yüksek - lighting/angle optimizasyonu gerekli")
        
        # Overall recommendations
        if combined['overall_swimming_ratio'] < 15:
            recommendations.append("Genel havuz aktivite oranı düşük - kamera pozisyonları kontrol edilmeli")
        
        if analysis['combined_stats']['coverage_complementarity'] == "High complementarity":
            recommendations.append("Mükemmel! Kameralar birbirini çok iyi tamamlıyor")
        
        return recommendations

    def _print_summary(self, analysis):
        """📋 Summary yazdır"""
        print(f"\n📊📊 COMBINED CAMERA ANALYSIS SUMMARY")
        print(f"=" * 60)
        
        cam1 = analysis['camera_comparison']['camera1']
        cam2 = analysis['camera_comparison']['camera2']
        combined = analysis['combined_stats']
        
        print(f"\n📹 CAMERA 1 PERFORMANCE:")
        print(f"   🎯 Total Detections: {cam1['total_detections']:,}")
        print(f"   🏊 Swimming: {cam1['swimming_detections']} ({cam1['swimming_ratio']}%)")
        print(f"   🏊‍♀️ Poolside: {cam1['poolside_detections']}")
        print(f"   🆔 Unique Tracks: {cam1['unique_tracks']}")
        print(f"   📈 Avg Confidence: {cam1['avg_confidence']}")
        print(f"   🎯 Focus: {cam1['coverage_focus']}")
        
        print(f"\n📹 CAMERA 2 PERFORMANCE:")
        print(f"   🎯 Total Detections: {cam2['total_detections']:,}")
        print(f"   🏊 Swimming: {cam2['swimming_detections']} ({cam2['swimming_ratio']}%)")
        print(f"   🏊‍♀️ Poolside: {cam2['poolside_detections']}")
        print(f"   🆔 Unique Tracks: {cam2['unique_tracks']}")
        print(f"   📈 Avg Confidence: {cam2['avg_confidence']}")
        print(f"   🎯 Focus: {cam2['coverage_focus']}")
        
        print(f"\n🎬🎬 COMBINED PERFORMANCE:")
        print(f"   🎯 Total Detections: {combined['total_detections']:,}")
        print(f"   🏊 Total Swimming: {combined['total_swimming']} ({combined['overall_swimming_ratio']}%)")
        print(f"   🆔 Total Tracks: {combined['total_unique_tracks']}")
        print(f"   🔄 Complementarity: {combined['coverage_complementarity']}")

def main():
    """🚀 Main execution function"""
    print("📊📊 RESULTS COMBINER - Multi-Camera Analysis")
    print("=" * 60)
    
    # Recent output directories
    output_base = Path(__file__).parent.parent.parent / "3_OUTPUT"
    
    # Find most recent camera outputs
    cam1_dirs = sorted(output_base.glob("LIVE_TEST_yolov8x_kamera1_*"), reverse=True)
    cam2_dirs = sorted(output_base.glob("LIVE_TEST_yolov8x_kamera2_*"), reverse=True)
    
    if not cam1_dirs:
        print("❌ Camera 1 test results bulunamadı")
        return
    
    if not cam2_dirs:
        print("❌ Camera 2 test results bulunamadı")
        return
    
    cam1_latest = cam1_dirs[0]
    cam2_latest = cam2_dirs[0]
    
    print(f"📹 Camera 1 Latest: {cam1_latest.name}")
    print(f"📹 Camera 2 Latest: {cam2_latest.name}")
    print(f"🚀 Analysis başlatılıyor...")
    
    # Results combiner oluştur
    combiner = ResultsCombiner(cam1_latest, cam2_latest)
    
    # Generate report
    success = combiner.generate_report()
    
    if success:
        print("✅ Combined analysis başarılı!")
    else:
        print("❌ Combined analysis başarısız!")

if __name__ == "__main__":
    main()