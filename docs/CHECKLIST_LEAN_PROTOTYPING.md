# ✅ CHECKLIST UAS RKPL - LEAN + RAPID PROTOTYPING
## SISTEM ABSENSI SHOLAT ONLINE SMK BINA PUTRA NUSANTARA

**Mata Kuliah:** Rancang Bangun Perangkat Lunak  
**Dosen:** Erna Haerani, S.T., M.Kom.  
**Metode:** **LEAN Software Development + Rapid Prototyping**  
**Jumlah Anggota:** 4 orang

---

## 🎯 **KENAPA LEAN + PROTOTYPING?**

### **Karakteristik Proyek:**
- ✅ Tim kecil (4 orang) → Lean cocok untuk small team
- ✅ Butuh feedback cepat → Prototyping bisa demo early
- ✅ Stakeholder non-teknis (guru, siswa) → Prototype lebih mudah dipahami
- ✅ Timeline ketat (12 minggu) → Lean eliminate waste
- ✅ Sudah ada mockup kasar di SRS → Tinggal iterate

### **Keunggulan vs Waterfall:**
| Aspek | Waterfall | Lean + Prototyping |
|-------|-----------|-------------------|
| Feedback | Late (pas testing) | Early (pas prototype) |
| Risk | High (kalau salah requirement) | Low (validasi tiap iterasi) |
| Dokumentasi | Heavy (semua detail di awal) | Light (cukup yang berguna) |
| Flexibility | Rigid | Flexible |
| Cocok untuk | Requirements jelas 100% | Requirements bisa berubah |

---

## 📅 **TIMELINE (12 WEEKS)**

### **WEEK 1: INCEPTION** 🚀
**Tujuan:** Kickoff, prioritize, setup

**Tim UI/UX:**
- [V] Meeting kelompok: discuss metode Lean + Prototyping
- [V] Define MVP (Minimum Viable Product):
  - Must Have: Login, Dashboard 6 role, Absensi RFID, Rekap basic
  - Should Have: Generate laporan, Manual input, Notifikasi
  - Could Have: Auto-generate SP, Real-time MQTT, Chat
- [V] Setup Figma (create project, invite team)
- [V] Buat design system awal (color palette, typography, spacing)

**Tim Dokumentasi Sistem:**
- [V] Setup Git repository
- [V] Buat README.md, .gitignore, LICENSE
- [ ] Meeting dengan dosen: jelaskan pilihan metode Lean + Prototyping
- [V] Mulai Skema Relasi (18 tabel - prioritize core tables dulu)

**Deliverable:**
- [ ] Meeting notes (hasil diskusi MVP)
- [V] Git repository ready
- [V] Design system initial (Figma)

---

### **WEEK 2-3: ITERASI 1 - LOW-FIDELITY PROTOTYPE** ✏️
**Tujuan:** Wireframe cepat, validasi flow

**Tim UI/UX:**
- [V] **High-Fi Wireframe F001-F009** (Auth + 6 Dashboards)
- [V] **High-Fi Wireframe F010-F027** (Feature pages)
- [V] **Clickable Prototype** di Figma (low-fi)
  - Link wireframes (klik button Login → ke Dashboard)
  - Basic interaction (tidak perlu animasi)

**Tim Dokumentasi Sistem:**
- [V] **ERD + Diagram Relasi** (focus on core tables first)
  - User, Siswa, Kelas, Absensi, WaktuSholat, SesiSholat (6 tabel utama dulu)
- [V] **Struktur Tabel** (6 tabel core - format WAJIB)
- [V] **Sequence Diagram SD-01, SD-02** (critical flows):
  - SD-01: Tap Kartu RFID → Simpan Absensi
  - SD-02: Login Multi-Role

**🎯 MILESTONE: DEMO KE DOSEN (End of Week 3)**
- [V] Present High-fi prototype (clickable Figma)

**Deliverable:**

- [V] ERD + Struktur Tabel (6 core tables)
- [V] Sequence Diagram SD-01, SD-02


