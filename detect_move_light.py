import cv2
import time
import serial
from ultralytics import YOLO
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Entry, StringVar

class YoloVideoApp:
    ## Obsługa GUI
    def __init__(self, window):
        self.window = window
        self.window.title("Detektor świateł drogowych")
        self.window.geometry("480x240") # -> stale rozmiary okna
        self.window.resizable(False,False) # -> blokada rozciagania okna
        self.model = YOLO("runs/detect/train24/weights/best.pt")
        self.arduino = None

        # Port COM wpisywany przez użytkownika - domyslnie ustawiony na COM3
        self.com_label = Label(window, text="Port COM Arduino:")
        self.com_label.pack()
        self.com_port = StringVar()
        self.com_entry = Entry(window, textvariable=self.com_port)
        self.com_entry.insert(0, "COM3")
        self.com_entry.pack()

        # Przycisk polazcenia z Arduino
        self.connect_button = Button(window, text="Połącz z Arduino", command=self.connect_to_arduino)
        self.connect_button.pack(pady=5)

        self.status_label = Label(window, text="Status: Niepołączono")
        self.status_label.pack()

        # Okienko wyboru filmu po kliknieciu
        self.label = Label(window, text="Wybierz plik MP4 i ustaw próg confidence")
        self.label.pack(pady=10)

        # Suwak do wyboru poziomu ufności modelu - domyślnie 25%
        self.conf_label = Label(window, text="Confidence: 0.25")
        self.conf_label.pack()

        self.conf_slider = Scale(window, from_=5, to=95, orient=HORIZONTAL, command=self.update_conf_label)
        self.conf_slider.set(25)
        self.conf_slider.pack()

        self.button = Button(window, text="Wybierz wideo", command=self.select_video)
        self.button.pack(pady=10)

    ## Funkcja - polaczenie z Arduino za pomoca serial portu
    def connect_to_arduino(self):
        port = self.com_port.get()
        try:
            self.arduino = serial.Serial(port, 9600)
            time.sleep(2)
            self.status_label.config(text=f"Status: Połączono z {port}")
        except Exception as e:
            self.arduino = None
            self.status_label.config(text=f"Status: Błąd połączenia ({e})")

    ## Funkcja - aktualizacja poziomu zaufania przy przesuwania suwaka
    def update_conf_label(self, val):
        self.conf_label.config(text=f"Confidence: {int(val)/100:.2f}")

    ## Funkcja - wybor filmu
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

            boxes = results[0].boxes
            labels = boxes.cls.tolist() if boxes is not None else []

            ## Przypisywanie liter w zalezności od wykrytego labelu -> labele są opisane w data.yaml
            # w przypadku tego projektu:
            # 0 - green light
            # 1 - red light
            # 2 - red yellow light
            # 3 - yellow light
            if self.arduino:
                command = ""

                if 0 in labels:  # red_light
                    command += "R"
                if 3 in labels:  # yellow_light
                    command += "Y"
                if 1 in labels:  # green_light
                    command += "G"
                if 2 in labels:  # red_yellow_light
                    command += "R"
                    command += "Y"

                command = "".join(sorted(set(command)))
                if not command:
                    command = "N"

                print(f"Komenda do Arduino: {command}")
                self.arduino.write((command + '\n').encode())
                self.arduino.flush()

            cv2.imshow("Detektor świateł drogowych", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    root = Tk()
    app = YoloVideoApp(root)
    root.mainloop()
