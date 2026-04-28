# Panduan Pengguna SIKAP

Dokumen ini ditujukan untuk pengguna akhir aplikasi SIKAP: admin, kepala sekolah, wali kelas, guru piket, siswa, dan orang tua.

## 1. Gambaran Singkat

SIKAP adalah sistem absensi sholat sekolah berbasis RFID. Tap kartu siswa akan tercatat ke sistem, lalu data tersebut diringkas pada dashboard, laporan, notifikasi, dan monitoring.

Fitur yang sudah tersedia di aplikasi web saat ini:

- Login dan logout berbasis JWT.
- Dashboard berbeda untuk 6 role.
- Halaman notifikasi.
- Halaman profil pengguna.
- Rekap data sekolah.
- Generate laporan PDF dan Excel.
- Input absensi manual untuk guru piket.
- Pengelolaan akun dan pengaturan waktu sholat untuk admin.
- Monitoring Grafana untuk admin dan kepala sekolah.

## 2. Cara Masuk ke Sistem

1. Buka aplikasi frontend.
2. Masukkan `username` dan `password`.
3. Tekan tombol login.
4. Setelah berhasil, sistem akan memuat profil, dashboard, dan notifikasi Anda.

Catatan:

- Jika token sudah tidak valid atau sesi berakhir, Anda akan diminta login ulang.
- Saat login berhasil tetapi dashboard belum termuat, sistem tetap menyimpan sesi dan Anda bisa mencoba tombol `Muat Ulang Data`.

## 3. Navigasi Umum

Menu yang paling umum dipakai:

- `Beranda`: dashboard utama sesuai role.
- `Pesan`: melihat notifikasi dan menandai pesan sebagai sudah dibaca.
- `Profil Saya`: melihat identitas akun dan relasi data yang terhubung.
- `Data Sekolah`: ringkasan statistik sekolah dan performa per kelas.
- `Laporan`: generate file PDF atau Excel.
- `Input Absensi`: halaman input manual untuk guru piket.
- `Waktu Sholat`: pengaturan jadwal adzan, iqamah, dan batas sesi.
- `Kelola Akun`: administrasi akun user oleh admin.

## 4. Hak Akses per Role

| Role | Menu utama | Tujuan utama |
| --- | --- | --- |
| `admin` | Beranda, Pesan, Data Sekolah, Laporan, Waktu Sholat, Kelola Akun, Profil Saya | Mengelola sistem secara penuh |
| `kepsek` | Beranda, Pesan, Data Sekolah, Laporan, Profil Saya | Memantau kondisi sekolah dan rekap lintas kelas |
| `wali_kelas` | Beranda, Pesan, Data Sekolah, Laporan, Profil Saya | Memantau kelas binaan dan tindak lanjut siswa |
| `guru_piket` | Beranda, Pesan, Input Absensi, Profil Saya | Memastikan absensi harian masuk dengan benar |
| `siswa` | Beranda, Pesan, Profil Saya | Melihat riwayat dan ringkasan absensi pribadi |
| `orangtua` | Beranda, Pesan, Profil Saya | Memantau kehadiran anak yang terhubung |

Catatan:

- `Monitoring Sistem` hanya bisa diakses oleh `admin` dan `kepsek`, biasanya dari tombol cepat di dashboard.
- Jika menu tidak muncul, kemungkinan role Anda memang tidak memiliki izin untuk halaman tersebut.

## 5. Alur Penggunaan per Role

### Admin

Halaman penting:

- Dashboard admin berisi total user, total siswa, jumlah tap hari ini, dan perangkat online.
- `Kelola Akun` untuk tambah, ubah, cari, dan hapus akun.
- `Waktu Sholat` untuk memperbarui jadwal sistem.
- `Laporan` untuk generate PDF atau Excel.
- `Data Sekolah` untuk melihat rekap lintas kelas.
- `Monitoring Sistem` untuk memantau kesehatan layanan dan perangkat.

Alur kerja yang disarankan:

1. Cek dashboard untuk melihat kondisi umum hari ini.
2. Buka `Kelola Akun` bila ada user baru atau perubahan data.
3. Pastikan `Waktu Sholat` sesuai jadwal sekolah.
4. Buka `Monitoring Sistem` bila perlu memeriksa perangkat atau performa layanan.
5. Generate laporan saat dibutuhkan oleh sekolah atau dosen pembimbing.

### Kepala Sekolah

Halaman penting:

- Dashboard kepsek menampilkan ringkasan kelas hari ini, trend kehadiran sekolah, dan distribusi status.
- `Data Sekolah` menampilkan performa per kelas.
- `Laporan` untuk laporan kelas, siswa, atau sekolah.
- `Monitoring Sistem` tersedia melalui tombol cepat dashboard.

Alur kerja yang disarankan:

1. Lihat dashboard untuk memantau keterlambatan dan kehadiran sekolah.
2. Gunakan `Data Sekolah` untuk membandingkan performa antar kelas.
3. Generate laporan sekolah untuk kebutuhan evaluasi dan pelaporan.

### Wali Kelas

Halaman penting:

