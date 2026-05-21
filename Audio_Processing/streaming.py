import serial
import numpy as np
import pyaudio

# --- CONFIGURATION ---
PORT = "COM4"  # Change to your ESP32 Bluetooth port
BAUD = 921600
SAMPLE_RATE = 8000
CHUNK_SIZE = 64  # Matches the BLOCK_SIZE from ESP32 code

# --- AUDIO SETUP ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE)

def stream_audio():
    try:
        print(f"Connecting to {PORT}...")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        ser.flushInput()
        print("Streaming live audio... Press Ctrl+C to stop.")

        bytes_to_read = CHUNK_SIZE * 2  # 2 bytes per 16-bit sample

        while True:
            # Read exactly one chunk of data
            raw_data = ser.read(bytes_to_read)
            
            # Check if we got a complete block of data
            if len(raw_data) == bytes_to_read:
                # 1. Convert bytes directly to signed 16-bit integers
                audio_data = np.frombuffer(raw_data, dtype=np.int16)
                
                # Write directly to the PyAudio output stream
                stream.write(audio_data.tobytes())
            else:
                # If a timeout or partial read happens, skip to maintain alignment
                continue

    except KeyboardInterrupt:
        print("\nStream stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing resources...")
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except:
            pass
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    stream_audio()