---

### **WEEK 4-5: ITERASI 2 - HIGH-FIDELITY PROTOTYPE** 🎨
**Tujuan:** Detail design, polish UI/UX

**Tim UI/UX:**
- [V] **High-Fi Mockup F001-F009** (Auth + Dashboards)
  - Apply colors (sesuai design system)
  - Real fonts (Arial 12pt, dll)
  - Icons, images, spacing
  - Gunakan real data (contoh nama siswa, rekap absensi)
- [V] **High-Fi Mockup F010-F027** (Feature pages)
  - Detail component (button, input, table, chart)
  - Responsive design (desktop + mobile)
- [V] **Interactive Prototype** (Figma advanced)
  - Hover states, click animations
  - Modal/popup interactions
  - Form validation feedback

**Tim Dokumentasi Sistem:**
- [V] **Struktur Tabel** (12 tabel remaining)
- [V] **Sequence Diagram SD-03 sampai SD-07** (5 diagram remaining):
  - SD-03: Edit Absensi (Wali Kelas)
  - SD-04: Verifikasi Sengketa (Guru Piket)
  - SD-05: Generate Laporan
  - SD-06: Auto-Generate SP
  - SD-07: Real-time MQTT
- [V] **API Specification** (OpenAPI/Swagger - 27 endpoints)
  - Authentication (3 endpoints)
  - Absensi (5 endpoints)
  - Rekapitulasi (3 endpoints)
  - dst. (total 27)
- [V] **Arsitektur Layered** (diagram + penjelasan)

**Deliverable:**
- [V] High-Fi Mockup F001-F027 (Figma)
- [V] Interactive Prototype (Figma)
- [V] Perancangan Data.docx (Skema + ERD + Struktur Tabel 18 tabel)
- [V] Diagram UML.docx (Sequence Diagram 7 diagram)
- [V] API_Specification.yaml
- [V] Perancangan Arsitektural.docx


---

### **WEEK 6-7: SPRINT 1 - MVP CORE FEATURES** 💻
**Tujuan:** Build working prototype (bisa jalan, bisa demo)

**FOCUS: MUST HAVE FEATURES**

**Tim Backend (2 orang):**
- [ ] **Setup Project**
  - Flask project structure
  - Database setup (MySQL)
  - SQLAlchemy models (6 core tables)
  - Migrations
- [ ] **Authentication Module**
  - JWT login/logout
  - Role-based access (6 roles)
  - Middleware authorization
  - API: POST /api/v1/auth/login, /logout
- [ ] **Absensi Module (CORE!)**
  - API: POST /api/v1/absensi (dari RFID)
  - Validasi: check kartu, check sesi aktif, tentukan status
  - Save ke MySQL
  - API: GET /api/v1/absensi (list)
- [ ] **Rekapitulasi Module (Basic)**
  - API: GET /api/v1/rekapitulasi/kelas/{id}
  - Aggregate: total hadir, terlambat, alpha per siswa
  - Return JSON
- [ ] **Unit Tests** (pytest)
  - test_auth.py (login, logout, token validation)
  - test_absensi.py (create, validate waktu)

**Tim Frontend (2 orang):**
- [ ] **Setup Project**
  - React + Vite
  - Material-UI (MUI)
  - React Router (routing)
  - Axios (API calls)
- [ ] **Authentication Pages**
  - F003: Login (form + API call + JWT storage + redirect)
  - ProtectedRoute component
- [ ] **Dashboards (6 role)**
  - F004: Dashboard Admin (cards: total siswa, hadir hari ini, alpha)
  - F005: Dashboard Kepsek (overview sekolah, grafik trend)
  - F006: Dashboard Wali Kelas (tabel rekap kelas, color indicator)
  - F007: Dashboard Guru Piket (list sengketa hari ini)
  - F008: Dashboard Siswa (riwayat pribadi 7 hari)
  - F009: Dashboard Orang Tua (data anak, riwayat, SP)
