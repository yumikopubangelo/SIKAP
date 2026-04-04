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
