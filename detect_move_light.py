import cv2
import time
import serial
import subprocess
import sys
import os
from ultralytics import YOLO
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Entry, StringVar

class App:
    ## INICJALIZACJA GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Detektor świateł drogowych")
        self.root.geometry("420x300")  # -> stałe rozmiary okna
        self.root.resizable(False,False) # -> blokada rozciagnania okna
        self.arduino = None
        self.model = YOLO("runs/detect/train24/weights/best.pt") # -> sciezka wyboru modelu Yolov8m

        # Port COM wpisywany przez użytkownika - domyslnie ustawiony na COM3 (potem se mozna wybrać)
        Label(root, text="Port COM Arduino:").pack()
        self.com_port = StringVar()
        self.com_entry = Entry(root, textvariable=self.com_port)
        self.com_entry.insert(0, "COM3")
        self.com_entry.pack()

        # Przycisk polaczenia z Arduino
        Button(root, text="Połącz z Arduino", command=self.connect_to_arduino).pack(pady=5)

        # Przycisk do wgrywania kodu do Arduino
        Button(root, text="Wgraj kod do Arduino", command=self.upload_code_to_arduino).pack(pady=5)


        self.status_label = Label(root, text="Status: Niepołączono")
        self.status_label.pack()

        # Okienko wyboru filmu po kliknieciu
        Label(root, text="Wybierz plik MP4 i ustaw próg confidence").pack(pady=10)

        # Suwak do wyboru poziomu ufności modelu - domyślnie 25%
        self.conf_label = Label(root, text="Confidence: 0.25")
        self.conf_label.pack()

        self.conf_slider = Scale(root, from_=5, to=95, orient=HORIZONTAL, command=self.update_conf_label)
        self.conf_slider.set(25)
        self.conf_slider.pack()

        Button(root, text="Wybierz wideo", command=self.select_video).pack(pady=10)

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

    ## Funkcja - uploader kodu Arduino obslugujacy kompilacje i wgrywanie - wykorzystano arduino-cli
    # przeniesiono z pliku uploader.py
    def upload_code_to_arduino(self):
        arduino_cli_path = r"C:\arduino-cli\arduino-cli.exe"
        sketch_path = r"D:/ICR/yolo_test/traffic_lights"
        fqbn = "arduino:avr:uno"
        port = self.com_port.get()

        ## 1. Zamknij połączenie z Arduino przed uploadem
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            self.arduino = None

        try:
            self.status_label.config(text="Status: Kompiluję...")
            self.root.update()

            subprocess.run([arduino_cli_path, "compile", "--fqbn", fqbn, sketch_path], check=True)

            self.status_label.config(text="Status: Wgrywam kod do Arduino...")
            self.root.update()

            subprocess.run([arduino_cli_path, "upload", "-p", port, "--fqbn", fqbn, sketch_path], check=True)

            ## 2. Po udanym uploadzie – ponowne połączenie z Arduino
            time.sleep(2)  # odczekaj chwilę na reset Arduino
            self.arduino = serial.Serial(port, 9600)
            time.sleep(2)

            self.status_label.config(text=f"Kod wgrany i połączono ponownie z {port}")

        ## Obsluga wyjatków - bledy przy uploadzie wraz z kodem
        except subprocess.CalledProcessError as e:
            self.status_label.config(text=f"Błąd uploadu: {e}")
        except serial.SerialException as e:
            self.status_label.config(text=f"Kod wgrany, ale nie można połączyć: {e}")

    ## Funkcja - aktualizacja poziomu zaufania przy przesuwaniu suwaka
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
                if 1 in labels:  # green_light
                    command += "G"
                if 0 in labels:  # red_light
                    command += "R"
                if 2 in labels:  # red_yellow_light
                    command += "R"
                    command += "Y"
                if 3 in labels:  # yellow_light
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
    app = App(root)
    root.mainloop()
