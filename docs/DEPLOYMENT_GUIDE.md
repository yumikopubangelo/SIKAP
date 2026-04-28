# Panduan Deployment SIKAP

Dokumen ini menjelaskan cara menjalankan SIKAP secara lokal, dengan Docker Compose, dan langkah pengecekan awal setelah layanan aktif.

## 1. Arsitektur Singkat

Stack utama pada repo ini:

- Frontend React + Vite
- Backend Flask
- MySQL
- Mosquitto untuk MQTT
- Redis
- Prometheus
- Grafana
- Elasticsearch
- Kibana opsional
- phpMyAdmin opsional

## 2. Port dan Service Default

| Service | Port | Keterangan |
| --- | --- | --- |
| Frontend | `8081` | UI utama saat memakai Docker |
| Frontend dev | `5173` | UI saat menjalankan Vite manual |
| Backend | `5000` | API utama |
| MySQL | `3306` | Database |
| phpMyAdmin | `8080` | Aktif bila profile `devtools` dipakai |
| MQTT | `1883` | Broker MQTT |
| MQTT WebSocket | `9001` | Dipakai frontend untuk real-time |
| Redis | `6379` | Cache atau queue pendukung |
| Prometheus | `9090` | Metrics collector |
| Grafana | `3000` | Dashboard monitoring |
| Elasticsearch | `9200` | Analitik dan pencarian |
| Kibana | `5601` | Aktif bila profile `monitoring` dipakai |

## 3. Environment Variable Penting

Gunakan file root `.env` yang disalin dari `.env.example`.

Variabel yang wajib diperhatikan:

- `DB_ROOT_PASSWORD`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`
- `RFID_REQUIRE_SIGNATURE`
- `RFID_SIGNATURE_TOLERANCE_SECONDS`
- `RFID_PUBLIC_KEY_DIR`
- `GRAFANA_USER`
- `GRAFANA_PASSWORD`

Rekomendasi:

- Ganti semua secret bawaan sebelum dipakai di lingkungan selain demo lokal.
- Jangan commit file `.env`.

## 4. Opsi A: Docker Compose

Ini adalah cara paling cepat untuk menyalakan seluruh stack.

### 4.1 Langkah menjalankan

1. Salin file environment.

```bash
cp .env.example .env
```

2. Sesuaikan nilai penting di `.env`.

3. Jalankan semua service.

```bash
docker compose up -d --build
```

4. Jika perlu phpMyAdmin:

```bash
docker compose --profile devtools up -d
```

5. Jika perlu Kibana:

```bash
docker compose --profile monitoring up -d
```

### 4.2 Cek hasil startup

```bash
docker compose ps
```

Lalu buka:

- Frontend: `http://localhost:8081`
- Backend: `http://localhost:5000`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- phpMyAdmin: `http://localhost:8080` bila profile devtools aktif
- Kibana: `http://localhost:5601` bila profile monitoring aktif

### 4.3 Menghentikan layanan

```bash
docker compose down
```

Untuk menghapus volume data:

```bash
docker compose down -v
```

Perintah di atas akan menghapus data database, Redis, Grafana, Prometheus, dan volume lain yang tersimpan secara lokal.

## 5. Opsi B: Menjalankan Secara Manual

### 5.1 Persiapan Database

Buat database:

```bash
mysql -u root -p -e "CREATE DATABASE sikap_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Import schema dan data awal:

```bash
mysql -u root -p sikap_db < database/schema.sql
mysql -u root -p sikap_db < database/seed.sql
```

### 5.2 Menjalankan Backend

```bash
cd backend
python -m venv venv
```

Aktivasi environment:

Windows:

```powershell
venv\Scripts\activate
```

Linux atau macOS:

```bash
source venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Pastikan backend dapat membaca konfigurasi database dari root `.env` atau environment shell. Setelah itu jalankan:

```bash
python run.py
```

Backend akan aktif di `http://localhost:5000`.

### 5.3 Menjalankan Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server biasanya aktif di `http://localhost:5173`.

