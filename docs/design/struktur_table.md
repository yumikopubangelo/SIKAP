# 📊 Struktur Tabel Database SIKAP
## Sistem Informasi Kepatuhan Absensi Peserta Didik

**Database:** `sikap_db`  
**Engine:** MySQL 8.0  
**Charset:** utf8mb4  
**Total Tabel:** 19 tabel  

---

## 🗂️ Daftar Tabel

| No | Nama Tabel | Kategori | Keterangan Singkat |
|----|------------|----------|--------------------|
| 1 | `users` | Auth & User | Data akun login semua role |
| 2 | `kelas` | Master | Data kelas + wali kelas |
| 3 | `siswa` | Master | Data siswa + ID kartu RFID |
| 4 | `guru` | Master | Data guru (wali kelas & piket) |
| 5 | `orangtua` | Master | Data orang tua siswa |
| 6 | `waktu_sholat` | Master | Jadwal adzan, iqamah, selesai |
| 7 | `sesi_sholat` | Transaksi | Sesi per hari per waktu sholat |
| 8 | `absensi` | **Transaksi Utama** | Catatan tap RFID per siswa |
| 9 | `status_absensi` | Referensi | Kode & deskripsi status |
| 10 | `perangkat` | IoT | Data ESP8266 + status online |
| 11 | `surat_peringatan` | Output | SP1/SP2/SP3 per siswa |
| 12 | `notifikasi` | Output | Notifikasi in-app per user |
| 13 | `laporan` | Output | Metadata file laporan PDF/Excel |
| 14 | `jadwal_piket` | Operasional | Jadwal piket guru per hari |
| 15 | `audit_log` | Log | Rekam jejak semua perubahan data |
| 16 | `sekolah_info` | Konfigurasi | Profil & logo sekolah |
| 17 | `password_reset_token` | Auth | Token reset password via email |
| 18 | `sengketa_absensi` | Operasional | Klaim siswa yang tidak terabsen |
| 19 | `izin_pengajuan` | Operasional | Pengajuan izin ketidakhadiran oleh siswa |

---

---

## 1. Tabel `users`
**Kategori:** Auth & User  
**Deskripsi:** Menyimpan akun login untuk semua role (Admin, Kepala Sekolah, Wali Kelas, Guru Piket, Siswa, Orang Tua).

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_user` | INT | PK, AUTO_INCREMENT | Primary key |
| `username` | VARCHAR(50) | NOT NULL, UNIQUE | Username untuk login |
| `password` | VARCHAR(255) | NOT NULL | Hash bcrypt |
| `full_name` | VARCHAR(100) | NOT NULL | Nama lengkap |
| `email` | VARCHAR(100) | UNIQUE | Email (untuk reset password) |
| `no_telp` | VARCHAR(20) | — | Nomor telepon |
| `role` | VARCHAR(20) | NOT NULL | Nilai: `admin`, `kepsek`, `wali_kelas`, `guru_piket`, `siswa`, `orangtua` |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu akun dibuat |

**Relasi:**
- ← `siswa.id_user` (1 siswa punya 1 akun)
- ← `orangtua.id_user` (1 ortu punya 1 akun)
- ← `kelas.id_wali` (guru yang jadi wali kelas)
- ← `absensi.id_verifikator` (guru yang verifikasi)
- ← `jadwal_piket.id_user`
- ← `notifikasi.id_user`
- ← `audit_log.id_user`

---

## 2. Tabel `kelas`
**Kategori:** Master Data  
**Deskripsi:** Data kelas beserta wali kelas dan tahun ajaran.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_kelas` | INT | PK, AUTO_INCREMENT | Primary key |
| `nama_kelas` | VARCHAR(20) | NOT NULL | Contoh: `XI RPL 1`, `X TKJ 2` |
| `tingkat` | VARCHAR(5) | NOT NULL | Nilai: `X`, `XI`, `XII` |
| `jurusan` | VARCHAR(50) | — | Contoh: `RPL`, `TKJ`, `AKL` |
| `id_wali` | INT | FK → `users.id_user` | Guru yang menjadi wali kelas |
| `tahun_ajaran` | VARCHAR(10) | NOT NULL | Contoh: `2024/2025` |

