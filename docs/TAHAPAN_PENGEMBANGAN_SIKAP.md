# Tahapan Pengembangan SIKAP

## 1. Pendekatan Pengembangan

SIKAP dikembangkan menggunakan pendekatan **Lean Software Development** dan **Rapid Prototyping**. Pemilihan metode ini cocok karena proyek dikerjakan oleh tim kecil, membutuhkan iterasi cepat, dan melibatkan stakeholder non-teknis seperti guru, siswa, dan pihak sekolah.

Dokumen acuan utamanya adalah:

- `docs/feature_roadmap.md`
- `docs/CHECKLIST_LEAN_PROTOTYPING.md`
- `docs/DEVELOPMENT_GUIDE.md`

## 2. Tahapan Pengembangan

### Tahap 1. Inception dan Penentuan MVP

Pada tahap awal, tim menentukan ruang lingkup sistem, target pengguna, serta prioritas fitur berdasarkan pendekatan MoSCoW.

Keluaran tahap ini:

- definisi fitur `must have`, `should have`, dan `could have`;
- struktur repositori proyek;
- setup awal Git, README, dan panduan pengembangan;
- rancangan awal kebutuhan sistem.

Artefak pendukung:

- `readme.md`
- `docs/feature_roadmap.md`
- `docs/CHECKLIST_LEAN_PROTOTYPING.md`

### Tahap 2. Prototyping dan Desain Sistem

Tahap ini berfokus pada validasi ide sebelum implementasi penuh. Tim menyiapkan rancangan antarmuka, struktur data, sequence diagram, dan daftar endpoint API.

Keluaran tahap ini:

- sequence diagram `SD-01` sampai `SD-07`;
- struktur tabel database;
- daftar endpoint API;
- dokumen presentasi proyek;
- panduan pengembangan untuk tim.

Artefak pendukung:

- `docs/design/SD-01.png` sampai `docs/design/SD-07.png`
- `docs/design/struktur_table.md`
- `docs/design/API_ENDPOINTS_LIST.md`
- `docs/design/API_endpoints.yaml`
- `docs/laporan_presentasi_sikap.md`

### Tahap 3. Implementasi Sprint 1: Fitur Inti

Tahap ini merealisasikan fondasi sistem agar alur utama dapat berjalan, yaitu login, dashboard, dan pencatatan absensi.

Fokus implementasi:

- backend Flask dan struktur modular;
- autentikasi JWT;
- model basis data inti;
- endpoint absensi dan rekapitulasi;
- dashboard awal untuk berbagai role;
- firmware awal perangkat RFID.

Artefak implementasi:

- `backend/app/routes/auth.py`
- `backend/app/routes/absensi.py`
- `backend/app/routes/dashboard.py`
- `backend/app/routes/rekapitulasi.py`
- `backend/app/services/absensi_service.py`
- `frontend/src/pages/AuthPage.jsx`
- `frontend/src/pages/DashboardPage.jsx`
- `hardware/esp8266_rfid/esp8266_rfid.ino`

### Tahap 4. Implementasi Sprint 2: Fitur Lanjutan

Setelah fitur inti berjalan, tahap berikutnya menambahkan fitur yang mendukung operasional sekolah dan pelaporan.

Fokus implementasi:

- generate laporan PDF dan Excel;
- input absensi manual;
- notifikasi aplikasi;
- user management;
- data master kelas dan siswa;
- pengaturan waktu sholat.

Artefak implementasi:

- `backend/app/routes/laporan.py`
- `backend/app/routes/notifikasi.py`
- `backend/app/routes/users.py`
- `backend/app/routes/kelas.py`
- `backend/app/routes/siswa.py`
- `backend/app/routes/waktu_sholat.py`
- `frontend/src/pages/ReportPage.jsx`
- `frontend/src/pages/ManualInputPage.jsx`
- `frontend/src/pages/NotificationPage.jsx`
- `frontend/src/pages/UserManagementPage.jsx`
- `frontend/src/pages/UserFormPage.jsx`

### Tahap 5. Refinement, Integrasi, dan Penguatan Operasional

Tahap ini memperluas sistem agar lebih siap dipakai dan lebih mendekati kebutuhan operasional nyata.

Fokus implementasi:

- surat peringatan;
- izin dan sengketa absensi;
- jadwal piket;
- monitoring sistem;
- MQTT untuk pembaruan dashboard real-time;
- dokumentasi operasional dan deployment.

