# Software Requirements Specification (SRS) - SIKAP

## 1. Pendahuluan
### 1.1 Tujuan
Dokumen ini bertujuan untuk mendefinisikan seluruh kebutuhan rekayasa perangkat lunak untuk **Sistem Informasi Kepatuhan Absensi Peserta Didik (SIKAP)**. Sistem ini diperuntukkan untuk mencatat, mengevaluasi, dan melaporkan kepatuhan ibadah wajib (khususnya sholat) bagi siswa secara otomatis.

### 1.2 Ruang Lingkup Produk
SIKAP mengintegrasikan hardware IoT (ESP8266 + MFRC522) dan aplikasi Web. Sistem ini akan menggantikan cara manual dengan pencatatan RFID. Data yang dikumpulkan akan digunakan untuk menghasilkan notifikasi Surat Peringatan (SP), evaluasi harian/bulanan, dan pengawas absensi realtime oleh Guru Piket dan Wali Kelas.

## 2. Deskripsi Umum
### 2.1 Kategori Pengguna (Aktor)
Sistem ini menggunakan Role-Based Access Control (RBAC) dengan 6 entitas pengguna utama:
1. **Admin:** Mengelola data master (siswa, guru, kartu RFID, device, jadwal).
2. **Kepala Sekolah:** Memiliki akses tingkat tinggi untuk melihat aggregate data, rekapitulasi level sekolah, dan laporan analitik bulanan.
3. **Wali Kelas:** Mengawasi data anak didiknya saja, memiliki kemampuan mengonfirmasi sengketa atau menerima SP.
4. **Guru Piket:** Memonitor absensi _realtime_ di area masjid, mendaftarkan absensi manual (jika RFID bermasalah), dan mengurus perangkat.
5. **Orang Tua:** Melihat riwayat absensi anaknya, menerima notifikasi (via web/WA integrasi) apabila ada indikasi SP/alpha.
6. **Siswa:** Mengakses history absensi pribadi dan pengajuan izin terbatas.

### 2.2 Arsitektur Sistem Berjalan
- **Layer Hardware:** Kartu RFID dideteksi oleh NodeMCU (ESP8266) yang terhubung ke internet lokal. Payload `{uid, timestamp, device_id}` dikirim via HTTP POST.
- **Layer Backend:** API Server (Flask) menerima request, mencocokkan UID dengan database, mencocokkan `timestamp` dengan `SesiSholat` terdekat, dan menentukan status kehadiran (Tepat Waktu, Terlambat, Alpha).
- **Layer Frontend:** Aplikasi React.js mengamalkan UI/UX untuk administrasi dan pemuatan _Dashboard_.

## 3. Kebutuhan Fungsional (Functional Requirements)

- **FR-01 (Manajemen Autentikasi):** Sistem harus memungkinkan user login, logout dengan proteksi JWT.
- **FR-02 (Pemrosesan RFID):** Sistem harus bisa memproses UID masuk secara realtime (Waktu Respon < 2 detik).
- **FR-03 (Manajemen Data Master):** Admin harus bisa menambah, mengubah, dan menghapus entitas Data Siswa, Guru, dan Kelas.
- **FR-04 (Peninjauan Absensi):** Backend memiliki algoritma yang memproses otomatis `Status` presensi dengan membandingkan `waktu_tap` vs `waktu_iqamah`.
- **FR-05 (Notifikasi SP Berjenjang):** Sistem harus auto-generate SP apabila mencapai _threshold_ akumulasi Alpha (contoh: 3x Alpha -> SP 1).
- **FR-06 (Export Laporan):** Sistem menyediakan fitur cetak data agregat dan detail dalam format .PDF dan .XLSX.
- **FR-07 (Sengketa / Komplain):** Menyediakan sarana bagi Wali Kelas/Siswa untuk meninjau status yang salah di-record oleh mesin.

## 4. Kebutuhan Non-Fungsional (Non-Functional Requirements)

- **NFR-01 (Reliability):** Sistem ditekankan pada konsistensi rekaman ketika _bottleneck_ trafik tinggi setelah adzan (hingga 500 tap/menit).
- **NFR-02 (Usability):** Antarmuka responsif dan ramah di _mobile view_ karena akan sering diakses Orang Tua dari *smartphone*.
- **NFR-03 (Security):** Semua traffic API harus ter-enkripsi. Password disimpan dengan _Bcrypt_. Endpoint sensitif harus memiliki perlindungan RBAC.
- **NFR-04 (Maintainability):** Penulisan kode berdasarkan MVC/MVT _Clean Architecture_ pattern agar lebih mudah di-_handover_.
