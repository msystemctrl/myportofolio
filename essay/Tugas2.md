# Tugas 2

## [Pertanyaan Reflektif](https://pbp.cs.ui.ac.id/assignments/individual/tugas-2.html#pertanyaan-reflektif)

> 1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada _browser_. Dalam jawabanmu, jelaskan peran `urls.py` proyek, `urls.py` aplikasi, _view_, model, dan _template_.

Contoh paling gampang saya jelaskan pakai halaman `/gallery/` saya sendiri, karena alurnya kebetulan paling berlapis dibanding halaman lain. Permintaan itu pertama kali mampir ke `urls.py` milik proyek, tapi isinya sebenarnya sangat pendek, hanya `path("admin/", admin.site.urls)` dan `path("", include("main.urls"))`. Jadi `urls.py` level proyek ini fungsinya lebih ke pos satpam yang cuma nentuin arah umum, dia tidak tahu dan memang tidak perlu tahu apa itu `/gallery/`, dia cuma tahu kalau bukan `/admin/`, lempar saja semuanya ke `main.urls`.

Baru di `main/urls.py`, permintaan itu benar-benar dicocokkan lewat `path("gallery/", show_gallery, name="show_gallery")`. Di sini `urls.py` aplikasi berperan sebagai peta jalan yang lebih rinci per fitur, dan praktik `app_name = "main"` digunakan supaya tidak terjadi bentrok kalau suatu saat ada aplikasi lain di proyek yang sama dengan nama route yang sama seperti `show_gallery`.

Bagian yang menurut saya paling penting justru ada di _view_. Fungsi `show_gallery` mengambil data lewat `GalleryPhoto.objects.all().order_by('order')[:6]`, dipotong maksimal 6 karena tata letak galeri saya memang dirancang khusus untuk 6 slot posisi, bukan grid biasa yang bisa menampung berapa pun foto. Nah, di sinilah saya sadar kenapa logika harus tinggal di _view_ dan bukan di _template_. Saya perlu memasangkan tiap foto dengan label posisinya lewat `zip(photos, GALLERY_POSITIONS)`, dan Django Template Language sendiri sama sekali tidak punya cara untuk melakukan pemetaan semacam itu. Kalau dipaksakan ke _template_, hasilnya justru template yang penuh logika, padahal harusnya dia cuma penyaji, bukan pemikir.

Setelah itu baru data yang sudah rapi ini dibungkus jadi `context` dan dikirim lewat `render(request, "gallery.html", context)`. `gallery.html` sendiri isinya cuma perulangan `{% for photo, position in gallery_items %}` yang menampilkan tiap foto di posisi CSS yang cocok, tanpa peduli sama sekali kenapa cuma ada 6 foto atau bagaimana data itu didapat. HTML yang dihasilkan dari sini yang akhirnya sampai lagi ke browser sebagai response.

Dari sini saya jadi paham kenapa pembagian tugas MVT itu bukan sekadar aturan formal, tapi memang masuk akal, `urls.py` sebagai pengatur arah, _view_ tempat semua keputusan logika, model satu-satunya sumber data yang bisa dipercaya, dan _template_ sengaja dibuat bodoh supaya tidak ikut-ikutan mikir hal yang bukan urusannya.

> 2. Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam _template_? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.

Saya kebetulan merasakan langsung bedanya karena Tugas 1 dan Tugas 2 ini dikerjakan di proyek yang sama persis. Dulu di Tugas 1 saya sempat tulis sebagai keterbatasan bahwa semua konten Experience, Education, Projects, sampai Gallery masih ditulis manual di HTML, jadi setiap mau nambah satu pengalaman organisasi baru, saya harus buka `index.html`, copy-paste blok markup yang mirip, terus edit teksnya satu-satu, dengan risiko merusak markup di sekitarnya kalau kurang teliti. Sekarang setelah dipindah ke model, menambah satu `Experience` baru cuma tinggal buka Admin Panel, isi form, selesai, tidak ada kode yang perlu disentuh sama sekali.

Yang menurut saya lebih penting dari sekadar jadi lebih cepat adalah soal seberapa sering masing-masing bagian ini berubah. Struktur `template` seperti `experience.html` itu sebenarnya jarang sekali diubah lagi begitu sudah final, tapi datanya bisa terus bertambah kapan saja. Kalau dua hal ini masih dicampur di satu file HTML seperti dulu, setiap kali mau update data kecil saja, itu berisiko merusak struktur yang sebenarnya sudah tidak perlu diutak-atik.

Saya juga tidak sengaja ketemu bukti nyatanya lewat sebuah bug. Waktu itu saya sempat tulis `default='full-time'` di field `category` milik `Experience` sebagai model default dari Tutorial 2, padahal nilai itu tidak ada di daftar `EXPERIENCE_CHOICES` saya yang terbaru. Karena field ini sudah jadi bagian dari model dengan validasi `choices` di Admin, kesalahan itu langsung ketahuan saat saya coba simpan data. Kalau kategori ini masih berupa teks bebas yang saya ketik manual di HTML dulu, kesalahan semacam ini kemungkinan besar tidak akan pernah ketahuan, cuma akan tampil sebagai teks salah tanpa peringatan apa-apa. Ini bukti kecil bahwa memindahkan data ke model bukan cuma soal rapi-rapi kode, tapi beneran memberi lapisan keamanan tambahan yang tidak bisa didapat kalau datanya masih statis di template.

> 3. Apa perbedaan fungsi `makemigrations` dan `migrate` pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.

