# SIKAP - Feature Roadmap
### Sistem Informasi Kepatuhan Absensi Peserta Didik
> SMK Bina Putra Nusantara | Semester Genap 2024/2025

**Metodologi:** Lean + Rapid Prototyping (12 Minggu)  
**Tim:** 4 orang (2 UI/UX, 2 Backend/Hardware)

---

## Prioritas Fitur (MoSCoW)

| Prioritas | Definisi | Target Sprint |
|-----------|----------|---------------|
| **MUST HAVE** | Tanpa ini sistem tidak berfungsi | Sprint 1 (Week 6-7) |
| **SHOULD HAVE** | Penting, tapi MVP bisa jalan tanpa ini | Sprint 2 (Week 8-9) |
| **COULD HAVE** | Nice to have, kerjakan jika waktu cukup | Refine (Week 10-11) |

---

## SPRINT 1 — MVP Core (Week 6-7)

> **Goal:** Siswa tap kartu RFID -> data masuk DB -> tampil di dashboard wali kelas

### BE-01: Project Setup & Database
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Setup Flask, SQLAlchemy, MySQL, migrations |
| **Detail** | Buat 6 core tables: `users`, `siswa`, `kelas`, `absensi`, `waktu_sholat`, `sesi_sholat` |
| **Output** | Database running, models ready, migrations applied |
| **Dependency** | - |

### BE-02: Authentication (JWT)
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Login/logout JWT untuk 6 role |
| **API Endpoints** | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| **Detail** | JWT token, role-based middleware, bcrypt password hashing |
| **Output** | User bisa login sesuai role, token expire 24 jam |
| **Dependency** | BE-01 |

### BE-03: Absensi RFID (Core)
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Terima data tap RFID, validasi, tentukan status, simpan |
| **API Endpoints** | `POST /absensi` (dari RFID), `GET /absensi` (list), `GET /absensi/{id}` |
| **Logika** | Tap -> cek kartu valid -> cek sesi aktif -> bandingkan waktu iqamah -> status: tepat_waktu / terlambat / alpha |
| **Output** | Data absensi tersimpan di MySQL |
| **Dependency** | BE-01, BE-02 |

### BE-04: Rekapitulasi (Basic)
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Aggregate data absensi per kelas dan per siswa |
| **API Endpoints** | `GET /rekapitulasi/kelas/{id}`, `GET /rekapitulasi/siswa/{id}`, `GET /rekapitulasi/sekolah` |
| **Output** | JSON: total hadir, terlambat, alpha, persentase |
| **Dependency** | BE-03 |

### FE-01: Project Setup
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Setup React + Vite + MUI + React Router + Axios |
| **Output** | Frontend dev server running, routing configured |
| **Dependency** | - |

### FE-02: Halaman Login (F003)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Form login + API call + simpan JWT + redirect sesuai role |
| **Halaman** | F003: Login |
| **Komponen** | ProtectedRoute, AuthContext |
| **Output** | User bisa login dan diarahkan ke dashboard sesuai role |
| **Dependency** | FE-01, BE-02 |

### FE-03: Dashboard 6 Role (F004-F009)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | 6 dashboard berbeda sesuai role |
| **Halaman** | F004: Admin, F005: Kepsek, F006: Wali Kelas, F007: Guru Piket, F008: Siswa, F009: Orang Tua |
| **Detail** | Setiap dashboard: summary cards + tabel data utama |
| **Output** | Setiap role melihat data relevan setelah login |
| **Dependency** | FE-02, BE-04 |

### FE-04: Halaman Rekap Kelas (F019)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Tabel rekap per siswa dalam kelas, filter tanggal & waktu sholat |
| **Halaman** | F019: Rekapitulasi Kelas |
| **Output** | Wali kelas bisa lihat persentase kehadiran per siswa |
| **Dependency** | FE-01, BE-04 |

### HW-01: ESP8266 + RFID Firmware
| Item | Detail |
|------|--------|
| **PIC** | Backend (Hardware) |
| **Prioritas** | MUST HAVE |
| **Deskripsi** | Firmware ESP8266 untuk baca kartu RFID dan kirim ke API |
| **Detail** | Read RFID UID -> POST /absensi via WiFi -> LED indicator (hijau=sukses, merah=gagal) |
| **Output** | 10 kartu RFID berhasil di-test, data masuk ke DB |
| **Dependency** | BE-03 |

