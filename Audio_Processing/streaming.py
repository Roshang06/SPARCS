import serial
import numpy as np
import pyaudio

# --- CONFIGURATION ---
PORT = "COM4"  # Change to your ESP32 Bluetooth port
BAUD = 921600
SAMPLE_RATE = 8000
CHUNK_SIZE = 256  # Number of samples to process at once

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

        while True:
            # Read a chunk of data (2 bytes per sample)
            raw_data = ser.read(CHUNK_SIZE * 2)
            
            if len(raw_data) > 0:
                # Convert bytes to numpy array (uint16)
                audio_data = np.frombuffer(raw_data, dtype=np.uint16)
                
                # Convert 12-bit unsigned to 16-bit signed (same logic as before)
                # Subtract midpoint and shift to fill 16-bit range
                processed_audio = (audio_data.astype(np.int16) - 2048) << 4
                
                # Write to the audio output stream
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