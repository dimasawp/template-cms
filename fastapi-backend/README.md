# System Storage CMS - Backend Template

Backend template ini merupakan fondasi API modern menggunakan **FastAPI** dengan arsitektur **Modular Monolith** berbasis *Service-Repository Pattern*. Struktur ini dirancang untuk kemudahan skalabilitas, kerapian kode, dan standarisasi antarmuka untuk semua layanan perusahaan.

## 🏗 Arsitektur & Struktur Folder

Proyek ini telah direstrukturisasi agar setiap domain bisnis memiliki *module*-nya masing-masing secara independen.

```bash
backend-template/
├── main.py                    # Entry point aplikasi (Uvicorn server)
├── requirements.txt           # Dependencies
├── app/
│   ├── core/                  # Konfigurasi inti (Database, Security, Config)
│   ├── exceptions/            # Custom exception class & Global Error Handler (@handle_errors)
│   ├── helpers/               # Utility global (Response standar, File handler, Email)
│   ├── seeds/                 # Skrip seeder database
│   └── modules/               # ✨ Domain Modules (Features)
│       ├── __init__.py        # Auto-Registry Loader untuk APIRouter
│       ├── _base/             # BaseService & BaseRepository
│       ├── auth/              # Modul Autentikasi & Swagger OAuth
│       ├── users/             # Modul Manajemen User
│       ├── roles/             # Modul RBAC (Role-Based Access)
│       └── notifications/     # Modul Notifikasi
```

### Pattern `Service-Repository`
Setiap fitur (misal: `users/`) diisolasi dalam satu folder dengan tanggung jawab spesifik:
- `controllers/`: Berisi `APIRouter` untuk menerima *http request* dan mereturn *standard response*.
- `services/`: Memuat *business logic* inti. 
- `repositories/`: Eksekusi query *database* murni menggunakan SQLAlchemy.
- `schemas/`: Pydantic schema untuk validasi Request & Response.
- `models/`: Definisi Entity class database (ORM).

## ✨ Fitur Unggulan

1. **Auto-Discovery Routing**
   Module router (semua file bernama `*_controller.py`) dideteksi dan didaftarkan ke FastAPI secara otomatis melalui `app/modules/__init__.py`. Dev tidak perlu *import* berulang kali di `main.py`.
2. **Global Error Handling & Standard Response**
   Semua respon API telah distandarisasi (*success*, *pagination*, dan *error constraint*) menggunakan `{"status": "...", "message": "...", "data": ...}` sehingga gampang ditangkap oleh Frontend. Lengkap dengan decorator `@handle_errors`.
3. **Swagger UI OAuth2 Full Integration**
   Dilengkapi dengan endpoint `/swagger-login` khusus untuk memfasilitasi login otorisasi via tombol **"Authorize"** bawaan Swagger UI (Khusus Role `super_admin`).

## 🚀 Panduan Menjalankan

### 1. Instalasi Requirements
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Database
Pastikan MySQL sudah berjalan dan sesuaikan kredensial di `app/core/config.py` atau via `.env` (*jika ada*).

### 3. Migrasi Table & Seeding
Jalankan file *seed* untuk generate tabel (via `metadata.create_all`) beserta data `super_admin` awal:
```bash
python -m app.seeds.seed
```
*Username awal: `sa` / `superadmin` | Password: `admin123`*

### 4. Menjalankan Server
Jalankan live-reload Uvicorn server:
```bash
uvicorn main:app --reload
```
Akses otomatis di:
- **API Base:** `http://localhost:8000/api/v1`
- **Swagger Docs:** `http://localhost:8000/docs`
