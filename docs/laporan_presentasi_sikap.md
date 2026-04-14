# 📊 LAPORAN PRESENTASI HASIL PENGEMBANGAN
# Sistem Informasi Kepatuhan Absensi Peserta Didik (SIKAP)

---

> **Mata Kuliah:** Rancang Bangun Perangkat Lunak (RKBL)  
> **Dosen Pengampu:** Erna Haerani, S.T., M.Kom.  
> **Program Studi:** Sistem Informasi — Universitas Siliwangi  
> **Semester:** Genap 2024/2025 · **Kelompok:** 1  
> **Metodologi:** Lean + Rapid Prototyping (12 Minggu)

---

## 1. Latar Belakang & Tujuan

### 1.1 Permasalahan
SMK Bina Putra Nusantara memiliki kebiasaan mencatat kehadiran ibadah sholat siswa secara **manual** (absensi kertas). Metode ini memiliki beberapa permasalahan:
- **Rentan kesalahan pencatatan** — human error saat mendata ratusan siswa
- **Tidak real-time** — wali kelas dan orang tua tidak bisa memantau secara langsung
- **Sulit menghasilkan rekap** — pembuatan laporan bulanan memakan waktu lama
- **Tidak ada mekanisme peringatan otomatis** — siswa yang sering alpha tidak tertangani cepat

### 1.2 Solusi: SIKAP
**SIKAP** (Sistem Informasi Kepatuhan Absensi Peserta Didik) dibangun untuk mengatasi permasalahan tersebut dengan mengintegrasikan **hardware IoT** (kartu RFID) dan **aplikasi web** sehingga proses pencatatan, evaluasi, dan pelaporan kehadiran ibadah siswa berjalan **otomatis**.

### 1.3 Tujuan Sistem
1. Mencatat kehadiran ibadah sholat siswa secara otomatis menggunakan RFID
2. Menentukan status kehadiran (tepat waktu / terlambat / alpha) berdasarkan waktu iqamah
3. Menyediakan dashboard multi-role untuk 6 jenis pengguna
4. Menghasilkan laporan rekap kehadiran dalam format PDF/Excel
5. Memberikan notifikasi Surat Peringatan (SP) otomatis kepada orang tua

---

## 2. Arsitektur Sistem

### 2.1 Diagram Arsitektur 3-Layer

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAYER FRONTEND                               │
│    React 18 + Vite 5 + Material UI 5 + Recharts + Axios            │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│    │ Dashboard │ │  Login   │ │  Rekap   │ │ Laporan  │ ... (10    │
│    │ (6 role) │ │   Page   │ │  Page    │ │  Page    │   halaman) │
│    └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LAYER BACKEND                                │
│    Python 3.10 + Flask 3 + SQLAlchemy + JWT + ReportLab            │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│    │   Auth   │ │ Absensi  │ │  Rekap   │ │ Laporan  │            │
│    │ Service  │ │ Service  │ │ Service  │ │ Service  │ ... (12    │
│    └──────────┘ └──────────┘ └──────────┘ └──────────┘   service) │
│    ┌──────────────────────────────────────────────────┐            │
│    │  Middleware: JWT Auth + Role-Based Access Control │            │
│    └──────────────────────────────────────────────────┘            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ SQLAlchemy ORM
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER DATA & HARDWARE                            │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│    │ MySQL 8  │ │  Redis 7 │ │Mosquitto │ │  Elastic │            │
│    │ (19 tbl) │ │ (Cache)  │ │ (MQTT)   │ │ search   │            │
│    └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│    ┌──────────────────────────────────────────────────┐            │
│    │  ESP8266 (NodeMCU) + MFRC522 RFID Reader         │            │
│    │  → POST /absensi via WiFi HTTP                    │            │
│    └──────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Alur Kerja Utama (Tap RFID → Dashboard)

