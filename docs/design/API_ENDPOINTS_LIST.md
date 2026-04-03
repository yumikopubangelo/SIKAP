# 🔌 API ENDPOINTS - COMPLETE LIST (27 Endpoints)


**Total:** 27 endpoints  
**Format:** OpenAPI 3.0 / Swagger  
**Base URL:** `https://api.sikap.sch.id/api/v1`  
**Authentication:** JWT Bearer Token (except /auth/login, /auth/forgot-password)

---

## 🔐 **1. AUTHENTICATION (3 Endpoints)**

### **POST /api/v1/auth/login**
**Deskripsi:** Login multi-role (Admin, Kepsek, Wali, Piket, Siswa, Ortu)

**Request Body:**
```json
{
  "username": "ahmad.fadil",
  "password": "password123",
  "role": "siswa"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 123,
    "username": "ahmad.fadil",
    "role": "siswa",
    "nama": "Ahmad Fadil",
    "siswa_id": 45 // jika role = siswa
  },
  "expires_in": 86400 // 24 jam
}
```

**Error (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Username atau password salah"
}
```

**Used in:** F003 (Login)

---

### **POST /api/v1/auth/logout**
**Deskripsi:** Logout user (blacklist token)

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout berhasil"
}
```

**Used in:** All pages (Logout button)

---

### **POST /api/v1/auth/refresh**
**Deskripsi:** Refresh JWT token (before expiration)

**Headers:** `Authorization: Bearer {old_token}`

**Response (200 OK):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

**Used in:** Auto-refresh mechanism (axios interceptor)

---

---

## 📊 **2. ABSENSI (5 Endpoints)**

### **POST /api/v1/absensi**
**Deskripsi:** Create absensi baru (dari RFID tap atau manual input)

**Headers:** `Authorization: Bearer {token}` (untuk manual) ATAU `X-API-Key: {device_api_key}` (untuk RFID)

**Request Body (dari RFID):**
```json
{
  "uid_card": "A3B2C1D4",
  "device_id": "ESP8266_MASJID_01",
  "timestamp": "2025-02-08T12:05:30Z"
}
```

**Request Body (manual dari Guru Piket):**
```json
{
  "siswa_id": 45,
  "tanggal": "2025-02-08",
  "waktu_sholat": "dzuhur",
  "status": "tepat_waktu",
  "keterangan": "Kartu hilang, manual input",
  "verified_by": "guru_piket_id"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1234,
    "siswa": {
      "id": 45,
      "nama": "Ahmad Fadil",
      "nisn": "0012345678",
      "kelas": "X-RPL-1"
    },
    "waktu_sholat": "dzuhur",
    "timestamp": "2025-02-08T12:05:30Z",
    "status": "tepat_waktu",
    "color": "green"
  },
  "message": "Absensi berhasil dicatat"
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "message": "Siswa sudah tercatat hadir untuk sesi ini"
}
```

**Error (404 Not Found):**
```json
{
  "success": false,
  "message": "Kartu tidak terdaftar"
}
```

**Used in:** Hardware (ESP8266), F023 (Manual Input)

---

### **GET /api/v1/absensi**
**Deskripsi:** Get list absensi (dengan filter & pagination)

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `siswa_id` (int, optional): Filter by siswa
- `kelas_id` (int, optional): Filter by kelas
- `start_date` (date, optional): Filter start date (YYYY-MM-DD)
- `end_date` (date, optional): Filter end date
- `waktu_sholat` (string, optional): dzuhur | ashar | maghrib
- `status` (string, optional): tepat_waktu | terlambat | alpha | sakit | izin | haid
- `page` (int, default: 1): Page number
- `limit` (int, default: 50): Items per page
- `sort` (string, default: desc): asc | desc

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1234,
      "tanggal": "2025-02-08",
      "waktu_sholat": "dzuhur",
      "siswa": {
        "nisn": "0012345678",
        "nama": "Ahmad Fadil",
        "kelas": "X-RPL-1"
      },
      "timestamp": "2025-02-08T12:05:30Z",
      "status": "tepat_waktu",
      "device": "ESP8266_MASJID_01",
      "keterangan": null
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 1250,
    "total_pages": 25
  }
}
```

**Used in:** F015 (Riwayat Absensi), F015A, F015B, F004 (Recent Activity)

---

### **GET /api/v1/absensi/{id}**
**Deskripsi:** Get detail absensi by ID

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1234,
    "siswa": {...},
    "waktu_sholat": "dzuhur",
    "timestamp": "2025-02-08T12:05:30Z",
    "status": "tepat_waktu",
    "device": "ESP8266_MASJID_01",
    "keterangan": null,
    "created_at": "2025-02-08T12:05:31Z",
    "updated_at": null,
    "audit_log": [] // jika ada perubahan
  }
}
```