- [ ] **Rekapitulasi Page (Basic)**
  - F019: Rekap Kelas (tabel siswa, persentase kehadiran)
  - Filter: tanggal, waktu sholat
  - API call: GET /rekapitulasi/kelas/{id}

**Hardware (dikerjakan Tim Backend - 1 orang):**
- [ ] **ESP8266 + RFID Firmware**
  - Read RFID UID
  - POST ke API /api/v1/absensi (WiFi)
  - LED indicator (hijau = sukses, merah = gagal)
  - Test with 10 kartu RFID

**🎯 MILESTONE: SPRINT 1 DEMO (End of Week 7)**
- [ ] **Working MVP:**
  - Siswa tap kartu → data masuk DB → tampil di dashboard wali kelas
  - Guru bisa login → lihat dashboard sesuai role
  - Wali kelas bisa lihat rekap kelas basic
- [ ] **Demo ke Dosen:**
  - Live demo (bukan mockup, tapi aplikasi jalan!)
  - Show RFID tap → real-time dashboard update (kalau MQTT sudah ada)
- [ ] Dapat feedback: Bug apa? Fitur apa yang priority selanjutnya?

**Deliverable:**
- [ ] Backend MVP (running di localhost)
- [ ] Frontend MVP (running di localhost)
- [ ] ESP8266 firmware (tested)
- [ ] Sprint 1 Demo Video (10-15 menit)

---

### **WEEK 8-9: SPRINT 2 - EXTENDED FEATURES** 🚀
**Tujuan:** Add SHOULD HAVE features

**Tim Backend:**
- [ ] **Laporan Module**
  - API: POST /api/v1/laporan/generate
  - Generate PDF (ReportLab) / Excel (openpyxl)
  - Save file ke /static/laporan/
  - Return download URL
- [ ] **Manual Input (Guru Piket)**
  - API: POST /api/v1/absensi/manual
  - Validasi: hanya Guru Piket yang bisa
  - Flag: "verified_by_guru_piket"
  - Insert ke AuditLog
- [ ] **Notifikasi Module (Basic)**
  - API: POST /api/v1/notifikasi/send
  - Simpan ke tabel Notifikasi
  - API: GET /api/v1/notifikasi (list per user)
  - Mark as read: PUT /api/v1/notifikasi/{id}/read
- [ ] **User Management CRUD**
  - API: POST /api/v1/users (create)
  - API: GET /api/v1/users (list - admin only)
  - API: PUT /api/v1/users/{id} (update)
  - API: DELETE /api/v1/users/{id} (delete)

**Tim Frontend:**
- [ ] **Generate Laporan Page**
  - F022: Form (pilih kelas, periode, format PDF/Excel)
  - API call: POST /laporan/generate
  - Download file (klik link)
- [ ] **Manual Input Page (Guru Piket)**
  - F023: Form (NISN, tanggal, waktu sholat, status, keterangan)
  - Validation (cek apakah NISN valid)
  - API call: POST /absensi/manual
- [ ] **Notifikasi Component**
  - F024: List notifikasi (badge unread count)
  - Click → mark as read
  - Real-time update (polling setiap 30 detik - belum MQTT)
- [ ] **User Management Page (Admin)**
  - F010: Table users (username, role, email, action)
  - F010A: Form tambah user
  - F010B: Form edit user
  - CRUD operations

**Testing (Both Teams):**
- [ ] Integration Testing (Frontend ↔ Backend)
  - Test login flow end-to-end
  - Test RFID tap → dashboard update
  - Test generate laporan → file downloaded
- [ ] Bug Fixing (track bugs di GitHub Issues)

**🎯 MILESTONE: SPRINT 2 DEMO (End of Week 9)**
- [ ] **Extended MVP:**
  - Guru piket bisa manual input absensi
  - Wali kelas bisa generate laporan PDF/Excel
  - Admin bisa CRUD user
  - Notifikasi basic working