```
Siswa tap kartu RFID
        │
        ▼
  ESP8266 baca UID ──────► POST /api/v1/absensi
        │                     │
        │              ┌──────┴──────┐
        │              │  Backend:   │
        │              │ 1. Cek UID  │
        │              │ 2. Cek sesi │
        │              │ 3. Hitung   │
        │              │    status   │
        │              └──────┬──────┘
        │                     │
  LED Indikator ◄────── Response JSON
  (Hijau/Merah)               │
                              ▼
                    Data tersimpan di MySQL
                              │
                    ┌─────────┴─────────┐
                    │   Dashboard Web    │
                    │  (Wali/Kepsek/dll) │
                    └───────────────────┘
```

---

## 3. Tech Stack

### 3.1 Tabel Teknologi

| Layer | Teknologi | Versi | Fungsi |
|-------|-----------|-------|--------|
| **Frontend** | React | 18+ | UI Framework |
| | Material UI (MUI) | 5+ | Component Library |
| | Recharts | 2+ | Grafik & Visualisasi |
| | Axios | 1+ | HTTP Client |
| | Vite | 5+ | Build Tool & Dev Server |
| **Backend** | Python | 3.10+ | Bahasa Pemrograman |
| | Flask | 3+ | Web Framework |
| | Flask-JWT-Extended | 4+ | Autentikasi JWT |
| | Flask-SQLAlchemy | 3+ | ORM Database |
| | Flask-Migrate | 4+ | Migrasi Database |
| | ReportLab | 4+ | Generate PDF |
| | OpenPyXL | 3+ | Generate Excel |
| **Database** | MySQL | 8.0 | Database Utama |
| | Redis | 7 | Caching |
| | Elasticsearch | 8.13 | Pencarian & Analitik |
| **Realtime** | Mosquitto | 2 | MQTT Broker |
| **Monitoring** | Prometheus + Grafana | — | Sistem Monitoring |
| **Hardware** | ESP8266 (NodeMCU) | — | Mikrokontroler WiFi |
| | MFRC522 | — | RFID Reader 13.56MHz |
| **DevOps** | Docker Compose | — | Container Orchestration |

### 3.2 Arsitektur Container (Docker Compose)

Seluruh layanan dikelola melalui `docker-compose.yml` dengan **8 service**:

| Service | Port | Keterangan |
|---------|------|------------|
| `db` (MySQL) | 3306 | Database utama + auto-init schema & seed |
| `backend` (Flask) | 5000 | API Server |
| `frontend` (React/Vite) | 8081 | Single Page Application |
| `mosquitto` | 1883/9001 | MQTT Broker (standard + WebSocket) |
| `elasticsearch` | 9200 | Search engine |
| `redis` | 6379 | Cache & message queue |
| `prometheus` | 9090 | Metrics collection *(profile: monitoring)* |
| `grafana` | 3000 | Monitoring dashboard *(profile: monitoring)* |

---

## 4. Skema Database

### 4.1 Ringkasan
- **Total tabel:** 19 tabel
- **Engine:** MySQL 8.0 (charset: utf8mb4)
- **Naming Convention:** snake_case, PK: `id_` + nama_tabel

### 4.2 Daftar Tabel per Kategori

| Kategori | Tabel | Keterangan |
|----------|-------|------------|
| **Auth & User** | `users` | Akun login semua role (6 role) |
| **Master Data** | `kelas` | Data kelas + wali kelas |
| | `siswa` | Data siswa + ID kartu RFID |
| | `guru` | Data guru (wali & piket) |
| | `orangtua` | Data orang tua siswa |
| | `sekolah_info` | Profil & logo sekolah |
| **Transaksi** | `absensi` ⭐ | Tabel inti — catatan tap RFID |
| | `sesi_sholat` | Sesi per hari per waktu sholat |
| **Referensi** | `waktu_sholat` | Jadwal adzan, iqamah, selesai |
| | `status_absensi` | Kode status (6 jenis) |
| **IoT** | `perangkat` | Data ESP8266 + status online |
| **Output** | `laporan` | Metadata file PDF/Excel |
| | `surat_peringatan` | SP1/SP2/SP3 per siswa |
| | `notifikasi` | Notifikasi in-app per user |
| **Operasional** | `jadwal_piket` | Jadwal piket guru per hari |
| | `sengketa_absensi` | Klaim absensi dari siswa |
| | `izin_pengajuan` | Pengajuan izin ketidakhadiran |
| **Log** | `audit_log` | Rekam jejak perubahan data |
| **Auth** | `password_reset_token` | Token reset password |