**Used in:** Detail view (jika ada)

---

### **PUT /api/v1/absensi/{id}**
**Deskripsi:** Update absensi (Wali Kelas / Kepsek only)

**Headers:** `Authorization: Bearer {token}`

**Authorization:**
- Wali Kelas: bisa edit absensi kelas yang diampu
- Kepsek: bisa edit semua absensi

**Request Body:**
```json
{
  "status": "sakit",
  "keterangan": "Siswa sakit, ada surat dokter"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {...},
  "message": "Absensi berhasil diupdate",
  "audit_log_id": 456 // ID audit log entry
}
```

**Trigger:** INSERT ke tabel `audit_log`

**Used in:** F020 (Edit Absensi), F017 (Intervensi Data)

---

### **DELETE /api/v1/absensi/{id}**
**Deskripsi:** Delete absensi (Admin only)

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Absensi berhasil dihapus"
}
```

**Used in:** F015 (jika ada button delete)

---

---

## 📈 **3. REKAPITULASI (3 Endpoints)**

### **GET /api/v1/rekapitulasi/kelas/{id_kelas}**
**Deskripsi:** Get rekapitulasi per kelas (agregasi per siswa)

**Headers:** `Authorization: Bearer {token}`

**Authorization:** 
- Wali Kelas: hanya bisa akses kelas yang diampu
- Kepsek/Admin: bisa akses semua kelas

**Query Params:**
- `bulan` (int, optional): 1-12, default current month
- `tahun` (int, optional): YYYY, default current year

**Response (200 OK):**
```json
{
  "success": true,
  "kelas": {
    "id": 10,
    "nama": "X-RPL-1",
    "wali_kelas": "Pak Budi",
    "total_siswa": 30
  },
  "periode": {
    "bulan": 2,
    "tahun": 2025
  },
  "summary": {
    "total_hadir": 850,
    "total_terlambat": 50,
    "total_alpha": 25,
    "rata_rata_kehadiran": 92.5
  },
  "data": [
    {
      "siswa": {
        "id": 45,
        "nisn": "0012345678",
        "nama": "Ahmad Fadil"
      },
      "total_hadir": 28,
      "total_terlambat": 2,
      "total_sakit": 0,
      "total_izin": 0,
      "total_alpha": 0,
      "total_haid": 0,
      "persentase_kehadiran": 100.0,
      "status_color": "green" // green | yellow | red
    },
    // ... 29 siswa lainnya
  ]
}
```

**Used in:** F006 (Dashboard Wali), F019 (Rekap Kelas)

---

### **GET /api/v1/rekapitulasi/siswa/{id_siswa}**
**Deskripsi:** Get rekapitulasi per siswa individual

**Headers:** `Authorization: Bearer {token}`

**Authorization:**
- Siswa: hanya bisa akses data sendiri
- Orang Tua: hanya bisa akses data anak
- Wali/Kepsek/Admin: bisa akses semua siswa

**Query Params:**
- `bulan` (int, optional): 1-12, default current month
- `tahun` (int, optional): YYYY

**Response (200 OK):**
```json
{
  "success": true,
  "siswa": {
    "id": 45,
    "nisn": "0012345678",
    "nama": "Ahmad Fadil",
    "kelas": "X-RPL-1"
  },
  "periode": {
    "bulan": 2,
    "tahun": 2025
  },
  "summary": {
    "total_hadir": 28,
    "total_terlambat": 2,
    "total_sakit": 0,
    "total_izin": 0,
    "total_alpha": 0,
    "total_haid": 0,
    "persentase_kehadiran": 100.0
  },
  "trend": [ // 7 hari terakhir untuk chart
    {"tanggal": "2025-02-01", "hadir": 3, "alpha": 0},
    {"tanggal": "2025-02-02", "hadir": 3, "alpha": 0},
    // ...
  ],
  "status_sp": {
    "jenis": null, // null | "SP1" | "SP2" | "SP3"
    "tanggal": null,
    "jumlah_alpha": 0
  }
}
```

**Used in:** F008 (Dashboard Siswa), F009 (Dashboard Ortu)

---

### **GET /api/v1/rekapitulasi/sekolah**
**Deskripsi:** Get rekapitulasi overview seluruh sekolah (Kepsek only)

**Headers:** `Authorization: Bearer {token}`

**Authorization:** Kepsek / Admin only

**Query Params:**
- `periode` (string, optional): bulan (default) | 6_bulan | tahun_ajaran

**Response (200 OK):**
```json
{
  "success": true,
  "periode": "6_bulan",
  "summary": {
    "total_siswa": 500,
    "rata_rata_kehadiran": 92.5,
    "total_hadir": 42500,
    "total_alpha": 1250,
    "total_sp": 25
  },
  "trend_per_bulan": [
    {"bulan": "2024-09", "persentase": 91.2},
    {"bulan": "2024-10", "persentase": 92.5},
    // ... 6 bulan
  ],
  "ranking_kelas": [
    {
      "rank": 1,
      "kelas": "XII-RPL-1",
      "wali_kelas": "Pak Asep",
      "persentase": 96.5,
      "total_siswa": 30,
      "status": "excellent" // excellent | good | poor
    },
    // ... semua kelas
  ]
}
```

**Used in:** F005 (Dashboard Kepsek), F016 (Rekap Sekolah)

---

---

## 📄 **4. LAPORAN (2 Endpoints)**

### **POST /api/v1/laporan/generate**
**Deskripsi:** Generate laporan PDF atau Excel

**Headers:** `Authorization: Bearer {token}`

**Authorization:**
- Wali Kelas: hanya bisa generate laporan kelas yang diampu
- Kepsek/Admin: bisa generate semua

**Request Body:**
```json
{
  "jenis": "rekap_kelas", // rekap_kelas | rekap_siswa | rekap_sekolah
  "kelas_id": 10, // required jika jenis = rekap_kelas
  "siswa_id": 45, // required jika jenis = rekap_siswa
  "start_date": "2025-02-01",
  "end_date": "2025-02-28",
  "format": "pdf", // pdf | excel
  "preview": false // true = return preview data, false = generate file
}
```

**Response (200 OK - file generated):**
```json
{
  "success": true,
  "laporan_id": 789,
  "download_url": "https://api.sikap.sch.id/static/laporan/20250208_rekap_kelas_10.pdf",
  "filename": "Rekap_X-RPL-1_Feb2025.pdf",
  "file_size": "245 KB",
  "generated_at": "2025-02-08T14:30:00Z"
}
```

**Response (200 OK - preview mode):**
```json
{
  "success": true,
  "preview_data": {
    "kelas": "X-RPL-1",
    "periode": "Feb 2025",
    "siswa": [...],
    "summary": {...}
  }
}
```

**Used in:** F022 (Generate Laporan)

---

### **GET /api/v1/laporan/{id}/download**
**Deskripsi:** Download laporan yang sudah di-generate

**Headers:** `Authorization: Bearer {token}`

**Response:** File stream (PDF atau Excel)

**Used in:** F022 (Download link), F019 (Export button)

---

---

## 🔔 **5. NOTIFIKASI (3 Endpoints)**

### **GET /api/v1/notifikasi**
**Deskripsi:** Get list notifikasi user

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `status` (string, optional): unread | read | all (default)
- `tipe` (string, optional): sp | absensi | sistem
- `limit` (int, default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "unread_count": 5,
  "data": [
    {
      "id": 100,
      "judul": "Surat Peringatan 1 untuk Ahmad Fadil",
      "isi": "Siswa Ahmad Fadil telah menerima SP1 karena alpha >5x pada periode Jan 2025",
      "tipe": "sp",
      "status_baca": false,
      "created_at": "2025-02-08T10:00:00Z",
      "link": "/surat-peringatan/123" // optional
    },
    // ... more notifikasi
  ]
}
```

**Used in:** F024 (Notifikasi), Navbar (Badge unread count)

---

### **PUT /api/v1/notifikasi/{id}/read**
**Deskripsi:** Mark notifikasi as read

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notifikasi ditandai telah dibaca"
}
```

**Used in:** F024 (Click notifikasi item)

---

### **DELETE /api/v1/notifikasi/{id}**
**Deskripsi:** Delete notifikasi

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notifikasi dihapus"
}
```

**Used in:** F024 (Delete button)

---

---

## 👥 **6. USER MANAGEMENT (5 Endpoints)**

### **POST /api/v1/users**
**Deskripsi:** Create user baru (Admin only)

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "username": "ahmad.fadil",
  "password": "password123",
  "role": "siswa",
  "email": "ahmad@example.com",
  "siswa_id": 45, // jika role = siswa
  "orangtua_id": null // jika role = orangtua
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 150,
    "username": "ahmad.fadil",
    "role": "siswa",
    "email": "ahmad@example.com"
  },
  "message": "User berhasil dibuat"
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "message": "Username sudah digunakan"
}
```

**Used in:** F010A (Form Tambah User)

---

### **GET /api/v1/users**
**Deskripsi:** Get list users (Admin only)

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `role` (string, optional): Filter by role
- `search` (string, optional): Search username/email
- `page` (int, default: 1)
- `limit` (int, default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 150,
      "username": "ahmad.fadil",
      "email": "ahmad@example.com",
      "role": "siswa",
      "status": "aktif",
      "created_at": "2025-01-15T10:00:00Z"
    },
    // ...
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 520,
    "total_pages": 26
  }
}
```

