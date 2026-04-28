# Dokumentasi SIKAP

Repositori ini sudah memiliki dokumen akademik, desain, dan panduan developer. File di bawah ini menjadi pintu masuk utama untuk dokumentasi operasional yang paling sering dibutuhkan.

## Dokumen Utama

| Dokumen | Audiens | Isi utama |
| --- | --- | --- |
| [LAPORAN_IMPLEMENTASI_SIKAP.md](./LAPORAN_IMPLEMENTASI_SIKAP.md) | Penyusun laporan, dosen, tim proyek | Ringkasan implementasi aktual sistem berdasarkan kode di repositori |
| [TAHAPAN_PENGEMBANGAN_SIKAP.md](./TAHAPAN_PENGEMBANGAN_SIKAP.md) | Penyusun laporan, tim proyek | Urutan tahapan pengembangan dari inception sampai deployment |
| [DOKUMEN_PENTING_LAPORAN_SIKAP.md](./DOKUMEN_PENTING_LAPORAN_SIKAP.md) | Penyusun laporan | Peta dokumen penting yang bisa dipakai per BAB dan lampiran |
| [CHECKLIST_MENUJU_100_SIKAP.md](./CHECKLIST_MENUJU_100_SIKAP.md) | Tim proyek, penyusun laporan | Checklist spesifik untuk menutup gap backend, frontend, RFID, testing, dan dokumentasi |
| [AUDIT_ENDPOINT_VERIFIKASI_RFID_DAN_COVERAGE.md](./AUDIT_ENDPOINT_VERIFIKASI_RFID_DAN_COVERAGE.md) | Tim teknis, penyusun laporan | Audit endpoint aktual, panduan verifikasi RFID, bukti uji, dan coverage report |
| [USER_GUIDE.md](./USER_GUIDE.md) | Seluruh pengguna aplikasi | Cara login, navigasi, dan penggunaan per role |
| [OPERATIONAL_GUIDE.md](./OPERATIONAL_GUIDE.md) | Admin sekolah, operator, guru piket | SOP harian, kelola akun, laporan, waktu sholat, monitoring |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Tim teknis, deployer, dosen pembimbing teknis | Setup Docker, setup manual, health check, troubleshooting awal |
| [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) | Developer | Workflow development, branch, coding convention |

## Dokumen Pendukung

| Dokumen | Kegunaan |
| --- | --- |
| [feature_roadmap.md](./feature_roadmap.md) | Rencana fitur dan prioritas pengembangan |
| [CHECKLIST_LEAN_PROTOTYPING.md](./CHECKLIST_LEAN_PROTOTYPING.md) | Checklist proses prototyping dan validasi |
| [laporan_presentasi_sikap.md](./laporan_presentasi_sikap.md) | Materi presentasi dan rangkuman proyek |
| [design/API_ENDPOINTS_LIST.md](./design/API_ENDPOINTS_LIST.md) | Ringkasan endpoint API |
| [design/API_endpoints.yaml](./design/API_endpoints.yaml) | Spesifikasi endpoint yang dipakai tim |
| [design/struktur_table.md](./design/struktur_table.md) | Struktur tabel dan relasi data |
| [../hardware/README.md](../hardware/README.md) | Wiring dan setup perangkat RFID ESP8266 |

## Rekomendasi Urutan Baca

1. Mulai dari [USER_GUIDE.md](./USER_GUIDE.md) bila tujuan utamanya memakai aplikasi.
2. Baca [OPERATIONAL_GUIDE.md](./OPERATIONAL_GUIDE.md) bila bertugas sebagai admin/operator sekolah.
3. Baca [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) bila perlu menyalakan stack lokal, Docker, atau perangkat.
4. Lanjut ke [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) bila akan mengubah kode.

## Catatan Implementasi Saat Ini

- Menu `Monitoring Sistem` tersedia untuk `admin` dan `kepsek`, tetapi akses utamanya muncul dari tombol cepat di dashboard, bukan dari menu navigasi samping.
- Laporan `per siswa` di frontend masih memakai input `id_siswa`, belum dropdown pencarian siswa.
- Profil sekolah di halaman `Data Sekolah` masih memakai fallback konfigurasi frontend, bukan data master sekolah dari backend.
- Backend sudah mendukung flow konfirmasi UID RFID dua kali untuk admin melalui API, tetapi flow tersebut belum diekspos penuh di UI frontend.
- Endpoint notifikasi dan heartbeat perangkat sudah diseragamkan ke pola `/api/v1/...`.
