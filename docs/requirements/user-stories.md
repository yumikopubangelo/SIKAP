# User Stories - Proyek SIKAP

Dokumen ini mendefinisikan *User Stories* dari berbagai _Role_ untuk menggambarkan skenario penggunaan yang terfokus pada pengguna nyata dalam sistem SIKAP.

## 1. Role: Siswa
- **US-SWA-01:** Sebagai seorang **Siswa**, saya ingin **dapat melihat riwayat kehadiran sholat harian saya di dashboard**, agar **saya bisa mengetahui berapa persentase kedisiplinan saya beribadah.**
- **US-SWA-02:** Sebagai seorang **Siswa**, saya ingin **mengajukan dispensasi/izin secara sistem**, agar **ketidakikutsertaan saya saat sedang berhalangan (misalnya sakit) dihitung sah secara sistem dan bukan alpha.**
- **US-SWA-03:** Sebagai seorang **Siswa**, saya ingin **menerima alert saat di-scan jika kartu terbaca dua kali**, agar **menghindari kecurangan sistem atau double-tapping**.

## 2. Role: Orang Tua
- **US-ORT-01:** Sebagai seorang **Orang Tua**, saya ingin **bisa masuk ke web portal di HP**, agar **memantau rekaman harian apakah anak saya telah menunaikan ibadah jamaah sholat di sekolah atau membolos.**
- **US-ORT-02:** Sebagai seorang **Orang Tua**, saya ingin **menerima notifikasi langsung apabila anak saya mendapatkan Surat Peringatan (SP)**, agar **saya dapat melakukan pembinaan sejak dini dari rumah.**

## 3. Role: Wali Kelas
- **US-WAK-01:** Sebagai seorang **Wali Kelas**, saya ingin **bisa melihat indikator persentase ketidakhadiran dari setiap anak dalam kelas saya**, agar **memudahkan saya untuk mengetahui siswa yang paling sering bolos (Top Ofenders).**
- **US-WAK-02:** Sebagai seorang **Wali Kelas**, saya ingin **dapat memberikan konfirmasi untuk _sengketa absensi_ atau pembenaran manual**, agar **apabila alat bermasalah, anak tetap tercatat adil.**

## 4. Role: Guru Piket
- **US-GPK-01:** Sebagai **Guru Piket**, saya ingin **melihat daftar absensi _real-time_ berjalan di layar**, agar **saya dapat memonitor berapa banyak siswa yang belum melakukan tap jelang waktu iqamah.**
- **US-GPK-02:** Sebagai **Guru Piket**, saya ingin **bisa melakukan input data kedatangan siswa secara manual sistem menggunakan NIS/Nama**, agar **siswa yang kartunya tertinggal tetap bisa difasilitasi.**

## 5. Role: Kepala Sekolah
- **US-KEP-01:** Sebagai **Kepala Sekolah**, saya ingin **melihat Laporan Eksekutif tingkat presensi seluruh sekolah di bulan ini**, agar **saya dapat menilai kebijakan sekolah terkait kedisiplinan.**
- **US-KEP-02:** Sebagai **Kepala Sekolah**, saya ingin **memiliki opsi mendownload Laporan berbentuk PDF / Excel yang telah direkap otomatis**, agar **mudah untuk disimpan di arsip akreditasi.**

## 6. Role: Admin
- **US-ADM-01:** Sebagai **System Admin**, saya ingin **mendaftarkan UID kartu RFID baru dan mengkaitkannya dengan NIS Siswa**, agar **kartu siap direkomendasi ke lapangan.**
- **US-ADM-02:** Sebagai **System Admin**, saya ingin **melakukan setup awal kalender/jadwal waktu Sholat setiap awal semester**, agar **sistem otomasi memiliki rujukan/baseline komparasi keterlambatan.**