Artefak implementasi:

- `backend/app/routes/surat_peringatan.py`
- `backend/app/routes/izin.py`
- `backend/app/routes/sengketa.py`
- `backend/app/routes/jadwal_piket.py`
- `backend/app/routes/rfid.py`
- `backend/app/routes/perangkat.py`
- `frontend/src/pages/WarningLetterPage.jsx`
- `frontend/src/pages/DutySchedulePage.jsx`
- `frontend/src/pages/MonitoringPage.jsx`
- `docker-compose.yml`
- `docs/OPERATIONAL_GUIDE.md`
- `docs/DEPLOYMENT_GUIDE.md`

### Tahap 6. Pengujian dan Validasi

Tahap pengujian dilakukan untuk memastikan fitur backend berjalan sesuai kebutuhan fungsional.

Status pengujian yang berhasil diverifikasi:

- seluruh test backend lulus dengan hasil `64 passed`;
- coverage backend mencapai `85%`;
- pengujian mencakup auth, absensi, dashboard, laporan, rekapitulasi, users, school resources, surat peringatan, dan waktu sholat.

Artefak pengujian:

- `backend/app/tests/test_auth.py`
- `backend/app/tests/test_absensi.py`
- `backend/app/tests/test_dashboard.py`
- `backend/app/tests/test_laporan.py`
- `backend/app/tests/test_rekapitulasi.py`
- `backend/app/tests/test_users.py`
- `backend/app/tests/test_school_resources.py`
- `backend/app/tests/test_surat_peringatan.py`
- `backend/app/tests/test_waktu_sholat.py`

### Tahap 7. Deployment dan Serah Terima

Tahap akhir pengembangan diarahkan pada kesiapan penggunaan sistem di lingkungan nyata.

Aktivitas utama:

- konfigurasi environment;
- orkestrasi stack melalui Docker Compose;
- health check backend;
- monitoring dengan Prometheus dan Grafana;
- penyiapan panduan pengguna dan operasional.

Artefak pendukung:

- `docker-compose.yml`
- `docs/USER_GUIDE.md`
- `docs/OPERATIONAL_GUIDE.md`
- `docs/DEPLOYMENT_GUIDE.md`

## 3. Ringkasan Status Per Tahap

| Tahap | Fokus | Status aktual |
| --- | --- | --- |
| Inception | Definisi MVP dan setup proyek | Selesai |
| Prototyping | Desain, diagram, struktur data, API | Selesai |
| Sprint 1 | Auth, absensi, dashboard, rekap | Selesai |
| Sprint 2 | Laporan, manual input, notifikasi, user management | Selesai |
| Refinement | Surat peringatan, monitoring, izin, sengketa, MQTT | Sebagian besar sudah ada |
| Testing | Backend automated tests | Sudah berjalan baik |
| Deployment | Dokumentasi dan stack service | Siap untuk tahap lanjutan |

## 4. Narasi Singkat yang Bisa Dipakai di Laporan

Contoh narasi yang bisa langsung Anda adaptasi:

> Pengembangan SIKAP dilakukan secara bertahap menggunakan pendekatan Lean dan Rapid Prototyping. Tahap awal difokuskan pada penentuan MVP dan penyusunan roadmap fitur. Setelah itu, tim membuat prototype dan dokumen desain seperti struktur tabel, sequence diagram, dan spesifikasi endpoint API. Tahap implementasi dilanjutkan melalui sprint fitur inti, yaitu autentikasi, absensi RFID, dashboard, dan rekapitulasi. Sprint berikutnya menambahkan fitur operasional seperti laporan PDF/Excel, notifikasi, input manual, dan manajemen pengguna. Pada tahap refinement, sistem diperluas dengan fitur surat peringatan, jadwal piket, izin, sengketa absensi, monitoring, serta dukungan real-time melalui MQTT. Selanjutnya, backend divalidasi melalui pengujian otomatis dan didukung oleh dokumentasi deployment serta panduan pengguna.

## 5. Kesimpulan

Tahapan pengembangan SIKAP menunjukkan bahwa proyek dikerjakan secara iteratif, dimulai dari perencanaan dan prototyping, lalu bergerak ke implementasi fitur inti, penambahan fitur operasional, pengujian, dan kesiapan deployment. Struktur artefak pada repositori juga memperlihatkan keterkaitan yang jelas antara dokumen desain, implementasi kode, dan dokumen operasional.
