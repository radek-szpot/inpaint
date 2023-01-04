import sys
from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QWidget,
    QVBoxLayout,
)
from app import inpaint_algorithms

combo_map = {
    'Skimage-biharmonic': 5,
    'OpenCV-NS': 0,
    'OpenCV-TELEA': 1,
    'OpenCV-Shiftmap': 4,
    'OpenCV-FSR fast': 2,
    'OpenCV-FSR best': 3,
}

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)

class MainWindow(QMainWindow):
    path_orginal: Optional[str] = None
    path_saving: Optional[str] = None

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Inpaint app")
        self.resize(1200, 900)
        self.setAcceptDrops(True)
        self.drag_image = ImageLabel()
        self.image_after = QLabel()
        self.mask_window = MaskWindow()
        self.drag_mask = ImageLabel()
        # add wigets
        self.btn_inpaint = QPushButton("Make inpaint")
        self.btn_inpaint.clicked.connect(self.inpaint_click)
        self.btn_mask = QPushButton("Add mask")
        self.btn_mask.clicked.connect(self.mask_window.show)
        self.btn_save_path = QPushButton("Add save path")
        self.btn_save_path.clicked.connect(self.inpainted_save)
        self.btn_save = QPushButton("Save image")
        self.btn_save.clicked.connect(self.inpainted_save)
        self.combobox_inpaint = QComboBox()
        self.combobox_inpaint.addItems(combo_map.keys())
        # set layout
        layout = QGridLayout()
        widget = QWidget()
        layout.addWidget(self.btn_inpaint, 0, 0) 
        layout.addWidget(self.combobox_inpaint, 0, 1) 
        layout.addWidget(self.btn_mask, 1, 0) 
        layout.addWidget(self.btn_save_path, 1, 1) 
        layout.addWidget(self.drag_image, 2, 0) 
        layout.addWidget(self.image_after, 2, 1) 
        layout.addWidget(self.btn_save, 3, 0, 1, 2)
        widget.setLayout(layout)        

        self.setCentralWidget(widget)
        self._createMenu()

    def _createMenu(self):
        menu = self.menuBar().addMenu("&Menu")
        help = self.menuBar().addMenu("&Help")
        menu.addAction("&Exit", self.close)
        # help.addAction()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.path_orginal = file_path
            self.set_image(file_path)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.drag_image.setPixmap(QPixmap(file_path))

    def _createStatusBar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def inpaint_click(self):
        inpaint_text = self.combobox_inpaint.currentText()
        inpaint_flag = combo_map[inpaint_text]
        self.statusBar().showMessage(f"Pressed {inpaint_flag} {self.path_orginal}")
        if self.path_orginal:
            try:
                img_inpainted = inpaint_algorithms(path=self.path_orginal, flag=combo_map[inpaint_text])
                if not img_inpainted:
                    self.statusBar().showMessage("Error while inpainting")
            except:
                self.statusBar().showMessage("Error while inpainting 2")
            else:
                self.photoAfter.setPixmap(QPixmap(img_inpainted))
        else:
            self.statusBar().showMessage(f"Please upload image to inpaint")


    def inpainted_save(self):
        if not self.path_saving:
            self.statusBar().showMessage(f"Please specify path")

        
class MaskWindow(QMainWindow):
    """
    Window to drag or give path to mask
    """
    def __init__(self):
        super(MaskWindow, self).__init__()
        self.resize(400, 300)

        # Label
        self.mask_window = ImageLabel()
        layout = QGridLayout()
        widget = QWidget()
        layout.addWidget(self.mask_window, 0, 0)
        widget.setLayout(layout)        

        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())