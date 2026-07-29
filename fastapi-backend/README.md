# CMS Template — Backend API (FastAPI)

REST API backend yang tangguh dan modular, dibangun dengan **FastAPI**, **SQLAlchemy 2.0**, dan **MySQL**. Mendukung RBAC tingkat lanjut, audit logging, manajemen sesi aktif, dan standarisasi waktu lokal (WIB).

## 🏗 Struktur Proyek

```
fastapi-backend/
├── app/
│   ├── core/                        # Konfigurasi, Database, Security, WebSocket
│   ├── modules/                     # Feature Modules (Auto-registered)
│   ├── helpers/                     # Response formats, Date helpers (WIB)
│   └── exceptions/                  # Global error handling
├── db/                              # Database tools
│   ├── migrations/                  # Alembic migration history
│   ├── seeds/                       # Master data seeder
│   └── scripts/                     # One-off migration scripts
├── storage/                         # Local file storage (uploads)
├── tests/                           # Integration tests (Pytest)
└── main.py                          # Entry point
```

## 🚀 Persiapan Awal

### 1. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Environment
```bash
cp .env.example .env
```
Edit `.env` dan sesuaikan kredensial database Anda.

### 3. Setup Database (Migrasi & Seed)
**Penting:** Selalu gunakan Alembic untuk sinkronisasi tabel.
```bash
# Membuat tabel awal & master data
python -m db.seeds.seed

# Menjalankan migrasi terbaru (dari folder db/)
cd db && alembic upgrade head
```

### 4. Jalankan Server
```bash
uvicorn main:app --reload
```
API dapat diakses di `http://localhost:8000` dan Swagger UI di `http://localhost:8000/docs`.

## 🕒 Standarisasi Waktu (WIB)

Seluruh sistem ini menggunakan waktu **WIB (UTC+7)** sebagai standar penyimpanan di database.
- **Helper**: Gunakan `app.helpers.date_helper.get_now_wib()` untuk mendapatkan waktu saat ini dalam format WIB.
- **Database**: Kolom `created_at` dan `updated_at` otomatis menggunakan WIB dan disimpan sebagai *naive datetime* (tanpa timezone info) untuk kompatibilitas MySQL `DATETIME`.

## 🗄 Manajemen Migrasi (Alembic)

Setiap kali Anda mengubah model di `app/modules/.../models/`, ikuti langkah ini:

1.  **Generate Migration**:
    ```bash
    cd db && alembic revision --autogenerate -m "deskripsi_perubahan"
    ```
2.  **Review**: Cek file baru di `db/migrations/versions/`.
3.  **Apply**:
    ```bash
    cd db && alembic upgrade head
    ```

## 🔐 Keamanan & RBAC

Sistem ini menggunakan **Permission-Based Access Control**:
- **Permissions**: Izin spesifik seperti `users.create`, `roles.delete`.
- **Roles**: Kumpulan izin (Super Admin, Admin, dll).
- **Session Validation**: Setiap request divalidasi terhadap `user_sessions` di database. Jika sesi dihapus/di-revoke oleh admin, user akan langsung ter-logout secara otomatis.

## 📁 Media & Storage

- **Auto-Organization**: File diupload ke `storage/uploads/YYYY/MM/`.
- **Soft Delete**: Menghapus media hanya akan menandai `deleted_at`, file fisik tetap ada kecuali dilakukan *hard delete*.

## 🧪 Testing

Gunakan Pytest untuk menjalankan tes integrasi:
```bash
pytest -v
```
Tes menggunakan **SQLite In-Memory**, sehingga database asli Anda tetap aman.

## 🏷 Versi Sistem
Versi dikontrol secara terpusat di `app/core/config.py` (`APP_VERSION`). Frontend akan otomatis menyesuaikan tampilan footer berdasarkan nilai ini.
