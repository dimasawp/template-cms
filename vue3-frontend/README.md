# CMS Template — Frontend Dashboard (Vue 3)

Dashboard administrasi premium yang dibangun dengan **Vue 3**, **Vite**, dan **Tailwind CSS**. Mengutamakan estetika modern, kemudahan penggunaan (UX), dan performa tinggi.

## 🎨 Design System & Aesthetics

Sistem ini menggunakan desain **Premium Matte** dengan dukungan penuh untuk mode terang dan gelap:
- **Adaptive Components**: Komponen seperti *Welcome Banner* otomatis menyesuaikan warna background dan teks berdasarkan tema aktif.
- **Glassmorphism**: Header dan beberapa elemen card menggunakan efek *blur* transparan untuk kesan premium.
- **Standardized Filters**: Semua modul (User, Role, Audit Log) menggunakan sistem filter "Audit Log Style" dengan indikator status berwarna dan tombol aksi yang kontras.

## 🚀 Persiapan Awal

### 1. Instalasi Dependensi
```bash
npm install
```

### 2. Konfigurasi Environment
```bash
cp .env.example .env
```
Sesuaikan `VITE_API_BASE_URL` ke `http://localhost:8000/api/v1`.

### 3. Jalankan Development Server
```bash
npm run dev
```
Aplikasi berjalan di `http://localhost:5173`.

## 🛠 Fitur Unggulan

- **Real-time Config Sync**: Frontend menunggu konfigurasi dari backend (`isInitialized`) sebelum mencoba koneksi WebSocket, mencegah error 403 saat WS dinonaktifkan.
- **Premium Modals**: Modal detail (seperti pada Audit Log) telah dioptimalkan ukurannya (`max-w-3xl`) agar tetap nyaman dibaca namun tidak memakan ruang layar secara berlebihan.
- **WIB Display**: Seluruh tampilan waktu di dashboard secara otomatis menampilkan zona waktu WIB (UTC+7) sesuai standar backend.
- **Session Control**: Dashboard integrasi untuk memantau sesi aktif dan melakukan *force logout* pada user tertentu.

## 🏗 Struktur Folder Penting

- `src/components/ui/`: Koleksi komponen UI dasar (Button, Input, Dialog, dll).
- `src/components/common/`: Komponen layout reusable (DataTableToolbar, MaintenanceBanner).
- `src/composables/`: Logika reusable seperti `useRealtime`, `useDataTable`, dan `useTheme`.
- `src/stores/`: Manajemen state global menggunakan Pinia (Auth, Settings).

## 📡 Integrasi Real-time (`useRealtime`)

Composabel `useRealtime` menangani sinkronisasi data secara cerdas:
1.  Mengecek status `enable_websockets` dari backend.
2.  Jika `True`, membuka koneksi WebSocket untuk update instan.
3.  Jika `False` atau gagal konek, otomatis beralih ke **HTTP Polling** setiap 60 detik.

## 🏷 Versi & Metadata
Frontend membaca versi aplikasi (`APP_VERSION`) dan nama situs secara dinamis dari backend. Untuk mengubahnya, Anda cukup memperbarui file `config.py` di backend.
