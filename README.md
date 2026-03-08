<div align="center">

```
 █████╗ ██████╗ ████████╗██████╗ ███╗   ███╗██╗███████╗
██╔══██╗██╔══██╗╚══██╔══╝╚════██╗████╗ ████║██║██╔════╝
███████║██████╔╝   ██║    █████╔╝██╔████╔██║██║███████╗
██╔══██║██╔══██╗   ██║    ╚═══██╗██║╚██╔╝██║██║╚════██║
██║  ██║██║  ██║   ██║   ██████╔╝██║ ╚═╝ ██║██║███████║
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝     ╚═╝╚═╝╚══════╝
```

**A game launcher that actually respects your taste.**

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.x-yellow?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Built with Claude](https://img.shields.io/badge/built%20with-Claude%20AI-blueviolet?style=flat-square)
![No Framework](https://img.shields.io/badge/framework-none-lightgrey?style=flat-square)

</div>

---

## Screenshots

<div align="center">

<img src="screenshots/Screenshot 2026-03-08 215347.png" width="32%" alt="ART3MIS – Game Library"/>
<img src="screenshots/Screenshot 2026-03-08 215408.png" width="32%" alt="ART3MIS – Settings & Themes"/>
<img src="screenshots/Screenshot 2026-03-08 215437.png" width="32%" alt="ART3MIS – Light Mode"/>

</div>

---

> 🇹🇷 **Türkçe için:** [aşağı kaydır ↓](#-türkçe)

---

## What is ART3MIS?

ART3MIS is a personal game launcher and shortcut manager built entirely from scratch — no Electron, no React, no bloat. Just a single HTML file and a lightweight Python server, communicating over localhost. You open it in your browser, it feels like a native app.

It was designed for people who want their launcher to look *exactly* the way they imagine it — with custom backgrounds, animated particle effects, ambient music from Spotify or SoundCloud or YouTube, and a UI that switches between four distinct visual themes, each with a dark and a light variant.

> 🤖 **ART3MIS was built in collaboration with [Claude AI](https://claude.ai) by Anthropic** — from architecture decisions and feature design to debugging and iteration. Every feature in this project went through a real back-and-forth conversation.

---

## Features

### 🎮 Game Library
Add your games with cover art, genre tags, release year, and a custom emoji icon. Search and filter in real time. Click any card to launch — the game opens with a smooth launch animation overlay. Right-click for context menu options.

### ⚡ Shortcuts
Anything you launch frequently — applications, folders, websites, scripts — can live here as a shortcut tile. Each one gets its own accent color, icon, and optional note.

### 🎨 Theme System — 4 Pairs, Day & Night

Every theme comes as a matched pair: one dark, one light. The 🌙/☀️ toggle in the header switches between them instantly. All four themes use CSS custom properties, so the switch is instant and smooth across the entire UI.

| Theme | Dark Mode | Light Mode |
|---|---|---|
| 🔵 **CYBER** | Deep navy, cyan neon accents | Clean sky blue and white |
| 💚 **TERMINAL** | Black canvas, phosphor green | Cream paper, olive green ink |
| 🟣 **AURORA** | Deep cosmic violet | Soft lavender, spring blossom |
| ⚪ **MINIMAL** | Dark slate, muted grey | Warm cream, stone beige |

### ✨ Particle Effects

The background isn't just decoration — it reacts to your cursor. Four modes, all canvas-rendered from scratch:

- 🌟 **STARDUST** — Colorful glowing nodes, spiking toward the mouse
- 🌌 **MILKY WAY** — Full 3D galaxy projection with yaw/pitch mouse control
- 🔵 **CLASSIC** — Connected node network with proximity highlighting
- 🟡 **FIREFLIES** — Drifting orbs with hue-shifting color cycles

Mouse tracking can be toggled off if you prefer a calmer background.

### 🎵 Music Player — 3 Sources

An ambient music player lives in the bottom-left corner, collapsed by default (🎵). Click it to expand.

| Source | What it supports |
|---|---|
| 🎧 **Spotify** | Playlists, albums, tracks, artists. `intl-XX` locale URLs supported |
| ☁️ **SoundCloud** | Profiles, sets, single tracks |
| ▶️ **YouTube** | Individual videos or playlists |

Build a playlist of multiple entries across different sources. The player cycles through them and remembers where you left off.

### 🖼 Custom Background
Drop any image — from a local file or a URL. A dimming slider lets you control how much it bleeds through. Backgrounds are stored in IndexedDB (no size limits, unlike localStorage).

### ⚙️ Settings — 5 Categories
1. **🎨 Appearance** — Theme pair, day/night, particle style, count, mouse tracking
2. **🖼 Background** — Image picker, URL input, dimming control
3. **🎵 Music** — Playlist management, loop toggle
4. **🔌 Server** — Connection status, ping
5. **💾 Data** — Export full config as JSON, import, reset to defaults

---

## Architecture

```
art3mis-launcher/
├── launcher.html   ← Everything: UI, logic, styles. ~2100 lines.
└── server.py       ← Python HTTP server. ~300 lines.
```

The two files talk over HTTP on `localhost:7842`. The HTML file is served by the Python server — so you always open `http://localhost:7842`, never `file://`.

### Why no framework?

Because a launcher doesn't need one. ART3MIS is vanilla JS, plain CSS custom properties for theming, and a minimal Python standard-library server. The total dependency list is: **Python 3** and **a browser**. No `npm install`, no virtual environments, no build step.

### Data Storage

```
localStorage['art3mis_db']   → { games: [...], shortcuts: [...] }
localStorage['art3mis_cfg']  → { theme, particles, playlist, ... }
IndexedDB['art3mis_idb']     → background image (no size limit)
```

### How Themes Work

```css
/* Each theme is a CSS class with custom properties */
.theme-aurora       { --bg: #07060f; --A: #a855f7; --txt: #e8d0ff; ... }
.theme-aurora.light { --bg: #f2eeff; --A: #8833cc; --txt: #1a0830; ... }
```

`setUITheme('aurora')` adds `theme-aurora` to `<body>`. The 🌙/☀️ toggle adds or removes `.light`. That's the entire theme engine.

### Server Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | GET | Serves `launcher.html` |
| `GET /ping` | GET | Health check |
| `GET /open?path=` | GET | Launches a file or program via OS |
| `GET /pick-file` | GET | Opens native tkinter file picker |
| `GET /pick-folder` | GET | Opens native tkinter folder picker |
| `GET /list-folder?path=` | GET | Returns directory listing with metadata |
| `GET /drives` | GET | Lists system drives (Windows: C:\\, D:\\...) |
| `GET /file?path=` | GET | Streams a local audio file (Range-request capable) |
| `POST /browse` | POST | Opens file or folder picker by `mode` param |

---

## Setup

**Requirements:** Python 3.x · Any modern browser (Firefox, Chrome, Edge)

```bash
# Clone or download the two files into a folder
git clone https://github.com/your-username/art3mis-launcher

# Run
python server.py
# or double-click start.bat on Windows
```

Then open: **`http://localhost:7842`**

That's it.

---

## Usage

**Add a game:** Games tab → `＋ Add Game` → browse for the `.exe` → fill in cover, genre, year → Save

**Add music:** Settings → 🎵 Music → `＋ Add Track` → pick source → paste URL → Save  
*(Spotify tip: `open.spotify.com/intl-tr/artist/ID?si=...` works directly)*

**Change theme:** Settings → 🎨 Appearance → click a theme card  
**Toggle day/night:** 🌙/☀️ button in the top-right header

**Export your data:** Settings → 💾 Data → Export JSON — move your entire setup to another machine

---

## Known Limitations

- **Embed restrictions:** Some YouTube videos and Spotify tracks block iframe embedding — this is a platform policy, not a bug. The player shows an "Open in..." button as fallback.
- **File manager:** Hidden pending a server connection fix — the code is preserved and will return.
- **`file://` protocol:** If you open `launcher.html` directly (not via the server), game launching, file pickers, and the music player won't work. Always use `localhost:7842`.

---

## Built With

- **Python 3** — HTTP server, file system access, OS integration
- **Vanilla JavaScript** — all UI logic, particle engine, theme system
- **CSS Custom Properties** — the entire theming system, zero JS for color changes
- **IndexedDB** — background image persistence
- **Canvas API** — hand-written particle renderer (Stardust, Milky Way, Classic, Fireflies)
- **[Claude AI](https://claude.ai)** — architecture, feature design, implementation, debugging

---

## License

MIT — use it, fork it, make it yours.

---

<div align="center">

*Made with 🎮 + ☕ + Claude AI*

*"The best launcher is the one that gets out of your way."*

</div>

---
---

<br>

<div align="center">

# 🇹🇷 Türkçe

</div>

---

## ART3MIS Nedir?

ART3MIS, sıfırdan yazılmış kişisel bir oyun başlatıcı ve kısayol yöneticisidir — Electron yok, React yok, gereksiz bağımlılık yok. Tek bir HTML dosyası ve hafif bir Python sunucusundan ibaret. `localhost` üzerinden haberleşir, tarayıcıda açarsın, native uygulama hissi verir.

Launcher'ının tam olarak hayal ettiğin gibi görünmesini isteyen insanlar için tasarlandı — özel arkaplanlar, animasyonlu parçacık efektleri, Spotify, SoundCloud veya YouTube'dan ortam müziği; dört farklı görsel tema, her birinin gece ve gündüz versiyonuyla.

> 🤖 **ART3MIS, Anthropic'in [Claude AI](https://claude.ai)'ı ile iş birliği içinde geliştirildi** — mimari kararlardan özellik tasarımına, hata ayıklamadan iterasyona kadar her adım gerçek bir konuşma sürecinden geçti.

---

## Özellikler

### 🎮 Oyun Kütüphanesi
Oyunlarını kapak resmi, tür etiketi, çıkış yılı ve özel emoji ikonu ile ekle. Anlık arama ve filtreleme. Herhangi bir karta tıkla, oyun başlasın — pürüzsüz bir başlatma animasyonu eşliğinde. Sağ tıkla bağlam menüsüne ulaş.

### ⚡ Kısayollar
Sık kullandığın her şey — uygulamalar, klasörler, web siteleri, scriptler — burada kısayol olarak yaşar. Her biri için özel renk, ikon ve not ekleyebilirsin.

### 🎨 Tema Sistemi — 4 Çift, Gece & Gündüz

Her tema eşleştirilmiş bir çift olarak gelir: biri koyu, biri açık. Header'daki 🌙/☀️ butonu anında geçiş yapar. Dört tema da CSS değişkenleriyle çalışır, geçiş tüm arayüzde anlık ve pürüzsüzdür.

| Tema | Gece Modu | Gündüz Modu |
|---|---|---|
| 🔵 **CYBER** | Derin lacivert, cyan neon | Temiz açık mavi ve beyaz |
| 💚 **TERMINAL** | Siyah zemin, fosforlu yeşil | Krem kağıt, zeytin yeşili |
| 🟣 **AURORA** | Derin kozmik mor | Yumuşak lavanta, bahar renkleri |
| ⚪ **MINIMAL** | Koyu slate, soluk gri | Sıcak krem, taş beji |

### ✨ Parçacık Efektleri

Arkaplan sadece dekor değil — imlecine tepki veriyor. Dört mod, hepsi sıfırdan canvas ile çiziliyor:

- 🌟 **STARDUST** — Renkli parlayan düğümler, mouse'a doğru canlanıyor
- 🌌 **MILKY WAY** — Mouse ile kontrol edilen yaw/pitch'li tam 3D galaksi projeksiyonu
- 🔵 **CLASSIC** — Yakınlık bazlı vurgulama ile bağlantılı nodes ağı
- 🟡 **FIREFLIES** — Ton değiştiren renk döngüleriyle süzülen ateşböcekleri

Mouse takibini kapatmak istersen sakin bir arkaplan için toggle mevcuttur.

### 🎵 Müzik Çalar — 3 Kaynak

Sol altta küçültülmüş bir ortam müzik çalar (🎵) bulunur. Tıklayınca genişler.

| Kaynak | Destekledikleri |
|---|---|
| 🎧 **Spotify** | Çalma listesi, albüm, şarkı, sanatçı. `intl-XX` yerel URL'leri destekleniyor |
| ☁️ **SoundCloud** | Profil, set, tekil şarkı |
| ▶️ **YouTube** | Tekil video veya çalma listesi |

Farklı kaynaklardan birden fazla giriş içeren çalma listesi oluştur. Çalar sıralarıyla geçer ve kaldığı yeri hatırlar.

### 🖼 Özel Arkaplan
Herhangi bir resim ekle — yerel dosyadan veya URL'den. Karartma slider'ı ne kadar görüneceğini kontrol etmeni sağlar. Arkaplanlar IndexedDB'de saklanır (localStorage'ın aksine boyut sınırı yok).

### ⚙️ Ayarlar — 5 Kategori
1. **🎨 Görünüm** — Tema çifti, gece/gündüz, parçacık stili, sayısı, mouse takibi
2. **🖼 Arkaplan** — Resim seçici, URL girişi, karartma kontrolü
3. **🎵 Müzik** — Çalma listesi yönetimi, döngü modu
4. **🔌 Sunucu** — Bağlantı durumu, ping
5. **💾 Veri** — Tüm konfigürasyonu JSON olarak dışa aktar, içe aktar, varsayılanlara sıfırla

---

## Mimari

```
art3mis-launcher/
├── launcher.html   ← Her şey: UI, mantık, stiller. ~2100 satır.
└── server.py       ← Python HTTP sunucusu. ~300 satır.
```

İki dosya `localhost:7842` üzerinden HTTP ile konuşur. HTML dosyası Python sunucusu tarafından servis edilir — her zaman `http://localhost:7842` açarsın, asla `file://` değil.

### Neden framework yok?

Çünkü bir launcher'a gerek yok. ART3MIS saf JS, tema için düz CSS değişkenleri ve minimal Python standart kütüphane sunucusundan oluşur. Bağımlılık listesinin tamamı: **Python 3** ve **bir tarayıcı**. `npm install` yok, sanal ortam yok, derleme adımı yok.

### Sunucu Endpoint'leri

| Endpoint | Metot | Açıklama |
|---|---|---|
| `GET /` | GET | `launcher.html` servis eder |
| `GET /ping` | GET | Sağlık kontrolü |
| `GET /open?path=` | GET | OS aracılığıyla dosya veya program başlatır |
| `GET /pick-file` | GET | Tkinter dosya seçici açar |
| `GET /pick-folder` | GET | Tkinter klasör seçici açar |
| `GET /list-folder?path=` | GET | Metadata ile klasör listesi döner |
| `GET /drives` | GET | Sistem sürücülerini listeler (Windows: C:\\, D:\\...) |
| `GET /file?path=` | GET | Yerel ses dosyası akışı (Range-request destekli) |
| `POST /browse` | POST | `mode` parametresine göre dosya veya klasör seçici |

---

## Kurulum

**Gereksinimler:** Python 3.x · Modern bir tarayıcı (Firefox, Chrome, Edge)

```bash
git clone https://github.com/kullanici-adiniz/art3mis-launcher
python server.py
# ya da Windows'ta start.bat'a çift tıkla
```

Ardından: **`http://localhost:7842`**

Bu kadar.

---

## Kullanım

**Oyun ekle:** Oyunlar sekmesi → `＋ Oyun Ekle` → `.exe` için gözat → kapak, tür, yıl doldur → Kaydet

**Müzik ekle:** Ayarlar → 🎵 Müzik → `＋ Parça Ekle` → kaynak seç → URL yapıştır → Kaydet  
*(Spotify ipucu: `open.spotify.com/intl-tr/artist/ID?si=...` formatı doğrudan çalışır)*

**Tema değiştir:** Ayarlar → 🎨 Görünüm → tema kartına tıkla  
**Gece/gündüz geçişi:** Sağ üst köşedeki 🌙/☀️ butonu

**Veri yedekle:** Ayarlar → 💾 Veri → JSON Dışa Aktar — kurulumunun tamamını başka bir bilgisayara taşı

---

## Bilinen Sınırlamalar

- **Embed kısıtlamaları:** Bazı YouTube videoları ve Spotify parçaları iframe ile gömülmeyi engelliyor — bu platform politikası, hata değil. Çalar yedek olarak "aç" butonu gösteriyor.
- **Dosya yöneticisi:** Sunucu bağlantı sorunu nedeniyle gizlendi — kod korunuyor, geri dönecek.
- **`file://` protokolü:** `launcher.html`'i doğrudan açarsan (sunucu üzerinden değil) oyun başlatma, dosya seçiciler ve müzik çalar çalışmaz. Her zaman `localhost:7842` kullan.

---

## Kullanılan Teknolojiler

- **Python 3** — HTTP sunucusu, dosya sistemi erişimi, OS entegrasyonu
- **Vanilla JavaScript** — tüm UI mantığı, parçacık motoru, tema sistemi
- **CSS Custom Properties** — tema sisteminin tamamı, renk değişikliği için sıfır JS
- **IndexedDB** — arkaplan resmi kalıcılığı
- **Canvas API** — elle yazılmış parçacık renderer'ı (Stardust, Milky Way, Classic, Fireflies)
- **[Claude AI](https://claude.ai)** — mimari, özellik tasarımı, uygulama, hata ayıklama

---

## Lisans

MIT — kullan, fork'la, kendin yap.

---

<div align="center">

*🎮 + ☕ + Claude AI ile yapıldı*

*"En iyi launcher, yolundan çekileni bilendir."*

</div>
