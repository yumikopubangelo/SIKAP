# Audit Endpoint, Verifikasi RFID, dan Coverage SIKAP

Dokumen ini menjadi referensi praktis untuk tiga hal:

1. hasil audit endpoint aktual dari aplikasi;
2. cara verifikasi mode RFID dengan signature dan tanpa signature;
3. cara menambahkan bukti uji dan coverage report untuk laporan.

Audit ini disusun berdasarkan route aktual aplikasi per 28 April 2026.

## 1. Konvensi Final Route

Konvensi route final backend yang dipakai adalah:

- endpoint aplikasi memakai prefix `/api/v1/...`;
- endpoint utilitas sistem tetap memakai `/` dan `/health`;
- file statis tetap memakai `/static/...`.

Perubahan yang sudah dirapikan:

- notifikasi sekarang memakai `/api/v1/notifikasi`;
- heartbeat perangkat sekarang memakai `/api/v1/perangkat/ping`;
- route download laporan final adalah `/api/v1/laporan/download/<id_laporan>`.

## 2. Hasil Audit Endpoint Aktual

Berikut route yang benar-benar terdaftar pada `app.url_map`.

### 2.1 Endpoint Sistem

| Method | Route |
| --- | --- |
| `GET` | `/` |
| `GET` | `/health` |

### 2.2 Authentication

| Method | Route |
| --- | --- |
| `POST` | `/api/v1/auth/login` |
| `POST` | `/api/v1/auth/logout` |
| `GET` | `/api/v1/auth/me` |
| `POST` | `/api/v1/auth/register` |
| `GET` | `/api/v1/auth/student-candidates` |

### 2.3 Absensi

| Method | Route |
| --- | --- |
| `POST` | `/api/v1/absensi` |
| `GET` | `/api/v1/absensi` |
| `PUT` | `/api/v1/absensi/<int:absensi_id>` |
| `POST` | `/api/v1/absensi/manual` |

### 2.4 Dashboard

| Method | Route |
| --- | --- |
| `GET` | `/api/v1/dashboard` |

### 2.5 Rekapitulasi

| Method | Route |
| --- | --- |
| `GET` | `/api/v1/rekapitulasi/kelas/<int:id_kelas>` |
| `GET` | `/api/v1/rekapitulasi/siswa/<int:id_siswa>` |
| `GET` | `/api/v1/rekapitulasi/sekolah` |

### 2.6 Laporan

| Method | Route |
| --- | --- |
| `POST` | `/api/v1/laporan/generate` |
| `GET` | `/api/v1/laporan/download/<int:id_laporan>` |

### 2.7 Notifikasi

| Method | Route |
| --- | --- |
| `GET` | `/api/v1/notifikasi` |
| `POST` | `/api/v1/notifikasi/send` |
| `PUT` | `/api/v1/notifikasi/<int:id_notifikasi>/read` |
| `PUT` | `/api/v1/notifikasi/read-all` |

### 2.8 Users

| Method | Route |
| --- | --- |
| `GET` | `/api/v1/users` |
| `POST` | `/api/v1/users` |
| `GET` | `/api/v1/users/<int:user_id>` |
| `PUT` | `/api/v1/users/<int:user_id>` |
| `DELETE` | `/api/v1/users/<int:user_id>` |
| `POST` | `/api/v1/users/rfid-capture/session` |
| `GET` | `/api/v1/users/rfid-capture/session` |
| `DELETE` | `/api/v1/users/rfid-capture/session` |
| `POST` | `/api/v1/users/rfid-capture/session/reset` |

### 2.9 RFID dan Perangkat

| Method | Route |
| --- | --- |
| `POST` | `/api/v1/rfid/capture` |
| `POST` | `/api/v1/rfid/verify` |
| `POST` | `/api/v1/perangkat/ping` |

### 2.10 Data Master dan Operasional

