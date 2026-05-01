import serial
import numpy as np
import wave

PORT = "COM3"        # change this
BAUD = 921600
SECONDS = 5
SAMPLE_RATE = 8000

ser = serial.Serial(PORT, BAUD)

num_samples = SAMPLE_RATE * SECONDS
data = []

print("Recording...")

while len(data) < num_samples:
    raw = ser.read(2)
    value = int.from_bytes(raw, byteorder='little')
    data.append(value)

print("Done.")

ser.close()

audio = np.array(data, dtype=np.uint16)

# convert unsigned ADC → signed audio centered at zero
audio = audio.astype(np.int16) - 2048
audio = audio << 4  # expand to 16-bit range

with wave.open("recording.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    f.writeframes(audio.tobytes())

print("Saved recording.wav")