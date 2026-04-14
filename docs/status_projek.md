# Status Projek SIKAP Saat Ini

Dokumen ini merangkum status pengembangan Sistem Informasi Kepatuhan Absensi Peserta Didik (SIKAP) berdasarkan iterasi pengembangan terakhir.

## 📊 Ringkasan Progress
Projek SIKAP saat ini sedang dalam fase pengembangan aktif, dengan fokus utama yang telah diselesaikan pada bagian **Backend API** dan **Database**. Beberapa fitur krusial (MVP) seperti sistem autentikasi, pencatatan absensi, dan manajemen data presensi sudah dapat beroperasi. 

**Persentase Penilaian Kasar:**
- **Database & Model:** 100% (Semua 19 entitas tabel telah dibuat)
- **Backend API Core:** 85% (Sebagian besar endpoint telah dirating dan diuji, tersisa fine-tuning)
- **Frontend:** Dalam tahap inisialisasi / berjalan paralel (tergantung sprint)

## 🛠️ Pencapaian Terbaru (Backend)

### 1. Model Database (Selesai)
18 file model SQLAlchemy telah berhasil dibuat dan dikonfigurasi, meliputi seluruh entitas dalam sistem:
- `User`, `Siswa`, `Guru`, `OrangTua`, `SekolahInfo`, `Kelas`
- `JadwalPiket`, `WaktuSholat`, `SesiSholat`, `Perangkat`
- Entitas transaksional: `Absensi`, `IzinPengajuan`, `SuratPeringatan`, `SengketaAbsensi`, `Laporan`, `Notifikasi`, `AuditLog`, `PasswordResetToken`.

### 2. Implementasi Endpoint API (Selesai & Direfactor)
Blueprint API telah di-registrasi dan mencakup fitur-fitur berikut:
- **Auth (`/auth`)**: Login dan autentikasi JWT selesai.
- **Absensi (`/absensi`)**: Logika validasi keterlambatan berdasarkan waktu sholat dan iqamah.
- **Dashboard (`/dashboard`)**: Agregasi data untuk role admin, kepsek, dsb.
- **Laporan (`/laporan`)**: Fitur export ke PDF/Excel selesai (BE-05).
- **Notifikasi (`/notifikasi`)**: Layanan notifikasi internal untuk SP/Izin selesai.
- **Rekapitulasi (`/rekapitulasi`)**: Layanan summary harian dan bulanan.
- **Users Manajemen (`/users`)**: CRUD untuk multi-role.
- **Waktu Sholat (`/waktu_sholat`)**: Pengelolaan jam sholat otomatis/manual.
- **Izin Pengajuan (`/izin`)**: Fitur administrasi pengajuan izin siswa yang terintegrasi ke db.
- **Sengketa Absensi (`/sengketa`)**: Fitur komplain ketidakhadiran (misal karena alat error).



## 🚧 Sedang/Akan Dikerjakan (Next Sprint)

1. **Frontend Integration**: Menghubungkan dashboard React JS (F001-F027) dengan API Backend yang sudah stabil.
2. **Hardware (IoT)**: Melanjutkan integrasi end-to-end antara hardware MFRC522 + ESP8266 ke endpoint POST `/absensi`.
3. **Automated Testing**: Peningkatan _coverage_ untuk testing terintegrasi di CI/CD.
4. **Surat Peringatan & Sekolah routes**: Melengkapi sisa route spesifik (`surat_peringatan.py`, `sekolah.py`, dll) jika belum digabung ke `notifikasi` atau `dashboard`.

## 📈 Status Blueprint Sprint Terbaru
- **Sprint 1 (MVP)**: ✅ *Selesai untuk scope Backend Utama.*
- **Sprint 2 (Laporan, Fitur Ekstra)**: ✅ *Selesai (Fitur export PDF/Excel dan Sengketa Absensi).*
- **Refinement API**: ✅ *Sedang berjalan.*

---

