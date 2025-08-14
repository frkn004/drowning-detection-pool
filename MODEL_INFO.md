# 🤖 DROWNING DETECTION MODELS

## 📦 Available Models

### 🎯 Base Models (Google Drive'da)
- `yolov8m.pt` - Baseline model
- `yolov8x.pt` - Large model  
- `yolo11x.pt` - Latest YOLO
- `yolo12m.pt` - Experimental

### 🏊 Trained Models (Eğitim sonrası)
- `best_phase1.pt` - Phase 1 en iyi model
- `best_phase2.pt` - Phase 2 en iyi model
- `best_phase3.pt` - Phase 3 en iyi model
- `best_phase4.pt` - Final production model

## 🚀 Model Download (VAST.AI'da)

Models otomatik olarak eğitim sırasında download edilir:

```bash
# YOLOv8 base model otomatik download
python scripts/train_model.py  # Otomatik yolov8m.pt indirir
```

## 📊 Expected Performance

| Phase | mAP50 Target | Training Time | Model Size |
|-------|--------------|---------------|------------|
| Phase 1 | >0.6 | 2-3 hours | ~50MB |
| Phase 2 | >0.75 | 8-12 hours | ~50MB |
| Phase 3 | >0.85 | 20-30 hours | ~50MB |
| Phase 4 | >0.90 | 40-60 hours | ~50MB |