**Relasi:**
- → `users.id_user` (wali kelas adalah user dengan role `wali_kelas`)
- ← `siswa.id_kelas` (banyak siswa dalam satu kelas)
- ← `laporan.id_kelas`

---

## 3. Tabel `siswa`
**Kategori:** Master Data  
**Deskripsi:** Data lengkap siswa, termasuk ID kartu RFID untuk absensi.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_siswa` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user`, UNIQUE | Akun login siswa |
| `nisn` | VARCHAR(20) | NOT NULL, UNIQUE | Nomor Induk Siswa Nasional |
| `nama` | VARCHAR(100) | NOT NULL | Nama lengkap siswa |
| `jenis_kelamin` | VARCHAR(10) | — | Nilai: `L` (Laki), `P` (Perempuan) |
| `alamat` | TEXT | — | Alamat rumah siswa |
| `no_telp_ortu` | VARCHAR(20) | — | Nomor HP orang tua |
| `id_card` | VARCHAR(50) | UNIQUE | UID kartu RFID (NULL jika belum registrasi) |
| `id_kelas` | INT | FK → `kelas.id_kelas` | Kelas siswa saat ini |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu data dibuat |

**Relasi:**
- → `users.id_user`
- → `kelas.id_kelas`
- ← `orangtua.id_siswa` (ortu memantau siswa ini)
- ← `absensi.id_siswa`
- ← `surat_peringatan.id_siswa`
- ← `laporan.id_siswa`

---

## 4. Tabel `guru`
**Kategori:** Master Data  
**Deskripsi:** Data guru yang berperan sebagai wali kelas atau guru piket.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_guru` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user`, UNIQUE | Akun login guru |
| `nip` | VARCHAR(30) | UNIQUE | Nomor Induk Pegawai |
| `nama` | VARCHAR(100) | NOT NULL | Nama lengkap guru |
| `jabatan` | VARCHAR(50) | — | Contoh: `Wali Kelas`, `Guru Piket` |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu data dibuat |

**Relasi:**
- → `users.id_user`

---

## 5. Tabel `orangtua`
**Kategori:** Master Data  
**Deskripsi:** Data orang tua/wali siswa yang dapat memantau kehadiran anak.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_ortu` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user`, UNIQUE | Akun login orang tua |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Siswa yang dipantau |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu data dibuat |

**Relasi:**
- → `users.id_user`
- → `siswa.id_siswa`

> **Catatan:** Satu akun orang tua dipasangkan ke satu siswa. Jika orang tua punya lebih dari satu anak di sekolah, dibuat akun terpisah per anak.

---