### 4.3 Logika Bisnis Status Absensi

| Status | Kondisi | Warna |
|--------|---------|-------|
| `tepat_waktu` | Tap antara `waktu_adzan` dan `waktu_iqamah` | 🟢 Hijau |
| `terlambat` | Tap antara `waktu_iqamah` dan `waktu_selesai` | 🟡 Kuning |
| `alpha` | Tidak tap sama sekali (auto-fill saat sesi ditutup) | 🔴 Merah |
| `sakit` | Dispensasi sakit (input manual) | 🔵 Biru |
| `izin` | Izin resmi | ⚪ Abu-abu |
| `haid` | Dispensasi haid | 🟣 Ungu |

### 4.4 Mekanisme Surat Peringatan Berjenjang

| Level | Threshold | Tindakan |
|-------|-----------|----------|
| **SP1** | Alpha ke-5 | Notifikasi ke orang tua & wali kelas |
| **SP2** | Alpha ke-10 | Panggilan orang tua |
| **SP3** | Alpha ke-15 | Tindakan disiplin lanjutan |

---

## 5. Implementasi Backend

### 5.1 Struktur Kode (Clean Architecture)

```
backend/
├── run.py                    ← Entry point
├── config.py                 ← Konfigurasi env
├── app/
│   ├── __init__.py           ← App Factory (create_app)
│   ├── extensions.py         ← db, jwt, cors, migrate
│   ├── models/               ← 18 file model SQLAlchemy
│   │   ├── user.py
│   │   ├── siswa.py
│   │   ├── absensi.py        ← Model inti
│   │   ├── waktu_sholat.py
│   │   └── ... (14 model lainnya)
│   ├── routes/               ← 16 file blueprint API
│   │   ├── auth.py
│   │   ├── absensi.py
│   │   ├── rekapitulasi.py
│   │   ├── laporan.py
│   │   └── ... (12 route lainnya)
│   ├── services/             ← 12 file business logic
│   │   ├── auth_service.py
│   │   ├── absensi_service.py  (16.5 KB)
│   │   ├── dashboard_service.py (16.3 KB)
│   │   ├── laporan_service.py
│   │   └── ... (8 service lainnya)
│   ├── middleware/
│   │   ├── auth_middleware.py  ← JWT validation
│   │   └── role_middleware.py  ← RBAC enforcement
│   └── utils/
│       └── response.py        ← Standardized response
├── migrations/                ← Alembic migrations
└── static/generated/          ← File PDF/Excel hasil generate
```

### 5.2 Daftar API Endpoints (27 Total)

