INSERT INTO status_absensi (kode, deskripsi) VALUES
    ('tepat_waktu', 'Tepat Waktu'),
    ('terlambat', 'Terlambat'),
    ('alpha', 'Alpha'),
    ('haid', 'Haid'),
    ('izin', 'Izin'),
    ('sakit', 'Sakit')
ON DUPLICATE KEY UPDATE deskripsi = VALUES(deskripsi);

INSERT INTO waktu_sholat (nama_sholat, waktu_adzan, waktu_iqamah, waktu_selesai) VALUES
    ('Dzuhur', '12:00:00', '12:10:00', '12:30:00'),
    ('Ashar', '15:15:00', '15:25:00', '15:45:00'),
    ('Maghrib', '18:00:00', '18:10:00', '18:25:00')
ON DUPLICATE KEY UPDATE
    waktu_adzan = VALUES(waktu_adzan),
    waktu_iqamah = VALUES(waktu_iqamah),
    waktu_selesai = VALUES(waktu_selesai);

INSERT INTO users (username, password, full_name, email, no_telp, role) VALUES
    ('admin', '$2b$12$NbNVZKsCr3eiSfyLhUSS/u93ecVvB0rdazoo1wNigVQAwSnjrB7fO', 'Administrator', 'admin@sikap.local', '081200000001', 'admin'),
    ('kepsek', '$2b$12$suxpawp.0ylhQBqBB.p9j.Q9Ms/FpsdOP0yMhnvtyXNe08F.bHbkO', 'Kepala Sekolah', 'kepsek@sikap.local', '081200000002', 'kepsek'),
    ('walikelas', '$2b$12$9XBa5SrjJth3dY53OQNS0eE4ej93MCdZ0JqrUaX.kLxt/XHmwMrKS', 'Wali Kelas', 'walikelas@sikap.local', '081200000003', 'wali_kelas'),
    ('gurupiket', '$2b$12$j.p4lsoUfFUdiKzfllFXAOUBUy4xIiMY0pe2hG2D24Kf55L3nkOP2', 'Guru Piket', 'gurupiket@sikap.local', '081200000004', 'guru_piket'),
    ('siswa001', '$2b$12$BabUV7eT1ScUuISRCQd4eecsz3DbjpCC.H4a7GpJxIWLZG.4TuhEW', 'Siswa Demo', 'siswa001@sikap.local', '081200000005', 'siswa'),
    ('ortu001', '$2b$12$17LGKJX3JNQ786AHEYLFbukCwP6Dk.KIXS2LeI9Z1e87l/fseoUzW', 'Orang Tua Demo', 'ortu001@sikap.local', '081200000006', 'orangtua')
ON DUPLICATE KEY UPDATE
    password = VALUES(password),
    full_name = VALUES(full_name),
    email = VALUES(email),
    no_telp = VALUES(no_telp),
    role = VALUES(role);

INSERT INTO kelas (nama_kelas, tingkat, jurusan, id_wali, tahun_ajaran) VALUES
    ('XI RPL 1', 'XI', 'RPL', (SELECT id_user FROM users WHERE username = 'walikelas'), '2025/2026'),
    ('XI RPL 2', 'XI', 'RPL', NULL, '2025/2026'),
    ('X TKJ 1', 'X', 'TKJ', NULL, '2025/2026')
ON DUPLICATE KEY UPDATE
    tingkat = VALUES(tingkat),
    jurusan = VALUES(jurusan),
    id_wali = VALUES(id_wali);

INSERT INTO siswa (id_user, nisn, nama, jenis_kelamin, alamat, no_telp_ortu, id_card, id_kelas) VALUES
    (
        (SELECT id_user FROM users WHERE username = 'siswa001'),
        '5000000001',
        'Siswa Demo',
        'L',
        'Jl. Melati No. 1',
        '081200000006',
        'CARD-001',
        (SELECT id_kelas FROM kelas WHERE nama_kelas = 'XI RPL 1' AND tahun_ajaran = '2025/2026')
    ),
    (
        NULL,
        '5000000002',
        'Ahmad Rifqi',
        'L',
        'Jl. Kenanga No. 2',
        '081200000021',
        'CARD-002',
        (SELECT id_kelas FROM kelas WHERE nama_kelas = 'XI RPL 1' AND tahun_ajaran = '2025/2026')
    ),
    (
        NULL,
        '5000000003',
        'Nabila Putri',
        'P',
        'Jl. Mawar No. 3',
        '081200000022',
        'CARD-003',
        (SELECT id_kelas FROM kelas WHERE nama_kelas = 'XI RPL 1' AND tahun_ajaran = '2025/2026')
    ),
    (
        NULL,
        '5000000004',
        'Fajar Hidayat',
        'L',
        'Jl. Anggrek No. 4',
        '081200000023',
        'CARD-004',
        (SELECT id_kelas FROM kelas WHERE nama_kelas = 'XI RPL 2' AND tahun_ajaran = '2025/2026')
    ),
    (
        NULL,
        '5000000005',
        'Siti Rahma',
        'P',
        'Jl. Flamboyan No. 5',
        '081200000024',
        'CARD-005',
        (SELECT id_kelas FROM kelas WHERE nama_kelas = 'X TKJ 1' AND tahun_ajaran = '2025/2026')
    )
