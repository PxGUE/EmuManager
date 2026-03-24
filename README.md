# EmuManager v0.2.1 - alpha

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Frontend: QML](https://img.shields.io/badge/Frontend-QML%20(Qt%20Quick)-41CD52.svg)
![Backend: PySide6](https://img.shields.io/badge/Backend-PySide6%20(Python)-3776AB.svg)
![Engine: Rust](https://img.shields.io/badge/Engine-Rust%20(MANGO)-DEA584.svg)
![Database: SQLite3](https://img.shields.io/badge/Database-SQLite3-003B57.svg)

**EmuManager** is a modern, high-performance, and privacy-focused game management system designed for retro and modern emulation. Built from the ground up as a **Local-First** application, it gives you total control over your digital library without compromising your data.

## 🚀 Key Features

- **M.A.N.G.O (Multithreaded Asynchronous Native Game Orchestrator)**: High-speed native Rust core for ultra-fast scanning and MD5/CRC32 hashing for precise game identification.
- **Premium 3D UI**: Fluid interface built with QML (Qt Quick), featuring a dynamic 3D console carousel with glassmorphism and smooth transitions.
- **Ultra-Fast Scraping**: Native integration with ScreenScraper API for metadata and high-quality 2D/3D cover art box-sets.
- **Libretro Ready**: Automatic orchestration and management of Libretro cores for the most popular retro consoles.
- **Privacy & Security**: Native SQLite3 database for local data management. Your credentials (ScreenScraper, RetroAchievements) are stored only on your machine.
- **Responsive Layout**: Sidebar-driven navigation with dedicated views for Dashboard, Library, Downloads, and Settings.

---

## 🛠️ Technological Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **User Interface** | Qt Quick (QML) | Modern, hardware-accelerated fluid UI & animations. |
| **Logic & Controller** | Python 3.12+ (PySide6) | High-level orchestration, threading, and QML bridges. |
| **Native Engine** | Rust (Ed. 2024 / PyO3) | Performance-critical file I/O, hashing, and low-latency API calls. |
| **Data Storage** | SQLite3 | Reliable, ACID-compliant local database. |
| **Orchestration** | Pathlib / Native Paths | Seamless cross-platform (Windows/Linux) compatibility. |

---

## 📁 Project Architecture

Following a strict **MVC Pattern**, EmuManager decouples logic from visuals:

- **`emumanager/ui/`**: QML views and reusable components.
- **`emumanager/backend/`**: Database manager, Libretro logic, and the M.A.N.G.O (Rust) binary engine.
- **`emumanager/controllers/`**: PySide6 slots and signals bridging UI and logic.
- **`core_scanner/`**: Rust source for the M.A.N.G.O native acceleration core.

---

## 🛠️ Development & Build

### Prerequisites
- Python 3.12 or newer.
- Rust Toolchain (Edition 2024 recommended).
- `pip install -r requirements.txt`

### Build Native Engine (MANGO)
The core scanner must be compiled for your specific Python version:
```bash
cd core_scanner
maturin build --release
```
Then, deploy the resulting `.pyd` (Windows) or `.so` (Linux) to `emumanager/backend/`.

### Launch App
```bash
python emumanager/app.py
```

---

## 📜 Philosophy: "Local-First"

EmuManager respects your library. It reads and indexes your ROMs using absolute paths from their original locations and **never** modifies, moves, or renames your files. All metadata and media are stored locally in the application's data directory.

## 🤝 Contributing

EmuManager is an open-source project. Contributions are welcome, whether it's through code, UI design, or bug reports!

---
*Created by the EmuManager Team.*
