# Panduan Operasional SIKAP

Dokumen ini ditujukan untuk admin sekolah, operator sistem, dan guru piket yang menjalankan SIKAP setiap hari.

## 1. Tujuan Operasional

Panduan ini membantu memastikan:

- Layanan web dan monitoring aktif.
- Jadwal sholat benar sebelum sesi dimulai.
- Perangkat RFID terhubung ke server.
- Akun pengguna terkelola rapi.
- Laporan dan data harian dapat diambil tanpa kebingungan.

## 2. Checklist Harian Singkat

Lakukan pengecekan ini sebelum jam operasional:

1. Pastikan frontend dan backend dapat diakses.
2. Pastikan database aktif.
3. Login sebagai `admin` atau `guru_piket`.
4. Cek jumlah perangkat online di dashboard.
5. Periksa `Waktu Sholat` bila ada perubahan jadwal sekolah.
6. Pastikan guru piket mengetahui prosedur fallback `Input Absensi Manual`.
7. Jika memakai monitoring, buka halaman `Monitoring Sistem` dan cek panel Grafana.

## 3. SOP Admin

### 3.1 Kelola Akun Pengguna

Halaman: `Kelola Akun`

Fitur yang tersedia:

- Cari user berdasarkan nama, username, atau email.
- Filter berdasarkan role.
- Tambah user baru.
- Edit user.
- Hapus user tertentu.

Aturan penting dari backend:

- Admin tidak bisa menghapus akun miliknya sendiri.
- User yang sudah terhubung ke data siswa tidak bisa dihapus dari menu biasa.
- User yang sudah terhubung ke data siswa tidak bisa diubah ke role selain `siswa`.

### 3.2 Menambah Akun Non-Siswa

Langkah:

1. Buka `Kelola Akun`.
2. Klik `Tambah User`.
3. Isi username, nama lengkap, email, nomor telepon, role, password, dan konfirmasi password.
4. Klik `Buat User`.

### 3.3 Menambah Akun Siswa

Langkah di UI:

1. Pilih role `Siswa`.
2. Isi NISN 10 digit.
3. Klik `Validasi NISN`.
4. Pastikan panel preview menunjukkan siswa yang benar.
5. Lengkapi username, nama lengkap, password, dan data akun lain.
6. Klik `Buat User`.

Catatan penting:

- Backend mewajibkan akun siswa terhubung ke data siswa yang valid.
- Jika data siswa belum memiliki `id_card`, pembuatan akun bisa gagal karena backend menunggu UID RFID yang sudah dikonfirmasi.
- Flow konfirmasi UID RFID sudah ada di backend, tetapi belum tersedia penuh di UI frontend saat ini.

### 3.4 Mengubah Akun

Langkah:

1. Cari user di daftar.
2. Klik `Edit`.
3. Ubah field yang diperlukan.
4. Kosongkan password bila tidak ingin mengganti password.
5. Klik `Simpan Perubahan`.

### 3.5 Menghapus Akun

Sebelum menghapus:

- Pastikan akun yang dihapus bukan akun sendiri.
- Pastikan akun tersebut tidak sedang terhubung ke entitas siswa.

Jika akun adalah akun siswa yang sudah terhubung, pendekatan yang lebih aman adalah menonaktifkan pemakaian akun secara administratif di luar flow hapus sederhana, atau menyesuaikan data relasinya melalui pengembangan backend lanjutan.

## 4. SOP Waktu Sholat

Halaman: `Waktu Sholat`

Halaman ini dipakai untuk:

- Mengubah `waktu_adzan`
- Mengubah `waktu_iqamah`
- Mengubah `waktu_selesai`

Dampak perubahan:

- Mempengaruhi logika sesi aktif pada backend.
- Mempengaruhi interpretasi absensi yang terkait sesi sholat.
- Mempengaruhi konteks operasional guru piket saat input manual.

Langkah:

1. Login sebagai admin.
2. Buka `Waktu Sholat`.
3. Ubah jam sesuai kebutuhan sekolah.
4. Klik `Simpan Waktu` pada kartu sholat yang diubah.

Saran operasional:

- Hindari mengubah jadwal saat sesi sholat sedang berlangsung kecuali sangat diperlukan.
- Setelah perubahan penting, minta guru piket refresh dashboard.

## 5. SOP Guru Piket

### 5.1 Saat Sesi Berlangsung

- Pantau dashboard guru piket untuk melihat tap masuk dan perangkat online.
- Jika kartu siswa gagal terbaca, gunakan `Input Absensi Manual`.
- Simpan keterangan bila absensi dimasukkan secara manual.

### 5.2 Input Absensi Manual

Field yang wajib diperhatikan:

- `NISN`
- `Tanggal`
- `Waktu Sholat`
- `Status`

Status yang tersedia:

- `tepat_waktu`
- `terlambat`
- `alpha`
- `izin`
- `sakit`
- `haid`

Tips:

