import serial
import numpy as np
import wave
import time

# --- CONFIGURATION ---
PORT = "COM4"  # Change this to your ESP32 Bluetooth COM Port
BAUD = 921600  # Note: Bluetooth ignores this, but pyserial requires it
SAMPLE_RATE = 8000
DURATION = 5   # Seconds to record
OUTPUT_FILE = "bluetooth_recording.wav"

def record_bt_audio():
    num_samples = SAMPLE_RATE * DURATION
    data = []

    try:
        print(f"Connecting to {PORT}...")
        ser = serial.Serial(PORT, BAUD, timeout=2)
        
        # Clear the buffer to remove any stale data from before we started the script
        ser.flushInput()
        
        print(f"Recording {DURATION} seconds of audio...")
        
        while len(data) < num_samples:
            # Read 2 bytes (one 16-bit sample)
            raw = ser.read(2)
            
            if len(raw) == 2:
                # Convert bytes to unsigned 16-bit integer
                value = int.from_bytes(raw, byteorder='little')
                data.append(value)
            else:
                # This handles timeouts or partial reads
                print("Warning: Dropped sample or timeout.")
                break

        print("Recording finished. Processing...")
        ser.close()

        # --- SIGNAL PROCESSING ---
        audio = np.array(data, dtype=np.uint16)

        # 1. ESP32 ADC is 12-bit (0-4095). 
        # Center it around zero by subtracting the midpoint (2048)
        audio_signed = audio.astype(np.int16) - 2048
        
        # 2. Scale 12-bit to 16-bit range 
        # (Left shift by 4: 2^12 * 2^4 = 2^16)
        audio_signed = audio_signed << 4

        # --- SAVE TO WAV ---
        with wave.open(OUTPUT_FILE, "wb") as f:
            f.setnchannels(1)      # Mono
            f.setsampwidth(2)      # 16-bit (2 bytes per sample)
            f.setframerate(SAMPLE_RATE)
            f.writeframes(audio_signed.tobytes())

        print(f"Success! Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    record_bt_audio()