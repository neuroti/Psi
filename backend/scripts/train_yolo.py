"""
YOLO v8 Training Script for Psi Food Detection
Fine-tunes YOLOv8 on custom food dataset
"""
import argparse
from ultralytics import YOLO
import torch


def train_yolo(
    data_yaml: str,
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    weights: str = 'yolov8m.pt',
    device: str = None
):
    """
    Train YOLO v8 model on food dataset

    Args:
        data_yaml: Path to data configuration file
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Input image size
        weights: Pre-trained weights path
        device: Device to use (cuda/cpu)
    """
    # Auto-detect device if not specified
    if device is None:
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    print(f"Training configuration:")
    print(f"  Data: {data_yaml}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Image Size: {img_size}")
    print(f"  Weights: {weights}")
    print(f"  Device: {device}")

    # Load model
    model = YOLO(weights)

    # Train model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        patience=50,  # Early stopping
        save=True,
        save_period=10,  # Save every 10 epochs
        cache=True,  # Cache images for faster training
        workers=8,  # Number of dataloader workers
        project='runs/train',
        name='psi_food',
        exist_ok=True,
        pretrained=True,
        optimizer='AdamW',
        lr0=0.001,  # Initial learning rate
        lrf=0.01,  # Final learning rate factor
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,  # Box loss gain
        cls=0.5,  # Class loss gain
        dfl=1.5,  # DFL loss gain
        # Data augmentation
        hsv_h=0.015,  # Hue augmentation
        hsv_s=0.7,  # Saturation augmentation
        hsv_v=0.4,  # Value augmentation
        degrees=10.0,  # Rotation
        translate=0.1,  # Translation
        scale=0.5,  # Scaling
        shear=0.0,  # Shear
        perspective=0.0,  # Perspective
        flipud=0.0,  # Flip up-down
        fliplr=0.5,  # Flip left-right
        mosaic=1.0,  # Mosaic augmentation
        mixup=0.1,  # MixUp augmentation
        copy_paste=0.0,  # Copy-paste augmentation
    )

    # Validate model
    print("\nValidating model...")
    metrics = model.val()

    print("\nValidation Results:")
    print(f"  mAP@0.5: {metrics.box.map50:.4f}")
    print(f"  mAP@0.5:0.95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")

    # Export model
    print("\nExporting model...")
    model.export(format='onnx')  # Export to ONNX for production

    print("\nTraining complete!")
    print(f"Best model saved to: runs/train/psi_food/weights/best.pt")

    return results


def main():
    parser = argparse.ArgumentParser(description='Train YOLO v8 for food detection')
    parser.add_argument('--data', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--img', type=int, default=640, help='Image size')
    parser.add_argument('--weights', type=str, default='yolov8m.pt', help='Initial weights')
    parser.add_argument('--device', type=str, default=None, help='Device (cuda/cpu)')

    args = parser.parse_args()

    train_yolo(
        data_yaml=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.img,
        weights=args.weights,
        device=args.device
    )


if __name__ == '__main__':
    main()
