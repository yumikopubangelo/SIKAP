#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>
#include "config.h"

// Pin wiring RFID RC522 ke NodeMCU ESP8266
// VCC  -> 3.3V
// RST  -> D3 / GPIO0
// GND  -> GND
// MISO -> D6 / GPIO12
// MOSI -> D7 / GPIO13
// SCK  -> D5 / GPIO14
// SDA  -> D4 / GPIO2
#define RST_PIN 0
#define SS_PIN  2

MFRC522 mfrc522(SS_PIN, RST_PIN);

unsigned long previousMillis = 0;
const long pingInterval = 60000; // 60 detik
unsigned long lastRfidIdleMillis = 0;
const long rfidIdleLogInterval = 3000; // 3 detik

String buatPingUrl() {
  String pingUrl = String(API_ENDPOINT);

  if (pingUrl.endsWith("/")) {
    pingUrl.remove(pingUrl.length() - 1);
  }

  int apiAbsensiIndex = pingUrl.indexOf("/api/v1/absensi");
  if (apiAbsensiIndex >= 0) {
    return pingUrl.substring(0, apiAbsensiIndex) + "/api/v1/perangkat/ping";
  }

  int absensiIndex = pingUrl.lastIndexOf("/absensi");
  if (absensiIndex >= 0) {
    return pingUrl.substring(0, absensiIndex) + "/api/v1/perangkat/ping";
  }

  return pingUrl + "/api/v1/perangkat/ping";
}

String buatHealthUrl() {
  String healthUrl = String(API_ENDPOINT);

  if (healthUrl.endsWith("/")) {
    healthUrl.remove(healthUrl.length() - 1);
  }

  int apiAbsensiIndex = healthUrl.indexOf("/api/v1/absensi");
  if (apiAbsensiIndex >= 0) {
    return healthUrl.substring(0, apiAbsensiIndex) + "/health";
  }

  int absensiIndex = healthUrl.lastIndexOf("/absensi");
  if (absensiIndex >= 0) {
    return healthUrl.substring(0, absensiIndex) + "/health";
  }

  return healthUrl + "/health";
}

void tampilkanInfoWifi() {
  Serial.print("IP ESP8266: ");
  Serial.println(WiFi.localIP());
  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());
  Serial.print("Subnet: ");
  Serial.println(WiFi.subnetMask());
  Serial.print("RSSI: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

void cekKoneksiBackend() {
  WiFiClient client;
  HTTPClient http;
  String healthUrl = buatHealthUrl();

  Serial.print("[CEK] Tes koneksi backend: ");
  Serial.println(healthUrl);

  http.begin(client, healthUrl);
  int httpCode = http.GET();

  if (httpCode > 0) {
    Serial.print("[CEK] Backend merespon HTTP ");
    Serial.println(httpCode);
  } else {
    Serial.printf("[CEK] Backend tidak bisa dijangkau: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

void cekReaderRfid() {
  byte version = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);

  Serial.print("[RFID] VersionReg RC522: 0x");
  if (version < 0x10) {
    Serial.print("0");
  }
  Serial.println(version, HEX);

  if (version == 0x00 || version == 0xFF) {
    Serial.println("[RFID] RC522 tidak terbaca. Cek VCC 3.3V, GND, SDA/SS D4, SCK D5, MOSI D7, MISO D6, RST D3.");
  } else {
    Serial.println("[RFID] RC522 terdeteksi. Tempelkan kartu ke reader.");
  }

  mfrc522.PCD_AntennaOn();
}

void tampilkanStatusRfidIdle() {
  byte version = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);

  Serial.print("[RFID] Menunggu kartu... VersionReg=0x");
  if (version < 0x10) {
    Serial.print("0");
  }
  Serial.println(version, HEX);
}

void setup() {
  Serial.begin(115200);
  pinMode(SS_PIN, OUTPUT);
  digitalWrite(SS_PIN, HIGH);
  SPI.begin();
  mfrc522.PCD_Init();
  cekReaderRfid();

  Serial.println("\n\nMemulai Perangkat IoT SIKAP...");
  Serial.print("Menghubungkan ke Wi-Fi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 20) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  if(WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[SUKSES] Terhubung ke Jaringan!");
    tampilkanInfoWifi();
    cekKoneksiBackend();
  } else {
    Serial.println("\n[GAGAL] Tidak dapat terhubung ke Wi-Fi. Restarting...");
    ESP.restart();
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[ERROR] Koneksi terputus. Mencoba reconnect...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(5000);
    return;
  }

  // Rutinitas Ping Heartbeat ke Backend
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= pingInterval) {
    previousMillis = currentMillis;
    kirimPingStatus();
  }

  // Cek apakah ada kartu baru yang mendekati reader
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    if (currentMillis - lastRfidIdleMillis >= rfidIdleLogInterval) {
      lastRfidIdleMillis = currentMillis;
      tampilkanStatusRfidIdle();
    }
    return;
  }

  Serial.println("[RFID] Kartu terdeteksi, membaca UID...");

  // Baca informasi serial pada kartu
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    Serial.println("[RFID] Kartu terdeteksi, tapi UID gagal dibaca. Coba tempel ulang lebih dekat.");
    return;
  }

  // Ambil UID (Unique ID) dari Kartu
  String uidCard = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uidCard += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    uidCard += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidCard.toUpperCase();

  Serial.print("Kartu RFID Terdeteksi! UID: ");
  Serial.println(uidCard);

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  mfrc522.PCD_AntennaOff();
  delay(50);

  // Kirim ke API SIKAP
  kirimDataAbsensi(uidCard);

  mfrc522.PCD_AntennaOn();

  // Jeda agar tidak terjadi multiple-tap beruntun (spam)
  delay(2000);
}