| # | Grup | Method | Endpoint | Status |
|---|------|--------|----------|--------|
| 1 | Auth | `POST` | `/auth/login` | ✅ |
| 2 | Auth | `POST` | `/auth/logout` | ✅ |
| 3 | Auth | `POST` | `/auth/refresh` | ✅ |
| 4 | Absensi | `POST` | `/absensi` | ✅ |
| 5 | Absensi | `GET` | `/absensi` | ✅ |
| 6 | Absensi | `GET` | `/absensi/{id}` | ✅ |
| 7 | Absensi | `PUT` | `/absensi/{id}` | ✅ |
| 8 | Absensi | `POST` | `/absensi/manual` | ✅ |
| 9 | Rekap | `GET` | `/rekapitulasi/kelas/{id}` | ✅ |
| 10 | Rekap | `GET` | `/rekapitulasi/siswa/{id}` | ✅ |
| 11 | Rekap | `GET` | `/rekapitulasi/sekolah` | ✅ |
| 12 | Dashboard | `GET` | `/dashboard` | ✅ |
| 13 | Laporan | `POST` | `/laporan/generate` | ✅ |
| 14 | Laporan | `GET` | `/laporan/download/{id}` | ✅ |
| 15 | Notifikasi | `GET` | `/notifikasi` | ✅ |
| 16 | Notifikasi | `POST` | `/notifikasi/send` | ✅ |
| 17 | Notifikasi | `PUT` | `/notifikasi/{id}/read` | ✅ |
| 18 | Users | `POST` | `/users` | ✅ |
| 19 | Users | `GET` | `/users` | ✅ |
| 20 | Users | `PUT` | `/users/{id}` | ✅ |
| 21 | Users | `DELETE` | `/users/{id}` | ✅ |
| 22 | Kelas | `GET` | `/kelas` | ✅ |
| 23 | Siswa | `GET` | `/siswa` | ✅ |
| 24 | Waktu Sholat | `GET` | `/waktu-sholat` | ✅ |
| 25 | Waktu Sholat | `PUT` | `/waktu-sholat` | ✅ |
| 26 | Izin | `POST/GET` | `/izin` | ✅ |
| 27 | Sengketa | `POST/GET` | `/sengketa` | ✅ |

### 5.3 Fitur Keamanan

| Fitur | Implementasi |
|-------|-------------|
| **Autentikasi** | JWT Token (expire 24 jam) |
| **Otorisasi** | Role-Based Access Control (6 role) |
| **Password** | Hash bcrypt sebelum disimpan |
| **SQL Injection** | Pencegahan via SQLAlchemy ORM |
| **Audit Trail** | Setiap perubahan absensi tercatat di `audit_log` |
| **Token Blacklist** | Logout invalidate token |
| **CORS** | Dikonfigurasi melalui Flask-CORS |

---

## 6. Implementasi Frontend

### 6.1 Daftar Halaman (10 Halaman Utama)

| No | Halaman | File | Deskripsi |
|----|---------|------|-----------|
| 1 | Login/Auth | `AuthPage.jsx` | Form login multi-role + redirect |
| 2 | Dashboard | `DashboardPage.jsx` | 6 tampilan dashboard berbeda per role |
| 3 | User Management | `UserManagementPage.jsx` | Tabel CRUD user (Admin only) |
| 4 | Form User | `UserFormPage.jsx` | Tambah/Edit user |
| 5 | Manual Input | `ManualInputPage.jsx` | Input absensi manual (Guru Piket) |
| 6 | Laporan | `ReportPage.jsx` | Generate & download PDF/Excel |
| 7 | Notifikasi | `NotificationPage.jsx` | Daftar notifikasi per user |
| 8 | Profil | `ProfilePage.jsx` | Lihat & edit profil pengguna |
| 9 | Waktu Sholat | `PrayerTimeSettingsPage.jsx` | Pengaturan jadwal sholat |
| 10 | Data Sekolah | `SchoolDataPage.jsx` | Profil & info sekolah |

### 6.2 Komponen Reusable

| Komponen | File | Deskripsi |
|----------|------|-----------|
| Common Components | `Common.jsx` | SummaryCard, StatusBadge, ConfirmDialog, SearchFilter |
| Dashboard Charts | `DashboardCharts.jsx` | TrendLineChart, StatusPieChart, BarChart |

### 6.3 Fitur Frontend Utama