Dua perintah ini menangani dua tahap yang benar-benar beda, dan saya melewati siklus ini berkali-kali karena menambah empat model baru secara bertahap yaitu `Experience`, lalu `Education`, `Project`, dan `GalleryPhoto`. `makemigrations` itu tugasnya membandingkan `models.py` sekarang dengan riwayat migrasi terakhir, terus nulis rencana perubahan itu jadi file Python di folder `migrations/`, tapi di tahap ini database belum disentuh sama sekali, masih sebatas rencana di atas kertas. `migrate` baru benar-benar mengeksekusi rencana itu jadi SQL sungguhan yang mengubah struktur tabel. Contoh paling jelasnya waktu saya nambah model `Project` dengan field `tags` dan `order`, kedua perintah ini wajib dijalankan berurutan, karena tanpa `migrate`, tabel `main_project` secara fisik belum pernah ada di database sama sekali, walaupun kodenya sudah benar di `models.py`.

Yang justru bikin saya lebih paham batasannya malah kasus sebaliknya. Waktu saya perbaiki `default='full-time'` jadi `default='organization'` di field `category`, awalnya saya kira perlu migrasi ulang. Ternyata tidak perlu, karena `default` itu cuma nilai bawaan yang diterapkan Django di level Python saat objek baru dibuat, bukan aturan yang tersimpan di struktur tabel SQL. Begitu juga kalau saya ubah isi list `EXPERIENCE_CHOICES`, itu juga tidak butuh migrasi, karena `choices` cuma validasi di level Django dan tampilan Admin, bukan bagian dari bentuk kolomnya. Jadi kesimpulan saya, migrasi cuma benar-benar diperlukan kalau perubahannya mengubah bentuk tabel secara fisik, seperti nambah kolom baru atau nambah tabel baru sepenuhnya, bukan setiap kali file `models.py` diedit sedikit saja.

### AI Disclosure

Di tugas ini saya pakai AI (Claude, Anthropic) jauh lebih intens dan bukan cuma nanya-nanya konsep lagi. Saya minta penjelasan tentang bagaimana cara penyusunan Model, _view_, `urls.py`, sampai _template_ baru buat tiap halaman, karena di tahap ini saya memang baru belajar pola MVT dari nol dan butuh lihat dulu contoh implementasi yang benar sebelum bisa nulis sendiri.

Saya berhenti di banyak titik buat nanya alasan di balik sebuah keputusan misalnya kenapa `urls.py` harus ada di dua level sebelum lanjut ke langkah berikutnya. Waktu ada error, saya juga coba pahami dulu akar masalahnya seperti `AttributeError: 'str' object has no attribute 'year'` waktu testing model `Education`.

Keterbatasannya juga mirip yang saya rasakan di Tugas 1, AI cukup bisa diandalkan buat jelasin konsep dan bantu penyusunan kode yang lebih detail daripada draft pola saya di awal, tapi keputusan desain dan layout yang sifatnya spesifik ke proyek saya, tetap butuh turun tangan saya sendiri. Jujur saya juga clueless sama design yang ingin saya pakai, menurut saya design itu perlu direnungkan jauh sebelum implementasinya. Mungkin untuk next PBP, tugas awalnya bisa disuruh bikin design dulu kali ya.

## Installation and Deployment

### Requirements

- Python 3.10+
- pip
- Git
- Django `~=5.2` (see `requirements.txt`; PWS's PostgreSQL setup does not yet support Django 6.x)

### Local Preview

Clone this repository
```bash
git clone https://github.com/<username>/myportofolio.git
cd myportofolio
```

Create a virtual environment
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

Create a `.env` file in the project root for local configuration:
```
PRODUCTION=False
```

Run migrations to create the tables for `Experience`, `Education`, `Project`, and `GalleryPhoto`, then start the server
```bash
python manage.py migrate  # local development uses SQLite by default
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

### Populating Data

The four new sections (`/experience/`, `/education/`, `/projects/`, `/gallery/`) read directly from the database, so a fresh clone will show the empty-state message until data is added. Two ways to add it:

**Option A — Django shell**
```bash
python manage.py shell
```
```python
from main.models import Experience
Experience.objects.create(
    title="XXX",
    description="XXX",
    category="XXX",
)
exit()
```

**Option B — Django Admin (more convenient for repeated entries)**
```bash
python manage.py createsuperuser
```
Open `http://127.0.0.1:8000/admin/`, log in, and add entries for each model from there. `Experience`, `Education`, `Project`, and `GalleryPhoto` are all registered in `main/admin.py`.

### Running Tests

```bash
python manage.py test
```
This runs the unit tests covering URL accessibility, template usage, data rendering, and empty-state handling for all four new pages.

### Deployment

Production uses PostgreSQL. Create a new project on [PWS](https://pws.cs.ui.ac.id), then set the following environment variables under the **Environs** tab:
```
PRODUCTION=True

DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=<database-port>
SCHEMA=tutorial
```

Add the PWS deployment URL to `ALLOWED_HOSTS` in `settings.py`, and make sure `WhiteNoiseMiddleware` is enabled so static files are served correctly in production.

To push changes to PWS:
```bash
git add .
git commit -m "chore: deploy"
git push pws main:master
```

Once deployed, run migrations and create a superuser directly on the PWS terminal so the production database has its own admin account and tables:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Referensi

- https://docs.djangoproject.com/en/5.2/topics/migrations/
- https://docs.djangoproject.com/en/5.2/ref/models/querysets/
- https://docs.djangoproject.com/en/5.2/ref/contrib/admin/