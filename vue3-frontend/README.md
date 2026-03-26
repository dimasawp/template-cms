# System Storage CMS - Frontend Template

Frontend template ini merupakan fondasi web dashboard menggunakan **Vue 3 + Composition API**, **TypeScript**, **Vite**, dan **Tailwind CSS**. Menggunakan sistem desain standar perusahaan (Matte Dark Mode Palette) dan integrasi komponen **Shadcn-Vue**.

## 🛠 Teknologi Utama

- **Framework**: Vue 3 (Composition API, `<script setup>`)
- **Routing**: Vue Router
- **State Management**: Pinia
- **Styling**: Tailwind CSS v3 (`index.css` global theme)
- **UI Components**: Shadcn-Vue (headless UI) + Lucide Icons
- **HTTP Client**: Axios (dengan Interceptor API & Error Handler)
- **Validation**: Zod / Vuelidate (terintegrasi jika diperlukan)

## 🏗 Struktur Proyek

```bash
frontend-template/
├── index.html                   # HTML Entry point
├── tailwind.config.js           # Konfigurasi utility Tailwind & Semantic Colors
├── src/
│   ├── main.ts                  # Inisiasi App, Router, Pinia, dan Sinkronisasi Tema
│   ├── assets/
│   │   └── index.css            # Root & Dark theme CSS Variables (Palet warna)
│   ├── components/
│   │   ├── common/              # Komponen standar (Pagination, Header, dll)
│   │   └── ui/                  # Shadcn UI Base Components (Button, Input, Card)
│   ├── composables/             # Vue Composables (Reusability Logic)
│   │   └── useTheme.ts          # Singleton state untuk Toggle Dark/Light Mode
│   ├── layouts/                 # Dashboard Layout & Auth Layout
│   ├── router/                  # Definisi routes
│   ├── services/                # Module API Call Axios (`authService.ts`, dll)
│   ├── stores/                  # Pinia Stores (Global state management)
│   └── views/                   # Halaman / Pages
│       ├── auth/                # Halaman Login
│       └── dashboard/           # Dashboard & Sub-menu
```

## ✨ Fitur Unggulan

1. **Persistent Theme Engine**
   Dark/Light mode *toggle* yang berifat singleton-state (`useTheme.ts`) berjalan mulus dari halaman Login hingga Dashboard tanpa berkedip (*flickering*) saat *reload* halaman karena sinkronisasi dari *localStorage* berjalan sinkronus.
   *Palet warna menggunakan sentuhan "Matte Desaturated"* untuk rasa premium.
2. **UI Component Gallery**
   Sudah disertai rute demonstrasi `http://localhost:5173/components` yang berisi dokumentasi dan *preview* semua komponen UI yang tersedia (Loading, Tables, Cards, Buttons, Inputs, Dialogs).
3. **Advanced Interceptors & Standar Integrasi API**
   Sistem penangkap error (*HTTP interceptors* di `api.ts`) yang langsung dihubungkan dengan error envelope dari `Backend-Template`, otomatis memunculkan global toast validation/error message tanpa harus menumpuk blok `try-catch` di komponen *views*.

## 🚀 Panduan Menjalankan

### 1. Instalasi Node Modules
Gunakan Node versi LTS yang direkomendasikan.
```bash
npm install
```

### 2. Environment Variables
Buat file `.env` di *root directory* dan sesuaikan dengan URL backend.
```env
VITE_API_URL=http://localhost:8000
```

### 3. Menjalankan Server Development
```bash
npm run dev
```
Buka browser dan arahkan ke `http://localhost:5173`.
Aplikasi akan secara otomatis terhubung dengan Backend-Template. Selamat mengembangkan!
