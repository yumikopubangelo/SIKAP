# Dokumen Penting untuk Menyusun Laporan SIKAP

## 1. Tujuan Dokumen

Dokumen ini membantu memilih file-file yang paling penting saat menyusun laporan akhir, laporan implementasi, atau lampiran presentasi proyek SIKAP.

## 2. Dokumen Inti yang Wajib Dipakai

| Dokumen | Lokasi | Fungsi dalam laporan |
| --- | --- | --- |
| Ringkasan proyek | `readme.md` | Bahan deskripsi umum sistem, fitur, stack, dan latar proyek |
| Roadmap fitur | `docs/feature_roadmap.md` | Bahan BAB metodologi, sprint, dan prioritas pengembangan |
| Checklist Lean | `docs/CHECKLIST_LEAN_PROTOTYPING.md` | Bahan justifikasi metode Lean dan Rapid Prototyping |
| Laporan implementasi | `docs/LAPORAN_IMPLEMENTASI_SIKAP.md` | Bahan BAB implementasi |
| Tahapan pengembangan | `docs/TAHAPAN_PENGEMBANGAN_SIKAP.md` | Bahan BAB metodologi dan proses pengembangan |

## 3. Dokumen Teknis untuk BAB Analisis dan Desain

| Dokumen | Lokasi | Kegunaan |
| --- | --- | --- |
| Struktur tabel | `docs/design/struktur_table.md` | Bahan BAB basis data dan desain data |
| Daftar endpoint API | `docs/design/API_ENDPOINTS_LIST.md` | Bahan BAB perancangan dan implementasi API |
| Spesifikasi API | `docs/design/API_endpoints.yaml` | Lampiran teknis API/OpenAPI |
| Sequence diagram | `docs/design/SD-01.png` s.d. `docs/design/SD-07.png` | Lampiran diagram perilaku sistem |
| Presentasi proyek | `docs/laporan_presentasi_sikap.md` | Bahan ringkas untuk latar belakang dan tujuan sistem |

## 4. Dokumen Operasional dan Implementasi

| Dokumen | Lokasi | Kegunaan |
| --- | --- | --- |
| Panduan pengguna | `docs/USER_GUIDE.md` | Bahan BAB penggunaan sistem per role |
| Panduan operasional | `docs/OPERATIONAL_GUIDE.md` | Bahan BAB operasional sistem di sekolah |
| Panduan deployment | `docs/DEPLOYMENT_GUIDE.md` | Bahan BAB implementasi infrastruktur dan deployment |
| Panduan development | `docs/DEVELOPMENT_GUIDE.md` | Bahan BAB standar coding, branch, dan workflow tim |
| Panduan hardware | `hardware/README.md` | Bahan BAB integrasi perangkat RFID |

## 5. Dokumen dan File Bukti Implementasi

File berikut berguna sebagai bukti bahwa implementasi memang ada dan berjalan:

| Bukti | Lokasi | Fungsi |
| --- | --- | --- |
| Entry point backend | `backend/run.py` | Bukti server backend dijalankan |
| App factory Flask | `backend/app/__init__.py` | Bukti struktur backend modular |
| Absensi service | `backend/app/services/absensi_service.py` | Bukti logika inti absensi |
| Laporan service | `backend/app/services/laporan_service.py` | Bukti generate PDF/Excel |
| Routing frontend | `frontend/src/App.jsx` | Bukti role-based routing dan integrasi frontend |
| Halaman laporan | `frontend/src/pages/ReportPage.jsx` | Bukti implementasi fitur laporan |
| Halaman manual input | `frontend/src/pages/ManualInputPage.jsx` | Bukti implementasi fallback operasional |
| Sketch RFID | `hardware/esp8266_rfid/esp8266_rfid.ino` | Bukti integrasi hardware |
| Docker stack | `docker-compose.yml` | Bukti kesiapan deployment dan service pendukung |

## 6. Dokumen untuk BAB Pengujian

| Dokumen/File | Lokasi | Kegunaan |
| --- | --- | --- |
| Test auth | `backend/app/tests/test_auth.py` | Bukti uji autentikasi |
| Test absensi | `backend/app/tests/test_absensi.py` | Bukti uji fitur inti absensi |
| Test dashboard | `backend/app/tests/test_dashboard.py` | Bukti uji agregasi dashboard |
| Test laporan | `backend/app/tests/test_laporan.py` | Bukti uji generate laporan |
| Test users | `backend/app/tests/test_users.py` | Bukti uji user management |
| Test school resources | `backend/app/tests/test_school_resources.py` | Bukti uji data sekolah, kelas, siswa |
| Test surat peringatan | `backend/app/tests/test_surat_peringatan.py` | Bukti uji fitur surat peringatan |
| Test waktu sholat | `backend/app/tests/test_waktu_sholat.py` | Bukti uji konfigurasi waktu |

Catatan hasil uji yang bisa ditulis di laporan:

- pada 28 April 2026, seluruh test backend berhasil lulus dengan hasil `64 passed`;
- coverage backend mencapai `85%`;
- warning legacy `Query.get()` utama yang sempat muncul pada alur laporan sudah dibersihkan.

## 7. Rekomendasi Pemakaian Dokumen per BAB

| BAB laporan | Dokumen yang disarankan |
| --- | --- |
| BAB 1 Pendahuluan | `readme.md`, `docs/laporan_presentasi_sikap.md` |
| BAB 2 Metodologi | `docs/feature_roadmap.md`, `docs/CHECKLIST_LEAN_PROTOTYPING.md`, `docs/TAHAPAN_PENGEMBANGAN_SIKAP.md` |
| BAB 3 Analisis dan Desain | `docs/design/struktur_table.md`, `docs/design/API_ENDPOINTS_LIST.md`, diagram `SD-01` s.d. `SD-07` |
| BAB 4 Implementasi | `docs/LAPORAN_IMPLEMENTASI_SIKAP.md`, `backend/app/services/absensi_service.py`, `frontend/src/App.jsx`, `docker-compose.yml` |
| BAB 5 Pengujian | folder `backend/app/tests/` |
| BAB 6 Deployment/Operasional | `docs/DEPLOYMENT_GUIDE.md`, `docs/OPERATIONAL_GUIDE.md`, `hardware/README.md` |
| Lampiran | `docs/design/API_endpoints.yaml`, diagram desain, contoh file laporan pada `backend/static/generated/` |

## 8. Susunan Lampiran yang Disarankan

Urutan lampiran yang rapi untuk laporan akhir:

1. struktur tabel dan relasi database;
2. daftar endpoint API;
3. sequence diagram;
4. screenshot halaman utama frontend;
5. contoh hasil laporan PDF/Excel;
6. hasil pengujian backend;
7. dokumentasi hardware RFID;
8. panduan deployment singkat.

## 9. Dokumen yang Paling Membantu Jika Waktu Anda Terbatas

Jika Anda ingin menulis laporan dengan cepat, prioritaskan membaca:

1. `docs/LAPORAN_IMPLEMENTASI_SIKAP.md`
2. `docs/TAHAPAN_PENGEMBANGAN_SIKAP.md`
3. `docs/design/struktur_table.md`
4. `docs/feature_roadmap.md`
5. `docs/DEPLOYMENT_GUIDE.md`

Kelima dokumen itu sudah cukup untuk menyusun narasi metodologi, implementasi, pengujian, dan deployment secara ringkas namun kuat.