- ✅ **Multi-role Dashboard** — 6 tampilan berbeda (Admin, Kepsek, Wali Kelas, Guru Piket, Siswa, Orang Tua)
- ✅ **Form Login** dengan JWT storage dan auto-redirect berdasarkan role
- ✅ **CRUD User Management** dengan filter, search, dan pagination
- ✅ **Manual Input Absensi** dengan validasi NISN dan form lengkap
- ✅ **Generate Laporan** dengan pilihan format PDF/Excel
- ✅ **Grafik & Visualisasi** menggunakan Recharts (line chart, pie chart)
- ✅ **Responsive Design** menggunakan Material UI
- ✅ **Notifikasi** badge unread count

---

## 7. Role-Based Access Control (RBAC)

### 7.1 Matriks Hak Akses per Role

| Fitur | Admin | Kepsek | Wali Kelas | Guru Piket | Siswa | Orang Tua |
|-------|:-----:|:------:|:----------:|:----------:|:-----:|:---------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Kelola User (CRUD) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Kelola Data Master | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manual Input Absensi | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Rekap Kelas | ✅ | ✅ | ✅* | ❌ | ❌ | ❌ |
| Rekap Sekolah | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Generate Laporan | ✅ | ✅ | ✅* | ❌ | ❌ | ❌ |
| Lihat Riwayat Absensi | ✅ | ✅ | ✅* | ✅ | ✅** | ✅** |
| Edit Absensi | ❌ | ✅ | ✅* | ❌ | ❌ | ❌ |
| Sengketa Absensi | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Pengajuan Izin | ❌ | ❌ | ✅ (verif) | ❌ | ✅ | ❌ |
| Notifikasi | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pengaturan Waktu Sholat | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

> *\* Hanya kelas yang diampu*  
> *\*\* Hanya data pribadi / anak*

---

## 8. Integrasi Hardware IoT

### 8.1 Spesifikasi Perangkat

| Komponen | Spesifikasi | Fungsi |
|----------|-------------|--------|
| ESP8266 (NodeMCU) | Mikrokontroler WiFi 2.4GHz | Pengirim data via HTTP |
| MFRC522 | RFID Reader 13.56MHz, SPI | Pembaca kartu RFID |
| Kartu RFID | 13.56MHz Mifare Classic 1K | ID Card siswa |
| LED RGB | Red/Green | Indikator sukses/gagal |

### 8.2 Alur Komunikasi

```
[Kartu RFID] → [MFRC522 SPI] → [ESP8266 WiFi] → [POST /api/v1/absensi]
                                                         │
                                                    Payload JSON:
                                                    {
                                                      "uid_card": "A3B2C1D4",
                                                      "device_id": "ESP-001",
                                                      "timestamp": "..."
                                                    }
```

### 8.3 Status Integrasi
- ✅ Firmware ESP8266 dirancang dan disiapkan (`hardware/esp8266_rfid/`)
- ✅ Endpoint `POST /absensi` siap menerima payload dari hardware
- ✅ Sistem autentikasi perangkat via `api_key` di tabel `perangkat`
- 🔄 Testing end-to-end hardware ↔ backend (dalam proses)

---

## 9. Progress Pengembangan

### 9.1 Timeline Sprint

| Fase | Minggu | Target | Status |
|------|--------|--------|--------|
| Inception | Week 1 | Definisi MVP, setup Git & tools | ✅ Selesai |
| Iterasi 1 | Week 2–3 | Low-fidelity prototype | ✅ Selesai |
| Iterasi 2 | Week 4–5 | High-fidelity prototype + API Spec | ✅ Selesai |
| **Sprint 1 (MVP)** | Week 6–7 | Login, RFID tap, 6 Dashboard | ✅ Selesai |
| **Sprint 2** | Week 8–9 | Laporan, Notifikasi, User Mgmt | ✅ Selesai |
| **Refine** | Week 10–11 | Testing, UAT, Polishing | 🔄 Sedang Berjalan |
| Deployment | Week 12 | Production + Pelatihan | ⏳ Belum Mulai |

### 9.2 Checklist Fitur per Sprint