void kirimDataAbsensi(String uid) {
  WiFiClient client;
  HTTPClient http;

  Serial.print("[WIFI] Status sebelum POST: ");
  Serial.println(WiFi.status());
  Serial.print("[WIFI] RSSI sebelum POST: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  Serial.print("Menembak API: ");
  Serial.println(API_ENDPOINT);

  client.setNoDelay(true);
  http.begin(client, API_ENDPOINT);
  http.setReuse(false);
  http.setTimeout(15000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Connection", "close");

  // Private Key Authentication untuk layer IoT -> Web Server
  // Backend akan mengecek X-Device-Id dan X-Api-Key ini untuk validasi asal usul alat
  http.addHeader("X-Device-Id", DEVICE_ID);
  http.addHeader("X-Api-Key", API_KEY);

  // Generate payload JSON pakai ArduinoJson library
  StaticJsonDocument<200> doc;
  doc["uid_card"] = uid;
  doc["device_id"] = DEVICE_ID;
  
  String requestBody;
  serializeJson(doc, requestBody);
  Serial.print("Payload: ");
  Serial.println(requestBody);

  int httpCode = http.POST(requestBody);

  if (httpCode > 0) {
    String payloadResponse = http.getString();
    Serial.print("Respon HTTP Code: ");
    Serial.println(httpCode);
    Serial.println("Isi Balasan: " + payloadResponse);

    if (httpCode == 201 || httpCode == 200) {
      Serial.println("[SUKSES] Tap berhasil dikenali dan dicatat.");
    } else {
      Serial.println("[ERROR] Tap ditolak server. Cek kartu, jadwal, atau konfigurasi backend.");
    }
  } else {
    // API mati / Timed out
    Serial.printf("[HTTP] POST... gagal, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// ============== RUTINITAS PING ==============

void kirimPingStatus() {
  WiFiClient client;
  HTTPClient http;

  String pingUrl = buatPingUrl();
  Serial.print("\n[PING] Mengirim heartbeat ke: ");
  Serial.println(pingUrl);

  http.begin(client, pingUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Id", DEVICE_ID);
  http.addHeader("X-Api-Key", API_KEY);

  StaticJsonDocument<100> doc;
  doc["status"] = "online";
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  if (httpCode > 0) {
    if (httpCode == 200 || httpCode == 201) {
      Serial.println("[PING] Sukses dicatat oleh Server.");
    } else {
      Serial.printf("[PING] Berhasil nembak tapi server membalas: %d\n", httpCode);
    }
  } else {
    Serial.printf("[PING] Gagal, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
