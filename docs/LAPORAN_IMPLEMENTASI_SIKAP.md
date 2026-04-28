# Laporan Implementasi SIKAP

## 1. Ringkasan

SIKAP adalah sistem informasi absensi sholat berbasis RFID untuk lingkungan sekolah. Implementasi saat ini sudah mencakup aplikasi web frontend, backend REST API, basis data relasional, integrasi perangkat RFID, monitoring layanan, dan dokumen operasional.

Laporan ini disusun berdasarkan implementasi aktual yang ada di repositori `d:\SIKAP` per 28 April 2026.

## 2. Tujuan Implementasi

Tujuan utama implementasi SIKAP adalah:

- mengotomatisasi pencatatan absensi sholat siswa melalui kartu RFID;
- menyediakan dashboard berbeda untuk beberapa role pengguna;
- memudahkan pembuatan rekapitulasi dan laporan PDF/Excel;
- mendukung pengawasan sekolah melalui notifikasi, monitoring, dan audit log;
- menyediakan dasar deployment yang siap dikembangkan ke lingkungan operasional sekolah.

## 3. Arsitektur Implementasi

Implementasi SIKAP dibangun dengan pendekatan full-stack dan terbagi menjadi empat lapisan utama:

| Lapisan | Implementasi |
| --- | --- |
| Frontend | React 18, Vite, Axios, MQTT client, Recharts |
| Backend | Flask 3, Flask-JWT-Extended, SQLAlchemy, Flask-Migrate |
| Data & Infrastruktur | MySQL 8, Redis, Elasticsearch, Mosquitto, Prometheus, Grafana |
| Hardware | NodeMCU ESP8266 dan RFID reader MFRC522 |

Secara teknis, frontend mengakses backend melalui REST API, backend menyimpan data ke MySQL melalui ORM SQLAlchemy, perangkat RFID mengirim data absensi ke endpoint backend, dan metrik layanan dikumpulkan melalui Prometheus lalu divisualisasikan di Grafana.

## 4. Implementasi Backend

Backend berada pada folder `backend/` dan menggunakan pola pemisahan `routes`, `services`, `models`, `middleware`, dan `utils`.

Ringkasan implementasi backend:

- terdapat `18` file route module pada `backend/app/routes/`;
- terdapat `17` file model pada `backend/app/models/` yang memuat `19` tabel basis data;
- terdapat `18` file service pada `backend/app/services/`;
- terdapat `56` handler endpoint HTTP yang terdefinisi pada layer route;
- tersedia `6` file migrasi Alembic pada `backend/migrations/versions/`.

Fitur backend yang sudah terimplementasi meliputi:

- autentikasi login, logout, dan profil pengguna berbasis JWT;
- pembatasan akses berbasis role untuk admin, kepala sekolah, wali kelas, guru piket, siswa, dan orang tua;
- pencatatan absensi RFID dan input manual;
- rekapitulasi per kelas, per siswa, dan tingkat sekolah;
- pembuatan laporan PDF dan Excel;
- notifikasi dalam aplikasi;
- pengelolaan data user, kelas, siswa, waktu sholat, perangkat, surat peringatan, izin, sengketa, dan jadwal piket;
- audit log untuk perubahan data absensi;
- endpoint health check dan metrics untuk monitoring layanan.

Implementasi logika absensi inti berada pada `backend/app/services/absensi_service.py`. File ini menangani validasi perangkat, verifikasi tanda tangan RFID, pembentukan sesi sholat, penentuan status `tepat_waktu` atau `terlambat`, pencegahan duplikasi absensi, dan pencatatan audit log.

## 5. Implementasi Frontend

Frontend berada pada folder `frontend/` dan dibangun sebagai single-page application menggunakan React dan Vite.

Ringkasan implementasi frontend:

- terdapat `14` halaman utama pada `frontend/src/pages/`;
- routing dan proteksi halaman dipusatkan pada `frontend/src/App.jsx`;
- frontend sudah memakai JWT di `localStorage` untuk mempertahankan sesi login;
- frontend sudah menghubungkan dashboard ke MQTT untuk refresh data real-time;
- frontend memiliki pembatasan akses per role di level routing.

Halaman yang sudah tersedia antara lain:

- `AuthPage.jsx`
- `DashboardPage.jsx`
- `ManualInputPage.jsx`
- `ReportPage.jsx`
- `NotificationPage.jsx`
- `UserManagementPage.jsx`
- `UserFormPage.jsx`
- `SchoolDataPage.jsx`
- `PrayerTimeSettingsPage.jsx`
- `MonitoringPage.jsx`
- `ProfilePage.jsx`
- `CsvImportPage.jsx`
- `DutySchedulePage.jsx`
- `WarningLetterPage.jsx`

Secara implementatif, frontend sudah mendukung:

- login dan logout;
- dashboard multi-role;
- pemanggilan data dashboard dan notifikasi;
- generate laporan dan unduh file hasil generate;
- input absensi manual untuk guru piket;
- pengelolaan akun pengguna untuk admin;
- pengaturan waktu sholat;
- monitoring sistem untuk admin dan kepala sekolah.

## 6. Implementasi Basis Data

