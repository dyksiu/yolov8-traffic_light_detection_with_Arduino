# yolov8-traffic_light_detection_with_Arduino
This repo contains yolov8 training environment and simple GUI for test yolo model.

# Concept
The project focuses on traffic light detection using the yolov8m model. Additionally, detection is signaled by LEDs programmed using Arduino UNO and the highest confidence detected is displayed on the LCD display.

### For example:

![the best](https://github.com/user-attachments/assets/274b2cc0-87b3-408b-b57f-40fdf30a38c9)



# Before use:
This project uses Pycharm version 2024.1.3. You can install libraries in Pycharm Terminal.

- install Ultralytics:
```
pip install ultralytics
```
- upgrade pip:
```
python.exe -m pip install --upgrade pip
```
- install opencv-python matplotlib:
```
 pip install ultralytics opencv-python matplotlib  
```
### CUDA 
CUDA version 12.3 was used to optimize model training. You can download it from Nvidia website but it is recommended to check if the card is supported by CUDA. 
- Download link from Nvidia official website: https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local  
- install PyTorch with torchvision and torchaudio compatible with CUDA 11.8 (if you use other version CUDA - use for example cu117, cu121 or use cpu):
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
- if you want to check what CUDA version you have. if everything works and what GPU you have create a new .py script:
```
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))  -> USE IT IF YOU USE GPU!
```
### Arduino CLI
If you want to compile .ino code from Python, you need to have Arduino CLI(Command Line Interface) installed. Download link: https://arduino.github.io/arduino-cli/1.2/ 
- create a folder on your disk, move and unzip the downloaded Arduino CLI file there
- run the file arduino-cli.exe and open new cmd window
- in new cmd window go to the directory where you have the arduino-cli.exe file, for example:
```
cd C:\arduino-cli
```
- initialize the environment
```
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr  
```

# GUI
The project uses a simple GUI that has two modes:
- detection without Arduino (Detekcja bez Arduino)
- detection with Arduino (Detekcja z Arduino)
  
 ![gui](https://github.com/user-attachments/assets/247f15d0-801a-4eae-9e98-0df015fe4b5a)
### Detection without Arduino
If you select detecion mode without Arduino (Detekcja bez Arduino) in the GUI you will be able to select the confidence level from which the detection should be displayed - using the slider. 
You can select the video on which detection is to be performed - it must be in .mp4 format. You can also choose to enable or disable Region of Interest (ROI) - (Obszar zainteresowania) and choose from which side detection should be performed.

![bez arduino](https://github.com/user-attachments/assets/ef29dd1c-85cd-486f-865a-a5e0a245759d)

### Detection with Arduino
If you select detection mode with Arduino (Detekcja z Arduino), the GUI will be more extensive. You can choose which COM port to connect to Arduino and upload the .ino file from the GUI to Arduino. IMPORTANT - the folder with the .ino files must be in the same folder as the .py file with the project. The rest of the options are the same as in the first mode.

![z arduino](https://github.com/user-attachments/assets/45b45723-3544-4056-9cd9-c87b8a683dee)

# Example of use 
### Detection with Arduino - with ROI

![with ROI](https://github.com/user-attachments/assets/0a890017-97ef-4d6b-a025-6c4b3475fd88)

### Detection without Arduino - no ROI

![no arduino no roi](https://github.com/user-attachments/assets/dfec7237-a687-4062-9c23-bd2b70cc0d3e)

