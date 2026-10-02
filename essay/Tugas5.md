# Tugas 5

## [Pertanyaan Reflektif](https://pbp.cs.ui.ac.id/assignments/individual/tugas-5.html#pertanyaan-reflektif)

> 1. Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!

Debouncing adalah teknik menunda eksekusi sebuah fungsi sampai suatu jeda waktu tertentu berlalu tanpa ada pemicu (event) baru. Setiap kali event baru terjadi sebelum jeda itu selesai, timer sebelumnya dibatalkan dan dihitung ulang dari awal, sehingga fungsi yang sebenarnya baru benar-benar dijalankan setelah pengguna "diam" sesaat.

Saya menerapkannya dengan pola yang sama di dua tempat berbeda minggu ini, pada kolom pencarian judul proyek di halaman Projects (`search-input`, `SEARCH_DEBOUNCE_DELAY = 300`) dan pada kolom pencarian nama institusi di halaman Education (`education-search-input`). Setiap event `input` memicu `clearTimeout(timer)` lalu `setTimeout(fn, 300)` yang baru benar-benar memanggil `fetchProjects()`/`fetchEducation()` setelah 300 milidetik tanpa karakter baru diketik.

Teknik ini penting justru karena karakteristik AJAX[^1] itu sendiri, setiap pemanggilan `fetch()` adalah satu permintaan jaringan nyata ke server, bukan sekadar perhitungan di sisi klien. Tanpa debouncing, event `input` terpicu untuk setiap karakter, jadi mencari kata "Django" berarti mengirim enam permintaan AJAX berturut-turut dalam hitungan detik, padahal lima di antaranya langsung terbuang begitu karakter berikutnya diketik. Ini membebani server tanpa perlu, dan kalau respons datang tidak berurutan, hasil pencarian yang ditampilkan bisa salah (hasil query lama menimpa hasil query terbaru). Saya menutup risiko balapan ini dengan `AbortController` sebelum setiap `fetch` baru, supaya permintaan lama yang belum selesai langsung dibatalkan begitu permintaan baru dikirim.

Satu hal yang justru saya pelajari lebih dalam ketika menerapkan pola serupa untuk filter kategori di halaman Experience: saya sengaja **tidak** memasang debounce di sana, karena filternya berbentuk `<select>` dropdown, bukan input teks bebas. Event `change` pada `<select>` hanya terpicu sekali setiap pengguna memilih satu opsi, jadi tidak ada "ketikan berturut-turut" yang perlu ditunda. Ini menyadarkan saya bahwa debouncing bukan aturan wajib setiap ada `fetch()`, tapi solusi spesifik untuk pola input yang memang bisa berulang cepat dalam waktu singkat.

> 2. Jelaskan fungsi dari penggunaan `await` ketika kita menggunakan `fetch()`! Apa yang akan terjadi jika kita tidak menggunakan `await`?

`await` adalah keyword yang hanya bisa dipakai di dalam `async function`, dan fungsinya menghentikan eksekusi baris kode berikutnya sampai *Promise* yang mengikutinya benar-benar selesai diproses (*resolved* atau *rejected*). Tanpa `await`, kode tidak menunggu, ia langsung lanjut ke baris selanjutnya sementara Promise-nya masih berjalan di belakang layar.

Hampir semua fungsi `async` saya minggu ini (`addProject`, `addEducation`, `addExperience`, `fetchProjects`, `fetchEducation`, `fetchExperience`) memakai pola yang sama: `const response = await fetch(...)` diikuti `const result = await response.json()`. Dua `await` ini menunggu dua hal berbeda, `await fetch(...)` menunggu sampai server membalas (header & status sudah diketahui), sedangkan `await response.json()` menunggu body respons itu selesai diparsing dari teks mentah menjadi objek JavaScript. Kalau saya hanya menulis `const response = fetch(...)` tanpa `await`, variabel `response` bukan berisi objek `Response` seperti yang saya harapkan, melainkan sebuah Promise yang masih *pending*. Baris berikutnya yang mencoba membaca `response.ok` atau memanggil `response.json()` akan langsung gagal, karena properti dan method itu memang belum ada pada Promise yang belum selesai.