### Sprint 1 Demo Checklist
- [ ] Siswa tap kartu -> data masuk DB -> tampil di dashboard wali kelas
- [ ] Login multi-role -> redirect ke dashboard masing-masing
- [ ] Wali kelas bisa lihat rekap kelas basic
- [ ] ESP8266 berhasil POST ke API

---

## SPRINT 2 — Extended Features (Week 8-9)

> **Goal:** Laporan, manual input, notifikasi, user management

### BE-05: Generate Laporan PDF/Excel
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | SHOULD HAVE |
| **API Endpoints** | `POST /laporan/generate`, `GET /laporan/download/{id}` |
| **Library** | ReportLab (PDF), OpenPyXL (Excel) |
| **Detail** | Generate rekap kehadiran per kelas/siswa/sekolah, simpan ke `/static/generated/` |
| **Dependency** | BE-04 |

### BE-06: Manual Input Absensi (Guru Piket)
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | SHOULD HAVE |
| **API Endpoints** | `POST /absensi/manual`, `PUT /absensi/{id}` |
| **Detail** | Hanya role Guru Piket, flag `verified_by_guru_piket`, catat di AuditLog |
| **Dependency** | BE-03 |

### BE-07: Notifikasi
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | SHOULD HAVE |
| **API Endpoints** | `POST /notifikasi/send`, `GET /notifikasi`, `PUT /notifikasi/{id}/read` |
| **Detail** | Simpan notifikasi per user, mark as read, unread count |
| **Dependency** | BE-01 |

### BE-08: User Management CRUD
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | SHOULD HAVE |
| **API Endpoints** | `POST /users`, `GET /users`, `PUT /users/{id}`, `DELETE /users/{id}` |
| **Detail** | Admin only, CRUD untuk semua role |
| **Dependency** | BE-02 |

### FE-05: Halaman Generate Laporan (F022)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | SHOULD HAVE |
| **Halaman** | F022: Generate Laporan |
| **Detail** | Form pilih kelas, periode, format (PDF/Excel) -> download file |
| **Dependency** | FE-01, BE-05 |

### FE-06: Halaman Manual Input (F023)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | SHOULD HAVE |
| **Halaman** | F023: Manual Input Absensi |
| **Detail** | Form NISN, tanggal, waktu sholat, status, keterangan. Validasi NISN. |
| **Dependency** | FE-01, BE-06 |

### FE-07: Komponen Notifikasi (F024)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | SHOULD HAVE |
| **Halaman** | F024: Notifikasi |
| **Detail** | Badge unread count, list notifikasi, click -> mark as read. Polling 30 detik. |
| **Dependency** | FE-01, BE-07 |

### FE-08: Halaman User Management (F010)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | SHOULD HAVE |
| **Halaman** | F010: User Management, F010A: Tambah User, F010B: Edit User |
| **Detail** | Tabel user + CRUD operations, admin only |
| **Dependency** | FE-01, BE-08 |

### Sprint 2 Demo Checklist
- [ ] Guru piket bisa manual input absensi
- [ ] Wali kelas bisa generate laporan PDF/Excel
- [ ] Admin bisa CRUD user
- [ ] Notifikasi basic berfungsi
- [ ] Integration test: frontend <-> backend semua flow

---

## REFINE & POLISH (Week 10-11)

> **Goal:** Fitur tambahan, optimasi, testing, UAT

### BE-09: Auto-Generate Surat Peringatan
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | COULD HAVE |
| **Detail** | Cron job harian: query siswa alpha > threshold -> generate SP1/SP2/SP3 -> kirim notifikasi ke orang tua & wali kelas |
| **Library** | APScheduler |
| **Dependency** | BE-03, BE-07 |

### BE-10: Real-time MQTT
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | COULD HAVE |
| **Detail** | Publish event `absensi/realtime` setiap tap kartu, topic `notifikasi/{user_id}` |
| **Broker** | Mosquitto (sudah ada di docker-compose) |
| **Dependency** | BE-03 |

### BE-11: Elasticsearch Integration
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | COULD HAVE |
| **Detail** | Index data absensi untuk pencarian & analitik cepat |
| **Dependency** | BE-03 |

### BE-12: Performance Optimization
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | COULD HAVE |
| **Detail** | Database indexes, query optimization (N+1), caching (Flask-Caching untuk rekap endpoint) |
| **Dependency** | BE-04 |

### FE-09: Real-time MQTT Client
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | COULD HAVE |
| **Detail** | MQTT.js subscribe `absensi/realtime`, auto-update dashboard tanpa refresh |
| **Dependency** | FE-03, BE-10 |

