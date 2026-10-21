import serial
import numpy as np
import pyaudio

# --- CONFIGURATION ---
PORT = "COM4"  # Change to your ESP32 Bluetooth outgoing COM port
BAUD = 921600  # Virtual COM port speed is ignored by BT, but kept for instantiation
SAMPLE_RATE = 8000
CHUNK_SIZE = 256  # Size of buffer PyAudio processes at once

# --- AUDIO SETUP ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,  # Standard 16-bit signed format matching ESP32 TX
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE)

def stream_audio():
    try:
        print(f"Connecting to {PORT}...")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        ser.flushInput()
        print("Streaming live digital audio... Press Ctrl+C to stop.")

        while True:
            # Each 16-bit sample is 2 bytes. Read a chunk's worth of data.
            raw_data = ser.read(CHUNK_SIZE * 2)   

            if len(raw_data) > 0:
                # Data arrives already formatted as 16-bit signed integers (int16)
                # No shifting or centering needed!
                processed_audio = np.frombuffer(raw_data, dtype=np.int16)   

                # Write directly to the sound card audio stream
                stream.write(processed_audio.tobytes())
                
    except KeyboardInterrupt:
        print("\nStream stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing resources...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    stream_audio()