## 6. Tabel `waktu_sholat`
**Kategori:** Master Data / Konfigurasi  
**Deskripsi:** Jadwal waktu sholat yang dikelola Admin. Digunakan ESP8266 untuk menentukan sesi aktif.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_waktu` | INT | PK, AUTO_INCREMENT | Primary key |
| `nama_sholat` | VARCHAR(20) | NOT NULL, UNIQUE | Nilai: `Dzuhur`, `Ashar`, `Maghrib` |
| `waktu_adzan` | TIME | NOT NULL | Waktu adzan berkumandang |
| `waktu_iqamah` | TIME | NOT NULL | Waktu iqamah (mulai sholat) |
| `waktu_selesai` | TIME | NOT NULL | Batas akhir absensi diterima |

**Relasi:**
- ← `sesi_sholat.id_waktu`

> **Logika bisnis:** Siswa tap RFID antara `waktu_adzan` dan `waktu_iqamah` → **Tepat Waktu**. Tap antara `waktu_iqamah` dan `waktu_selesai` → **Terlambat**. Tidak tap sama sekali → **Alpha** (diisi otomatis saat sesi ditutup).

---

## 7. Tabel `sesi_sholat`
**Kategori:** Transaksi  
**Deskripsi:** Satu sesi = satu waktu sholat pada satu tanggal. Dibuat otomatis atau manual oleh sistem.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_sesi` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_waktu` | INT | FK → `waktu_sholat.id_waktu` | Waktu sholat yang bersangkutan |
| `tanggal` | DATE | NOT NULL | Tanggal sesi berlangsung |
| `status` | VARCHAR(20) | DEFAULT `aktif` | Nilai: `aktif`, `selesai` |

**Relasi:**
- → `waktu_sholat.id_waktu`
- ← `absensi.id_sesi`

> **Catatan:** Kombinasi `(id_waktu, tanggal)` harus unik — tidak boleh ada 2 sesi Dzuhur di tanggal yang sama.

---

## 8. Tabel `absensi` ⭐
**Kategori:** Transaksi Utama  
**Deskripsi:** Tabel inti sistem. Setiap record = satu kejadian tap RFID atau input manual.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_absensi` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Siswa yang absen |
| `id_sesi` | INT | FK → `sesi_sholat.id_sesi` | Sesi sholat yang diikuti |
| `timestamp` | DATETIME | NOT NULL | Waktu tap RFID / input manual |
| `status` | VARCHAR(20) | FK → `status_absensi.kode` | Kode status kehadiran |
| `device_id` | VARCHAR(50) | FK → `perangkat.device_id` | Perangkat yang digunakan (NULL jika manual) |
| `id_verifikator` | INT | FK → `users.id_user` | Guru yang verifikasi/input manual (NULL jika RFID) |
| `verified_at` | DATETIME | — | Waktu verifikasi oleh guru |
| `keterangan` | VARCHAR(255) | — | Catatan tambahan (wajib diisi jika status diedit) |

**Relasi:**
- → `siswa.id_siswa`
- → `sesi_sholat.id_sesi`
- → `status_absensi.kode`
- → `perangkat.device_id`
- → `users.id_user` (verifikator)
- ← `audit_log` (setiap perubahan absensi tercatat)

> **Constraint:** Kombinasi `(id_siswa, id_sesi)` harus UNIQUE — satu siswa hanya bisa absen sekali per sesi.

---

## 9. Tabel `status_absensi`
**Kategori:** Referensi / Lookup  
**Deskripsi:** Tabel referensi kode status untuk kolom `absensi.status`.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `kode` | VARCHAR(20) | PK | Kode status (Primary Key) |
| `deskripsi` | VARCHAR(50) | NOT NULL | Label tampilan di UI |

**Data bawaan (seed):**

| kode | deskripsi |
|------|-----------|
| `tepat_waktu` | Tepat Waktu |
| `terlambat` | Terlambat |
| `alpha` | Alpha |
| `haid` | Haid (Dispensasi) |
| `izin` | Izin |
| `sakit` | Sakit |

---

## 10. Tabel `perangkat`
**Kategori:** IoT / Infrastruktur  
**Deskripsi:** Data perangkat ESP8266 yang terpasang di titik absensi (pintu masjid).

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `device_id` | VARCHAR(50) | PK | ID unik perangkat (contoh: `ESP-001`) |
| `nama_device` | VARCHAR(100) | NOT NULL | Nama lokasi perangkat |
| `lokasi` | VARCHAR(100) | — | Deskripsi lokasi fisik |
| `api_key` | VARCHAR(100) | NOT NULL, UNIQUE | API key untuk autentikasi request dari ESP8266 |
| `status` | VARCHAR(20) | DEFAULT `offline` | Nilai: `online`, `offline` |
| `last_ping` | DATETIME | — | Terakhir kali perangkat mengirim heartbeat |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu perangkat didaftarkan |

**Relasi:**
- ← `absensi.device_id`

---

