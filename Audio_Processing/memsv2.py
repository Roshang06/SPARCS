#!/usr/bin/env python3
"""
1. Pair the laptop with "ESP32_Audio_Link" in your OS Bluetooth settings.
2. Find the serial port the OS created for it:
     Windows: a COM port (Device Manager -> Ports, or Bluetooth settings ->
              "More Bluetooth options" -> COM Ports, the *Outgoing* one)
NOT TESTED:
    macOS:   /dev/cu.ESP32_Audio_Link
    Linux:   sudo rfcomm connect /dev/rfcomm0 <ESP32 MAC>   (then /dev/rfcomm0)
3. Run:
     python bt_audio_player.py --list
     python bt_audio_player.py COM5 --delay 1.5
"""

import argparse
import sys
import threading
import time

import numpy as np
import serial
import serial.tools.list_ports
import sounddevice as sd

DEFAULT_RATE = 16000  # must match SAMPLE_RATE in the ESP32 sketch
BYTES_PER_SAMPLE = 2


class DelayedPlayer:
    def __init__(self, delay_s: float, gain: float, remove_dc: bool, rate: int):
        self.rate = rate
        self.delay_bytes = int(delay_s * rate) * BYTES_PER_SAMPLE
        # Cap the buffer so clock drift between ESP32 and laptop can't
        # grow the delay forever (drop oldest audio past this point).
        self.max_bytes = self.delay_bytes + rate * BYTES_PER_SAMPLE  # +1 s slack
        self.gain = gain
        self.remove_dc = remove_dc

        self.buf = bytearray()
        self.lock = threading.Lock()
        self.playing = False      # False = still (re)filling the delay buffer
        self.dc = 0.0
        self.underruns = 0
        self.stop_flag = threading.Event()

    # ---- producer: called from the serial thread ----
    def feed(self, data: bytes):
        with self.lock:
            self.buf.extend(data)
            if len(self.buf) > self.max_bytes:
                # drop oldest, keep sample alignment
                excess = len(self.buf) - self.max_bytes
                excess -= excess % BYTES_PER_SAMPLE
                del self.buf[:excess]

    # ---- consumer: called from the audio thread ----
    def callback(self, outdata, frames, time_info, status):
        need = frames * BYTES_PER_SAMPLE
        with self.lock:
            if not self.playing and len(self.buf) >= self.delay_bytes:
                self.playing = True
            if self.playing and len(self.buf) >= need:
                chunk = bytes(self.buf[:need])
                del self.buf[:need]
            else:
                if self.playing:
                    # ran dry -> go silent and rebuild the delay cushion
                    self.playing = False
                    self.underruns += 1
                chunk = None

        if chunk is None:
            outdata[:] = 0
            return

        samples = np.frombuffer(chunk, dtype="<i2").astype(np.float32)

        if self.remove_dc:
            # slow-moving average of the signal = DC offset from the mic
            self.dc = 0.999 * self.dc + 0.001 * float(samples.mean())
            samples -= self.dc

        samples *= self.gain
        np.clip(samples, -32768, 32767, out=samples)
        outdata[:, 0] = samples.astype(np.int16)

    def buffered_seconds(self):
        with self.lock:
            return len(self.buf) / (self.rate * BYTES_PER_SAMPLE)


def serial_reader(ser: serial.Serial, player: DelayedPlayer):
    carry = b""  # keeps 16-bit sample alignment if a read ends mid-sample
    while not player.stop_flag.is_set():
        try:
            data = ser.read(max(1, ser.in_waiting))
        except serial.SerialException as e:
            print(f"\nSerial error: {e}")
            player.stop_flag.set()
            return
        if not data:
            continue
        data = carry + data
        usable = len(data) - (len(data) % BYTES_PER_SAMPLE)
        carry = data[usable:]
        if usable:
            player.feed(data[:usable])


def main():
    ap = argparse.ArgumentParser(description="Play ESP32 Bluetooth audio with a delay")
    ap.add_argument("port", nargs="?", help="serial port (e.g. COM5, /dev/rfcomm0)")
    ap.add_argument("--list", action="store_true", help="list serial ports and exit")
    ap.add_argument("--delay", type=float, default=1.0, help="playback delay in seconds (default 1.0)")
    ap.add_argument("--gain", type=float, default=1.0,
                    help="volume multiplier (default 1.0; ESP32 already applies >>14)")
    ap.add_argument("--rate", type=int, default=DEFAULT_RATE,
                    help=f"sample rate, must match the ESP32 (default {DEFAULT_RATE})")
    ap.add_argument("--no-dc-filter", action="store_true", help="disable DC offset removal")
    args = ap.parse_args()

    if args.list:
        for p in serial.tools.list_ports.comports():
            print(f"{p.device}\t{p.description}")
        return
    if not args.port:
        ap.error("port is required (use --list to see options)")

    ser = serial.Serial(args.port, baudrate=115200, timeout=0.1)  # baud is ignored by SPP
    player = DelayedPlayer(args.delay, args.gain, remove_dc=not args.no_dc_filter, rate=args.rate)

    t = threading.Thread(target=serial_reader, args=(ser, player), daemon=True)
    t.start()

    print(f"Connected to {args.port}. Buffering {args.delay:.1f}s before playback... Ctrl+C to quit.")
    try:
        with sd.OutputStream(samplerate=args.rate, channels=1, dtype="int16",
                             blocksize=512, callback=player.callback):
            while not player.stop_flag.is_set():
                state = "playing " if player.playing else "buffering"
                print(f"\r[{state}] buffered: {player.buffered_seconds():4.2f}s  "
                      f"underruns: {player.underruns}   ", end="", flush=True)
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        player.stop_flag.set()
        ser.close()
        print("\nStopped.")


if __name__ == "__main__":
    sys.exit(main())