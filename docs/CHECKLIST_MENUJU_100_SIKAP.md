# Checklist Menuju 100% SIKAP

## Tujuan

Dokumen ini merangkum sisa pekerjaan paling realistis agar backend dan frontend SIKAP dapat dianggap `100% selesai` untuk scope proyek akhir, yaitu:

- fitur dalam scope final benar-benar berjalan;
- dokumentasi sesuai dengan implementasi aktual;
- seluruh flow utama bisa didemokan tanpa workaround besar;
- pengujian inti sudah memadai;
- tidak ada gap besar antara backend, frontend, dan perangkat RFID.

## Definisi 100%

Backend dan frontend dapat dianggap `100%` bila memenuhi kondisi berikut:

1. semua fitur final pada scope proyek aktif dan stabil;
2. semua role dapat menjalankan flow utamanya;
3. integrasi backend, frontend, dan hardware tidak terputus;
4. dokumentasi, API, dan implementasi sinkron;
5. pengujian fungsional utama lulus.

## Ringkasan Prioritas

| Area | Prioritas | Target hasil |
| --- | --- | --- |
| Backend API consistency | Tinggi | Semua endpoint konsisten dan terdokumentasi |
| Frontend feature completeness | Tinggi | Semua flow utama bisa dipakai tiap role |
| RFID end-to-end | Tinggi | Registrasi UID dan absensi perangkat berjalan nyata |
| Testing | Tinggi | Flow inti punya bukti uji yang cukup |
| Dokumentasi sinkron | Menengah | Tidak ada angka/fitur yang bertentangan |
| UX polish | Menengah | Error, loading, empty state, success state rapi |
| Deployment readiness | Menengah | Stack lokal dan demo siap dijalankan ulang |

## A. Checklist Backend Menuju 100%

### A1. Rapikan konsistensi endpoint

- [x] Samakan prefix endpoint notifikasi agar konsisten dengan endpoint lain.
  Final route: `/api/v1/notifikasi/...`.
- [x] Putuskan format final route download laporan dan pastikan dokumen API mengikuti implementasi aktual.
  Final route: `/api/v1/laporan/download/<id_laporan>`.
- [x] Periksa semua endpoint terhadap route aktual aplikasi.
  Hasil audit dicatat pada `docs/AUDIT_ENDPOINT_VERIFIKASI_RFID_DAN_COVERAGE.md`.

### A2. Finalisasi flow RFID dan perangkat

- [V] Pastikan flow `rfid-capture/session` benar-benar stabil untuk create/edit user siswa.
- [V] Uji alur lengkap:
  admin buka sesi scan -> kartu ditap dua kali -> UID terkonfirmasi -> UID tersimpan ke akun siswa.
- [V] Uji alur absensi perangkat nyata:
  perangkat kirim `device_id` + `uid_card` + `X-API-Key` -> backend validasi -> absensi tersimpan.
- [ ] Verifikasi mode dengan signature dan tanpa signature sama-sama terdokumentasi jelas.
- [ ] Tambahkan bukti uji untuk endpoint RFID:
  `backend/app/routes/rfid.py` dan flow `backend/app/routes/users.py`.

### A3. Bereskan warning dan technical debt

- [X] Ganti pemakaian `Query.get()` legacy pada fitur laporan ke pola SQLAlchemy yang lebih baru.
- [X] Audit warning lain saat menjalankan test penuh agar tidak ada warning penting yang tertinggal.
- [X] Pastikan semua response error memakai format yang konsisten.

### A4. Lengkapi validasi dan business rules

- [X] Review semua endpoint create/update agar validasi field wajib lengkap.
- [X] Pastikan role access benar untuk semua fitur:
  admin, kepsek, wali_kelas, guru_piket, siswa, orangtua.
- [X] Pastikan semua business rule utama punya test:
  duplikasi absensi, status terlambat, manual input, surat peringatan, izin, sengketa.

### A5. Testing backend sampai layak disebut final

- [X] Tambah test untuk modul yang masih relatif minim:
  notifikasi, RFID, perangkat, jadwal piket, izin, sengketa.
- [x] Jalankan test penuh dan hasilkan bukti awal untuk laporan.
  Hasil verifikasi 28 April 2026: `64 passed`, coverage backend `85%`, HTML report tersedia di `backend/htmlcov/`.
- [x] Tambahkan panduan coverage report agar klaim kualitas backend lebih kuat.
  Lihat `docs/AUDIT_ENDPOINT_VERIFIKASI_RFID_DAN_COVERAGE.md`.

## B. Checklist Frontend Menuju 100%

### B1. Selesaikan flow utama per role

- [ ] Admin dapat:
  login, lihat dashboard, kelola user, scan RFID siswa, atur waktu sholat, buka monitoring, generate laporan.
- [ ] Kepsek dapat:
  login, lihat dashboard sekolah, lihat data sekolah, monitoring, generate laporan.
- [ ] Wali kelas dapat:
  login, lihat dashboard kelas, lihat rekap, generate laporan kelas/siswa, lihat surat peringatan.
- [ ] Guru piket dapat:
  login, lihat dashboard, input absensi manual, lihat jadwal piket.
- [ ] Siswa dapat:
  login, lihat dashboard pribadi, notifikasi, surat peringatan bila ada.
- [ ] Orang tua dapat:
  login, lihat data anak, notifikasi, surat peringatan.

