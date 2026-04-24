# How to use
Go to Vscode or other text editor, open desired folder

### Step 1: Clone the Repository

```bash
git clone https://github.com/Roshang06/SPARCS.git
cd sparcs
```

### Step 2: Install Python (if necessary)

If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

Verify your installation:
```bash
python --version
```

### Step 3: Create a Virtual Environment

Creating a virtual environment is recommended to keep your project dependencies isolated. Go to **command prompt**:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Required Packages

Install all required dependencies using pip:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `pyserial` - Serial communication with ESP32
- `numpy` - Audio signal processing
- `pyaudio` - Real-time audio playback and capture

If you prefer to install manually:
```bash
pip install pyserial numpy pyaudio
```
Arduino scripts are found in the ArduinoFiles Folder
