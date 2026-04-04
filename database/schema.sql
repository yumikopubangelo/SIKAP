SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS absensi;
DROP TABLE IF EXISTS perangkat;
DROP TABLE IF EXISTS status_absensi;
DROP TABLE IF EXISTS sesi_sholat;
DROP TABLE IF EXISTS waktu_sholat;
DROP TABLE IF EXISTS siswa;
DROP TABLE IF EXISTS kelas;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    no_telp VARCHAR(20),
    role VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_users_role_valid CHECK (
        role IN ('admin', 'kepsek', 'wali_kelas', 'guru_piket', 'siswa', 'orangtua')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE kelas (
    id_kelas INT AUTO_INCREMENT PRIMARY KEY,
    nama_kelas VARCHAR(20) NOT NULL,
    tingkat VARCHAR(5) NOT NULL,
    jurusan VARCHAR(50),
    id_wali INT NULL,
    tahun_ajaran VARCHAR(10) NOT NULL,
    CONSTRAINT fk_kelas_id_wali
        FOREIGN KEY (id_wali) REFERENCES users(id_user)
        ON DELETE SET NULL,
    CONSTRAINT uq_kelas_nama_tahun_ajaran UNIQUE (nama_kelas, tahun_ajaran),
    CONSTRAINT ck_kelas_tingkat_valid CHECK (tingkat IN ('X', 'XI', 'XII'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE siswa (
    id_siswa INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL UNIQUE,
    nisn VARCHAR(20) NOT NULL UNIQUE,
    nama VARCHAR(100) NOT NULL,
    jenis_kelamin VARCHAR(10),
    alamat TEXT,
    no_telp_ortu VARCHAR(20),
    id_card VARCHAR(50) UNIQUE,
    id_kelas INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_siswa_id_user
        FOREIGN KEY (id_user) REFERENCES users(id_user)
        ON DELETE CASCADE,
    CONSTRAINT fk_siswa_id_kelas
        FOREIGN KEY (id_kelas) REFERENCES kelas(id_kelas)
        ON DELETE SET NULL,
    CONSTRAINT ck_siswa_jenis_kelamin_valid CHECK (
        jenis_kelamin IS NULL OR jenis_kelamin IN ('L', 'P')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE waktu_sholat (
    id_waktu INT AUTO_INCREMENT PRIMARY KEY,
    nama_sholat VARCHAR(20) NOT NULL UNIQUE,
    waktu_adzan TIME NOT NULL,
    waktu_iqamah TIME NOT NULL,
    waktu_selesai TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sesi_sholat (
    id_sesi INT AUTO_INCREMENT PRIMARY KEY,
    id_waktu INT NOT NULL,
    tanggal DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'aktif',
    CONSTRAINT fk_sesi_sholat_id_waktu
        FOREIGN KEY (id_waktu) REFERENCES waktu_sholat(id_waktu)
        ON DELETE CASCADE,
    CONSTRAINT uq_sesi_sholat_id_waktu_tanggal UNIQUE (id_waktu, tanggal),
    CONSTRAINT ck_sesi_sholat_status_valid CHECK (status IN ('aktif', 'selesai'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE status_absensi (
    kode VARCHAR(20) PRIMARY KEY,
    deskripsi VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE perangkat (
    device_id VARCHAR(50) PRIMARY KEY,
    nama_device VARCHAR(100) NOT NULL,
    lokasi VARCHAR(100),
    api_key VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'offline',
    last_ping DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_perangkat_status_valid CHECK (status IN ('online', 'offline'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE absensi (
    id_absensi INT AUTO_INCREMENT PRIMARY KEY,
    id_siswa INT NOT NULL,
    id_sesi INT NOT NULL,
    `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    device_id VARCHAR(50) NULL,
    id_verifikator INT NULL,
    verified_at DATETIME NULL,
    keterangan VARCHAR(255) NULL,
    CONSTRAINT fk_absensi_id_siswa
        FOREIGN KEY (id_siswa) REFERENCES siswa(id_siswa)
        ON DELETE CASCADE,
    CONSTRAINT fk_absensi_id_sesi
        FOREIGN KEY (id_sesi) REFERENCES sesi_sholat(id_sesi)
        ON DELETE CASCADE,
    CONSTRAINT fk_absensi_status
        FOREIGN KEY (status) REFERENCES status_absensi(kode)
        ON DELETE RESTRICT,
    CONSTRAINT fk_absensi_device_id
        FOREIGN KEY (device_id) REFERENCES perangkat(device_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_absensi_id_verifikator
        FOREIGN KEY (id_verifikator) REFERENCES users(id_user)
        ON DELETE SET NULL,
    CONSTRAINT uq_absensi_id_siswa_id_sesi UNIQUE (id_siswa, id_sesi),
    CONSTRAINT ck_absensi_status_valid CHECK (
        status IN ('tepat_waktu', 'terlambat', 'alpha', 'haid', 'izin', 'sakit')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
