import cv2
from ultralytics import YOLO
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL

class YoloVideoApp:
    def __init__(self, window):
        self.window = window
        self.window.title("YOLOv8 Video Detector")
        self.model = YOLO("runs/detect/train20/weights/best.pt")

        self.label = Label(window, text="Wybierz plik MP4 i ustaw próg confidence")
        self.label.pack(pady=10)

        self.conf_label = Label(window, text="Confidence: 0.25")
        self.conf_label.pack()

        self.conf_slider = Scale(window, from_=5, to=95, orient=HORIZONTAL, command=self.update_conf_label)
        self.conf_slider.set(25)  # Default 0.25
        self.conf_slider.pack()

        self.button = Button(window, text="Wybierz wideo", command=self.select_video)
        self.button.pack(pady=10)

    def update_conf_label(self, val):
        self.conf_label.config(text=f"Confidence: {int(val)/100:.2f}")

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if not video_path:
            return

        conf_value = self.conf_slider.get() / 100
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, conf=conf_value, device=0)
            annotated = results[0].plot()

            cv2.imshow("YOLOv8 Detection", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    app = YoloVideoApp(root)
    root.mainloop()