### FE-10: Grafik & Chart (Recharts)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | COULD HAVE |
| **Detail** | Trend kehadiran (line chart), distribusi status (pie chart) di dashboard |
| **Dependency** | FE-03, BE-04 |

### FE-11: UI/UX Polish
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | COULD HAVE |
| **Detail** | Loading spinners, error toast, responsive mobile, accessibility (ARIA) |
| **Dependency** | FE-03 |

### FE-12: Halaman Tambahan (F013, F026, F027)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | COULD HAVE |
| **Halaman** | F013: Pengaturan Waktu Sholat, F026: Profil Pengguna, F027: Data Sekolah |
| **Dependency** | FE-01 |

### QA-01: Unit & Integration Testing
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | SHOULD HAVE |
| **Target** | Coverage >80% backend (pytest --cov), React Testing Library untuk frontend |
| **Dependency** | Semua modul |

### QA-02: UAT dengan Stakeholder SMK
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | SHOULD HAVE |
| **Detail** | On-site testing 1-2 hari di SMK Bina Putra, feedback dari guru & siswa |
| **Dependency** | Sprint 1 & 2 selesai |

---

## DEPLOYMENT (Week 12)

### DP-01: Production Server
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Detail** | MySQL production, Flask + Waitress + Nginx, React production build, SSL/HTTPS |

### DP-02: Hardware Installation
| Item | Detail |
|------|--------|
| **PIC** | Backend (Hardware) |
| **Detail** | Install ESP8266 + RFID di masjid, test WiFi + API, siapkan backup reader |

### DP-03: Data Migration
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Detail** | Import data siswa/kelas/guru dari DB sekolah, assign kartu RFID |

### DP-04: Dokumentasi & Training
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Detail** | User manual, admin manual, API docs (Swagger), training session 2-3 jam, video tutorial |

---

## Dependency Graph

```
BE-01 (Setup DB)
  |
  +---> BE-02 (Auth JWT)
  |       |
  |       +---> BE-08 (User CRUD) ---> FE-08 (User Mgmt Page)
  |       +---> FE-02 (Login Page)
  |               |
  |               +---> FE-03 (6 Dashboard) ---> FE-09 (MQTT Client)
  |                                          ---> FE-10 (Charts)
  |                                          ---> FE-11 (UI Polish)
  |
  +---> BE-03 (Absensi RFID)
  |       |
  |       +---> BE-04 (Rekap) ---> BE-05 (Laporan) ---> FE-05 (Laporan Page)
  |       |                   ---> FE-04 (Rekap Page)
  |       |                   ---> BE-12 (Optimasi)
  |       +---> BE-06 (Manual Input) ---> FE-06 (Manual Input Page)
  |       +---> BE-09 (Auto SP)
  |       +---> BE-10 (MQTT) ---> FE-09 (MQTT Client)
  |       +---> BE-11 (Elasticsearch)
  |       +---> HW-01 (ESP8266 Firmware)
  |
  +---> BE-07 (Notifikasi) ---> FE-07 (Notifikasi Component)
                            ---> BE-09 (Auto SP)
```

---

## Daftar Halaman Frontend (F001-F027)

| Kode | Halaman | Sprint | PIC |
|------|---------|--------|-----|
| F001 | Splash Screen | 1 | Frontend |
| F002 | Home / Landing | 1 | Frontend |
| F003 | Login | 1 | Frontend |
| F004 | Dashboard Admin | 1 | Frontend |
| F005 | Dashboard Kepala Sekolah | 1 | Frontend |
| F006 | Dashboard Wali Kelas | 1 | Frontend |
| F007 | Dashboard Guru Piket | 1 | Frontend |
| F008 | Dashboard Siswa | 1 | Frontend |
| F009 | Dashboard Orang Tua | 1 | Frontend |
| F010 | User Management (Admin) | 2 | Frontend |
| F011 | Data Master Kelas | 2 | Frontend |
| F012 | Data Master Siswa | 2 | Frontend |
| F013 | Pengaturan Waktu Sholat | Refine | Frontend |
| F014 | Monitoring Perangkat | Refine | Frontend |
| F015 | Riwayat Absensi (Siswa) | 1 | Frontend |
| F016 | Riwayat Absensi (Orang Tua) | 1 | Frontend |
| F017 | Detail Absensi | 2 | Frontend |
| F018 | Edit Absensi (Wali Kelas) | 2 | Frontend |
| F019 | Rekapitulasi Kelas | 1 | Frontend |
| F020 | Rekapitulasi Sekolah (Kepsek) | 2 | Frontend |
| F021 | Rekapitulasi Siswa | 2 | Frontend |
| F022 | Generate Laporan | 2 | Frontend |
| F023 | Manual Input (Guru Piket) | 2 | Frontend |
| F024 | Notifikasi | 2 | Frontend |
| F025 | Surat Peringatan | Refine | Frontend |
| F026 | Profil Pengguna | Refine | Frontend |
| F027 | Data Sekolah | Refine | Frontend |

