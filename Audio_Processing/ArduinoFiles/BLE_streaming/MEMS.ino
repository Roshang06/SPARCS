#include "BluetoothSerial.h"
#include "driver/i2s.h"

// Check if Bluetooth is properly enabled
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to enable it
#endif

BluetoothSerial SerialBT;

// --- I2S Configuration ---
#define I2S_PORT        I2S_NUM_0
#define SAMPLE_RATE     8000      // Great for standard stethoscopes, though 16000Hz is also common
#define BLOCK_SIZE      64        // Number of samples per chunk

// Pin definitions (Adjust these based on your actual ESP32 wiring)
#define I2S_WS_PIN      25        // Word Select (LRCLK)
#define I2S_BCK_PIN     26        // Bit Clock (BCLK)
#define I2S_SD_PIN      33        // Serial Data (DOUT from mic)

// Buffer to store 32-bit or 16-bit samples. 
// Most MEMS mics output 24-bit data padded inside a 32-bit integer.
int32_t i2sBuffer[BLOCK_SIZE]; 
int16_t transmitBuffer[BLOCK_SIZE]; // Downsampled to 16-bit to match your original format size

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX), // Master receiver
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,        // MEMS mics usually send 24/32 bits
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,         // Single mic (pull SD pin to GND or VCC accordingly)
    .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,            // Interrupt level 1
    .dma_buf_count = 4,                                  // Number of DMA buffers
    .dma_buf_len = BLOCK_SIZE                            // Size of each DMA buffer
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD_PIN
  };

  // Install and start I2S driver
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  i2s_start(I2S_PORT);
}

void setup() {
  Serial.begin(115200);
  
  // Initialize Bluetooth
  SerialBT.begin("ESP32_Stethoscope_Link"); 
  Serial.println("Bluetooth Started. Pair your device now.");

  // Initialize I2S MEMS Mic
  setupI2S();
  Serial.println("I2S Microphone initialized.");
}

void loop() {
  size_t bytesRead = 0;

  // i2s_read blocks automatically until the requested buffer size is full.
  // No micros() timing math needed! DMA handles the timing perfectly.
  esp_err_t result = i2s_read(I2S_PORT, &i2sBuffer, sizeof(i2sBuffer), &bytesRead, portMAX_DELAY);
  
  if (result == ESP_OK && bytesRead > 0) {
    int samplesRead = bytesRead / sizeof(int32_t);

    // Process and downsample 32-bit data to 16-bit data for transmission
    for (int i = 0; i < samplesRead; i++) {
      // MEMS data is often high-passed/signed. Shift it down to 16-bit depth.
      // (Depending on your exact mic, you might need to adjust the bit shift >> 14 or >> 16)
      transmitBuffer[i] = (int16_t)(i2sBuffer[i] >> 14); 
    }

    // Transmit via Bluetooth if a client is connected
    if (SerialBT.connected()) {
      SerialBT.write((uint8_t*)transmitBuffer, samplesRead * sizeof(int16_t));
    }
  }
}