Jika frontend berjalan terpisah dari backend, pastikan `VITE_API_URL` dan `VITE_MQTT_WS_URL` sesuai.

### 5.4 Menjalankan Hardware

Konfigurasi contoh:

- `hardware/esp8266_rfid/config.h.example`

Langkah:

1. Salin menjadi `config.h`.
2. Isi `WIFI_SSID`, `WIFI_PASSWORD`, `API_ENDPOINT`, `DEVICE_ID`, dan `API_KEY`.
3. Upload sketch `esp8266_rfid.ino` ke NodeMCU ESP8266.

Contoh endpoint backend:

- `http://192.168.x.x:5000/api/v1/absensi`

## 6. Health Check Setelah Deploy

Lakukan pengecekan berikut.

### 6.1 Backend health endpoint

```bash
curl http://localhost:5000/health
```

Respons sehat minimal:

- `status: healthy`

### 6.2 Backend root endpoint

```bash
curl http://localhost:5000/
```

Respons ini berguna untuk memastikan service Flask benar-benar terangkat.

### 6.3 Metrics endpoint

```bash
curl http://localhost:5000/metrics
```

Jika exporter aktif, endpoint ini akan menampilkan metrik Prometheus.

### 6.4 Frontend

Buka frontend dan pastikan:

- halaman login muncul
- proses login berhasil
- dashboard termuat

### 6.5 Monitoring

Pastikan halaman monitoring memuat panel Grafana tanpa error iframe.

## 7. Akun Demo Seed

Jika memakai `database/seed.sql`, akun berikut tersedia:

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Kepala Sekolah | `kepsek` | `kepsek123` |
| Wali Kelas | `walikelas` | `wali123` |
| Guru Piket | `gurupiket` | `piket123` |
| Siswa | `siswa001` | `siswa123` |
| Orang Tua | `ortu001` | `ortu123` |

Ganti password default sebelum lingkungan dipakai pengguna nyata.

## 8. Public Key RFID

Jika signature RFID diaktifkan:

- simpan public key perangkat di `backend/keys/rfid_public`
- nama file harus sama dengan `device_id`, misalnya `ESP-RFID-01.pem`

Header yang relevan untuk mode signature:

- `X-API-Key`
- `X-RFID-Signature`
- `X-RFID-Signature-Timestamp`

Jika `RFID_REQUIRE_SIGNATURE=0`, backend masih bisa menerima mode development berbasis `X-API-Key`.

## 9. Troubleshooting Deployment

### Backend hidup tapi frontend gagal login

- Pastikan `VITE_API_URL` mengarah ke backend yang benar.
- Pastikan CORS mengizinkan origin frontend.
- Pastikan database dan backend memakai secret JWT yang konsisten.

### Dashboard monitoring kosong

- Pastikan Grafana aktif di `http://localhost:3000`.
- Pastikan Prometheus aktif.
- Pastikan backend `metrics` tidak error.

### Perangkat RFID gagal mengirim data

- Pastikan `DEVICE_ID` dan `API_KEY` sama dengan data di tabel `perangkat`.
- Pastikan perangkat dapat menjangkau backend melalui jaringan lokal.
- Bila mode signature aktif, pastikan public key perangkat tersedia di server.

### Error saat membuat akun siswa

- Pastikan data siswa ada di database.
- Pastikan NISN belum dipakai akun lain.
- Pastikan siswa sudah punya `id_card` atau lakukan flow konfirmasi UID RFID.

### Parent dashboard kosong

- Pastikan nomor telepon user orang tua sama dengan `no_telp_ortu` pada data siswa.

## 10. Checklist Serah Terima

Sebelum sistem dianggap siap dipakai, verifikasi:

1. Frontend bisa diakses.
2. Backend sehat.
3. Database berisi schema dan seed yang benar.
4. Akun demo bisa login.
5. Minimal satu perangkat RFID dapat ping dan tercatat online.
6. Halaman `Laporan` dapat generate file.
7. Halaman `Monitoring Sistem` dapat memuat Grafana.
