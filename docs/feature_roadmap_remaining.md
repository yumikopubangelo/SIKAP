# SIKAP - Roadmap Pekerjaan Tersisa
### Backlog Fitur, Integrasi, dan Validasi yang Belum Selesai
> Disusun dari audit repositori per 12 April 2026

**Tujuan:** memisahkan pekerjaan yang masih terbuka dari `docs/feature_roadmap.md` agar tim bisa fokus pada closure MVP, integrasi nyata, dan kesiapan deploy.  
**Cakupan audit:** `backend/app/routes`, `backend/app/services`, `frontend/src`, `hardware/`, `docs/feature_roadmap.md`

---

## Status Pengerjaan

| Status | Arti |
|--------|------|
| **BELUM ADA** | Artefak utama belum terlihat di codebase |
| **PARSIAL** | Sebagian implementasi sudah ada, tetapi belum end-to-end |
| **PERLU VALIDASI** | Implementasi ada, namun belum dibuktikan pada skenario nyata |
| **BLOCKED** | Tidak bisa ditutup sebelum dependency lain selesai |

---

## Prioritas Eksekusi

| Level | Fokus | Keterangan |
|-------|-------|------------|
| **KRITIS** | Closure MVP | Menutup gap antara demo dan alur nyata RFID |
| **TINGGI** | Fitur Sprint 2 yang masih parsial | Sudah ada sebagian di code, belum utuh |
| **MENENGAH** | QA, UAT, dan deployment readiness | Memastikan sistem siap dipakai |
| **RENDAH** | Refinement dan optimasi | Dikerjakan setelah core stabil |

---

## SPRINT PENYELESAIAN 1 - Closure MVP dan Integrasi RFID

> **Goal:** Tap kartu RFID fisik benar-benar menghasilkan absensi yang tampil di dashboard wali kelas.

### RV-01: Endpoint Absensi RFID Production
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | KRITIS |
| **Status** | BELUM ADA |
| **Deskripsi** | Endpoint khusus untuk menerima payload dari perangkat RFID dan memproses absensi otomatis |
| **API Endpoints** | `POST /absensi` atau `POST /absensi/rfid`, plus `GET /absensi` untuk verifikasi hasil |
| **Logika** | Validasi UID kartu, validasi perangkat, cari sesi aktif, hitung status `tepat_waktu` / `terlambat` / `alpha`, simpan absensi, siapkan event notifikasi bila perlu |
| **Output** | Perangkat dapat mengirim data tap nyata tanpa lewat menu manual input |
| **Dependency** | BE-02, BE-03 data model, RV-02 |
| **Catatan Audit** | Backend saat ini baru memiliki `POST /api/v1/absensi/manual` dan `PUT /api/v1/absensi/{id}` |

### RV-02: Firmware ESP8266 + RFID Siap Integrasi
| Item | Detail |
|------|--------|
| **PIC** | Backend (Hardware) |
| **Prioritas** | KRITIS |
| **Status** | BELUM ADA |
| **Deskripsi** | Firmware untuk membaca UID RFID, mengirim request ke API, dan memberi indikator sukses/gagal |
| **Detail** | Konfigurasi WiFi, mapping endpoint backend, retry saat gagal, timeout, LED hijau/merah, log serial untuk debugging |
| **Output** | Minimal 10 kartu RFID bisa diuji ke server lokal tanpa intervensi manual |
| **Dependency** | RV-01 |
| **Catatan Audit** | Folder `hardware/esp8266_rfid` masih kosong |

### RV-03: Uji End-to-End Tap Kartu ke Dashboard
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | KRITIS |
| **Status** | BELUM ADA |
| **Deskripsi** | Verifikasi alur penuh dari perangkat, backend, database, rekap, sampai dashboard wali kelas |
| **Skenario Uji** | Kartu valid, kartu tidak dikenal, sesi aktif, sesi tidak aktif, absensi ganda, perangkat offline |
| **Output** | Ada bukti bahwa alur utama MVP benar-benar berjalan di lingkungan dev/lab |
| **Dependency** | RV-01, RV-02, FE-03, BE-04 |
| **Catatan Audit** | Checklist Sprint 1 masih menyisakan alur tap kartu dan POST ESP8266 |

### Checklist Closure MVP
- [ ] Endpoint RFID menerima request perangkat nyata
- [ ] UID kartu berhasil dipetakan ke data siswa
- [ ] Status absensi otomatis tersimpan sesuai aturan waktu
- [ ] Data absensi muncul di dashboard wali kelas
- [ ] Minimal 10 kartu diuji dan dicatat hasilnya
- [ ] Ada log error yang jelas untuk kartu/perangkat tidak valid

---

## SPRINT PENYELESAIAN 2 - Menutup Fitur Parsial

> **Goal:** Menyelesaikan fitur yang sebagian sudah ada di codebase, tetapi belum utuh sebagai pengalaman pengguna.

