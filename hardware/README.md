# Hardware SIKAP - NodeMCU ESP8266 + RFID RC522

Folder ini berisi sketch Arduino untuk perangkat absensi RFID SIKAP.

## Wiring RFID RC522 ke NodeMCU ESP8266

| Pin RFID RC522 | Pin NodeMCU ESP8266 |
| --- | --- |
| VCC | 3.3V |
| RST | D3 / GPIO0 |
| GND | GND |
| MISO | D6 / GPIO12 |
| MOSI | D7 / GPIO13 |
| SCK | D5 / GPIO14 |
| SDA / SS | D4 / GPIO2 |

Catatan: RC522 wajib memakai 3.3V, jangan sambungkan VCC ke 5V.

## Sketch

Kode utama ada di:

```text
hardware/esp8266_rfid/esp8266_rfid.ino
```

Sketch ini hanya memakai RFID RC522 dan koneksi Wi-Fi. Tidak ada kode buzzer atau LED.

## Library Arduino yang dibutuhkan

- ESP8266 board package
- MFRC522
- ArduinoJson

## Konfigurasi

1. Salin `hardware/esp8266_rfid/config.h.example` menjadi `hardware/esp8266_rfid/config.h`.
2. Isi `WIFI_SSID`, `WIFI_PASSWORD`, `API_ENDPOINT`, `DEVICE_ID`, dan `API_KEY`.
3. Upload `esp8266_rfid.ino` ke board NodeMCU ESP8266.
