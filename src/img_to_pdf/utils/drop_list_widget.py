from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtCore import Qt
from qfluentwidgets import ListWidget

class DropListWidget(ListWidget):
    def __init__(self, onFilesDropped, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onFilesDropped = onFilesDropped
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")
        files = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p.lower().endswith(exts):
                files.append(p)
        if files:
            self.onFilesDropped(files)
        event.acceptProposedAction()