## 11. Tabel `surat_peringatan`
**Kategori:** Output Sistem  
**Deskripsi:** Surat Peringatan yang digenerate otomatis saat jumlah alpha siswa melebihi threshold.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_sp` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Siswa penerima SP |
| `sp_ke` | INT | NOT NULL | Urutan SP: `1`, `2`, atau `3` |
| `tanggal` | DATE | NOT NULL | Tanggal SP diterbitkan |
| `jenis` | VARCHAR(10) | NOT NULL | Nilai: `SP1`, `SP2`, `SP3` |
| `status_kirim` | VARCHAR(20) | DEFAULT `belum_kirim` | Nilai: `belum_kirim`, `terkirim`, `dibaca` |
| `id_pengirim` | INT | FK → `users.id_user` | Wali kelas yang menerbitkan SP |
| `alasan` | TEXT | — | Ringkasan pelanggaran |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu SP dibuat |

**Relasi:**
- → `siswa.id_siswa`
- → `users.id_user` (pengirim)
- ← `notifikasi.id_sp`

> **Logika bisnis:** SP1 = alpha ke-5, SP2 = alpha ke-10, SP3 = alpha ke-15.

---

## 12. Tabel `notifikasi`
**Kategori:** Output Sistem  
**Deskripsi:** Notifikasi in-app untuk semua role. Dikirim otomatis oleh sistem.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_notif` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user` | Penerima notifikasi |
| `tipe` | VARCHAR(20) | NOT NULL | Nilai: `sp`, `absensi`, `sistem` |
| `id_sp` | INT | FK → `surat_peringatan.id_sp` | Referensi SP (NULL jika bukan tipe `sp`) |
| `judul` | VARCHAR(100) | NOT NULL | Judul singkat notifikasi |
| `pesan` | TEXT | NOT NULL | Isi lengkap notifikasi |
| `tanggal` | DATETIME | DEFAULT NOW() | Waktu notifikasi dibuat |
| `dibaca` | BOOLEAN | DEFAULT FALSE | Status baca |

**Relasi:**
- → `users.id_user`
- → `surat_peringatan.id_sp`

---

## 13. Tabel `laporan`
**Kategori:** Output Sistem  
**Deskripsi:** Menyimpan metadata file laporan PDF/Excel yang sudah digenerate.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_laporan` | INT | PK, AUTO_INCREMENT | Primary key |
| `tipe` | VARCHAR(30) | NOT NULL | Nilai: `rekap_kelas`, `rekap_siswa`, `rekap_sekolah` |
| `id_kelas` | INT | FK → `kelas.id_kelas` | Filter kelas (NULL jika rekap sekolah) |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Filter siswa (NULL jika rekap kelas/sekolah) |
| `periode_mulai` | DATE | NOT NULL | Awal periode laporan |
| `periode_selesai` | DATE | NOT NULL | Akhir periode laporan |
| `generated_by` | INT | FK → `users.id_user` | User yang generate laporan |
| `tanggal_generate` | DATETIME | DEFAULT NOW() | Waktu file digenerate |
| `file_path` | VARCHAR(255) | NOT NULL | Path file di server (relatif dari `static/generated/`) |

**Relasi:**
- → `kelas.id_kelas`
- → `siswa.id_siswa`
- → `users.id_user`

---

## 14. Tabel `jadwal_piket`
**Kategori:** Operasional  
**Deskripsi:** Jadwal piket guru. Digunakan untuk menampilkan info jadwal di Dashboard Guru Piket.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_jadwal` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user` | Guru yang bertugas piket |
| `hari` | VARCHAR(10) | NOT NULL | Nilai: `Senin`, `Selasa`, ..., `Sabtu` |
| `jam_mulai` | TIME | NOT NULL | Jam mulai tugas piket |
| `jam_selesai` | TIME | NOT NULL | Jam selesai tugas piket |

**Relasi:**
- → `users.id_user`

---