- [ ] **Demo ke Stakeholder:**
  - Show ke guru SMK
  - Explain: "Begini cara manual input kalau ada siswa lupa tap"
- [ ] Dapat feedback untuk polish

**Deliverable:**
- [ ] Sprint 2 features implemented
- [ ] Integration test results
- [ ] Sprint 2 Demo Video

---

### **WEEK 10-11: REFINE & POLISH** ✨
**Tujuan:** Add COULD HAVE features + polish UI/UX + testing

**Tim Backend:**
- [ ] **Auto-Generate SP (Cron Job)**
  - Script: `scripts/generate_sp.py`
  - Daily check (APScheduler)
  - Query siswa alpha >N kali
  - Generate SP (insert tabel SuratPeringatan)
  - Send notifikasi ke orang tua + wali kelas
- [ ] **Real-time MQTT (Optional - if time permits)**
  - Setup Mosquitto MQTT Broker
  - Publish event: absensi/realtime (setiap tap kartu)
  - Topic: notifikasi/{user_id}
- [ ] **Elasticsearch Integration (Optional)**
  - Index absensi data
  - Search & analytics endpoint
- [ ] **Performance Optimization**
  - Add indexes (idx_absensi_siswa, idx_absensi_tanggal)
  - Query optimization (reduce N+1 queries)
  - Caching (Flask-Caching for rekap endpoint)

**Tim Frontend:**
- [ ] **Real-time MQTT (if backend ready)**
  - MQTT.js client
  - Subscribe topic: absensi/realtime
  - Auto-update dashboard (without refresh)
- [ ] **UI/UX Polish**
  - Loading indicators (spinner saat API call)
  - Error handling (toast notification untuk error)
  - Responsive design (mobile-friendly)
  - Accessibility (keyboard navigation, ARIA labels)
- [ ] **Grafik & Chart**
  - Dashboard charts (Recharts)
  - Trend kehadiran (line chart)
  - Distribusi status (pie chart)
- [ ] **Additional Pages (if time permits)**
  - F026: Profil Pengguna
  - F027: Data Sekolah
  - F013: Pengaturan Waktu Sholat

**Testing (Both Teams):**
- [ ] **Unit Testing (Coverage >80%)**
  - Backend: pytest --cov
  - Frontend: React Testing Library (if time permits)
- [ ] **System Testing**
  - End-to-end scenarios (siswa tap → SP auto-generated → ortu dapat notif)
  - Load testing (simulate 100 siswa tap bersamaan)
- [ ] **UAT (User Acceptance Testing)**
  - Koordinasi dengan SMK Bina Putra
  - On-site testing (1-2 hari)
  - Collect feedback dari guru, teknisi, siswa (sample)
  - Bug fixing dari UAT

**Deliverable:**
- [ ] Auto-generate SP working (cron job)
- [ ] Real-time MQTT (if implemented)
- [ ] UI/UX polished
- [ ] Test coverage >80%
- [ ] UAT results documented

---

### **WEEK 12: DEPLOYMENT & HANDOVER** 🚢
**Tujuan:** Go live, training, documentation

**Deployment:**
- [ ] **Production Server Setup**
  - MySQL database (create production DB)
  - Elasticsearch + Mosquitto MQTT (if used)
  - Flask backend (Waitress + Nginx)
  - Frontend build (React production build)
  - SSL certificate (HTTPS)
- [ ] **Hardware Installation**
  - Install ESP8266 + RFID Reader di masjid
  - Test connectivity (WiFi + API)
  - Backup device (Reader 2 - redundancy)
- [ ] **Data Migration**
  - Import siswa dari DB sekolah existing
  - Import kelas, guru (if any)
  - Assign RFID cards to siswa
- [ ] **Smoke Testing**
  - Test login production
  - Test RFID tap production
  - Test all critical flows
  - Monitor logs (24 jam pertama)

