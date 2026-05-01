import serial
import numpy as np
import wave
import time
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
PORT = "COM4"  # Change this to your ESP32 Bluetooth COM Port
BAUD = 921600  # Note: Bluetooth ignores this, but pyserial requires it
SAMPLE_RATE = 8000
CHUNK_SIZE = 256
DURATION = 20   # Seconds to record
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
            raw_data = ser.read(CHUNK_SIZE * 2)
            
            if len(raw_data) > 0:
                # Convert bytes to numpy array (uint16)
                audio_data = np.frombuffer(raw_data, dtype=np.uint16)
                data.extend(audio_data.tolist())
            else:
                print("Warning: Timeout or no data received.")
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

        return audio_signed, SAMPLE_RATE

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audio_signal, fs = record_bt_audio()

    if audio_signal is not None:
        # Create a time axis in seconds
        time_axis = np.linspace(0, len(audio_signal) / fs, num=len(audio_signal))

        # --- PLOT PHONOCARDIOGRAM ---
        plt.figure(figsize=(15, 6))
        plt.plot(time_axis, audio_signal, color='#2c3e50', linewidth=0.5)
        
        # Formatting the PCG
        plt.title("Phonocardiogram (PCG) - Heart Sound Waveform", fontsize=14)
        plt.xlabel("Time (seconds)", fontsize=12)
        plt.ylabel("Amplitude (ADC Units)", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Zoom into a 3-second window to see individual heart beats (S1/S2)
        # You can remove this line to see the full 20 seconds
        #plt.xlim(2, 5) 
        
        plt.tight_layout()
        plt.show()



