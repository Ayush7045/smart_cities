# How to Run the Smart Traffic Management System

## Quick Demo (Record This)

This section gives you two easy demos you can screen-record for your faculty:

1. Local Desktop Dashboard (no extra installs beyond Python)
2. Wokwi Arduino Simulation (online)

### Option 1: Local Desktop Dashboard (Recommended for quick recording)

1. Open PowerShell in the project directory:
   ```powershell
   cd "C:\Ayush\smart cities\smart_traffic_management_using_iotdevices_and_-netwrokcommprotocols_for_emergencyvehicles"
   ```
2. Run the demo:
   ```powershell
   python .\demo_dashboard.py
   ```
3. Click "Start Ambulance" and narrate how each intersection turns GREEN when distance < 20 cm and returns to RED after the vehicle passes (< 10 cm). Click "Reset" if you want to rerun.

Tips for recording:
- Start your screen recorder, then click Start Ambulance.
- Keep the window visible and explain the control logic as lights change.

### Option 2: Wokwi Arduino Simulation (Online)

This shows the same logic running on a simulated Arduino Uno with ultrasonic sensors and LEDs.

1. Go to [https://wokwi.com](https://wokwi.com) and create a new Arduino Uno project.
2. Import the wiring layout using `diagram.json`:
   - In Wokwi, click the project menu (three dots) → "Import project" → upload `diagram.json` from this repo.
   - Alternatively, wire manually as described below in Part 2.
3. Open `arduino_code.ino`, copy all code, and paste into Wokwi's code editor.
4. Click Start. Open the Serial Monitor to see distances. Drag the HC-SR04 distance sliders to simulate an ambulance approaching each node.
5. Record your screen while the LEDs switch from RED to GREEN as the distance drops.

### Option 3: Detection Demo (Record model output / overlay)

Use this to show an “Ambulance detected” style overlay. It works in two modes:
- If Ultralytics YOLO is installed (and a small model like `yolov8n.pt` is available), it draws real detections.
- Otherwise it simulates a detection overlay you can toggle for recording.

Run with webcam (default):
```powershell
python .\detect_demo.py
```

Run with a video file:
```powershell
python .\detect_demo.py .\path\to\your_video.mp4
```

Controls while recording:
- E: Toggle “EMERGENCY VEHICLE DETECTED” banner
- Space: Pause/Resume (simulation mode)
- Q: Quit

Note: COCO models don’t have an explicit “ambulance” class, so vehicles (car/truck/bus) are highlighted as a stand-in. Use the E key to clearly show the emergency banner during your narration.

### Option 4: Integrated Image → YOLO → Signal Demo (Ambulance triggers GREEN)

Use a single app that loads an image, runs YOLO, and flips the signal GREEN only if the target class (default 'ambulance') is detected. Perfect for a quick, clear recording.

1. Prepare a YOLO model (recommended: your custom model trained with an 'ambulance' class). If you don't provide a model, the app attempts small public checkpoints, but they may not include an ambulance class.
2. Run the app:
   ```powershell
   python .\integrated_demo.py --model C:\path\to\your_ambulance_model.pt --classes ambulance
   ```
3. Click Browse, select your image (JPEG/PNG), then click Run Detection.
4. The right panel signal turns GREEN if an 'ambulance' is detected; otherwise remains RED.
5. Record the window while explaining the linkage: detection → SDN/IoT signal change.

This guide will help you run both components of the project:
1. **YOLO Model Training** (Python/Notebook)
2. **Arduino IoT Simulation** (Arduino/Wokwi)

---

## Part 1: Running the YOLO Model Training (Notebook)

### Option A: Using Google Colab (Recommended)

The notebook is configured for Google Colab, which provides free GPU access and pre-installed libraries.

#### Steps:

1. **Open the Notebook in Colab:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click on "File" → "Upload notebook"
   - Upload `Untitled0.ipynb`
   - Or click the "Open in Colab" badge in the first cell

2. **Mount Google Drive (Cell 1):**
   - Run the first cell to mount your Google Drive
   - You'll need to authenticate and allow access

3. **Install Dependencies (Cell 2):**
   - Run: `!pip install ultralytics`
   - This installs YOLO and all required dependencies

4. **Load the Model (Cell 3):**
   - Run to download the YOLOv10 model (will auto-download)

5. **Navigate to Dataset (Cell 4):**
   - ⚠️ **IMPORTANT**: Update the path to match your dataset location
   - Currently set to: `/content/drive/MyDrive/papermodel-20241122T191738Z-001/papermodel`
   - Change `%cd` command to your actual dataset path

6. **Train the Model (Cell 5):**
   - ⚠️ **Make sure you have a `data.yaml` file in the dataset directory**
   - The `data.yaml` should contain your dataset configuration
   - Training will run for 150 epochs
   - Results will be saved in `runs/detect/trainXX/`

7. **Run SDN Controller Simulation (Cells 6-10):**
   - These cells demonstrate the SDN traffic light control logic
   - Update the path in Cell 6 to point to your training results

---

### Option B: Running Locally on Windows

#### Prerequisites:
- Python 3.8+ installed
- Git (optional)

#### Steps:

1. **Open PowerShell in the project directory:**
   ```powershell
   cd "C:\Ayush\smart cities\smart_traffic_management_using_iotdevices_and_-netwrokcommprotocols_for_emergencyvehicles"
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

   If you have an NVIDIA GPU with CUDA support:
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

   For CPU only:
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

4. **Install Jupyter Notebook:**
   ```powershell
   pip install notebook jupyter
   ```

5. **Launch Jupyter:**
   ```powershell
   jupyter notebook
   ```

6. **Open and Run the Notebook:**
   - Open `Untitled0.ipynb` in the browser
   - ⚠️ **Modify the cells** to work locally:
     - Remove or comment out Cell 1 (Google Drive mount)
     - Update Cell 4 to use a local dataset path
     - Update Cell 6 path to point to local training results

7. **Run cells sequentially** (Cell 0 → Cell 10)

---

## Part 2: Running Arduino IoT Simulation

### Option A: Using Wokwi (Online Simulator - Recommended)

1. **Go to Wokwi:**
   - Visit [https://wokwi.com](https://wokwi.com)
   - Sign up for a free account (if needed)

2. **Create a New Project:**
   - Click "New Project"
   - Select "Arduino Uno"

3. **Add Components:**
   - Click the "+" button to add components
   - Add **3x HC-SR04** (Ultrasonic sensors)
   - Add **6x LED** (2 red, 2 green, 2 red, 2 green, 2 red, 2 green)
   - Add **6x 220Ω Resistor** (one for each LED)

4. **Wire the Components:**
   Connect according to the pin definitions:
   ```
   Node 1:
   - HC-SR04 #1: Trig → Pin 2, Echo → Pin 3, VCC → 5V, GND → GND
   - Green LED #1: + → Pin 8, - → Resistor → GND
   - Red LED #1: + → Pin 9, - → Resistor → GND
   
   Node 2:
   - HC-SR04 #2: Trig → Pin 4, Echo → Pin 5, VCC → 5V, GND → GND
   - Green LED #2: + → Pin 10, - → Resistor → GND
   - Red LED #2: + → Pin 11, - → Resistor → GND
   
   Node 3:
   - HC-SR04 #3: Trig → Pin 6, Echo → Pin 7, VCC → 5V, GND → GND
   - Green LED #3: + → Pin 12, - → Resistor → GND
   - Red LED #3: + → Pin 13, - → Resistor → GND
   ```

5. **Copy the Code:**
   - Open `arduino_code.ino` in this project
   - Copy all the code
   - Paste it into the Wokwi editor (replace default code)

6. **Run the Simulation:**
   - Click the green "Start" button
   - Open Serial Monitor (bottom panel) to see distance readings
   - Adjust sensor distances in Wokwi to simulate ambulance approach
   - Watch LEDs change from red to green as distance decreases

---

### Option B: Using Real Arduino Hardware

#### Required Components:
- Arduino Uno
- 3x HC-SR04 Ultrasonic Sensors
- 6x LEDs (3 green, 3 red)
- 6x 220Ω Resistors
- Jumper wires
- Breadboard

#### Steps:

1. **Install Arduino IDE:**
   - Download from [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)
   - Install on your computer

2. **Open the Code:**
   - Open Arduino IDE
   - Go to File → Open
   - Select `arduino_code.ino`

3. **Connect Hardware:**
   - Wire components exactly as described in Wokwi section above
   - Connect Arduino to computer via USB cable

4. **Select Board and Port:**
   - Tools → Board → Arduino Uno
   - Tools → Port → Select your Arduino's COM port

5. **Upload Code:**
   - Click the Upload button (→ arrow icon)
   - Wait for "Done uploading" message

6. **Open Serial Monitor:**
   - Tools → Serial Monitor (or Ctrl+Shift+M)
   - Set baud rate to 9600
   - You should see distance readings from each node
   - Test by moving objects in front of sensors

---

## Troubleshooting

### Notebook Issues:

1. **ModuleNotFoundError:**
   - Run `pip install -r requirements.txt` again
   - Make sure virtual environment is activated

2. **Dataset not found:**
   - Verify the path in Cell 4 matches your dataset location
   - Ensure `data.yaml` exists in that directory

3. **CUDA/GPU errors:**
   - Install CPU version of PyTorch (see Option B, step 3)
   - Training will be slower but will work

### Arduino Issues:

1. **Compilation errors:**
   - Make sure you're using Arduino IDE 1.8+ or 2.0+
   - Check that all code is copied correctly

2. **No sensor readings:**
   - Verify wiring connections
   - Check Serial Monitor baud rate (9600)
   - Ensure sensors are powered (5V and GND)

3. **LEDs not working:**
   - Verify LED polarity (long leg = positive)
   - Check resistor connections
   - Test LEDs individually

---

## Project Structure

```
smart_traffic_management/
├── Untitled0.ipynb          # YOLO training and SDN simulation notebook
├── arduino_code.ino         # Arduino code for IoT simulation
├── wokwi_code              # Arduino code (documentation format)
├── requirements.txt        # Python dependencies
├── RUN.md                  # This file
└── README.md              # Project overview
```

---

## Next Steps

After running both components:

1. **Train your YOLO model** with your emergency vehicle dataset
2. **Test the SDN controller** logic with different scenarios
3. **Combine both systems** - use YOLO detections to trigger traffic light changes
4. **Extend the system** - add more nodes, improve distance calculations, etc.

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the README.md for project details
- Ensure all dependencies are installed correctly

Happy coding! 🚦🚑🚨