## 15. Tabel `audit_log`
**Kategori:** Log / Keamanan  
**Deskripsi:** Merekam semua perubahan data absensi. Diisi otomatis setiap kali ada INSERT, UPDATE, atau DELETE pada tabel `absensi`.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_log` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user` | User yang melakukan aksi |
| `aksi` | VARCHAR(10) | NOT NULL | Nilai: `INSERT`, `UPDATE`, `DELETE` |
| `tabel` | VARCHAR(50) | NOT NULL | Nama tabel yang diubah |
| `record_pk` | VARCHAR(50) | NOT NULL | Primary key record yang diubah |
| `timestamp` | DATETIME | DEFAULT NOW() | Waktu aksi dilakukan |
| `old_value` | TEXT | — | Data sebelum diubah (JSON) |
| `new_value` | TEXT | — | Data sesudah diubah (JSON) |

**Relasi:**
- → `users.id_user`

> **Catatan:** Tabel ini **tidak boleh didelete** datanya kecuali oleh admin dengan prosedur khusus. Berfungsi sebagai bukti audit untuk Kepala Sekolah.

---

## 16. Tabel `sekolah_info`
**Kategori:** Konfigurasi  
**Deskripsi:** Menyimpan profil dan identitas sekolah. Hanya ada 1 record, dikelola oleh Admin.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_sekolah` | INT | PK | Selalu bernilai `1` |
| `nama_sekolah` | VARCHAR(150) | NOT NULL | Nama lengkap sekolah |
| `alamat` | TEXT | — | Alamat sekolah |
| `no_telp` | VARCHAR(20) | — | Nomor telepon sekolah |
| `email` | VARCHAR(100) | — | Email resmi sekolah |
| `logo_path` | VARCHAR(255) | — | Path file logo (relatif dari `static/uploads/`) |
| `foto_masjid_path` | VARCHAR(255) | — | Path foto masjid sekolah |
| `updated_at` | DATETIME | — | Terakhir kali data diupdate |

---

## 17. Tabel `password_reset_token`
**Kategori:** Auth / Keamanan  
**Deskripsi:** Token sementara untuk proses reset password via email (fitur "Lupa Password").

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_token` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_user` | INT | FK → `users.id_user` | User yang request reset |
| `token` | VARCHAR(255) | NOT NULL, UNIQUE | Token unik (random 64 karakter) |
| `expired_at` | DATETIME | NOT NULL | Token kadaluarsa (biasanya 1 jam dari dibuat) |
| `used` | BOOLEAN | DEFAULT FALSE | Apakah token sudah dipakai |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu token dibuat |

**Relasi:**
- → `users.id_user`

> **Catatan:** Token yang sudah `used = TRUE` atau sudah lewat `expired_at` dianggap tidak valid.

---

## 18. Tabel `sengketa_absensi`
**Kategori:** Operasional  
**Deskripsi:** Klaim dari siswa yang merasa hadir tapi tidak terabsen (kartu error, dsb). Diverifikasi oleh Guru Piket.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_sengketa` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Siswa yang mengajukan klaim |
| `id_sesi` | INT | FK → `sesi_sholat.id_sesi` | Sesi yang diklaim |
| `alasan` | TEXT | NOT NULL | Penjelasan dari siswa |
| `status` | VARCHAR(20) | DEFAULT `pending` | Nilai: `pending`, `diterima`, `ditolak` |
| `id_verifikator` | INT | FK → `users.id_user` | Guru Piket yang memverifikasi |
| `catatan_verifikator` | TEXT | — | Keterangan dari guru piket |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu klaim diajukan |
| `verified_at` | DATETIME | — | Waktu verifikasi selesai |

**Relasi:**
- → `siswa.id_siswa`
- → `sesi_sholat.id_sesi`
- → `users.id_user` (verifikator)

---

## 19. Tabel `izin_pengajuan`
**Kategori:** Operasional  
**Deskripsi:** Pengajuan izin ketidakhadiran (seperti izin haid, sakit, acara keluarga) yang diajukan oleh siswa dan diverifikasi oleh wali kelas.