#### Sprint 1 — MVP Core ✅
- [x] **BE-01:** Project Setup & Database (19 tabel)
- [x] **BE-02:** Authentication JWT (login/logout 6 role)
- [x] **BE-03:** Absensi RFID Core (validasi, status otomatis)
- [x] **BE-04:** Rekapitulasi Basic (kelas, siswa, sekolah)
- [x] **FE-01:** Project Setup (React + Vite + MUI)
- [x] **FE-02:** Halaman Login
- [x] **FE-03:** Dashboard 6 Role
- [x] **FE-04:** Halaman Rekap Kelas
- [ ] **HW-01:** ESP8266 + RFID Firmware (end-to-end test pending)

#### Sprint 2 — Extended Features ✅
- [x] **BE-05:** Generate Laporan PDF/Excel
- [x] **BE-06:** Manual Input Absensi (Guru Piket)
- [x] **BE-07:** Notifikasi
- [x] **BE-08:** User Management CRUD
- [x] **FE-05:** Halaman Generate Laporan
- [x] **FE-06:** Halaman Manual Input
- [x] **FE-07:** Komponen Notifikasi
- [x] **FE-08:** Halaman User Management

#### Refine & Polish 🔄 (Sedang Berjalan)
- [x] Izin Pengajuan (backend + tabel)
- [x] Sengketa Absensi (backend + tabel)
- [x] MQTT Client Integration (real-time updates)
- [x] Dashboard service aggregation
- [ ] Unit & Integration Testing (target >80% coverage)
- [ ] UAT dengan stakeholder SMK
- [ ] Hardware end-to-end test

### 9.3 Persentase Progress Keseluruhan