### RV-04: Halaman Generate Laporan (Frontend)
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | TINGGI |
| **Status** | BELUM ADA |
| **Deskripsi** | Halaman UI untuk memilih jenis laporan, filter, format, lalu mengunduh file hasil generate |
| **Halaman** | F022: Generate Laporan |
| **Detail** | Form `jenis`, `filter_id`, periode, format `pdf/excel`, tombol generate, status loading, link download |
| **Output** | User tidak perlu memanggil endpoint laporan secara manual |
| **Dependency** | BE-05 |
| **Catatan Audit** | Backend laporan sudah ada dan sudah dites, tetapi route/halaman frontend belum terlihat |

### RV-05: Data Sekolah dari Backend, Bukan Fallback Frontend
| Item | Detail |
|------|--------|
| **PIC** | Frontend + Backend |
| **Prioritas** | TINGGI |
| **Status** | PARSIAL |
| **Deskripsi** | Ganti profil sekolah statis dengan sumber data backend yang bisa diubah |
| **Halaman** | F027: Data Sekolah |
| **Detail** | Tambah endpoint profil sekolah atau konfigurasi sekolah, lalu tampilkan identitas sekolah tanpa hard-coded fallback |
| **Output** | Nama sekolah, fokus, dan identitas sistem berasal dari satu sumber data resmi |
| **Dependency** | Endpoint profil sekolah atau konfigurasi backend |
| **Catatan Audit** | Halaman Data Sekolah sudah ada, tetapi identitas sekolah masih memakai fallback di frontend |

### RV-06: Kontrak API Notifikasi Disatukan
| Item | Detail |
|------|--------|
| **PIC** | Backend + Frontend |
| **Prioritas** | TINGGI |
| **Status** | PARSIAL |
| **Deskripsi** | Samakan path, bentuk respons, dan perilaku endpoint notifikasi antara backend dan frontend |
| **API Endpoints** | Konsisten di satu namespace, misalnya `/api/v1/notifikasi` atau `/api/notifikasi` |
| **Detail** | Hapus fallback ganda di frontend, rapikan payload unread count, dan sepakati format respons final |
| **Output** | Frontend tidak perlu mencoba beberapa endpoint untuk satu aksi yang sama |
| **Dependency** | BE-07, FE-07 |
| **Catatan Audit** | Frontend masih mencoba dua kandidat path endpoint notifikasi |

### RV-07: Integration Test Frontend <-> Backend Semua Flow Utama
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | TINGGI |
| **Status** | BELUM ADA |
| **Target** | Login, dashboard per role, manual input, user management, notifikasi, laporan, waktu sholat |
| **Tools** | Disarankan Playwright untuk flow UI dan pytest untuk API support data |
| **Output** | Ada regression suite yang memverifikasi alur lintas layer, bukan hanya unit test backend |
| **Dependency** | RV-04, RV-05, RV-06 |
| **Catatan Audit** | Checklist Sprint 2 masih menandai integration test belum selesai |

### Checklist Penutupan Sprint 2
- [ ] Halaman generate laporan bisa dipakai dari UI
- [ ] Data Sekolah tidak lagi bergantung pada fallback hard-coded
- [ ] Endpoint notifikasi konsisten di frontend dan backend
- [ ] Minimal satu regression suite lintas frontend-backend berjalan

---

## BACKLOG TEKNIS DAN PENYELESAIAN PARSIAL

> **Goal:** Merapikan area yang belum menghambat demo utama, tetapi berisiko menjadi sumber bug atau kebingungan tim.

### TD-01: Rapikan Service User Ganda
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MENENGAH |
| **Status** | PARSIAL |
| **Deskripsi** | Konsolidasikan `user_service.py` dan `users_service.py` agar hanya satu sumber logika aktif |
| **Detail** | Hapus service lama yang tidak lagi dipakai, samakan exception, dan pastikan import tidak membingungkan |
| **Output** | Alur CRUD user lebih mudah dirawat dan tidak menyisakan logika usang |
| **Dependency** | RV-07 |
| **Catatan Audit** | Saat ini ada dua service user dengan tanggung jawab yang mirip |

### TD-02: Filter Sengketa Berdasarkan Role
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MENENGAH |
| **Status** | PARSIAL |
| **Deskripsi** | Batasi data sengketa yang bisa dilihat user sesuai role masing-masing |
| **API Endpoints** | `GET /sengketa`, `PUT /sengketa/{id}/resolve` |
| **Detail** | Siswa melihat sengketa miliknya, wali/guru melihat yang relevan, admin punya visibilitas penuh |
| **Output** | Data sengketa tidak terekspos terlalu luas |
| **Dependency** | Kebijakan akses per role |
| **Catatan Audit** | Route sengketa masih memiliki TODO filtering by role |