ON DUPLICATE KEY UPDATE
    id_user = VALUES(id_user),
    nama = VALUES(nama),
    jenis_kelamin = VALUES(jenis_kelamin),
    alamat = VALUES(alamat),
    no_telp_ortu = VALUES(no_telp_ortu),
    id_card = VALUES(id_card),
    id_kelas = VALUES(id_kelas);

INSERT INTO perangkat (device_id, nama_device, lokasi, api_key, status, last_ping) VALUES
    ('ESP-RFID-01', 'RFID Gerbang Masjid', 'Masjid Utama', 'demo-device-key-001', 'online', NOW()),
    ('ESP-RFID-02', 'RFID Koridor Kelas', 'Koridor XI', 'demo-device-key-002', 'online', NOW())
ON DUPLICATE KEY UPDATE
    nama_device = VALUES(nama_device),
    lokasi = VALUES(lokasi),
    api_key = VALUES(api_key),
    status = VALUES(status),
    last_ping = VALUES(last_ping);

INSERT INTO sesi_sholat (id_waktu, tanggal, status)
SELECT waktu.id_waktu, daftar_hari.tanggal, CASE WHEN daftar_hari.tanggal = CURDATE() THEN 'aktif' ELSE 'selesai' END
FROM waktu_sholat AS waktu
JOIN (
    SELECT CURDATE() AS tanggal
    UNION ALL SELECT CURDATE() - INTERVAL 1 DAY
    UNION ALL SELECT CURDATE() - INTERVAL 2 DAY
    UNION ALL SELECT CURDATE() - INTERVAL 3 DAY
    UNION ALL SELECT CURDATE() - INTERVAL 4 DAY
    UNION ALL SELECT CURDATE() - INTERVAL 5 DAY
    UNION ALL SELECT CURDATE() - INTERVAL 6 DAY
) AS daftar_hari
WHERE waktu.nama_sholat IN ('Dzuhur', 'Ashar')
ON DUPLICATE KEY UPDATE
    status = VALUES(status);

INSERT INTO absensi (id_siswa, id_sesi, `timestamp`, status, device_id, id_verifikator, verified_at, keterangan)
SELECT
    siswa_target.id_siswa,
    sesi_target.id_sesi,
    TIMESTAMP(seed.tanggal, seed.jam_absen),
    seed.status,
    seed.device_id,
    verifikator.id_user,
    CASE
        WHEN seed.jam_verifikasi IS NOT NULL THEN TIMESTAMP(seed.tanggal, seed.jam_verifikasi)
        ELSE NULL
    END,
    seed.keterangan
