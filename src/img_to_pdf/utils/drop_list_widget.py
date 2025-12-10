from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtCore import Qt
from qfluentwidgets import ListWidget

class DropListWidget(ListWidget):
    def __init__(self, onFilesDropped, onItemsReordered=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onFilesDropped = onFilesDropped
        self.onItemsReordered = onItemsReordered  # Callback when items reordered by drag
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # Allow both external file drops AND internal reordering
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            # Allow internal drag for reordering
            super().dragEnterEvent(event)
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            # Allow internal drag for reordering
            super().dragMoveEvent(event)
            
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # External file drop
            exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp", ".html", ".htm")
            files = []
            for url in event.mimeData().urls():
                p = url.toLocalFile()
                if p.lower().endswith(exts):
                    files.append(p)
            if files:
                self.onFilesDropped(files)
            event.acceptProposedAction()
        else:
            # Internal reorder
            super().dropEvent(event)
            # Notify parent to sync its file list
            if self.onItemsReordered:
                self.onItemsReordered()
