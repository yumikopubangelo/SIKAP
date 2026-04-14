# Development Guidelines - SIKAP

Dokumen ini berisi panduan alur kerja (workflow) rekayasa perangkat lunak dan standarisasi penulisan kode untuk anggota tim developer proyek SIKAP.

## 1. Lingkungan Pengembangan (Environtment Setup)

### 1.1 Persyaratan Sistem
Pastikan machine Anda memiliki dependensi berikut sebelum memulai:
- Python 3.10+
- Node.js 18+ (beserta NPM terbaru)
- MySQL 8.0 (Pastikan *daemon/service* berjalan di _background_)
- Visual Studio Code dengan ekstensi Python, Prettier, dan ESLint aktif.

### 1.2 Git Branching Strategy
SIKAP menggunakan pendekatan standar **Feature Branch Workflow** (Mirip Git Flow tapi lebih _simplified_):
- `main` : Hanya berisi _production-ready_ kode. _Branch_ ini terproteksi.
- `dev` : Branch utama kolaborasi _developer_.
- `feature/*` : Branch iterasi. Contoh penamaan: `feature/be-login-auth` atau `feature/fe-dashboard-admin`.
- `hotfix/*` : Branch pembenaran langsung jika terjadi _critical error_ di prod.

**Penting:** Selalu mulai dengan `git pull origin dev` sebelum membuat *branch* baru.

## 2. Standar Penulisan Kode (Coding Convention)

### 2.1 Backend (Python - Flask)
Sistem menggunakan style guide **PEP-8**. Lakukan formating otomatis:
- Harus meggunakan `black` formatter.
- Gunakan `isort` untuk pengurutan *imports*.
- Struktur endpoint harus mengembalikan format *JSON response* terpadat:
```json
{
  "status": "success",
  "data": { ... },
  "message": "Data berhasil diambil"
}
```
- Dokumentasikan argumen _Request_ dan _Response_ model baru di `docs/design/API_endpoints.yaml`.

### 2.2 Frontend (JS/React)
- Gunakan konfigurasi _Prettier_ bawaan pada _repository_:
  - Identation: 2 Spaces.
  - Single Quotes.
- Setiap komponen React usahakan menggunakan *Functional Component* beserta *Hooks*.
- Variabel API Fetch (`axios` request) harus diregistrasi di folder `services/`.
- Perhatikan konsistensi UI *Theme* (terutama _color-pallete_ / Typography) dari *library* MUI v5 yang telah diinisialiasi di `src/theme.js`.

### 2.3 Standar Commit Message (Conventional Commits)
Harap gunakan _prefix_ yang memperjelas perubahan kode:
- `feat:` Menambah fitur baru
- `fix:` Memperbaiki celah/bug
- `docs:` Perubahan dokumen (`README.md`, file `.md` lain)
- `refactor:` Perbaikan struktur alur algoritma fungsi code tanpa mengubah output
- `test:` Upgrade mock dan pengujian coverage pytest/jest

*(Contoh: `feat: add PDF and Excel report generator endpoint`)*

## 3. Database dan Migrasi M-M (Model-Migrations)
Seluruh skema tidak diubah paksa melalui SQL query langsung di *database*. Lakukan hal-hal berikut:
1. Ubah struktur di file modelnya secara langsung (`app/models/[nama_file].py`).
2. Generate skema _Alembic_ menggunakan terminal: `flask db migrate -m "penjelasan_perubahan"`.
3. Validasi *script migration* yang terbentuk di folder `migrations/versions/`. Pastikan kolom benar.
4. Tembakkan ke database menggunkan: `flask db upgrade`.

## 4. Pengujian / Testing
- **Backend Unit Testing:** Simpan di `tests/backend/`. Jalankan eksekusi run via Root directory:
  `pytest tests/backend -v`
- Pastikan _API Endpoint Integration_ lulus uji dengan mock _Authentication Header_.

---
**Happy Coding! Jaga Konsistensi, Jaga Ketelitian!**
Tim Pengembang SIKAP