| Kolom | Tipe Data | Constraint | Keterangan |
|-------|-----------|------------|------------|
| `id_izin` | INT | PK, AUTO_INCREMENT | Primary key |
| `id_siswa` | INT | FK → `siswa.id_siswa` | Siswa yang mengajukan |
| `tanggal_mulai` | DATE | NOT NULL | Tanggal izin dimulai |
| `tanggal_selesai` | DATE | NOT NULL | Tanggal izin berakhir |
| `alasan` | TEXT | NOT NULL | Deskripsi alasan izin (haid/sakit/dll) |
| `status` | VARCHAR(20) | DEFAULT `pending` | Nilai: `pending`, `disetujui`, `ditolak` |
| `id_verifikator` | INT | FK → `users.id_user` | Wali kelas yang memverifikasi |
| `catatan_verifikator` | TEXT | — | Keterangan tambahan dari wali kelas |
| `created_at` | DATETIME | DEFAULT NOW() | Waktu pengajuan dibuat |
| `updated_at` | DATETIME | — | Waktu update terakhir |

**Relasi:**
- → `siswa.id_siswa`
- → `users.id_user` (verifikator)

---

---

## 🔗 Ringkasan Relasi Antar Tabel

```
users ──────────────────────────────────────────────────────────
  │ 1:1 → siswa (id_user)
  │ 1:1 → guru (id_user)
  │ 1:1 → orangtua (id_user)
  │ 1:N → jadwal_piket (id_user)
  │ 1:N → notifikasi (id_user)
  │ 1:N → laporan (generated_by)
  │ 1:N → audit_log (id_user)
  └ 1:N → absensi (id_verifikator)

kelas ──────────────────────────────────────────────────────────
  │ N:1 → users (id_wali) ← wali kelas
  └ 1:N → siswa (id_kelas)

siswa ──────────────────────────────────────────────────────────
  │ N:1 → kelas (id_kelas)
  │ 1:N → absensi (id_siswa)
  │ 1:N → surat_peringatan (id_siswa)
  │ 1:1 → orangtua (id_siswa)
  └ 1:N → izin_pengajuan (id_siswa)

waktu_sholat ───────────────────────────────────────────────────
  └ 1:N → sesi_sholat (id_waktu)

sesi_sholat ────────────────────────────────────────────────────
  │ N:1 → waktu_sholat (id_waktu)
  │ 1:N → absensi (id_sesi)
  └ 1:N → sengketa_absensi (id_sesi)

absensi ────────────────────────────────────────────────────────
  │ N:1 → siswa (id_siswa)
  │ N:1 → sesi_sholat (id_sesi)
  │ N:1 → status_absensi (status → kode)
  │ N:1 → perangkat (device_id)
  └ N:1 → users (id_verifikator)

surat_peringatan ───────────────────────────────────────────────
  │ N:1 → siswa (id_siswa)
  │ N:1 → users (id_pengirim)
  └ 1:N → notifikasi (id_sp)
```

---

## 📐 Aturan Naming Convention

| Aturan | Contoh |
|--------|--------|
| Nama tabel: `snake_case`, plural | `sesi_sholat`, `surat_peringatan` |
| Primary key: `id_` + nama tabel | `id_siswa`, `id_kelas` |
| Foreign key: sama dengan PK yang direferensi | `id_siswa` di tabel `absensi` |
| Boolean: tanpa prefix `is_` | `dibaca` bukan `is_dibaca` |
| Timestamp: `_at` suffix | `created_at`, `verified_at` |
| Status/enum: `snake_case` lowercase | `tepat_waktu`, `belum_kirim` |

---

*Dokumen ini dibuat berdasarkan ERD SIKAP v1.0*  
*Kelompok 1 — Rancang Bangun Perangkat Lunak — SI UNSIL 2026*