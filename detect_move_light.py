import cv2
import time
import serial
import subprocess
from ultralytics import YOLO
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Entry, StringVar, Frame

class App:
    ## INICJALIZACJA GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Detektor świateł drogowych")
        self.root.geometry("420x320") # -> stałe rozmiary okna
        self.root.resizable(False, False) # -> blokada rozciagnania okna
        self.arduino = None
        self.model = YOLO("runs/detect/train24/weights/best.pt")  # -> sciezka wyboru modelu Yolov8m

        self.main_frame = Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.create_start_menu()

    ## EKRAN STARTOWY Z WYBOREM TRYBU
    def create_start_menu(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        Label(self.main_frame, text="Wybierz tryb detekcji").pack(pady=20)

        Button(self.main_frame, text="Detekcja bez Arduino", width=25, command=self.setup_without_arduino).pack(pady=10)
        Button(self.main_frame, text="Detekcja z Arduino", width=25, command=self.setup_with_arduino).pack(pady=10)

    ## INTERFEJS BEZ ARDUINO
    def setup_without_arduino(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        Label(self.main_frame, text="Tryb: Detekcja bez Arduino").pack(pady=10)

        # Suwak do wyboru poziomu ufności modelu - domyślnie 25%
        self.conf_label = Label(self.main_frame, text="Confidence: 0.25")
        self.conf_label.pack()

        self.conf_slider = Scale(self.main_frame, from_=5, to=95, orient=HORIZONTAL, command=self.update_conf_label)
        self.conf_slider.set(25)
        self.conf_slider.pack()

        Button(self.main_frame, text="Wybierz wideo", command=self.select_video_without_arduino).pack(pady=10)

        self.best_detection_label = Label(self.main_frame, text="")  # -> nowy label do pokazywania najlepszego wyniku
        self.best_detection_label.pack(pady=5)

        # Przycisk "powrot" -> powrot do poprzedniej warstwy
        Button(self.main_frame, text="Powrót", command=self.create_start_menu).pack(pady=10)

    ## INTERFEJS Z ARDUINO
    def setup_with_arduino(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        Label(self.main_frame, text="Port COM Arduino:").pack()
        self.com_port = StringVar()
        self.com_entry = Entry(self.main_frame, textvariable=self.com_port)
        self.com_entry.insert(0, "COM3")
        self.com_entry.pack()

        # Przycisk polaczenia z Arduino
        Button(self.main_frame, text="Połącz z Arduino", command=self.connect_to_arduino).pack(pady=5)
        Button(self.main_frame, text="Wgraj kod do Arduino", command=self.upload_code_to_arduino).pack(pady=5)

        # Przycisk do wgrywania kodu do Arduino
        self.status_label = Label(self.main_frame, text="Status: Niepołączono")
        self.status_label.pack()

        # Okienko wyboru filmu po kliknieciu
        Label(self.main_frame, text="Wybierz plik MP4 i ustaw próg confidence").pack(pady=10)

        # Suwak do wyboru poziomu ufności modelu - domyślnie 25%
        self.conf_label = Label(self.main_frame, text="Confidence: 0.25")
        self.conf_label.pack()

        self.conf_slider = Scale(self.main_frame, from_=5, to=95, orient=HORIZONTAL, command=self.update_conf_label)
        self.conf_slider.set(25)
        self.conf_slider.pack()

        # Przycisk - wyboru wideo
        Button(self.main_frame, text="Wybierz wideo", command=self.select_video_with_arduino).pack(pady=10)

        # Przycisk "powrot" - do poprzedniej sceny
        Button(self.main_frame, text="Powrót", command=self.create_start_menu).pack(pady=5)

        self.best_detection_label = Label(self.main_frame, text="")
        self.best_detection_label.pack(pady=5)

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
            time.sleep(2)
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

    ## Funkcja - wybor filmu (dla trybu bez Arduino)
    def select_video_without_arduino(self):
        video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if not video_path:
            return

        conf_value = self.conf_slider.get() / 100
        cap = cv2.VideoCapture(video_path)

        max_score = 0
        max_label = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, conf=conf_value, device=0)
            annotated = results[0].plot()

            boxes = results[0].boxes
            labels = boxes.cls.tolist() if boxes is not None else []
            scores = boxes.conf.tolist() if boxes is not None else []

            # Petla do zapamietywania najwyzszego confa
            for lbl, score in zip(labels, scores):
                if score > max_score:
                    max_score = score
                    max_label = int(lbl)

            cv2.imshow("Detektor świateł drogowych (bez Arduino)", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Po zakończeniu – pokazanie najlepszego wyniku na GUI
        if max_label is not None:
            label_names = {
                0: "Zielone",
                3: "Żółte",
                2: "Czerwono-żółte",
                1: "Czerwone"
            }

            label_name = label_names.get(max_label, "Nieznane")
            confidence_percent = int(max_score * 100)
            self.best_detection_label.config(
                text=f"Najpewniejsze: {label_name} światło ({confidence_percent}%)"
            )
            print(f"[Koniec filmu] Najlepsze wykrycie: {label_name} ({confidence_percent}%)")
        else:
            self.best_detection_label.config(text="Nie wykryto świateł.")
            print("[Koniec filmu] Nie wykryto świateł.")

    ## Funkcja - wybor filmu (dla trybu z Arduino)
    def select_video_with_arduino(self):
        video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if not video_path:
            return

        conf_value = self.conf_slider.get() / 100
        cap = cv2.VideoCapture(video_path)

        max_score = 0
        max_label = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, conf=conf_value, device=0)
            annotated = results[0].plot()

            boxes = results[0].boxes
            labels = boxes.cls.tolist() if boxes is not None else []
            scores = boxes.conf.tolist() if boxes is not None else []

            ## Przypisywanie liter w zalezności od wykrytego labelu -> labele są opisane w data.yaml
            # w przypadku tego projektu:
            # 0 - green light
            # 1 - red light
            # 2 - red yellow light
            # 3 - yellow light
            if self.arduino:
                if scores and labels:
                    max_idx = scores.index(max(scores))
                    current_score = scores[max_idx]
                    current_label = int(labels[max_idx])

                    label_map = {
                        0: "G", # G -> GREEN -> ZIELONE SWIATLO
                        3: "Y", # Y -> YELLOW -> ZOLTE SWIATLO
                        2: "RY", # RY -> RED-YELLOW -> CZERWONO-ZOLTE SWIATLO
                        1: "R"  # R -> RED -> CZERWONE SWIATLO
                    }
                    # w tym miejscu przypisuje chara w zaleznosci od wykrytego labela
                    # i biore confa
                    label_char = label_map.get(current_label, "N")
                    confidence_percent = int(current_score * 100)
                    command = f"{label_char}:{confidence_percent}"
                else:
                    command = "N:0"

                self.arduino.write((command + '\n').encode())
                self.arduino.flush()

            # Petla do zapamietywania najwyzszego confa
            for lbl, score in zip(labels, scores):
                if score > max_score:
                    max_score = score
                    max_label = int(lbl)

            cv2.imshow("Detektor świateł drogowych", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Po zakończeniu filmu – wysłanie najlepszego wykrycia
        if self.arduino:
            if max_label is not None:
                label_map = {
                    0: "G",
                    3: "Y",
                    2: "RY",
                    1: "R"
                }
                label_names = {
                    0: "Zielone",
                    3: "Żółte",
                    2: "Czerwono-żółte",
                    1: "Czerwone"
                }

                label_char = label_map.get(max_label, "N")
                label_name = label_names.get(max_label, "Nieznane")
                confidence_percent = int(max_score * 100)
                final_command = f"{label_char}:{confidence_percent}"

                self.arduino.write((final_command + '\n').encode())
                self.arduino.flush()

                self.best_detection_label.config(
                    text=f"Najpewniejsze: {label_name} światło ({confidence_percent}%)"
                )
                print(f"[Koniec filmu] Najlepsze wykrycie: {final_command}")
            else:
                self.arduino.write(b"N:0\n")
                self.arduino.flush()
                self.best_detection_label.config(text="Nie wykryto świateł.")
                print("[Koniec filmu] Nie wykryto świateł.")

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