### TD-03: Lengkapi Service Surat Peringatan
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MENENGAH |
| **Status** | BELUM ADA |
| **Deskripsi** | Isi service surat peringatan agar model dan workflow SP benar-benar bisa dipakai |
| **Detail** | Query threshold alpha, penentuan level SP1/SP2/SP3, generate data surat, catat status kirim, hubungkan ke notifikasi |
| **Output** | Fitur surat peringatan siap dipanggil oleh scheduler atau admin |
| **Dependency** | BE-09, BE-07 |
| **Catatan Audit** | `sp_service.py` masih kosong meskipun model `SuratPeringatan` sudah ada |

---

## REFINE DAN POLISH YANG MASIH TERBUKA

> **Goal:** Menyelesaikan fitur tambahan setelah core closure dan fitur parsial sudah stabil.

### BE-09: Auto-Generate Surat Peringatan
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | RENDAH |
| **Status** | BELUM ADA |
| **Detail** | Scheduler harian untuk mendeteksi siswa dengan alpha melewati threshold dan membuat SP otomatis |
| **Library** | APScheduler |
| **Dependency** | TD-03, BE-07 |

### BE-10: Real-time MQTT Publish dari Backend
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | RENDAH |
| **Status** | BELUM ADA |
| **Detail** | Publish event `absensi/realtime` saat tap kartu berhasil diproses dan siapkan topic notifikasi per user |
| **Broker** | Mosquitto |
| **Dependency** | RV-01 |

### FE-09: Real-time MQTT Client Hardening
| Item | Detail |
|------|--------|
| **PIC** | Frontend |
| **Prioritas** | RENDAH |
| **Status** | PARSIAL |
| **Detail** | Klien MQTT sudah ada, tetapi masih bergantung pada event backend yang belum dipublish secara nyata |
| **Dependency** | BE-10 |
| **Catatan Audit** | Frontend sudah subscribe topic MQTT dan refresh dashboard saat pesan datang |

### BE-11: Elasticsearch Integration
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | RENDAH |
| **Status** | BELUM ADA |
| **Detail** | Index data absensi agar pencarian dan analitik cepat dapat dipakai saat skala data naik |
| **Dependency** | RV-01 |

### BE-12: Performance Optimization
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | RENDAH |
| **Status** | BELUM ADA |
| **Detail** | Tambah index, audit query N+1, cache rekap, dan pengukuran endpoint berat |
| **Dependency** | RV-07 |

### QA-02: UAT dengan Stakeholder Sekolah
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | MENENGAH |
| **Status** | BELUM ADA |
| **Detail** | Uji lapangan dengan guru, wali kelas, guru piket, dan siswa menggunakan skenario nyata |
| **Output** | Daftar temuan UAT, prioritas revisi, dan persetujuan go-live |
| **Dependency** | RV-03, RV-07 |

---

## DEPLOYMENT READINESS

> **Goal:** Menyiapkan sistem agar layak dipasang dan dipakai di lingkungan sekolah.

### DP-01: Production Server
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MENENGAH |
| **Status** | BELUM ADA |
| **Detail** | Siapkan konfigurasi production untuk database, backend, frontend build, reverse proxy, dan HTTPS |

### DP-02: Hardware Installation
| Item | Detail |
|------|--------|
| **PIC** | Backend (Hardware) |
| **Prioritas** | MENENGAH |
| **Status** | BLOCKED |
| **Detail** | Pemasangan ESP8266 + RFID reader di lokasi, pengujian WiFi, pengujian API, dan pembaca cadangan |
| **Dependency** | RV-02, RV-03 |

### DP-03: Data Migration
| Item | Detail |
|------|--------|
| **PIC** | Backend |
| **Prioritas** | MENENGAH |
| **Status** | BELUM ADA |
| **Detail** | Import data siswa/kelas/guru dari sumber sekolah, mapping user, dan assign UID kartu RFID |
| **Dependency** | RV-01, RV-02 |

### DP-04: Dokumentasi dan Training
| Item | Detail |
|------|--------|
| **PIC** | Semua |
| **Prioritas** | MENENGAH |
| **Status** | BELUM ADA |
| **Detail** | User manual, admin manual, API docs, panduan troubleshooting RFID, dan sesi pelatihan operator |
| **Dependency** | RV-07, QA-02 |

---

## Urutan Eksekusi yang Disarankan

1. Tutup dulu gap MVP: `RV-01`, `RV-02`, `RV-03`
2. Selesaikan fitur parsial yang langsung terasa ke user: `RV-04`, `RV-05`, `RV-06`
3. Tambahkan integration test lintas layer: `RV-07`
4. Rapikan tech debt yang berpotensi membingungkan tim: `TD-01`, `TD-02`, `TD-03`
5. Lanjut ke refine, UAT, dan deployment readiness

---

## Checklist Akhir Sebelum Go-Live

- [ ] Alur RFID nyata sudah terbukti berjalan end-to-end
- [ ] Semua fitur inti bisa dipakai dari UI tanpa memanggil API manual
- [ ] Kontrak API frontend-backend sudah konsisten
- [ ] Ada regression test untuk flow penting
- [ ] UAT sekolah selesai dan temuan kritis ditutup
- [ ] Firmware, backend, frontend, dan data master siap dipasang di lingkungan target