**Used in:** F010 (List User)

---

### **GET /api/v1/users/{id}**
**Deskripsi:** Get detail user by ID

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 150,
    "username": "ahmad.fadil",
    "email": "ahmad@example.com",
    "role": "siswa",
    "status": "aktif",
    "siswa": { // jika role = siswa
      "nisn": "0012345678",
      "nama": "Ahmad Fadil",
      "kelas": "X-RPL-1"
    }
  }
}
```

**Used in:** F010B (Form Edit - load data)

---

### **PUT /api/v1/users/{id}**
**Deskripsi:** Update user (Admin only)

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "email": "ahmad.new@example.com",
  "password": "newpassword123", // optional, kosongkan jika tidak mau ubah
  "status": "aktif" // aktif | nonaktif
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {...},
  "message": "User berhasil diupdate"
}
```

**Used in:** F010B (Form Edit User)

---

### **DELETE /api/v1/users/{id}**
**Deskripsi:** Delete user (Admin only)

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User berhasil dihapus"
}
```

**Used in:** F010 (Delete button)

---

---

## 📚 **7. MASTER DATA (6 Endpoints)**

### **GET /api/v1/kelas**
**Deskripsi:** Get list kelas

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "nama_kelas": "X-RPL-1",
      "tahun_ajaran": "2024/2025",
      "wali_kelas": {
        "id": 5,
        "nama": "Pak Budi"
      },
      "jumlah_siswa": 30
    },
    // ...
  ]
}
```

**Used in:** F011 (List Kelas), Filters (dropdown kelas)

---

### **POST /api/v1/kelas**
**Deskripsi:** Create kelas baru (Admin only)

**Request Body:**
```json
{
  "nama_kelas": "X-RPL-2",
  "tahun_ajaran": "2024/2025",
  "wali_kelas_id": 6
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {...},
  "message": "Kelas berhasil dibuat"
}
```

**Used in:** F011 (Tambah Kelas)

---

### **GET /api/v1/siswa**
**Deskripsi:** Get list siswa (dengan filter)

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `kelas_id` (int, optional): Filter by kelas
- `search` (string, optional): Search NISN/Nama
- `page`, `limit`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 45,
      "nisn": "0012345678",
      "nama": "Ahmad Fadil",
      "kelas": "X-RPL-1",
      "id_card_uid": "A3B2C1D4",
      "no_telp_ortu": "08123456789",
      "status_kartu": "terdaftar" // terdaftar | belum
    },
    // ...
  ]
}
```

**Used in:** F012 (List Siswa)

---

### **POST /api/v1/siswa**
**Deskripsi:** Create siswa baru (Admin only)

**Request Body:**
```json
{
  "nisn": "0012345679",
  "nama": "Budi Santoso",
  "kelas_id": 10,
  "alamat": "Jl. Merdeka No. 123",
  "no_telp_ortu": "08123456790"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {...},
  "message": "Siswa berhasil ditambahkan"
}
```

**Used in:** F012 (Tambah Siswa)

---

### **GET /api/v1/waktu-sholat**
**Deskripsi:** Get jadwal waktu sholat (Adzan, Iqamah, Selesai)

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nama_sholat": "dzuhur",
      "waktu_adzan": "12:00:00",
      "waktu_iqamah": "12:10:00",
      "waktu_selesai": "12:30:00"
    },
    {
      "id": 2,
      "nama_sholat": "ashar",
      "waktu_adzan": "15:00:00",
      "waktu_iqamah": "15:10:00",
      "waktu_selesai": "15:30:00"
    },
    {
      "id": 3,
      "nama_sholat": "maghrib",
      "waktu_adzan": "18:00:00",
      "waktu_iqamah": "18:10:00",
      "waktu_selesai": "18:30:00"
    }
  ]
}
```