---

## API Endpoints (27 total)

| Grup | Endpoint | Method | Sprint |
|------|----------|--------|--------|
| **Auth** | `/auth/login` | POST | 1 |
| | `/auth/logout` | POST | 1 |
| | `/auth/me` | GET | 1 |
| **Absensi** | `/absensi` | POST | 1 |
| | `/absensi` | GET | 1 |
| | `/absensi/{id}` | GET | 1 |
| | `/absensi/{id}` | PUT | 2 |
| | `/absensi/manual` | POST | 2 |
| **Rekap** | `/rekapitulasi/kelas/{id}` | GET | 1 |
| | `/rekapitulasi/siswa/{id}` | GET | 1 |
| | `/rekapitulasi/sekolah` | GET | 1 |
| **Laporan** | `/laporan/generate` | POST | 2 |
| | `/laporan/download/{id}` | GET | 2 |
| **Notifikasi** | `/notifikasi` | GET | 2 |
| | `/notifikasi/send` | POST | 2 |
| | `/notifikasi/{id}/read` | PUT | 2 |
| **Users** | `/users` | GET | 2 |
| | `/users` | POST | 2 |
| | `/users/{id}` | PUT | 2 |
| | `/users/{id}` | DELETE | 2 |
| **Kelas** | `/kelas` | GET | 2 |
| | `/kelas/{id}` | GET | 2 |
| **Siswa** | `/siswa` | GET | 2 |
| | `/siswa/{id}` | GET | 2 |
| **Waktu Sholat** | `/waktu-sholat` | GET | Refine |
| | `/waktu-sholat` | PUT | Refine |
| **Perangkat** | `/perangkat` | GET | Refine |

---

## Database Tables (18 total)

| Kategori | Tabel | Sprint |
|----------|-------|--------|
| **Auth** | `users` | 1 |
| **Master Data** | `kelas`, `siswa`, `guru`, `orangtua`, `sekolah` | 1 (core), 2 (extended) |
| **Transaksi** | `absensi`, `sesi_sholat` | 1 |
| **Referensi** | `waktu_sholat` | 1 |
| **IoT** | `perangkat` | 1 |
| **Output** | `laporan`, `surat_peringatan` | 2 / Refine |
| **Operasional** | `notifikasi` | 2 |
| **Log** | `audit_log` | 2 |
| **Konfigurasi** | `konfigurasi` | Refine |

---

## Tech Stack Ringkas

| Layer | Teknologi |
|-------|-----------|
| Frontend | React 18 + Vite 5 + MUI 5 + Recharts + Axios |
| Backend | Python 3.10 + Flask 3 + SQLAlchemy + JWT |
| Database | MySQL 8.0 |
| Cache | Redis 7 |
| Search | Elasticsearch 8.12 |
| Realtime | Mosquitto MQTT 2 + paho-mqtt |
| Monitoring | Prometheus + Grafana |
| Hardware | ESP8266 (NodeMCU) + MFRC522 RFID Reader |
| DevOps | Docker Compose |

---

## Catatan untuk Tim

1. **Kerjakan MUST HAVE dulu** — jangan loncat ke fitur COULD HAVE sebelum Sprint 1 selesai
2. **Komunikasi via Git** — buat branch per fitur (`feature/BE-03-absensi`), PR sebelum merge
3. **Test setiap selesai** — minimal manual test, idealnya pytest/unit test
4. **Demo setiap akhir sprint** — rekam video demo untuk dokumentasi UAS
5. **Docker Compose** sudah siap — `docker compose up -d --build` untuk jalankan semua service
6. **API spec lengkap** ada di `docs/design/API_endpoints.yaml` (OpenAPI 3.0)
7. **Struktur tabel** ada di `docs/design/struktur_table.md`

---

*Dokumen ini akan di-update seiring progress sprint. Tandai [x] pada checklist setelah fitur selesai.*
