from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage

class BrowserEngineView(QWebEngineView):
    """
    Subclass of QWebEngineView for enhanced functionality.
    """
    # Signal to update URL bar when page changes
    url_changed = pyqtSignal(str)
    title_changed = pyqtSignal(str)
    new_window_requested = pyqtSignal(QUrl)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.urlChanged.connect(lambda qurl: self.url_changed.emit(qurl.toString()))
        self.titleChanged.connect(lambda title: self.title_changed.emit(title))

    def createWindow(self, _type):
        """
        Overrides the create window request (e.g. target="_blank").
        """
        # We signal to the main window that a new tab is needed
        # Since we don't have a direct reference to MainWindow here easily, 
        # we can't easily return a view. Instead, we'll let the user click and handle it.
        # However, for a fully functional browser, we should return a new view instance.
        # But this view needs to be added to the tabs in MainWindow.
        # A common trick is to have a signal.
        return self._create_new_tab_view()

    def _create_new_tab_view(self):
        # This is tricky because we need the MainWindow instance to add the tab.
        # For now, let's keep it simple. Usually you'd use a parent reference.
        # Let's emit a signal that MainWindow can catch.
        # Actually, if we return a QWebEngineView here, Qt will use it.
        # But it won't be in our tab widget.
        # We'll fix this in MainWindow by connecting to a custom signal if we had one.
        # For now, let's just use the default behavior or return a new detached view.
        # Actually, let's just support it by returning a new view that the parent will manage.
        if self.window() and hasattr(self.window(), 'add_new_tab'):
             new_view = BrowserEngineView()
             self.window().add_new_tab_from_view(new_view)
             return new_view
        return None

    def get_page_text(self, callback):
        """
        Extracts plain text from the current page.
        """
        self.page().toPlainText(callback)