| Method | Route |
| --- | --- |
| `GET` | `/api/v1/kelas` |
| `POST` | `/api/v1/kelas` |
| `GET` | `/api/v1/kelas/<int:kelas_id>` |
| `PUT` | `/api/v1/kelas/<int:kelas_id>` |
| `DELETE` | `/api/v1/kelas/<int:kelas_id>` |
| `GET` | `/api/v1/siswa` |
| `POST` | `/api/v1/siswa` |
| `GET` | `/api/v1/siswa/<int:siswa_id>` |
| `PUT` | `/api/v1/siswa/<int:siswa_id>` |
| `DELETE` | `/api/v1/siswa/<int:siswa_id>` |
| `POST` | `/api/v1/siswa/import-csv` |
| `GET` | `/api/v1/waktu-sholat` |
| `PUT` | `/api/v1/waktu-sholat/<int:waktu_id>` |
| `GET` | `/api/v1/school/` |
| `GET` | `/api/v1/izin` |
| `POST` | `/api/v1/izin` |
| `PUT` | `/api/v1/izin/<int:izin_id>/approve` |
| `GET` | `/api/v1/sengketa` |
| `POST` | `/api/v1/sengketa` |
| `PUT` | `/api/v1/sengketa/<int:sengketa_id>/resolve` |
| `GET` | `/api/v1/surat-peringatan` |
| `GET` | `/api/v1/surat-peringatan/<int:sp_id>` |
| `GET` | `/api/v1/jadwal-piket` |
| `POST` | `/api/v1/jadwal-piket` |
| `PUT` | `/api/v1/jadwal-piket/<int:jadwal_id>` |
| `DELETE` | `/api/v1/jadwal-piket/<int:jadwal_id>` |

## 3. Temuan Audit Endpoint

Temuan penting dari audit:

- dokumen lama masih menyebut beberapa endpoint yang tidak ada, seperti `POST /api/v1/auth/refresh`;
- dokumen lama masih menyebut `GET /api/v1/absensi/{id}` dan `DELETE /api/v1/absensi/{id}`, padahal route itu belum ada di implementasi saat ini;
- dokumen lama menyebut download laporan sebagai `/api/v1/laporan/{id}/download`, padahal implementasi aktual adalah `/api/v1/laporan/download/{id_laporan}`;
- dokumen lama menyebut notifikasi dengan variasi yang tidak sinkron; implementasi final sekarang adalah `/api/v1/notifikasi/...`;
- dokumen lama menyebut endpoint perangkat seperti `GET /api/v1/perangkat` dan `POST /api/v1/perangkat/test-connection/{id}`, padahal implementasi aktual yang ada saat ini hanya heartbeat `POST /api/v1/perangkat/ping`.

Kesimpulan audit:

- untuk laporan akhir, gunakan dokumen ini sebagai referensi endpoint aktual;
- `docs/design/API_ENDPOINTS_LIST.md` dan dokumen sejenis masih perlu penyelarasan penuh bila ingin dijadikan lampiran resmi API.

## 4. Cara Verifikasi RFID Tanpa Signature

Mode ini dipakai saat:

- `RFID_REQUIRE_SIGNATURE=0`;
- perangkat hanya divalidasi dengan `X-API-Key`.

### Langkah

1. Pastikan tabel `perangkat` memiliki data `device_id` dan `api_key`.
2. Pastikan backend aktif.
3. Kirim request ke endpoint absensi RFID.

Contoh:

```bash
curl -X POST http://localhost:5000/api/v1/absensi \
  -H "Content-Type: application/json" \
  -H "X-API-Key: device-secret" \
  -d "{\"device_id\":\"ESP-001\",\"uid_card\":\"CARD-RFID-001\",\"timestamp\":\"2026-04-28T12:05:00\"}"
```

### Hasil yang diharapkan

- status HTTP `201`;
- data absensi tersimpan;
- field `signature_verified` bernilai `false`;
- perangkat berubah menjadi `online`.

Validasi ini juga sudah dibuktikan pada test:

- `backend/app/tests/test_absensi.py::test_rfid_device_can_create_absensi`

## 5. Cara Verifikasi RFID Dengan Signature

Mode ini dipakai saat:

- `RFID_REQUIRE_SIGNATURE=1`;
- server memiliki public key perangkat;
- perangkat mengirim header signature.

### Header yang wajib

- `X-API-Key`
- `X-RFID-Signature`
- `X-RFID-Signature-Timestamp`

