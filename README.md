# NovaBrowse: A Modern Python Web Browser

NovaBrowse is a lightweight, modular web browser built with Python and PyQt6. It leverages the QtWebEngine (Chromium-based) for high-performance rendering and includes essential browsing features.

## 1. Browser Architecture

The browser is designed with a modular architecture:

### Core Components
- **UI (User Interface)**: Built using PyQt6 Widgets. Manages the multi-tab interface, dynamic navigation bar, and custom home page.
- **Rendering Engine**: Utilizes `QtWebEngine` (Chromium/Blink).
- **Networking**: Handles SSL/TLS, HTTP/2, and caching via Chromium's network stack.
- **Storage Layer**: SQLite for persistent history and bookmarks.

### Features
- **Multi-Tab Browsing**: Open multiple sites simultaneously.
- **Smart URL Bar**: Automatically distinguishes between URLs and search queries.
- **Custom Home Page**: High-performance start page with search and quick shortcuts.
- **History & Bookmarks**: Save and view your favorite pages.
- **Progress Tracking**: Real-time loading progress visualization.

## 2. Setup Instructions

### Missing Dependencies (Linux)
If you encounter a `Qt platform plugin "xcb"` error, install the missing cursor library:
```bash
sudo apt-get install libxcb-cursor0
```

### Install Python Requirements
```bash
pip install -r requirements.txt
```

### Run the Browser
```bash
python main.py
```

## 3. Future Roadmap
- Extensions API
- Ad-blocking and Tracker prevention
- Private/Incognito mode
- Download Manager