**Documentation:**
- [ ] **User Manual** (PDF - 10-15 halaman)
  - Untuk Guru: Cara login, lihat rekap, generate laporan
  - Untuk Siswa: Cara tap kartu, lihat riwayat pribadi
  - Untuk Orang Tua: Cara login, lihat data anak
- [ ] **Admin Manual** (PDF - 15-20 halaman)
  - Setup server, database, hardware
  - Troubleshooting (WiFi issue, RFID not detected, dll.)
  - Maintenance tasks (backup DB, update waktu sholat)
- [ ] **API Documentation** (Swagger HTML)
  - Export dari Swagger Editor
  - Host di /api-docs
- [ ] **Deployment Guide** (PDF - 5-7 halaman)
  - Step-by-step deploy to production
  - Environment variables
  - Firewall configuration

**Training:**
- [ ] **Training Session dengan Guru/Teknisi** (2-3 jam)
  - PowerPoint presentation
  - Live demo sistem
  - Hands-on: guru coba login, generate laporan
  - Q&A session
- [ ] **Video Tutorial** (3-5 video, masing-masing 5-10 menit)
  - Video 1: Cara login & navigasi dashboard
  - Video 2: Cara generate laporan PDF/Excel
  - Video 3: Cara manual input absensi (guru piket)
  - Video 4: (Optional) Troubleshooting common issues

**Final Deliverable:**
- [ ] **Laporan Akhir UAS** (PDF - 50-80 halaman)
  - BAB 1: Pendahuluan (latar belakang, tujuan, scope)
  - BAB 2: Metodologi (LEAN + Prototyping - explain why)
  - BAB 3: Analisis & Desain (requirements, prototype iterations, architecture)
  - BAB 4: Implementasi (tech stack, sprint 1-2, code structure)
  - BAB 5: Testing (unit, integration, UAT results)
  - BAB 6: Deployment (server setup, hardware installation)
  - BAB 7: Kesimpulan & Saran
  - Lampiran: Sequence Diagram, API Spec, Test Cases
- [ ] **Source Code** (Git repository - complete with README)
- [ ] **Demo Video Final** (15-20 menit)
  - Introduction proyek
  - Demo RFID tap → dashboard update
  - Demo generate laporan
  - Demo auto-generate SP
  - Conclusion
- [ ] **Presentation Slides** (PowerPoint - 20-30 slides)
  - Untuk presentasi UAS di depan dosen

**🎯 FINAL MILESTONE: UAS PRESENTATION**
- [ ] Present di depan dosen (15-20 menit)
- [ ] Q&A dari dosen
- [ ] Submit all deliverables

---

---

## 📊 **DOKUMENTASI YANG TETAP WAJIB (untuk UAS)**

Meskipun pakai Lean (eliminate waste), beberapa docs tetap WAJIB untuk nilai UAS:

### **✅ CRITICAL DOCUMENTS (WAJIB!):**

1. **Perancangan Data** (10-15 halaman)
   - Skema Relasi (18 tabel)
   - Diagram Relasi (ERD)
   - Struktur Tabel (format WAJIB dari materi dosen)

2. **Diagram UML** (15-20 halaman) ⭐ **MOST IMPORTANT**
   - Use Case Diagram
   - Activity Diagram
   - Class Diagram
   - **Sequence Diagram (7 diagram)** ← Ini yang paling penting!
   - Deployment Diagram

3. **API Specification** (YAML + HTML)
   - OpenAPI 3.0 format (Swagger)
   - 27 endpoints documented

4. **Perancangan Antarmuka** (SIMPLIFIED - 30-50 halaman)
   - Low-Fi Wireframe F001-F027 (sketsa)
   - High-Fi Mockup F001-F027 (final design)
   - Keterangan per form (ukuran, font, navigasi)
   - ⚠️ **Tidak perlu super detail seperti Waterfall** (cukup visual + keterangan singkat)

5. **Arsitektur Layered** (5-7 halaman)
   - Diagram arsitektur
   - Penjelasan layer (Presentation, Application, Data, Hardware)

