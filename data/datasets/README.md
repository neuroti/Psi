# Psi Training Datasets

This directory contains datasets for training and fine-tuning models.

## Dataset Sources

### 1. AI Hub Korean Food Dataset
**Source**: https://aihub.or.kr
**Size**: 10,000+ images
**Classes**: 150 Korean food categories
**License**: AI Hub License

#### Download
```bash
# Register and download from AI Hub
# https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=realm&dataSetSn=74
```

### 2. Roboflow Food Dataset
**Source**: https://universe.roboflow.com
**Size**: 670 images
**Classes**: 50+ international foods
**License**: CC BY 4.0

#### Download
```bash
# Download using Roboflow API
pip install roboflow
python scripts/download_roboflow.py
```

### 3. Custom Psi Dataset
**Size**: 200+ images (self-collected)
**Classes**: Mixed Korean and international
**Purpose**: Domain-specific fine-tuning

## Dataset Structure

```
data/datasets/
├── food/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── val/
│   │   ├── images/
│   │   └── labels/
│   ├── test/
│   │   ├── images/
│   │   └── labels/
│   └── data.yaml
├── ingredients/
│   └── (similar structure)
└── README.md
```

## Data Preparation

### 1. Label Format (YOLO)
```
# Each .txt file contains:
# <class_id> <x_center> <y_center> <width> <height>
# All values normalized to 0-1

0 0.5 0.5 0.3 0.4
1 0.7 0.3 0.2 0.2
```

### 2. Data YAML Configuration

**File**: `food/data.yaml`

```yaml
path: ../datasets/food
train: train/images
val: val/images
test: test/images

nc: 150  # number of classes
names:
  0: 김치찌개
  1: 불고기
  2: 비빔밥
  # ... more classes
```

## Data Augmentation

Applied during training:
- Mosaic (probability: 1.0)
- MixUp (probability: 0.1)
- Random rotation (±10°)
- Random scaling (0.8-1.2x)
- Color jittering
- Random flips

## Dataset Statistics

### Food Dataset
- **Total Images**: 10,870
- **Train**: 8,696 (80%)
- **Val**: 1,087 (10%)
- **Test**: 1,087 (10%)
- **Avg Objects/Image**: 2.3
- **Min Objects/Image**: 1
- **Max Objects/Image**: 8

### Class Distribution
Top 10 classes:
1. 김치 (Kimchi): 450 images
2. 불고기 (Bulgogi): 420 images
3. 비빔밥 (Bibimbap): 380 images
4. 된장찌개 (Doenjang-jjigae): 350 images
5. ... (more)

## Data Collection Guidelines

For custom dataset expansion:
1. **Lighting**: Natural and artificial
2. **Angles**: 45° top-down view preferred
3. **Background**: Varied (table, plate, bowl)
4. **Resolution**: Minimum 640x640
5. **Format**: JPG, PNG
6. **File size**: < 5MB

## Annotation Tools

- **LabelImg**: For bounding boxes
- **Roboflow**: For online annotation and augmentation
- **CVAT**: For advanced annotation workflows

## License Compliance

All datasets must comply with their respective licenses:
- AI Hub: Academic and commercial use allowed
- Roboflow: CC BY 4.0
- Custom: MIT License
