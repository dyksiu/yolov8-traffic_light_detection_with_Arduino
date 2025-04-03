import cv2
import time
import serial
import subprocess
from ultralytics import YOLO
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Entry, StringVar, Frame, BooleanVar, OptionMenu

class App:
    ## INICJALIZACJA GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Detektor świateł drogowych")
        self.root.geometry("420x420") # -> stałe rozmiary okna
        self.root.resizable(False, False) # -> blokada rozciagnania okna
        self.arduino = None
        self.model = YOLO("runs/detect/train24/weights/best.pt")  # -> sciezka wyboru modelu Yolov8m

        self.use_roi = BooleanVar()
        self.lane_choice = StringVar(value="Środkowy")  # -> ustawiamy domyslnie srodkowy pas w trybie ROI

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

        # Checkbox do ROI
        self.roi_checkbox = Button(self.main_frame, text="Włącz obszar zainteresowania", command=self.toggle_roi_menu)
        self.roi_checkbox.pack(pady=5)

        self.lane_dropdown = OptionMenu(self.main_frame, self.lane_choice, "Lewy", "Środkowy", "Prawy")
        self.lane_dropdown.pack(pady=5)
        self.lane_dropdown.pack_forget()  # ukryj na start

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

        # Checkbox do ROI
        self.roi_checkbox = Button(self.main_frame, text="Włącz obszar zainteresowania", command=self.toggle_roi_menu)
        self.roi_checkbox.pack(pady=5)

        self.lane_dropdown = OptionMenu(self.main_frame, self.lane_choice, "Lewy", "Środkowy", "Prawy")
        self.lane_dropdown.pack(pady=5)
        self.lane_dropdown.pack_forget()  # ukryj na start

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

    def toggle_roi_menu(self):
        self.use_roi.set(not self.use_roi.get())
        if self.use_roi.get():
            self.roi_checkbox.config(text="Wyłącz obszar zainteresowania")
            self.lane_dropdown.pack(pady=5)
        else:
            self.roi_checkbox.config(text="Włącz obszar zainteresowania")
            self.lane_dropdown.pack_forget()

    def apply_lane_roi(self, frame):
        h, w, _ = frame.shape
        lane = self.lane_choice.get()

        if lane == "Lewy":
            roi = frame[:, :w // 3]
        elif lane == "Środkowy":
            roi = frame[:, w // 3: 2 * w // 3]
        elif lane == "Prawy":
            roi = frame[:, 2 * w // 3:]
        else:
            roi = frame  # fallback

        return roi


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
            boxes = results[0].boxes

            annotated = frame.copy()

            if boxes is not None:
                labels = boxes.cls.tolist()
                scores = boxes.conf.tolist()
                xyxy = boxes.xyxy.tolist()

                filtered_labels, filtered_scores, filtered_boxes = [], [], []

                h, w, _ = frame.shape
                roi_active = self.use_roi.get()

                if roi_active:
                    if self.lane_choice.get() == "Lewy":
                        x_min, x_max = 0, w // 3
                    elif self.lane_choice.get() == "Środkowy":
                        x_min, x_max = w // 3, 2 * w // 3
                    elif self.lane_choice.get() == "Prawy":
                        x_min, x_max = 2 * w // 3, w
                    else:
                        x_min, x_max = 0, w

                for box, lbl, score in zip(xyxy, labels, scores):
                    x1, y1, x2, y2 = box
                    cx = (x1 + x2) / 2
                    if not self.use_roi.get() or (x_min <= cx <= x_max):
                        filtered_labels.append(lbl)
                        filtered_scores.append(score)
                        filtered_boxes.append(box)

                # Rysuj tylko filtrowane boxy -> reszta nie jest brana pod uwage
                for box, lbl, score in zip(filtered_boxes, filtered_labels, filtered_scores):
                    x1, y1, x2, y2 = map(int, box)
                    label_names = {
                        0: "Zielone",
                        1: "Czerwone",
                        2: "Czerw.-żółte",
                        3: "Żółte"
                    }
                    label_text = f"{label_names.get(int(lbl), 'Nieznane')} ({int(score * 100)}%)"
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(annotated, label_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # zolty prostokat w trybie roi dla wybranej strony
                # mozna zmienic kolor z lapy jak trzeba
                if self.use_roi.get():
                    overlay = annotated.copy()
                    cv2.rectangle(overlay, (x_min, 0), (x_max, h), (0, 255, 255), -1)
                    alpha = 0.3
                    cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)

                for lbl, score in zip(filtered_labels, filtered_scores):
                    if score > max_score:
                        max_score = score
                        max_label = int(lbl)

            else:
                filtered_labels, filtered_scores = [], []

            cv2.imshow("Detektor świateł drogowych (bez Arduino)", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

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
            boxes = results[0].boxes
            annotated = frame.copy()

            if boxes is not None:
                labels = boxes.cls.tolist()
                scores = boxes.conf.tolist()
                xyxy = boxes.xyxy.tolist()

                filtered_labels, filtered_scores, filtered_boxes = [], [], []

                h, w, _ = frame.shape
                roi_active = self.use_roi.get()

                if roi_active:
                    if self.lane_choice.get() == "Lewy":
                        x_min, x_max = 0, w // 3
                    elif self.lane_choice.get() == "Środkowy":
                        x_min, x_max = w // 3, 2 * w // 3
                    elif self.lane_choice.get() == "Prawy":
                        x_min, x_max = 2 * w // 3, w
                    else:
                        x_min, x_max = 0, w

                for box, lbl, score in zip(xyxy, labels, scores):
                    x1, y1, x2, y2 = box
                    cx = (x1 + x2) / 2
                    if not roi_active or (x_min <= cx <= x_max):
                        filtered_labels.append(lbl)
                        filtered_scores.append(score)
                        filtered_boxes.append(box)

                # Rysuj tylko filtrowane boxy -> reszta nie jest brana pod uwage
                for box, lbl, score in zip(filtered_boxes, filtered_labels, filtered_scores):
                    x1, y1, x2, y2 = map(int, box)
                    label_names = {
                        0: "Zielone",
                        1: "Czerwone",
                        2: "Czerw.-żółte",
                        3: "Żółte"
                    }
                    label_text = f"{label_names.get(int(lbl), 'Nieznane')} ({int(score * 100)}%)"
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(annotated, label_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                  # zolty prostokat w trybie roi dla wybranej strony
                # mozna zmienic kolor z lapy jak trzeba
                if roi_active:
                    overlay = annotated.copy()
                    cv2.rectangle(overlay, (x_min, 0), (x_max, h), (0, 255, 255), -1)
                    alpha = 0.3
                    cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)

                # Wyslanie najwyzszego conf do Arduino z obszaru ROI
                if self.arduino:
                    if filtered_scores and filtered_labels:
                        max_idx = filtered_scores.index(max(filtered_scores))
                        current_score = filtered_scores[max_idx]
                        current_label = int(filtered_labels[max_idx])

                        label_map = {
                            0: "G",
                            3: "Y",
                            2: "RY",
                            1: "R"
                        }
                        label_char = label_map.get(current_label, "N")
                        confidence_percent = int(current_score * 100)
                        command = f"{label_char}:{confidence_percent}"
                    else:
                        command = "N:0"

                    self.arduino.write((command + '\n').encode())
                    self.arduino.flush()

                # Zapisuje najlepszy wynik conf dla ROI
                for lbl, score in zip(filtered_labels, filtered_scores):
                    if score > max_score:
                        max_score = score
                        max_label = int(lbl)

            else:
                filtered_labels, filtered_scores = [], []

            cv2.imshow("Detektor świateł drogowych", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Wysylanie najlepszego wykrycia conf do Arduino po skonczeniu filmu lub przerwaniu
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