### **⭕ MEDIUM PRIORITY (Bagus kalau ada, tapi boleh simplified):**

6. **Perancangan Pesan** (3-5 halaman - SIMPLIFIED)
   - Tidak perlu M001-M015 super detail
   - Cukup: screenshot 3-5 pesan representatif (Konfirmasi, Error, Sukses)
   - Explain pattern (semua konfirmasi pakai pattern yang sama)

7. **Flowchart Prosedural** (10-15 halaman - CRITICAL ONLY)
   - P001: Proses Login
   - P002: Proses Tap Kartu RFID ⭐ (yang paling penting!)
   - P003: Auto-Generate SP
   - ⚠️ **Skip P004, P005 jika waktu terbatas** (not critical)

### **❌ BISA DISKIP (Lean - eliminate waste):**

8. ~~Jaringan Semantik super lengkap~~ → Cukup 1 diagram simple di Laporan Akhir
9. ~~State Diagram~~ → Optional, skip jika waktu terbatas
10. ~~Security Design Document terpisah~~ → Explain di section Security di Laporan Akhir

---

---

## 🎯 **LEAN PRINCIPLES APPLIED:**

### **1. Eliminate Waste (Mubazir)**
**Waste yang dihilangkan:**
- ❌ Dokumentasi detail yang tidak dibaca (misal: 80 halaman Perancangan Antarmuka dengan 3 komponen per form → simplified jadi 30-50 halaman dengan visual + keterangan ringkas)
- ❌ Flowchart untuk semua proses (P001-P010) → Fokus hanya critical (P001-P003)
- ❌ Meeting panjang tanpa outcome → Timebox meeting: max 2 jam, harus ada actionable

### **2. Build Quality In**
**Kualitas dari awal:**
- ✅ Prototype iteration (validasi design sebelum coding)
- ✅ Unit testing dari Sprint 1 (bukan nunggu semua selesai)
- ✅ Code review (pull request sebelum merge)
- ✅ Feedback loop (demo tiap 2 minggu)

### **3. Amplify Learning**
**Belajar terus:**
- ✅ Sprint retrospective (apa yang bisa diperbaiki sprint berikutnya?)
- ✅ Feedback dari dosen & stakeholder (incorporate ASAP)
- ✅ Post-mortem bugs (kenapa bug ini muncul? gimana prevent?)

### **4. Decide as Late as Possible**
**Keputusan fleksibel:**
- ⏳ MQTT real-time: Decide di Sprint 2 (tunggu lihat MVP dulu, kalau perlu banget baru implement)
- ⏳ Elasticsearch: Decide di Week 10 (kalau search MySQL cukup fast, skip Elasticsearch)
- ⏳ Chat feature: Decide setelah UAT (kalau user minta, baru add)

### **5. Deliver Fast**
**Cepat rilis:**
- ✅ Sprint 1 (Week 7): MVP sudah jalan (bukan full features, tapi working!)
- ✅ Sprint 2 (Week 9): Extended features
- ✅ Week 12: Production deployment (live!)

### **6. Respect People (Empower Team)**
**Trust tim:**
- ✅ Tim UI/UX: Bebas pilih design (asal sesuai design system)
- ✅ Tim Backend: Bebas pilih library (asal dokumentasi jelas)
- ✅ Self-organizing: Tidak ada micromanagement, tim decide sendiri how to achieve goals

### **7. Optimize the Whole (Holistic)**
**Sistem keseluruhan:**
- ✅ Integration testing (tidak cuma unit test per module)
- ✅ UAT dengan real user (guru, siswa)
- ✅ Production-like environment (staging server for testing)

---

---

## 🔄 **PROTOTYPING ITERATION WORKFLOW:**

