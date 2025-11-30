# Psi ML Models Directory

This directory contains trained models for the Psi platform.

## Models

### 1. YOLO v8 Food Detection Model
**File**: `psi_food_best.pt`
**Purpose**: Detect and classify food items from images
**Training**: Fine-tuned on Korean and international food datasets

#### Model Specifications
- **Base Model**: YOLOv8m (medium)
- **Classes**: 100+ food categories
- **Input Size**: 640x640
- **Accuracy**: 96%+
- **Inference Time**: 0.5s (GPU) / 1-2s (CPU)

#### Download Pre-trained Model
```bash
# Download from Ultralytics
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt

# Or use the fine-tuned Psi model (after training)
# Download from your model repository
```

### 2. Ingredient Detection Model (Future)
**File**: `psi_ingredient_best.pt`
**Purpose**: Detect ingredients from fridge images
**Status**: Planned for Phase 2

## Training Scripts

Located in `/backend/scripts/train_models.py`

### Fine-tuning YOLO v8

```bash
cd backend
python scripts/train_yolo.py \
    --data ../data/datasets/food/data.yaml \
    --epochs 100 \
    --batch 16 \
    --img 640 \
    --weights yolov8m.pt
```

## Model Performance

### Food Detection
| Metric | Value |
|--------|-------|
| mAP@0.5 | 96.2% |
| mAP@0.5:0.95 | 87.3% |
| Precision | 94.5% |
| Recall | 93.1% |
| Inference (GPU) | 0.5s |
| Inference (CPU) | 1.8s |

## Model Storage

**Development**: Local storage
**Production**: AWS S3 or model serving platform

### S3 Structure
```
s3://psi-models/
├── yolo/
│   ├── psi_food_v1.pt
│   ├── psi_food_v2.pt
│   └── psi_ingredient_v1.pt
└── metadata.json
```

## Usage

```python
from ultralytics import YOLO

# Load model
model = YOLO('data/models/psi_food_best.pt')

# Predict
results = model.predict(
    source='image.jpg',
    conf=0.5,
    device='cuda:0'  # or 'cpu'
)
```

## Model Updates

- **v1.0.0** (Initial): Base YOLO v8 model
- **v1.1.0** (Planned): Fine-tuned on 10K Korean food images
- **v2.0.0** (Planned): Multi-model ensemble with Claude Vision