FROM (
    SELECT '5000000001' AS nisn, CURDATE() AS tanggal, 'Dzuhur' AS nama_sholat, '12:08:00' AS jam_absen, 'tepat_waktu' AS status, 'ESP-RFID-01' AS device_id, NULL AS username_verifikator, NULL AS jam_verifikasi, 'Tap RFID otomatis di masjid utama' AS keterangan
    UNION ALL
    SELECT '5000000002', CURDATE(), 'Dzuhur', '12:17:00', 'terlambat', 'ESP-RFID-01', NULL, NULL, 'Datang setelah iqamah'
    UNION ALL
    SELECT '5000000003', CURDATE(), 'Dzuhur', '12:20:00', 'izin', NULL, 'gurupiket', '12:35:00', 'Izin kegiatan sekolah'
    UNION ALL
    SELECT '5000000004', CURDATE(), 'Dzuhur', '12:06:00', 'tepat_waktu', 'ESP-RFID-02', NULL, NULL, 'Tap RFID koridor kelas'
    UNION ALL
    SELECT '5000000005', CURDATE(), 'Dzuhur', '12:18:00', 'sakit', NULL, 'gurupiket', '12:40:00', 'Izin sakit dari guru piket'
    UNION ALL
    SELECT '5000000001', CURDATE() - INTERVAL 1 DAY, 'Dzuhur', '12:05:00', 'tepat_waktu', 'ESP-RFID-01', NULL, NULL, 'Tap RFID otomatis'
    UNION ALL
    SELECT '5000000002', CURDATE() - INTERVAL 1 DAY, 'Dzuhur', '12:13:00', 'terlambat', 'ESP-RFID-01', NULL, NULL, 'Datang mepet waktu selesai'
    UNION ALL
    SELECT '5000000003', CURDATE() - INTERVAL 2 DAY, 'Ashar', '15:26:00', 'tepat_waktu', 'ESP-RFID-02', NULL, NULL, 'Tap RFID sesi ashar'
    UNION ALL
    SELECT '5000000004', CURDATE() - INTERVAL 3 DAY, 'Dzuhur', '12:09:00', 'tepat_waktu', 'ESP-RFID-02', NULL, NULL, 'Tap RFID otomatis'
    UNION ALL
    SELECT '5000000005', CURDATE() - INTERVAL 4 DAY, 'Ashar', '15:32:00', 'alpha', NULL, 'gurupiket', '15:50:00', 'Tidak hadir pada sesi ashar'
) AS seed
JOIN siswa AS siswa_target
    ON siswa_target.nisn = seed.nisn
JOIN waktu_sholat AS waktu_target
    ON waktu_target.nama_sholat = seed.nama_sholat
JOIN sesi_sholat AS sesi_target
    ON sesi_target.id_waktu = waktu_target.id_waktu
    AND sesi_target.tanggal = seed.tanggal
LEFT JOIN users AS verifikator
    ON verifikator.username = seed.username_verifikator
LEFT JOIN absensi AS existing_absensi
    ON existing_absensi.id_siswa = siswa_target.id_siswa
    AND existing_absensi.id_sesi = sesi_target.id_sesi
WHERE existing_absensi.id_absensi IS NULL;

INSERT INTO notifikasi (id_user, judul, pesan, tipe, is_read, read_at, created_at)
SELECT
    user_target.id_user,
    seed.judul,
    seed.pesan,
    seed.tipe,
    seed.is_read,
    CASE WHEN seed.is_read = 1 THEN NOW() - INTERVAL seed.jam_lalu HOUR ELSE NULL END,
    NOW() - INTERVAL seed.jam_lalu HOUR
FROM (
    SELECT 'admin' AS username, 'Sinkronisasi Berhasil' AS judul, 'Data demo absensi berhasil dimuat ke sistem.' AS pesan, 'sistem' AS tipe, 1 AS is_read, 8 AS jam_lalu
    UNION ALL
    SELECT 'kepsek', 'Ringkasan Hari Ini', 'Absensi sholat hari ini sudah mulai masuk dari perangkat RFID.' , 'informasi', 0, 2
    UNION ALL
    SELECT 'walikelas', 'Siswa Terlambat', 'Ada siswa XI RPL 1 yang tercatat terlambat pada sesi Dzuhur.' , 'peringatan', 0, 1
    UNION ALL
    SELECT 'gurupiket', 'Perlu Verifikasi', 'Beberapa data izin dan sakit sudah dicatat untuk ditinjau.' , 'informasi', 0, 3
    UNION ALL
    SELECT 'siswa001', 'Absensi Tercatat', 'Kehadiran Dzuhur kamu hari ini sudah tercatat tepat waktu.' , 'absensi', 0, 1
    UNION ALL
    SELECT 'ortu001', 'Laporan Kehadiran Anak', 'Absensi anak Anda hari ini sudah tersedia di dashboard orang tua.' , 'absensi', 0, 1
) AS seed
JOIN users AS user_target
    ON user_target.username = seed.username
LEFT JOIN notifikasi AS existing_notifikasi
    ON existing_notifikasi.id_user = user_target.id_user
    AND existing_notifikasi.judul = seed.judul
    AND existing_notifikasi.pesan = seed.pesan
WHERE existing_notifikasi.id_notifikasi IS NULL;
