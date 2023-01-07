from app.ui import *


def main():
    app = QApplication([])
    app.setFont(QFont("Helvetica [Cronyx]", 12))
    window = MainWindow()
    window.movie = QMovie("assets/loading.gif")
    window.loading_gif.setMovie(window.movie)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