### Alur verifikasi

1. server membaca public key perangkat dari `backend/keys/rfid_public/<device_id>.pem` atau dari kolom `public_key`;
2. backend membentuk canonical message dari `device_id`, `uid_card`, `timestamp`, dan `request timestamp`;
3. signature diverifikasi dengan public key;
4. nonce/timestamp dicek untuk mencegah replay attack.

### Bukti implementasi

- logika signature: `backend/app/security.py`
- endpoint verifikasi: `backend/app/routes/rfid.py`
- integrasi ke absensi: `backend/app/services/absensi_service.py`

### Bukti test

- `test_rfid_device_can_use_public_key_signature_when_enabled`
- `test_rfid_signature_is_required_when_enforced`
- `test_rfid_signature_rejects_replay_timestamp`

Semua test tersebut ada di:

- `backend/app/tests/test_absensi.py`

## 6. Cara Menambahkan Bukti Uji ke Laporan

Bukti uji bisa ditambahkan dalam tiga bentuk:

### 6.1 Output test otomatis

Contoh yang baik untuk lampiran:

```bash
cd backend
pytest app/tests -q
```

Contoh narasi laporan:

> Pengujian backend dilakukan menggunakan pytest pada 28 April 2026. Hasil pengujian menunjukkan seluruh `43` test case berhasil lulus.

### 6.2 Screenshot atau log request

Untuk bukti uji integrasi RFID, simpan:

- screenshot terminal `curl`;
- screenshot serial monitor ESP8266;
- screenshot dashboard setelah data berubah;
- screenshot file laporan PDF/Excel yang berhasil diunduh.

### 6.3 Tabel bukti uji

Format yang bisa dipakai:

| No | Fitur | Skenario | Bukti | Hasil |
| --- | --- | --- | --- | --- |
| 1 | Login | Admin login berhasil | Screenshot / output test | Lulus |
| 2 | Absensi RFID | Tap kartu tercatat | Output request + dashboard | Lulus |
| 3 | Laporan | PDF berhasil digenerate | File hasil generate | Lulus |
| 4 | RFID signature | Signature valid diterima | Output test pytest | Lulus |

## 7. Cara Menambahkan Coverage Report

### 7.1 Dependency

`pytest-cov` sudah ditambahkan ke:

- `backend/requirements.txt`

Jika environment belum menginstal dependency terbaru, jalankan:

```bash
cd backend
pip install -r requirements.txt
```

### 7.2 Menjalankan coverage report

Contoh perintah:

```bash
cd backend
pytest app/tests --cov=app --cov-report=term-missing --cov-report=html
```

Hasilnya:

- ringkasan coverage tampil di terminal;
- folder `htmlcov/` dibuat otomatis;
- file utama laporan coverage berada di `backend/htmlcov/index.html`.

Hasil yang sudah berhasil diverifikasi pada repo ini tanggal 28 April 2026:

- `64 passed`;
- total coverage backend `85%`;
- report HTML berhasil dibuat di `backend/htmlcov/`.

### 7.3 Coverage report XML

Jika dibutuhkan untuk CI atau lampiran tooling:

```bash
cd backend
pytest app/tests --cov=app --cov-report=xml --cov-report=term
```

Hasilnya:

- file `backend/coverage.xml`

### 7.4 Bukti yang bisa dimasukkan ke laporan

Masukkan salah satu atau beberapa hal berikut:

- screenshot ringkasan coverage terminal;
- screenshot `htmlcov/index.html`;
- tabel modul dengan coverage tertinggi dan terendah;
- catatan area yang masih perlu ditambah test.

## 8. A3 yang Sudah Dibereskan

Perbaikan technical debt yang sudah dilakukan:

- `Query.get()` pada route download laporan diganti ke `db.session.get(...)`;
- route notifikasi dirapikan ke `/api/v1/notifikasi`;
- route heartbeat perangkat dirapikan ke `/api/v1/perangkat/ping`.

Sisa A3 yang masih bisa dilanjutkan:

- audit semua warning setelah menjalankan full test;
- review konsistensi format error response lintas route.