- Dashboard wali kelas menampilkan rekap siswa di kelas binaan.
- `Data Sekolah` membantu melihat posisi kelas terhadap kelas lain.
- `Laporan` bisa dipakai untuk laporan kelas atau laporan siswa.

Alur kerja yang disarankan:

1. Cek dashboard untuk melihat siswa yang sering terlambat atau perlu perhatian.
2. Gunakan `Laporan` untuk membuat rekap kelas berdasarkan periode.
3. Gunakan `Laporan per siswa` bila perlu memeriksa satu siswa tertentu.

Catatan:

- Laporan `per siswa` di frontend masih memakai `id_siswa`, bukan pencarian nama/NISN.

### Guru Piket

Halaman penting:

- Dashboard guru piket menampilkan tap hari ini, jumlah tepat waktu, jumlah terlambat, dan perangkat online.
- `Input Absensi Manual` dipakai bila kartu siswa tidak bisa dipakai.

Langkah input absensi manual:

1. Buka menu `Input Absensi`.
2. Masukkan NISN 10 digit siswa.
3. Klik `Validasi NISN`.
4. Pastikan panel validasi menampilkan siswa yang benar.
5. Pilih tanggal, waktu sholat, dan status absensi.
6. Isi keterangan bila ada alasan khusus, misalnya kartu tertinggal atau rusak.
7. Klik `Simpan Absensi Manual`.

Catatan:

- Sistem akan menolak simpan bila siswa sudah memiliki absensi pada sesi yang sama.
- Keterangan sangat membantu untuk audit dan penelusuran perubahan data.

### Siswa

Halaman penting:

- Dashboard siswa menampilkan ringkasan absensi bulan berjalan, status terakhir, grafik trend, dan riwayat absensi pribadi.
- `Pesan` menampilkan notifikasi yang masuk ke akun siswa.
- `Profil Saya` menampilkan identitas akun.

Alur kerja yang disarankan:

1. Cek dashboard untuk melihat status terakhir dan trend kehadiran.
2. Buka `Pesan` bila ada notifikasi baru.
3. Gunakan `Profil Saya` untuk memastikan akun yang sedang dipakai sudah benar.

### Orang Tua

Halaman penting:

- Dashboard orang tua menampilkan data absensi anak yang terhubung.
- `Pesan` menampilkan notifikasi terkait anak.
- `Profil Saya` menampilkan relasi akun orang tua ke data siswa.

Catatan penting:

- Relasi orang tua ke siswa saat ini dibangun dari kecocokan `no_telp` user dengan `no_telp_ortu` pada data siswa.
- Bila tidak ada kecocokan, dashboard tetap bisa dibuka tetapi data anak tidak akan muncul.

## 6. Membaca Notifikasi

1. Buka menu `Pesan`.
2. Sistem akan menampilkan jumlah notifikasi belum dibaca.
3. Klik notifikasi untuk melihat isi.
4. Gunakan aksi `tandai sudah dibaca` bila tersedia.

## 7. Membuat Laporan

Role yang bisa memakai laporan: `admin`, `kepsek`, dan `wali_kelas`.

Langkah umum:

1. Buka halaman `Laporan`.
2. Pilih `Jenis Laporan`: `kelas`, `sekolah`, atau `siswa`.
3. Pilih `Format`: `PDF` atau `Excel`.
4. Isi filter yang diperlukan.
5. Pilih rentang tanggal.
6. Klik `Generate Laporan`.
7. Setelah metadata laporan muncul, klik `Download File`.

Tips:

- Gunakan `Excel` bila data ingin diolah ulang.
- Gunakan rentang tanggal yang lebih sempit bila PDF terlalu panjang.
- Untuk `laporan sekolah`, filter tambahan tidak diperlukan.

## 8. Akun Demo

Jika database menggunakan `seed.sql`, akun berikut tersedia:

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Kepala Sekolah | `kepsek` | `kepsek123` |
| Wali Kelas | `walikelas` | `wali123` |
| Guru Piket | `gurupiket` | `piket123` |
| Siswa | `siswa001` | `siswa123` |
| Orang Tua | `ortu001` | `ortu123` |

Gunakan akun demo hanya untuk pengujian lokal. Ganti password sebelum digunakan di lingkungan nyata.

## 9. Kendala Umum

### Tidak bisa login

- Pastikan username dan password benar.
- Pastikan backend aktif.
- Jika token lama rusak, logout lalu login ulang.

### Dashboard kosong atau data belum muncul

- Klik `Muat Ulang Data`.
- Pastikan backend dan database berjalan normal.
- Untuk role `orangtua`, pastikan nomor telepon akun cocok dengan data siswa.

### Tidak bisa membuka halaman tertentu

- Cek kembali role akun Anda.
- Beberapa halaman memang hanya tersedia untuk role tertentu.

### Monitoring tidak tampil

- Pastikan service Grafana aktif.
- Pada setup Docker default, Grafana berjalan di `http://localhost:3000`.

### Laporan siswa membingungkan karena minta ID

- Saat ini field laporan siswa memakai `id_siswa` dari database, bukan NISN atau nama.
- Minta admin atau cek data master untuk mengetahui `id_siswa` yang benar.
