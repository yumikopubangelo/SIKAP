# 🕌 SIKAP
### Sistem Informasi Kepatuhan Absensi Peserta Didik

> Sistem absensi sholat otomatis berbasis RFID & IoT untuk SMK Bina Putra Nusantara

[![Status](https://img.shields.io/badge/Status-In%20Development-yellow)]()
[![Stack](https://img.shields.io/badge/Stack-Flask%20%7C%20React%20%7C%20MySQL-blue)]()
[![Metodologi](https://img.shields.io/badge/Metodologi-Lean%20%2B%20Prototyping-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![Node](https://img.shields.io/badge/Node.js-18+-green)]()

---

## 📚 Tentang Proyek

**SIKAP** adalah sistem informasi yang mencatat kehadiran ibadah sholat siswa secara otomatis menggunakan kartu RFID. Siswa cukup tap kartu saat masuk masjid — sistem langsung mencatat, merekap, dan mengirim laporan ke wali kelas maupun orang tua secara real-time.

| Info | Detail |
|------|--------|
| **Mata Kuliah** | Rancang Bangun Perangkat Lunak (RKBL) |
| **Dosen** | Erna Haerani, S.T., M.Kom. |
| **Semester** | Genap 2025/2026 |
| **Prodi** | Sistem Informasi — Universitas Siliwangi |
| **Kelompok** | 1 |

### 👥 Tim Pengembang

| No | Nama | NIM | Role |
|----|------|-----|------|
| 1 | Azzahra Putri Aulia | 247007111014 | UI/UX Designer (Lead) |
| 2 | Maitsa Wahsfa Syahira | 247007111008 | UI/UX Designer |
| 3 | Hegira Musyafa Kartiwan | 247007111028 | Backend Developer (Lead) |
| 4 | Ramadhan Bagus Hendrawan | 247007111030 | Backend Developer + Hardware |

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔖 **Absensi RFID Otomatis** | Tap kartu → sistem catat waktu, tentukan status (tepat waktu / terlambat / alpha) |
| 📊 **Dashboard Multi-Role** | 6 dashboard berbeda: Admin, Kepsek, Wali Kelas, Guru Piket, Siswa, Orang Tua |
| 📄 **Laporan PDF/Excel** | Generate rekap kehadiran per siswa / kelas / sekolah otomatis |
| 🔔 **Notifikasi Surat Peringatan** | SP1/SP2/SP3 otomatis dikirim ke orang tua jika alpha melebihi threshold |
| ✏️ **Manual Input** | Guru Piket bisa input manual jika kartu hilang atau rusak |
| 📱 **Real-time Monitoring** | Status perangkat ESP8266 dan absensi update secara real-time |

---

## 🛠️ Tech Stack

### Frontend
| Library | Versi | Fungsi |
|---------|-------|--------|
| React | 18+ | UI Framework |
| Material-UI (MUI) | 5+ | Component Library |
| Recharts | 2+ | Charts (line, bar, pie) |
| React Hook Form | 7+ | Form handling & validasi |
| Axios | 1+ | HTTP Client (API calls) |
| Vite | 5+ | Build Tool |

### Backend
| Library | Versi | Fungsi |
|---------|-------|--------|
| Python | 3.10+ | Bahasa pemrograman |
| Flask | 3+ | Web Framework |
| Flask-JWT-Extended | 4+ | JWT Authentication |
| Flask-SQLAlchemy | 3+ | ORM Database |
| Flask-Migrate | 4+ | Database Migrations |
| ReportLab | 4+ | Generate PDF |
| OpenPyXL | 3+ | Generate Excel |

### Database & Hardware
| Teknologi | Fungsi |
|-----------|--------|
| MySQL 8.0 | Database utama |
| ESP8266 (NodeMCU) | Modul WiFi IoT |
| MFRC522 | RFID Reader |
| Kartu RFID 13.56MHz | ID Card Siswa |

---

## 📁 Struktur Folder

```
sikap/
│
├── 📄 README.md                         ← File ini
├── 📄 .gitignore
├── 📄 .env.example                      ← Template environment variables
│
├── 📁 docs/                             ← Semua dokumentasi projek
│   ├── 01-requirements/
│   │   ├── SRS.md
│   │   └── user-stories.md
│   ├── 02-design/
│   │   ├── ERD.png / ERD.drawio
│   │   ├── class-diagram.png
│   │   ├── use-case-diagram.png
│   │   ├── sequence-diagrams/           ← SD-01 sampai SD-07
│   │   ├── activity-diagrams/           ← P001 sampai P003
│   │   ├── architecture-diagram.png
│   │   └── API_Specification.yaml       ← OpenAPI 3.0 (30 endpoints)
│   ├── 03-mockups/
│   │   ├── low-fidelity/                ← Wireframe F001–F027
│   │   └── high-fidelity/               ← Final mockup F001–F027
│   ├── 04-database/
│   │   └── struktur-tabel.md
│   └── 05-final-report/
│       └── Laporan_Akhir_SIKAP.docx
│
├── 📁 backend/                          ← Flask API Server
│   ├── run.py                           ← Entry point: python run.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env                             ← JANGAN di-commit ke Git!
│   ├── app/
│   │   ├── __init__.py
│   │   ├── extensions.py
│   │   ├── models/                      ← 18 tabel SQLAlchemy
│   │   ├── routes/                      ← 30 API endpoints
│   │   ├── services/                    ← Business logic
│   │   ├── middleware/                  ← JWT & Role validation
│   │   └── utils/
│   ├── migrations/
│   └── static/generated/               ← File PDF/Excel hasil generate
│
├── 📁 frontend/                         ← React App
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── pages/                       ← F001–F027 (dibagi per role)
│       │   ├── general/                 ← Splash, Home, Login
│       │   ├── admin/                   ← Dashboard, User Mgmt, Data Master
│       │   ├── kepsek/                  ← Dashboard, Rekap Sekolah, Laporan
│       │   ├── wali-kelas/              ← Dashboard, Rekap Kelas, Edit Absensi
│       │   ├── guru-piket/              ← Dashboard, Manual Input
│       │   ├── siswa/                   ← Dashboard, Riwayat
│       │   ├── orangtua/                ← Dashboard, Riwayat Anak, Notif SP
│       │   └── shared/                  ← Notifikasi, Reset PW, Profil
│       ├── components/
│       │   ├── layout/                  ← Navbar, Sidebar, DashboardLayout
│       │   ├── common/                  ← SummaryCard, StatusBadge, ConfirmDialog
│       │   ├── tables/                  ← DataTable, RekapTable
│       │   ├── charts/                  ← TrendLineChart, StatusPieChart
│       │   └── forms/                   ← SearchFilter, DateRangePicker
│       ├── services/                    ← Axios API calls
│       ├── context/                     ← AuthContext, NotifikasiContext
│       ├── hooks/                       ← useAuth, useNotifikasi, useDebounce
│       └── utils/                       ← formatDate, roleRedirect
│
├── 📁 hardware/                         ← ESP8266 + RFID firmware
│   └── esp8266_rfid/
│       ├── esp8266_rfid.ino
│       ├── config.h.example             ← Copy jadi config.h lalu isi
│       └── README.md
│
├── 📁 database/                         ← SQL scripts
│   ├── schema.sql                       ← CREATE TABLE 18 tabel
│   ├── seed.sql                         ← Data awal
│   └── migrations/
│
├── 📁 tests/                            ← Semua file testing
│   ├── backend/
│   │   ├── conftest.py                  ← Pytest fixtures
│   │   ├── unit/                        ← Test per fungsi/service
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_absensi_service.py
│   │   │   └── test_sp_service.py
│   │   └── integration/                 ← Test API endpoint
│   │       ├── test_auth_routes.py
│   │       ├── test_absensi_routes.py
│   │       └── test_laporan_routes.py
│   ├── frontend/
│   │   └── components/
│   │       ├── Login.test.jsx
│   │       └── StatusBadge.test.jsx
│   └── docs/
│       ├── test-plan.md                 ← Rencana & strategi testing
│       ├── test-cases.md                ← Tabel TC-001 sampai TC-0XX
│       └── uat-results.md               ← Hasil UAT dengan stakeholder SMK
│
└── 📁 scripts/                          ← Script utilitas
    ├── sync_siswa.py                    ← Import data siswa dari Excel
    ├── generate_sp.py                   ← Trigger generate SP manual
    └── backup_db.sh                     ← Backup database MySQL
```

---

## 🧪 Kenapa Ada Folder `tests/` Terpisah?

Folder `tests/` di root dipilih supaya semua file testing terkumpul di satu tempat dan mudah diconfigure untuk CI/CD. Isinya dibagi menjadi tiga bagian:

**`tests/backend/unit/`** — Test per fungsi/service secara terisolasi, contohnya: apakah logika penentuan status "tepat waktu / terlambat / alpha" sudah benar berdasarkan timestamp tap vs waktu iqamah.

**`tests/backend/integration/`** — Test API endpoint secara end-to-end, mulai dari request masuk hingga response keluar, termasuk validasi JWT dan cek role.

**`tests/frontend/components/`** — Test React components, memastikan render dan interaksi form berjalan sesuai ekspektasi.

**`tests/docs/`** — Dokumen test plan dan hasil UAT yang bisa dilampirkan di laporan UAS sebagai bukti pengujian.

Target coverage: **>80% untuk backend**, test manual untuk 5 skenario UAT utama bersama stakeholder SMK.

---

## 🗺️ Metodologi: Lean + Rapid Prototyping

```
Week 1      Inception         → Definisi MVP, setup Git & tools
Week 2–3    Iterasi 1         → Low-fidelity prototype + demo ke dosen
Week 4–5    Iterasi 2         → High-fidelity prototype + demo ke SMK
Week 6–7    Sprint 1 (MVP)    → Login, RFID tap, 6 Dashboard ← demo aplikasi nyata!
Week 8–9    Sprint 2          → Laporan, Notifikasi, User Management
Week 10–11  Refine            → Polish UI, Unit Test, UAT
Week 12     Deployment        → Production, Pelatihan Guru, Laporan Akhir
```

---

## 🚀 Cara Menjalankan Projek

### Prasyarat

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [MySQL 8.0+](https://dev.mysql.com/downloads/)
- [Arduino IDE](https://www.arduino.cc/en/software) — untuk upload firmware ESP8266

---

### 1. Clone Repository

```bash
git clone https://github.com/[username]/sikap.git
cd sikap
```

### 2. Setup Database

```bash
# Buat database
mysql -u root -p -e "CREATE DATABASE sikap_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import schema dan seed data
mysql -u root -p sikap_db < database/schema.sql
mysql -u root -p sikap_db < database/seed.sql
```

### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp ../.env.example .env
# Edit .env: isi DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY

python run.py
# Server jalan di http://localhost:5000
```

### 4. Setup Frontend

```bash
cd frontend
npm install

cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:5000

npm run dev
# App jalan di http://localhost:5173
```

### 5. Setup Hardware

```bash
cd hardware/esp8266_rfid
cp config.h.example config.h
# Edit config.h: WiFi SSID, password, API_URL

# Buka esp8266_rfid.ino di Arduino IDE
# Install library: MFRC522, ESP8266WiFi, ESP8266HTTPClient, ArduinoJson
# Board: NodeMCU 1.0 (ESP-12E Module)
# Upload ke ESP8266
```

### 6. Jalankan Testing

```bash
# Backend — dari folder root
cd backend && source venv/bin/activate
pytest ../tests/backend/ -v
pytest ../tests/backend/ --cov=app --cov-report=html   # dengan coverage report

# Frontend
cd frontend
npm run test
```

---

## 🔑 Akun Default (Setelah Seed)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Kepala Sekolah | `kepsek` | `kepsek123` |
| Wali Kelas | `walikelas` | `wali123` |
| Guru Piket | `gurupiket` | `piket123` |
| Siswa (contoh) | `siswa001` | `siswa123` |
| Orang Tua (contoh) | `ortu001` | `ortu123` |

> ⚠️ **Ganti semua password default sebelum deploy ke production!**

---

## 🔌 API Quick Reference

Base URL: `http://localhost:5000/api/v1`

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `POST` | `/auth/login` | Login semua role |
| `POST` | `/auth/logout` | Logout |
| `POST` | `/absensi` | Catat absensi (RFID/manual) |
| `GET` | `/absensi` | List riwayat absensi |
| `PUT` | `/absensi/{id}` | Edit absensi |
| `GET` | `/rekapitulasi/kelas/{id}` | Rekap per kelas |
| `GET` | `/rekapitulasi/siswa/{id}` | Rekap per siswa |
| `GET` | `/rekapitulasi/sekolah` | Rekap seluruh sekolah |
| `POST` | `/laporan/generate` | Generate PDF/Excel |
| `GET` | `/notifikasi` | List notifikasi user |

📄 Spec lengkap: `docs/02-design/API_Specification.yaml`  
🌐 Swagger UI (saat server jalan): `http://localhost:5000/api-docs`

---

## 🔐 Keamanan

- **JWT Authentication** — Token expire 24 jam
- **Role-Based Access Control** — 6 role, permission berbeda-beda
- **bcrypt** — Hash password sebelum disimpan
- **SQLAlchemy ORM** — Mencegah SQL Injection
- **Audit Log** — Semua perubahan data absensi tercatat (siapa, kapan, apa)
- **HTTPS** — Wajib di environment production

---

## 📊 Progress

| Sprint | Target | Status |
|--------|--------|--------|
| Week 1: Inception | Definisi MVP, setup Git | ✅ Selesai |
| Week 2–3: Iterasi 1 | Low-fi prototype | ✅ Selesai |
| Week 4–5: Iterasi 2 | High-fi prototype + API Spec | ✅ Selesai |
| Week 6–7: Sprint 1 | MVP (Login, RFID, Dashboard BE) | ✅ Selesai (Backend Selesai) |
| Week 8–9: Sprint 2 | Laporan, Notifikasi, User Mgmt BE | ✅ Selesai (Backend Selesai) |
| Week 10–11: Refine | Testing, UAT, Polishing Bug API | 🔄 Sedang Berjalan |
| Week 12: Deployment | Production + Pelatihan | ⏳ Belum Mulai |

---

## 📞 Kontak

**Dosen Pengampu:** Erna Haerani, S.T., M.Kom. — `[email dosen]`

**Tim Pengembang:** `[Nama 1]` · `[Nama 2]` · `[Nama 3]` · `[Nama 4]`

---



SMK Bina Putra Nusantara · Universitas Siliwangi — Program Studi Sistem Informasi

---

_Dibuat oleh Kelompok 1 — SI UNSIL 2026_