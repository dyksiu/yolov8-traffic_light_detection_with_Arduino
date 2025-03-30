## Uploader - wykorzystanie adruino-cli do uplodowania kodu arduino bez koniecznosci odpalania programu Arduino IDE
import subprocess

def upload_arduino_code(sketch_path, port, fqbn):
    try:
        # musialem podac sciezke gdzie mam arduino-cli bo bez tego nie dziala
        # inny sposob - zmienne srodowiskowe? ale to tez nie dziala
        arduino_cli_path = r"C:\arduino-cli\arduino-cli.exe"

        subprocess.run([arduino_cli_path, "compile", "--fqbn", fqbn, sketch_path], check=True)
        subprocess.run([arduino_cli_path, "upload", "-p", port, "--fqbn", fqbn, sketch_path], check=True)

        print("Kod wgrany pomyslnie do Arduino!")

    # zwracamy wyjatek przy niepowodzeniu - wyswietlamy blad
    except subprocess.CalledProcessError as e:
        print("Błąd podczas kompilacji lub uploadu:", e)

# tu mozna ustawic parametry takie jak:
# -> sciezka do projektu z rozszerzeniem .ino
# -> numer portu COM - trzeba to zmienic zeby nie wpisywac z lapy w kodzie
# -> typ plytki

upload_arduino_code(
    sketch_path="D:/ICR/yolo_test/traffic_lights",
    port="COM7",
    fqbn="arduino:avr:uno"
)