```
┌────────────────────────────────────────┐
│  ITERASI 1: LOW-FI (Week 2-3)          │
├────────────────────────────────────────┤
│  1. Sketch wireframe (Figma - basic)   │
│  2. Link wireframes (clickable)        │
│  3. Demo ke dosen                      │
│  4. Dapat feedback:                    │
│     - "Form login terlalu kompleks"    │
│     - "Dashboard admin kurang overview"│
│  5. Revisi wireframe                   │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  ITERASI 2: HIGH-FI (Week 4-5)         │
├────────────────────────────────────────┤
│  1. Apply colors, fonts, spacing       │
│  2. Add real data (contoh siswa)       │
│  3. Interactions (hover, click)        │
│  4. Demo ke stakeholder SMK            │
│  5. Dapat feedback:                    │
│     - "Warna terlalu gelap"            │
│     - "Button kurang jelas"            │
│  6. Finalize design                    │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  IMPLEMENTATION (Week 6-9)             │
├────────────────────────────────────────┤
│  Convert mockup → React components     │
│  (Design sudah validated, risk rendah) │
└────────────────────────────────────────┘
```

**Keuntungan:**
- ✅ Feedback EARLY (bukan pas semua sudah di-code)
- ✅ Revisi MURAH (ganti warna di Figma < 5 menit, ganti warna di code bisa 1 jam)
- ✅ Stakeholder HAPPY (mereka lihat visual, bukan baca dokumentasi 80 halaman)

---

---

## 📋 **PEMBAGIAN TUGAS (4 ORANG - UPDATED)**

### **👨‍🎨 PERSON 1 (UI/UX Lead):**
- Week 1: Setup Figma, design system
- Week 2-3: Low-Fi Wireframe F001-F013
- Week 4-5: High-Fi Mockup F001-F013
- Week 6-7: Frontend - Auth pages + Dashboard (3 role)
- Week 8-9: Frontend - Laporan, Notifikasi
- Week 10-11: Frontend - Polish UI/UX, charts
- Week 12: User Manual, Training materials

### **👨‍🎨 PERSON 2 (UI/UX Support):**
- Week 1: Bantuin design system
- Week 2-3: Low-Fi Wireframe F014-F027
- Week 4-5: High-Fi Mockup F014-F027
- Week 6-7: Frontend - Dashboard (3 role remaining)
- Week 8-9: Frontend - Manual Input, User Management
- Week 10-11: Frontend - Responsive, accessibility
- Week 12: Video tutorials

### **👨‍💻 PERSON 3 (Backend Lead):**
- Week 1: Git setup, README
- Week 2-3: ERD + Struktur Tabel (core 6 tables), SD-01, SD-02
- Week 4-5: Struktur Tabel (remaining 12), SD-03 to SD-07, API Spec
- Week 6-7: Backend - Auth, Absensi module
- Week 8-9: Backend - Laporan, Manual Input
- Week 10-11: Backend - Auto-generate SP, MQTT (optional)
- Week 12: Deployment, Admin Manual

### **👨‍💻 PERSON 4 (Backend Support + Hardware):**
- Week 1: Meeting notes, MVP definition
- Week 2-3: Bantuin ERD
- Week 4-5: API Spec, Arsitektur Layered
- Week 6-7: Backend - Rekapitulasi, Hardware (ESP8266 firmware)
- Week 8-9: Backend - Notifikasi, User Management
- Week 10-11: Backend - Performance optimization, Testing
- Week 12: Hardware installation, Deployment Guide

---

---

## ✅ **SUCCESS METRICS:**

### **Sprint 1 (Week 7):**
- [ ] MVP bisa demo: Login → Tap RFID → Dashboard update
- [ ] 3 core APIs working (auth, absensi, rekapitulasi)
- [ ] 6 dashboards rendered (bisa dummy data dulu)

### **Sprint 2 (Week 9):**
- [ ] Generate laporan PDF/Excel working
- [ ] Manual input working
- [ ] User management CRUD working
- [ ] Integration test pass rate >80%

### **Final (Week 12):**
- [ ] Production deployment sukses (live di server SMK)
- [ ] Hardware installed (ESP8266 di masjid)
- [ ] User training selesai (guru trained)
- [ ] All critical bugs fixed
- [ ] UAS presentation ready