**Used in:** F013 (Pengaturan Waktu), ESP8266 (validasi waktu)

---

### **PUT /api/v1/waktu-sholat/{id}**
**Deskripsi:** Update waktu sholat (Admin only)

**Request Body:**
```json
{
  "waktu_adzan": "12:05:00",
  "waktu_iqamah": "12:15:00",
  "waktu_selesai": "12:35:00"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {...},
  "message": "Waktu sholat berhasil diupdate"
}
```

**Used in:** F013 (Edit Waktu)

---

---

## 🔧 **8. ADDITIONAL ENDPOINTS (Optional - 3 Endpoints)**

### **GET /api/v1/perangkat**
**Deskripsi:** Get list perangkat (ESP8266 devices)

**Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "device_id": "ESP8266_MASJID_01",
      "nama_perangkat": "RFID Reader Masjid Lantai 1",
      "lokasi": "Masjid Sekolah",
      "status": "online", // online | offline
      "last_ping": "2025-02-08T14:55:00Z",
      "signal_strength": -45 // dBm WiFi
    }
  ]
}
```

**Used in:** F014 (Monitoring Device)

---

### **POST /api/v1/perangkat/test-connection/{id}**
**Deskripsi:** Test koneksi device (ping)

**Response (200 OK):**
```json
{
  "success": true,
  "latency": 25, // ms
  "message": "Device online"
}
```

**Used in:** F014 (Test button)

---

### **GET /api/v1/surat-peringatan**
**Deskripsi:** Get list Surat Peringatan

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `siswa_id` (int, optional): Filter by siswa

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "siswa": {
        "id": 45,
        "nama": "Ahmad Fadil"
      },
      "jenis_sp": "SP1",
      "tanggal_sp": "2025-02-05",
      "periode_pelanggaran": {
        "start": "2025-01-01",
        "end": "2025-01-31"
      },
      "jumlah_alpha": 6,
      "status": "terkirim", // belum_terkirim | terkirim | dibaca
      "download_url": "https://api.sikap.sch.id/static/sp/SP1_Ahmad_Fadil_20250205.pdf"
    }
  ]
}
```

**Used in:** F021 (Laporan Pelanggaran), F024A (Notifikasi SP Ortu)

---

---

## 📊 **SUMMARY API ENDPOINTS:**

| Category | Endpoints | Count |
|----------|-----------|-------|
| **Authentication** | POST login, POST logout, POST refresh | 3 |
| **Absensi** | POST create, GET list, GET detail, PUT update, DELETE | 5 |
| **Rekapitulasi** | GET kelas, GET siswa, GET sekolah | 3 |
| **Laporan** | POST generate, GET download | 2 |
| **Notifikasi** | GET list, PUT read, DELETE | 3 |
| **User Management** | POST, GET list, GET detail, PUT, DELETE | 5 |
| **Master Data** | GET kelas, POST kelas, GET siswa, POST siswa, GET waktu-sholat, PUT waktu-sholat | 6 |
| **Additional** | GET perangkat, POST test-connection, GET surat-peringatan | 3 |
| **TOTAL** | | **30 endpoints** |

*(Note: Lebih dari 27 karena ada tambahan optional endpoints)*

---

## 🔑 **AUTHENTICATION & AUTHORIZATION:**

### **JWT Token Structure:**
```json
{
  "user_id": 123,
  "username": "ahmad.fadil",
  "role": "siswa",
  "iat": 1707393600,
  "exp": 1707480000
}
```

### **Authorization Matrix:**

| Endpoint | Admin | Kepsek | Wali | Piket | Siswa | Ortu |
|----------|-------|--------|------|-------|-------|------|
| POST /absensi | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| PUT /absensi/{id} | ✅ | ✅ | ✅ (own class) | ❌ | ❌ | ❌ |
| GET /rekapitulasi/kelas | ✅ | ✅ | ✅ (own class) | ❌ | ❌ | ❌ |
| GET /rekapitulasi/siswa | ✅ | ✅ | ✅ | ✅ | ✅ (self) | ✅ (child) |
| POST /users | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| POST /laporan/generate | ✅ | ✅ | ✅ (own class) | ❌ | ❌ | ❌ |

---

## 🛠️ **ERROR CODES:**

| Code | Message | Description |
|------|---------|-------------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate entry |
| 500 | Internal Server Error | Server error |

---


