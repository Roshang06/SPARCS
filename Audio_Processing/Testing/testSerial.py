import serial

ser = serial.Serial("COM3", 921600)

for i in range(20):
    raw = ser.read(2)
    print(int.from_bytes(raw, "little"))