```
┌─────────────────────────────────────────────────────────────┐
│ Backend API        ████████████████████░░  85%  (27/27 EP)  │
│ Database & Model   ████████████████████    100% (19/19 tbl) │
│ Frontend Pages     ████████████████░░░░░░  75%  (10 pages)  │
│ Hardware IoT       ████████░░░░░░░░░░░░░░  40%  (firmware)  │
│ Testing            ████████░░░░░░░░░░░░░░  40%  (unit test) │
│ Dokumentasi        ████████████████░░░░░░  75%  (docs)      │
│ ─────────────────────────────────────────────────────────── │
│ TOTAL PROGRESS     ████████████████░░░░░░  ~72%             │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Dokumentasi Proyek

### 10.1 Dokumen yang Tersedia

| Dokumen | Lokasi | Keterangan |
|---------|--------|------------|
| Software Requirements Spec (SRS) | `docs/requirements/SRS.md` | FR-01 s/d FR-07, NFR-01 s/d NFR-04 |
| Feature Roadmap | `docs/feature_roadmap.md` | MoSCoW prioritas, 471 baris |
| API Specification (OpenAPI 3.0) | `docs/design/API_endpoints.yaml` | 27 endpoints, 45KB |
| API Endpoints List | `docs/design/API_ENDPOINTS_LIST.md` | Dokumentasi detail per endpoint |
| Struktur Tabel Database | `docs/design/struktur_table.md` | 19 tabel, relasi, seed data |
| Checklist Lean Prototyping | `docs/CHECKLIST_LEAN_PROTOTYPING.md` | Tracking metodologi |
| Development Guide | `docs/DEVELOPMENT_GUIDE.md` | Panduan setup & development |
| Status Projek | `docs/status_projek.md` | Ringkasan progress terkini |

### 10.2 Diagram UML yang Tersedia

| Diagram | File |
|---------|------|
| Sequence Diagram 01 | `docs/design/SD-01.png` |
| Sequence Diagram 01 (Alt) | `docs/design/SD-01 Alternative.png` |
| Sequence Diagram 02 | `docs/design/SD-02.png` |
| Sequence Diagram 03 | `docs/design/SD-03 (1).png` |
| Sequence Diagram 04 | `docs/design/SD-04.png` |
| Sequence Diagram 05 | `docs/design/SD-05.png` |
| Sequence Diagram 06 | `docs/design/SD-06.png` |
| Sequence Diagram 07 | `docs/design/SD-07.png` |

---

## 11. Git History & Kolaborasi

### 11.1 Commit History (Terbaru)

| Hash | Commit Message |
|------|---------------|
| `ac73bba` | feat: add project documentation, database seed, and sample report files |
| `7933822` | feat: initialize frontend architecture, core pages, and system documentation |
| `1590e7e` | feat: initialize full-stack SIKAP project with core backend services |
| `5be905b` | feat: implement user management routes, school info model, and frontend pages |
| `26c5c47` | Merge pull request #13 (feature06) |
| `1286c77` | Merge pull request #12 (feat-komponen-notifikasi) |
| `792b991` | Add unit tests for user and prayer time management |
| `693868d` | Add user management and prayer time routes with admin access control |
| `dedfa7a` | Merge pull request #11 (feat-mqtt-client) |
| `eaa758d` | feat: implement izin and sengketa management modules |

### 11.2 Branch Strategy
- `main` — Production-ready code
- `feature/*` — Feature branches per task (BE-01, FE-03, dll.)
- Pull Request review sebelum merge ke main

---

## 12. Rencana Selanjutnya

### 12.1 Yang Perlu Diselesaikan (Week 10-12)

| Prioritas | Tugas | PIC |
|-----------|-------|-----|
| 🔴 Tinggi | End-to-end test hardware RFID ↔ API | Backend/Hardware |
| 🔴 Tinggi | Integration test frontend ↔ backend semua flow | Semua |
| 🟡 Sedang | Unit test coverage >80% (pytest) | Backend |
| 🟡 Sedang | UAT dengan stakeholder SMK (1-2 hari on-site) | Semua |
| 🟢 Normal | Auto-generate Surat Peringatan (cron job) | Backend |
| 🟢 Normal | UI/UX Polish (responsive mobile, loading states) | Frontend |
| 🟢 Normal | Deployment production (MySQL + Nginx + SSL) | Backend |
| 🟢 Normal | User manual & training session | Semua |

### 12.2 Deployment Plan

```
Production Environment:
├── Server: VPS / On-premise PC di SMK
├── Database: MySQL 8 (production)
├── Backend: Flask + Waitress + Nginx (reverse proxy)
├── Frontend: React production build (static files)
├── SSL: Let's Encrypt / self-signed
└── Hardware: ESP8266 installed di pintu masjid
```

---

## 13. Kesimpulan

### 13.1 Capaian Utama
1. **Database lengkap** — 19 tabel dengan relasi kompleks telah berhasil dibangun
2. **Backend API fungsional** — 27 endpoint REST API dengan autentikasi JWT dan RBAC
3. **Frontend responsif** — 10 halaman utama dengan Material UI dan visualisasi Recharts
4. **Arsitektur scalable** — Docker Compose dengan 8 service terintegrasi
5. **Dokumentasi lengkap** — SRS, API Spec, ERD, dan 7 sequence diagram

### 13.2 Nilai Tambah Proyek
- **Otomatisasi penuh** — dari tap RFID hingga laporan PDF
- **Multi-role** — 6 jenis pengguna dengan hak akses berbeda
- **Real-time** — dukungan MQTT untuk update dashboard tanpa refresh
- **Auditability** — setiap perubahan data tercatat di `audit_log`
- **Containerized** — seluruh infrastruktur dapat dideploy dengan satu perintah `docker compose up`

### 13.3 Pelajaran yang Didapat
- Pentingnya perencanaan database schema sebelum coding
- Manfaat metodologi Lean + Rapid Prototyping untuk iterasi cepat
- Kompleksitas integrasi multi-layer (hardware ↔ backend ↔ frontend)
- Pentingnya role-based access control dalam sistem multi-user

---

> **Kelompok 1 — Sistem Informasi — Universitas Siliwangi**  
> **SMK Bina Putra Nusantara · Semester Genap 2025/2026**