Dokumen struktur tabel pada `docs/design/struktur_table.md` menunjukkan bahwa SIKAP menggunakan `19` tabel. Tabel-tabel tersebut mencakup area autentikasi, master data, transaksi utama, operasional, output sistem, dan audit.

Tabel inti sistem adalah:

- `users`
- `kelas`
- `siswa`
- `waktu_sholat`
- `sesi_sholat`
- `absensi`
- `perangkat`
- `surat_peringatan`
- `notifikasi`
- `laporan`
- `audit_log`

Basis data juga sudah didukung oleh:

- `database/schema.sql` untuk inisialisasi skema;
- `database/seed.sql` untuk data awal;
- Alembic migration pada `backend/migrations/versions/`.

## 7. Implementasi Hardware dan Integrasi RFID

Implementasi perangkat berada pada `hardware/esp8266_rfid/`. Integrasi ini memakai NodeMCU ESP8266 sebagai mikrokontroler dan MFRC522 sebagai RFID reader.

Fungsi integrasi hardware yang sudah disiapkan:

- pembacaan UID kartu RFID;
- pengiriman data ke endpoint backend;
- autentikasi perangkat dengan `device_id` dan `api_key`;
- dukungan mode keamanan tambahan melalui signature verification;
- flow capture UID RFID dua kali untuk konfirmasi kartu siswa.

Dokumen pendukung hardware tersedia pada:

- `hardware/README.md`
- `hardware/esp8266_rfid/esp8266_rfid.ino`
- `hardware/esp8266_rfid/config.h.example`

## 8. Implementasi Keamanan

Aspek keamanan yang sudah diterapkan dalam implementasi adalah:

- JWT authentication dengan active key dan legacy key;
- token revocation saat logout;
- role-based access control pada endpoint dan halaman;
- bcrypt untuk penyimpanan password;
- security header HTTP seperti `X-Frame-Options` dan `X-Content-Type-Options`;
- validasi perangkat RFID berbasis `X-API-Key`;
- opsi verifikasi signature RFID untuk meningkatkan keamanan integrasi perangkat;
- audit log untuk jejak perubahan data penting.

## 9. Implementasi Monitoring dan Deployment

Repositori sudah menyiapkan stack deployment berbasis Docker Compose. File `docker-compose.yml` memuat service:

- `db`
- `phpmyadmin`
- `backend`
- `frontend`
- `mosquitto`
- `elasticsearch`
- `kibana`
- `redis`
- `prometheus`
- `grafana`

Artinya, implementasi tidak berhenti pada coding aplikasi, tetapi juga sudah menyentuh:

- orkestrasi service;
- health check backend;
- observability melalui metrics Prometheus;
- dashboard monitoring Grafana;
- dukungan pengembangan lokal dan simulasi lingkungan produksi.

## 10. Hasil Pengujian

Pengujian backend berhasil dijalankan pada 28 April 2026 dengan hasil:

- `64 passed` dari seluruh test pada `backend/app/tests`;
- coverage backend saat ini `85%`;
- waktu eksekusi full test + coverage sekitar `5 menit 32 detik`;
- warning legacy `Query.get()` pada fitur download laporan sudah dibersihkan.

Modul pengujian yang tersedia mencakup:

- autentikasi;
- absensi;
- dashboard;
- laporan;
- rekapitulasi;
- user management;
- waktu sholat;
- school resources;
- surat peringatan.

Hasil ini menunjukkan bahwa implementasi backend sudah memiliki dasar verifikasi fungsional yang baik, walaupun masih ada ruang perbaikan pada kualitas coverage dan pembaruan API SQLAlchemy.

## 11. Temuan dan Catatan Implementasi Saat Ini

Berdasarkan kode dan dokumentasi yang ada, beberapa catatan penting untuk ditulis dalam laporan adalah:

- flow konfirmasi UID RFID sudah tersedia di backend dan widget admin sudah ada di frontend, tetapi masih perlu validasi end-to-end di lingkungan nyata;
- laporan per siswa di frontend masih menggunakan `id_siswa`, belum berbasis pencarian nama atau NISN;
- profil sekolah di halaman frontend masih memiliki ketergantungan pada fallback konfigurasi tertentu;
- terdapat warning legacy SQLAlchemy pada proses download laporan.
- route notifikasi dan heartbeat perangkat kini sudah dirapikan ke pola `/api/v1/...`, sehingga konsistensi API lebih baik daripada kondisi sebelumnya.

Catatan-catatan ini justru penting untuk dimasukkan dalam laporan karena menunjukkan evaluasi implementasi yang jujur dan area pengembangan berikutnya.

## 12. Kesimpulan

Secara keseluruhan, implementasi SIKAP sudah berada pada tahap aplikasi yang fungsional, bukan sekadar prototype antarmuka. Sistem telah memiliki backend modular, frontend multi-role, basis data terstruktur, integrasi perangkat RFID, monitoring service, dan pengujian backend yang berjalan baik.

Dengan kondisi ini, SIKAP sudah sangat layak dijadikan bahan laporan implementasi, khususnya untuk membahas:

- realisasi arsitektur sistem;
- penerapan metodologi Lean dan prototyping;
- integrasi hardware dan software;
- penerapan keamanan, testing, dan deployment;
- evaluasi kekuatan dan keterbatasan implementasi saat ini.