### B2. Rapikan fitur yang masih membatasi usability

- [ ] Ubah laporan siswa agar tidak lagi bergantung pada input `id_siswa` manual di `frontend/src/pages/ReportPage.jsx`.
  Target akhir: pakai dropdown atau pencarian siswa.
- [ ] Hubungkan identitas sekolah di `frontend/src/pages/SchoolDataPage.jsx` ke data backend final, bukan hanya `schoolProfileFallback` dari `frontend/src/config.js`.
- [ ] Pastikan flow RFID di `frontend/src/pages/UserFormPage.jsx` selesai dan nyaman dipakai admin saat demo.
- [ ] Review apakah semua halaman yang sudah ada di `frontend/src/pages/` benar-benar bisa diakses dan dipakai sesuai role.

### B3. Rapikan UX dan state handling

- [ ] Semua halaman punya state:
  loading, error, success, dan empty state.
- [ ] Semua form penting punya validasi yang jelas dan pesan error yang membantu.
- [ ] Setelah aksi penting seperti simpan, update, hapus, generate laporan, user mendapat feedback yang konsisten.
- [ ] Pastikan logout, session expiry, dan refresh data tidak membingungkan pengguna.

### B4. Finalisasi real-time dan integrasi data

- [ ] Pastikan MQTT benar-benar menyegarkan dashboard sesuai event yang dikirim.
- [ ] Pastikan notifikasi frontend tidak lagi perlu fallback dua jalur yang membingungkan jika endpoint sudah diseragamkan.
- [ ] Uji ulang seluruh integrasi frontend terhadap backend setelah route diseragamkan.

### B5. UI readiness untuk demo akhir

- [ ] Pastikan semua halaman inti terlihat rapi di desktop.
- [ ] Uji minimal tampilan mobile/tablet untuk halaman penting.
- [ ] Hilangkan flow yang masih terasa “developer oriented”, seperti input ID mentah, jika masih ada.

## C. Checklist Integrasi Hardware dan Sistem

- [ ] Siapkan minimal satu perangkat RFID yang benar-benar terdaftar di tabel `perangkat`.
- [ ] Pastikan `DEVICE_ID`, `API_KEY`, `API_ENDPOINT`, dan Wi-Fi perangkat benar.
- [ ] Lakukan uji nyata:
  satu siswa tap kartu -> absensi masuk -> dashboard berubah -> data muncul di rekap/laporan.
- [ ] Uji kegagalan:
  kartu tidak terdaftar, device salah API key, sesi sholat tidak aktif, duplikasi absensi.
- [ ] Dokumentasikan hasil uji tersebut dengan screenshot atau log untuk lampiran laporan.

## D. Checklist Dokumentasi Menuju 100%

- [ ] Sinkronkan angka endpoint, jumlah modul, dan status fitur antar dokumen.
- [ ] Perbarui catatan implementasi yang sudah berubah.
  Contoh: UI RFID di frontend tampak sudah mulai tersedia, jadi dokumen harus mencerminkan status terbaru.
- [ ] Pastikan `readme.md`, `docs/README.md`, `docs/LAPORAN_IMPLEMENTASI_SIKAP.md`, dan `docs/design/API_ENDPOINTS_LIST.md` tidak saling bertentangan.
- [ ] Tambahkan satu tabel “fitur selesai vs belum selesai” di laporan akhir agar penguji mudah memahami posisi sistem.

## E. Checklist Siap Presentasi / Siap Demo

- [ ] Seed data dan akun demo berjalan normal.
- [ ] Backend bisa hidup tanpa error.
- [ ] Frontend bisa login dan memuat dashboard.
- [ ] Generate laporan PDF/Excel berhasil.
- [ ] Notifikasi dan role access dapat diperlihatkan.
- [ ] Satu flow RFID berhasil ditunjukkan, atau jika perangkat tidak siap, siapkan simulasi yang jujur dan konsisten.
- [ ] Monitoring Grafana dapat dibuka jika ingin menunjukkan aspek infrastruktur.

## F. Urutan Eksekusi yang Disarankan

Urutan paling efisien untuk menutup sisa pekerjaan:

1. rapikan backend API dan dokumentasi endpoint;
2. finalkan flow RFID end-to-end;
3. benahi frontend pada laporan siswa, data sekolah, dan role flow;
4. tambah pengujian untuk modul yang belum kuat;
5. sinkronkan seluruh dokumen dan tabel presentasi;
6. lakukan gladi demo dari awal sampai akhir.

## G. Target Persentase Setelah Checklist Diselesaikan

Jika checklist prioritas tinggi selesai, estimasi statusnya bisa naik menjadi:

| Komponen | Estimasi setelah perbaikan |
| --- | --- |
| Backend REST API | 100% |
| Frontend React | 100% |
| Integrasi Hardware RFID | 85-100% tergantung uji nyata |
| Pengujian Backend | 95-100% |
| Dokumentasi | 95-100% |

## H. Kesimpulan

Sisa pekerjaan menuju `100%` pada SIKAP bukan lagi membangun fondasi dari nol, melainkan menyelesaikan integrasi terakhir, menyamakan dokumentasi dengan implementasi, dan memastikan semua flow utama benar-benar siap dipresentasikan serta diuji.

Dengan kata lain, sistem ini sudah punya pondasi kuat. Target berikutnya adalah `closing gaps`, bukan `starting over`.
