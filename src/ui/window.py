from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QLineEdit, QPushButton, QTabWidget, 
    QVBoxLayout, QWidget, QStatusBar, QMessageBox, QTextEdit, 
    QDialog, QProgressBar, QHBoxLayout, QLabel, QListWidget, QFormLayout, QComboBox
)
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont
from src.engine.web_view import BrowserEngineView
from src.storage.manager import StorageManager
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaBrowse")
        self.resize(1280, 800)

        # Initialize Modules
        self.storage = StorageManager()
        
        # Apply Global Styles
        self.apply_styles()

        # UI Elements
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        # Toolbar
        self.navbar = QToolBar("Navigation")
        self.navbar.setMovable(False)
        self.navbar.setIconSize(QSize(22, 22))
        self.addToolBar(self.navbar)

        # Navigation buttons
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navbar.addAction(back_btn)

        next_btn = QAction("→", self)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navbar.addAction(next_btn)

        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        self.navbar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        self.navbar.addSeparator()

        # Features
        bookmark_btn = QAction("⭐", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        self.navbar.addAction(bookmark_btn)

        history_btn = QAction("📜", self)
        history_btn.triggered.connect(self.show_history)
        self.navbar.addAction(history_btn)

        settings_btn = QAction("⚙️", self)
        settings_btn.triggered.connect(self.show_settings)
        self.navbar.addAction(settings_btn)

        new_tab_btn = QAction("➕", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(2)
        self.progress.setTextVisible(False)
        
        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.addPermanentWidget(self.progress)
        self.progress.hide()

        # Add initial tab
        self.add_new_tab(QUrl("about:blank"), "New Tab")

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f1f3f4;
            }
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dee1e5;
                padding: 4px;
                spacing: 8px;
            }
            QLineEdit {
                background-color: #f1f3f4;
                color: #202124;
                border: none;
                border-radius: 18px;
                padding: 6px 15px;
                font-size: 14px;
                selection-background-color: #c2e7ff;
            }
            QLineEdit:hover {
                background-color: #e8eaed;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #1a73e8;
            }
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #5f6368;
                padding: 8px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 140px;
                margin-top: 5px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1a73e8;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8eaed;
            }
            QProgressBar {
                background-color: #e8eaed;
                border: none;
                height: 2px;
            }
            QProgressBar::chunk {
                background-color: #1a73e8;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #5f6368;
                border-top: 1px solid #dee1e5;
            }
            QPushButton {
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
        """)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None or isinstance(qurl, bool):
            qurl = QUrl("about:blank")

        browser = BrowserEngineView()
        self._setup_browser_connections(browser)
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        if qurl.toString() == "about:blank":
            self._load_home_page(browser)
        else:
            browser.setUrl(qurl)

    def add_new_tab_from_view(self, browser):
        self._setup_browser_connections(browser)
        i = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(i)

    def _setup_browser_connections(self, browser):
        browser.url_changed.connect(lambda url: self.update_url(url, browser))
        browser.title_changed.connect(lambda title: self.tabs.setTabText(self.tabs.indexOf(browser), (title[:20] or "New Tab")))
        
        browser.loadProgress.connect(lambda p: self.update_progress(p, browser))
        browser.loadStarted.connect(lambda: self.progress.show() if self.tabs.currentWidget() == browser else None)
        browser.loadFinished.connect(lambda: self.progress.hide() if self.tabs.currentWidget() == browser else None)

        browser.loadFinished.connect(lambda: self.storage.add_history_item(browser.url().toString(), browser.title()) if browser.url().toString() != "about:blank" and not browser.url().toString().startswith("data:") else None)

    def _load_home_page(self, browser):
        home_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "homepage.html")
        if os.path.exists(home_path):
            with open(home_path, 'r') as f:
                html = f.read()
                browser.setHtml(html)
        else:
            # Fallback if file missing
            browser.setHtml("<h1>NovaBrowse</h1><p>Home page missing.</p>")

    def update_progress(self, p, browser):
        if browser == self.tabs.currentWidget():
            self.progress.setValue(p)
            if p == 100:
                self.progress.hide()
            else:
                self.progress.show()

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        if i == -1: return
        browser = self.tabs.widget(i)
        qurl = browser.url()
        self.update_url(qurl.toString(), browser)
        self.setWindowTitle(f"{browser.title()} - NovaBrowse")

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            self._load_home_page(self.tabs.currentWidget())
            return
        self.tabs.removeTab(i)

    def update_url(self, url, browser=None):
        if browser != self.tabs.currentWidget():
            return
        if url.startswith("data:") or url == "about:blank":
            self.url_bar.setText("")
        else:
            self.url_bar.setText(url)
        self.url_bar.setCursorPosition(0)

    def navigate_home(self):
        self._load_home_page(self.tabs.currentWidget())

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text: return

        if "." not in text or " " in text:
            url = f"https://www.google.com/search?q={text}"
        else:
            if not text.startswith(("http://", "https://", "about:", "file://")):
                url = "https://" + text
            else:
                url = text
        
        self.tabs.currentWidget().setUrl(QUrl(url))

    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        url = browser.url().toString()
        title = browser.title()
        self.storage.add_bookmark(url, title)
        self.status.showMessage(f"Bookmarked: {title}", 3000)

    def show_history(self):
        history = self.storage.get_history()
        dialog = QDialog(self)
        dialog.setWindowTitle("Browsing History")
        dialog.setStyleSheet("background-color: #1e293b; color: white;")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setStyleSheet("background-color: #0f172a; border-radius: 10px; padding: 10px;")
        
        for url, title, ts in history:
            list_widget.addItem(f"{title}\n{url} - {ts}")
            
        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.resize(700, 500)
        dialog.exec()

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setStyleSheet("background-color: #1e293b; color: white; padding: 20px;")
        layout = QFormLayout()

        # Search Engine
        engine_combo = QComboBox()
        engine_combo.addItems(["Google", "DuckDuckGo", "Bing"])
        current_engine = self.storage.get_setting("search_engine", "Google")
        engine_combo.setCurrentText(current_engine)
        layout.addRow("Search Engine:", engine_combo)

        # Home Page
        home_input = QLineEdit()
        home_input.setText(self.storage.get_setting("homepage", "Internal"))
        layout.addRow("Homepage URL:", home_input)

        # Save Button
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("background-color: #38bdf8; color: #0f172a; font-weight: bold; padding: 10px; border-radius: 8px;")
        save_btn.clicked.connect(lambda: self._save_settings(dialog, engine_combo.currentText(), home_input.text()))
        layout.addRow(save_btn)

        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec()

    def _save_settings(self, dialog, engine, home):
        self.storage.set_setting("search_engine", engine)
        self.storage.set_setting("homepage", home)
        self.status.showMessage("Settings saved successfully", 3000)
        dialog.accept()
