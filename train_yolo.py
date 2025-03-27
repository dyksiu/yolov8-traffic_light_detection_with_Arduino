from ultralytics import YOLO

def main():
    model = YOLO("D:/ICR/yolo_test/runs/detect/train19/weights/best.pt")

    model.train(
        data="datasets/traffic_dataset/data.yaml",
        epochs=300,
        imgsz=640,
        device=0 # WYBÓR GPU

    )

if __name__ == "__main__":
    main()