---

---

## 📞 **KONSULTASI DOSEN (PENTING!):**

### **Week 2: Show Metode**
**Agenda:**
- Explain kenapa pilih Lean + Prototyping (bukan Waterfall)
- Show MVP definition (Must/Should/Could)
- Show low-fi wireframe (progress)
- **ASK:** "Apakah metode ini acceptable untuk UAS? Apakah ada dokumentasi tambahan yang wajib?"

### **Week 4: Show Prototype**
**Agenda:**
- Demo high-fi prototype (interactive Figma)
- Walk through flow (login → tap → dashboard)
- Show Sequence Diagram progress (SD-01, SD-02)
- **ASK:** "Apakah design sudah sesuai? Ada yang perlu direvisi?"

### **Week 7: Show MVP**
**Agenda:**
- Demo working application (bukan mockup!)
- Show RFID tap → real data masuk DB
- Explain Sprint 1 achievements
- **ASK:** "Untuk Sprint 2, priority features apa yang paling penting?"

### **Week 10: Final Review**
**Agenda:**
- Demo full features (Sprint 1 + 2 + polish)
- Explain deployment plan
- Show documentation progress (Laporan Akhir outline)
- **ASK:** "Ada yang kurang untuk UAS deliverable?"

---

---

## 🎓 **PERLU DIJELASKAN DI LAPORAN AKHIR:**

### **BAB 2: METODOLOGI**

**2.1 Pemilihan Metode**

"Kelompok kami memilih **Lean Software Development + Rapid Prototyping** sebagai metodologi pengembangan dengan pertimbangan:

1. **Karakteristik Proyek:**
   - Tim kecil (4 orang) → Lean cocok untuk small team
   - Stakeholder non-teknis (guru, siswa) → Prototype lebih mudah dipahami daripada dokumentasi teknis
   - Timeline ketat (12 minggu) → Perlu iterasi cepat dengan feedback loop

2. **Keunggulan vs Waterfall:**
   - **Early feedback:** Prototype di-demo di Week 3 & 5 → dapat feedback sebelum coding (Waterfall: feedback baru pas testing)
   - **Risk mitigation:** Validasi design early → risk salah requirement rendah
   - **Flexibility:** Bisa adjust berdasarkan feedback stakeholder

3. **Lean Principles Applied:**
   - Eliminate waste: Fokus dokumentasi yang berguna (Sequence Diagram, API Spec), skip yang redundant
   - Deliver fast: Sprint 1 (Week 7) MVP sudah jalan, bukan tunggu semua selesai
   - Amplify learning: Sprint retrospective, incorporate feedback cepat

4. **Prototyping Iterations:**
   - Iterasi 1 (Low-Fi): Validasi flow & layout
   - Iterasi 2 (High-Fi): Finalize design & interactions
   - Implementation: Convert validated prototype → code (risk rendah)

Meskipun menggunakan Lean, **dokumentasi design tetap lengkap** untuk memenuhi requirement UAS, termasuk Sequence Diagram (7 diagram), API Specification (27 endpoints), dan Perancangan Data (18 tabel)."

**2.2 Iterasi Prototyping**

[Tabel iterasi, feedback yang didapat, revisi yang dilakukan]

---

---

**SEMANGAT KELOMPOK 1!** 💪🚀

**Dengan LEAN + PROTOTYPING:**
- ✅ Lebih cepat dapat feedback
- ✅ Risk lebih rendah
- ✅ Dokumentasi fokus (tidak waste)
- ✅ Stakeholder lebih happy (lihat visual)
- ✅ Nilai UAS tetap bagus (karena semua critical docs tetap ada)

**START NOW! BUILD, DEMO, LEARN, ITERATE!** 🔥✨

---

_Dibuat dengan ❤️ oleh Claude  
Untuk Kelompok 1 - UAS RKPL  
Metode: Lean + Rapid Prototyping  
Tanggal: 8 Februari 2025_