Saya membayangkan konsekuensi paling nyatanya lewat `submitButton.disabled = true` yang saya pasang sebelum `fetch` dan `submitButton.disabled = false` di blok `finally`. Kalau `await` di depan `fetch()` dihilangkan, blok `try` akan langsung lompat ke `finally` tanpa menunggu server membalas sama sekali, jadi tombol submit akan langsung aktif lagi padahal permintaan sebelumnya belum diketahui berhasil atau gagal. Padahal `disabled` ini justru saya pasang untuk mencegah klik ganda yang mengirim dua permintaan `POST` yang sama sebelum yang pertama selesai diproses server.

> 3. Jelaskan apa itu serangan XSS (*Cross-Site Scripting*) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!

XSS[^2] adalah serangan di mana penyerang berhasil menyisipkan kode skrip miliknya ke dalam halaman web yang kemudian ikut dijalankan oleh browser pengunjung lain, seolah-olah skrip itu memang bagian sah dari halaman tersebut. Salah satu variannya, *stored XSS*, menyimpan skrip berbahaya itu ke database (misalnya sebagai judul proyek) sehingga ia otomatis dijalankan ulang setiap kali data itu ditampilkan ke siapa pun yang membuka halamannya, bukan hanya sekali ke orang yang pertama kali menyisipkannya.

Saya benar-benar membuktikan celah ini sendiri sebelum menambalnya. Saya menambahkan proyek baru dengan Nama Proyek persis `<img src="x" onerror="alert('XSS!')">` lewat modal tambah proyek yang sudah saya bangun. Begitu kartu proyek itu dimuat ulang lewat AJAX, alert "XSS!" benar-benar muncul, dan akan muncul juga untuk siapa pun yang membuka `/projects/`, termasuk pengunjung yang belum login.

Penyebabnya ada di cara saya merender kartu proyek lewat `buildProjectCardElement`, nilai dari JSON seperti `project.title` langsung disisipkan ke dalam *template literal* JavaScript lalu dipasang lewat `articleElement.innerHTML`. Di titik ini tidak ada mekanisme apa pun yang melakukan *escaping*, browser memperlakukan setiap tag HTML di dalam data itu sebagai markup sungguhan, termasuk atribut event handler seperti `onerror`. Ini berbeda jauh dari cara Django Template Language merender `{{ variabel }}` biasa, di mana karakter seperti `<` dan `>` otomatis diubah jadi entity HTML (`&lt;` dan `&gt;`) sebelum dikirim ke browser, jadi walaupun saya menyisipkan judul proyek yang sama persis lewat form Django biasa (bukan AJAX), ia akan tampil sebagai teks mentah, bukan dieksekusi sebagai HTML.

Karena itu saya menerapkan dua lapis pertahanan, bukan cuma satu. Pertama, fungsi `escapeHtml` di JavaScript yang mengubah lima karakter khusus HTML (`&`, `<`, `>`, `"`, `'`) jadi entity sebelum nilainya disisipkan ke `innerHTML`, meniru persis apa yang sebelumnya dikerjakan otomatis oleh Django. Kedua, di sisi server saya menambahkan method `clean_title`, `clean_meta`, `clean_tags`, `clean_description` pada `ProjectForm` (dan pola serupa pada `EducationForm`, `ExperienceForm`) yang memanggil `strip_tags` untuk membuang tag HTML sejak data masuk. Saya sengaja tidak mengandalkan satu lapis saja karena `strip_tags` sendiri, menurut dokumentasi Django, tidak dijamin aman untuk ditampilkan langsung sebagai HTML, jadi *escaping* di sisi tampilan tetap jadi pertahanan utama, sementara pembersihan di server berfungsi sebagai lapisan tambahan yang mencegah data kotor tersimpan sejak awal.

### AI Disclosure

Minggu ini saya menggunakan AI (Claude, Anthropic) untuk membantu memahami dan mengecek kembali hasil pekerjaan yang sudah saya kerjakan sebelumnya. Sebelum menggunakan AI, saya sudah lebih dulu berdiskusi dengan asisten dosen dan mengerjakan beberapa bagian bersama teman-teman. Dari proses tersebut, saya mendapatkan gambaran mengenai cara pengerjaan dan mencoba menerapkannya sendiri di proyek saya.

Setelah itu, saya menggunakan AI lebih banyak untuk bertanya ketika ada bagian yang masih membingungkan atau ketika hasil implementasi saya tidak berjalan seperti yang diharapkan. Saya memberikan kode dan beberapa file dari proyek saya kepada AI agar penjelasannya bisa disesuaikan dengan kondisi proyek yang sudah saya buat, bukan hanya berdasarkan contoh umum. AI membantu saya memahami hubungan antar file dan mencari kemungkinan penyebab ketika muncul error.

