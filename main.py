from gui import VideoDownloaderApp
from settings import initialize_settings

if __name__ == "__main__":
    app = VideoDownloaderApp()
    initialize_settings(app)
    app.run()