- Selalu validasi NISN terlebih dahulu.
- Gunakan keterangan yang spesifik, misalnya `kartu tertinggal`, `izin kegiatan sekolah`, atau `konfirmasi guru piket`.
- Bila sistem menolak simpan, cek kemungkinan sudah ada absensi untuk sesi yang sama.

## 6. SOP Kepala Sekolah dan Wali Kelas

### Kepala Sekolah

Gunakan:

- Dashboard untuk melihat ringkasan sekolah hari ini.
- `Data Sekolah` untuk performa kelas.
- `Laporan` untuk unduh rekap sekolah.
- `Monitoring Sistem` untuk validasi layanan saat ada masalah.

### Wali Kelas

Gunakan:

- Dashboard wali kelas untuk melihat performa siswa di kelas binaan.
- `Laporan per kelas` untuk rekap periodik.
- `Laporan per siswa` untuk follow up individual.

## 7. Monitoring dan Pengecekan Layanan

Halaman: `Monitoring Sistem`

Akses:

- `admin`
- `kepsek`

Isi utama:

- Status sistem
- Request rate
- Response time
- HTTP status code
- User per role
- Surat peringatan
- Notifikasi

Jika panel tidak tampil:

1. Pastikan Grafana aktif.
2. Pastikan backend `/metrics` aktif.
3. Bila memakai Docker, jalankan semua service monitoring.

## 8. Operasional Perangkat RFID

### 8.1 Kebutuhan Dasar

Perangkat ESP8266 perlu mengetahui:

- `DEVICE_ID`
- `API_KEY`
- `API_ENDPOINT`
- `WIFI_SSID`
- `WIFI_PASSWORD`

Konfigurasi contoh ada di:

- `hardware/esp8266_rfid/config.h.example`

### 8.2 Heartbeat Perangkat

Backend menyediakan endpoint ping perangkat:

- `POST /api/v1/perangkat/ping`

Header yang dipakai:

- `X-Device-Id`
- `X-Api-Key`

Tujuan:

- Mengubah `last_ping`
- Menandai perangkat sebagai `online`

### 8.3 Absensi RFID Normal

Untuk absensi biasa, perangkat mengirim data ke:

- `POST /api/v1/absensi`

Payload minimum:

- `device_id`
- `uid_card`

Dalam mode keamanan bertanda tangan, perangkat juga harus mengirim header signature yang sesuai konfigurasi backend.

## 9. Flow Konfirmasi UID RFID via API

Flow ini penting bila admin perlu menyiapkan UID kartu siswa, tetapi frontend belum menyediakan layar khususnya.

### 9.1 Mulai sesi scan UID

```bash
curl -X POST http://localhost:5000/api/v1/users/rfid-capture/session \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1}'
```

`student_id` boleh dikosongkan bila hanya ingin membaca UID kartu tanpa langsung mengaitkan ke siswa tertentu.

### 9.2 Tempelkan kartu yang sama dua kali

Dalam mode development tanpa signature (`RFID_REQUIRE_SIGNATURE=0`), contoh capture dapat memakai:

```bash
curl -X POST http://localhost:5000/api/v1/rfid/capture \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-device-key-001" \
  -d '{"device_id":"ESP-RFID-01","uid_card":"CARD-999","timestamp":"2026-04-20T08:00:00Z"}'
```

Ulangi request/tap kedua dengan UID yang sama sampai status sesi menjadi `confirmed`.

### 9.3 Cek status sesi

```bash
curl http://localhost:5000/api/v1/users/rfid-capture/session \
  -H "Authorization: Bearer <admin_token>"
```

Yang perlu diperhatikan:

- `confirmed_uid`
- `status`
- `card_owner`
- `expires_in_seconds`

### 9.4 Reset atau tutup sesi

```bash
curl -X POST http://localhost:5000/api/v1/users/rfid-capture/session/reset \
  -H "Authorization: Bearer <admin_token>"
```

```bash
curl -X DELETE http://localhost:5000/api/v1/users/rfid-capture/session \
  -H "Authorization: Bearer <admin_token>"
```

### 9.5 Simpan UID ke akun siswa

Backend menerima field `id_card` saat create atau update user siswa. Artinya, bila dibutuhkan, admin dapat memakai API client untuk mengirim `nisn` dan `id_card` yang sudah dikonfirmasi.

## 10. Troubleshooting Operasional

### Perangkat terlihat offline

- Cek Wi-Fi sekolah.
- Cek `DEVICE_ID` dan `API_KEY`.
- Pastikan endpoint backend bisa dijangkau dari jaringan perangkat.
- Cek `last_ping` dan panel monitoring.

### Input manual gagal disimpan

- Pastikan NISN valid.
- Pastikan siswa belum punya absensi pada sesi yang sama.
- Pastikan guru piket masih login.

### Akun orang tua tidak melihat data anak

- Samakan `no_telp` user orang tua dengan `no_telp_ortu` pada data siswa.

### Pembuatan akun siswa gagal

- Pastikan NISN memang ada di data siswa.
- Pastikan data siswa belum terhubung ke akun lain.
- Pastikan siswa sudah memiliki `id_card`, atau lakukan flow konfirmasi UID RFID terlebih dahulu.