Saya juga tidak langsung menganggap solusi dari AI pasti benar. Kalau ada saran perubahan kode, saya mencoba menerapkannya terlebih dahulu dan melihat hasilnya sendiri. Ketika muncul error, saya biasanya memberikan traceback atau hasil dari browser dan DevTools kepada AI agar saya bisa mengetahui bagian mana yang sebenarnya bermasalah. Setelah mendapatkan penjelasan, saya tetap melakukan pengecekan dan pengujian sendiri untuk memastikan perubahan tersebut benar-benar bekerja.

Menurut saya, penggunaan AI minggu ini lebih banyak berperan sebagai teman diskusi dan alat bantu debugging. Hasil pekerjaan tetap berasal dari proses belajar, diskusi dengan asisten dosen dan teman-teman, serta percobaan yang saya lakukan sendiri. Saya juga menyadari bahwa menggunakan AI tidak berarti saya bisa langsung menyalin kode yang diberikan, karena kode tersebut tetap harus disesuaikan dengan struktur proyek saya dan saya harus memahami alasan di balik setiap perubahan yang dilakukan.

## Installation and Deployment

*(Tidak ada perubahan `models.py` atau migrasi baru minggu ini — Tutorial 05 dan Tugas 5 murni perubahan di level view, template, dan JavaScript. Langkah instalasi di bawah masih sama seperti Tugas 2, ditambah penjelasan singkat soal berkas statis baru.)*

### Requirements

- Python 3.10+
- pip
- Git
- Django `~=5.2` (lihat `requirements.txt`; setup PostgreSQL PWS belum mendukung Django 6.x)

### Local Preview

Clone repositori ini
```bash
git clone https://github.com/<username>/myportofolio.git
cd myportofolio
```

Buat virtual environment
```bash
python -m venv env

# Windows (cmd/PowerShell)
env\Scripts\activate

# Unix (macOS/Linux)
source env/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Buat file `.env` di root proyek untuk konfigurasi lokal:
```
PRODUCTION=False
```

Jalankan migrasi dan server
```bash
python manage.py migrate  # pengembangan lokal memakai SQLite secara default
python manage.py runserver
```

Lalu buka `http://127.0.0.1:8000/`.

Fitur AJAX, toast notification, dan modal minggu ini tidak memerlukan langkah setup tambahan, berkas statis baru (`static/js/common.js`, `static/js/toast.js`) otomatis termuat lewat `{% static %}` di `base.html` dan disajikan langsung oleh `runserver` saat pengembangan.

### Populating Data

Lihat bagian "Populating Data" di Tugas 2 (tidak berubah) — gunakan Django shell atau Admin Panel untuk mengisi data awal `Experience`, `Education`, `Project`, dan `GalleryPhoto`.

### Running Tests

```bash
python manage.py test
```
Perlu dicatat, test suite yang ada saat ini baru mencakup aksesibilitas URL, penggunaan template, rendering data, dan empty-state untuk keempat halaman, **belum** menguji endpoint AJAX baru (`/api/projects/`, `/api/education/`, `/api/experience/`, maupun endpoint `*-ajax/` untuk submit form). Ini jadi salah satu hal yang ingin saya tambahkan di iterasi berikutnya.

### Deployment

Produksi memakai PostgreSQL. Buat proyek baru di [PWS](https://pws.cs.ui.ac.id), lalu set environment variable berikut di tab **Environs**:
```
PRODUCTION=True

DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=<database-port>
SCHEMA=tutorial
```

Tambahkan URL deployment PWS ke `ALLOWED_HOSTS` di `settings.py`, dan pastikan `WhiteNoiseMiddleware` aktif agar berkas statis (termasuk `common.js` dan `toast.js`) tersaji dengan benar di produksi.

Untuk push perubahan ke PWS:
```bash
git add .
git commit -m "chore: deploy"
git push pws main:master
```

## Referensi

- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Async_JS/Promises
- https://owasp.org/www-community/attacks/xss/
- https://docs.djangoproject.com/en/5.2/ref/templates/language/#automatic-html-escaping

[^1]: AJAX: *Asynchronous JavaScript and XML*, teknik mengirim dan menerima data dari server tanpa me-*reload* halaman secara penuh.
[^2]: XSS: *Cross-Site Scripting*, serangan yang menyisipkan skrip berbahaya ke halaman yang kemudian dijalankan oleh browser pengguna lain.