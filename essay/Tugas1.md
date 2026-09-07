# Tugas 1

## [Pertanyaan Reflektif](https://pbp.cs.ui.ac.id/assignments/individual/tugas-1.html#pertanyaan-reflektif)

> 1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat _static web_? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?

Ya, saya menggunakan elemen semantik HTML5 secara konsisten di seluruh halaman, `<header>` dan `<nav>` untuk navigasi utama, `<main>` sebagai pembungkus konten inti, beberapa `<section>` untuk membagi halaman menjadi blok-blok independen (`hero`/profile, `experience`, `education`, `projects`, `gallery`), `<article>` untuk unit konten yang berulang dan berdiri sendiri seperti kartu riwayat pendidikan (`education-card`) dan kartu proyek (`project-card`), serta `<footer>` di bagian penutup.

Struktur ini membantu dalam dua hal konkret. Pertama, setiap `<section>` punya `id` yang secara langsung dipetakan ke tautan navigasi (`#experience`, `#education`, `#projects`, `#gallery`), jadi struktur navigasi halaman sudah mendokumentasikan dirinya sendiri tanpa saya perlu menjaga daftar terpisah antara menu dan konten. Kedua, penggunaan `<article>` untuk kartu-kartu yang berulang menegaskan bahwa setiap kartu adalah unit konten yang bisa berdiri sendiri secara makna. Setiap `<article>` pada dasarnya sudah punya bentuk yang pas untuk dipetakan menjadi satu instance model Django nanti, dirender lewat perulangan `{% for %}` di template.

Saya belum menggunakan `<aside>` karena tidak ada konten yang sifatnya benar-benar tangensial atau suplementer terhadap section induknya. Semua yang saya tampilkan seperti deskripsi, tanggal, dan tag teknologi adalah bagian inti dari kartu tersebut, bukan informasi pendamping seperti sidebar atau catatan tambahan. Memaksakan `<aside>` di sini justru akan mengaburkan makna semantiknya.

> 2. Ketika Anda mengatur CSS Anda agar tetap _responsive_, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?

Tantangan terbesar justru bukan pada satu section spesifik, melainkan pada proses berpindah dari versi desktop yang sudah jadi ke versi mobile yang masih harus dipikirkan ulang. Saya sering kali tidak punya bayangan yang jelas soal bagaimana seharusnya tampilan mobile-nya sebelum benar-benar menuliskan breakpoint-nya, sehingga penyesuaian layout terasa lebih seperti tambal-sulam reaktif daripada hasil dari desain yang memang direncanakan sejak awal. Section Gallery adalah contoh paling jelas dalam masalah ini, grid asimetris dengan area kustom (`g-a` sampai `g-f`) yang terlihat rapi di desktop butuh susunan ulang total di layar kecil, dan sejujurnya sampai sekarang saya masih merasa hasilnya belum serapi versi desktopnya. Ini jadi salah satu hal yang ingin saya perbaiki lagi ke depannya.

Dari pengalaman ini saya sadar bahwa evaluasi saya terhadap elemen mana yang harus diprioritaskan bukan berdasarkan hierarki ketat elemen A lebih penting dari elemen B, melainkan berdasarkan kenyamanan visual secara keseluruhan. Yang paling saya jaga adalah agar palet warna tidak menyakitkan mata, nuansa halaman tetap konsisten dari satu section ke section lain, dan keselarasan antar-elemen tetap terjaga meskipun posisinya berubah drastis saat breakpoint aktif. Dengan kata lain, prioritas saya lebih ke arah *unity* ketimbang *hierarchy*.

> 3. Website yang Anda buat saat ini adalah _static web_ murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?

Batasan yang paling terasa adalah seluruh konten di section Experience, Education, Projects, dan Gallery masih di-hardcode langsung di dalam HTML. Ini berarti setiap kali saya ingin menambah satu pengalaman organisasi baru, satu proyek baru, atau satu foto baru ke galeri, saya harus membuka dan mengedit template secara manual dan tidak ada pemisahan antara data dan presentasi, padahal proyek ini sudah berjalan di atas Django[^1] yang di-deploy ke PWS[^2] sejak tutorial sebelumnya.

Berdasarkan batasan itu, pada iterasi selanjutnya saya ingin memindahkan section **Projects** dan **Gallery** menjadi arsitektur MVT yang sesungguhnya yakni disimpan sebagai model di database dan dikelola lewat admin panel Django, bukan lagi ditulis manual di template. Saya memilih dua section ini secara spesifik karena keduanya adalah bagian yang paling mungkin terus bertambah isinya seiring waktu, proyek baru akan terus muncul, dan foto galeri idealnya bisa ditambah kapan saja tanpa saya harus menyentuh kode HTML/CSS lagi setiap kali.

### AI Disclosure

Saya memanfaatkan AI sebatas untuk bertanya seputar fungsi tag dan atribut HTML5/CSS3 yang belum saya pahami, sebagai bagian dari rasa ingin tahu saya dalam belajar. Seluruh struktur dan penulisan kode tetap saya kerjakan sendiri.

Tool yang saya gunakan adalah Claude Anthropic. Strategi prompting yang saya terapkan bersifat konseptual, saya bertanya "apa kegunaan elemen ini" atau "atribut apa saja yang tersedia untuk tag ini dan bagaimana pengaruhnya", bukan meminta AI menuliskan kode untuk saya. Pendekatan ini saya pilih agar pemahaman saya terhadap struktur HTML tetap terbentuk melalui proses saya sendiri, dengan AI berperan sebagai referensi cepat, semacam dokumentasi yang bisa saya ajak berdiskusi.

Ketika menyusun hamburger menu untuk navigasi mobile, saya mengandalkan eksperimen langsung dengan JavaScript untuk toggle tampilan, mencoba, gagal, dan mencoba ulang, hingga perilakunya sesuai yang saya inginkan. Begitu pula dengan audio player, penentuan skema warna ink blue dan aksen oranye-merah, serta penataan grid asimetris pada bagian Gallery, semuanya lahir dari proses coba-coba saya sendiri, bukan dari saran AI. Dari pengalaman ini saya juga menyadari keterbatasan AI cukup jelas, terutama ketika berhadapan dengan sesuatu yang sifatnya visual dan bukan tekstual. Penataan grid foto pada bagian Gallery adalah contoh paling nyata, AI bisa menjelaskan atribut grid-template-columns atau grid-gap secara definitif, tapi tidak bisa melihat apakah susunan foto tersebut sudah enak dipandang atau belum, apalagi pada tampilan mobile. Kerapian itu sepenuhnya soal rasa dan penilaian visual saya sendiri, dan sampai sekarang bagian tersebut masih saya anggap belum sepenuhnya rapi, sesuatu yang tidak bisa diselesaikan lewat penjelasan AI sebaik apa pun itu.

[^1]: Django: web framework Python yang digunakan untuk menyajikan halaman ini lewat template rendering.
[^2]: PWS: Pacil Web Service, layanan hosting internal milik Fakultas Ilmu Komputer Universitas Indonesia.

## Referensi

- https://developer.mozilla.org/en-US/docs/Web/HTML/Element
- https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout