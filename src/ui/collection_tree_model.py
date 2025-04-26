"""
Modelo para a árvore de coleções
"""

from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.core.storage import Storage
from src.models.collection import Collection, Folder


class CollectionTreeItem(QStandardItem):
    """Item personalizado para a árvore de coleções"""
    
    def __init__(self, name, item_type, data=None):
        super().__init__(name)
        self.item_type = item_type  # "collection", "folder", ou "request"
        self.data = data  # O ID da coleção/pasta/requisição


class CollectionTreeModel(QStandardItemModel):
    """
    Modelo para a árvore de coleções, pastas e requisições
    """
    
    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self.setHorizontalHeaderLabels(["Coleções"])
        
        # Adicionar nós raiz
        self.collections_root = QStandardItem("Coleções")
        self.history_root = QStandardItem("Histórico")
        
        self.appendRow(self.collections_root)
        self.appendRow(self.history_root)
    
    def load_collections(self):
        """Carrega as coleções do armazenamento"""
        # Limpar os nós existentes
        self.collections_root.removeRows(0, self.collections_root.rowCount())
        self.history_root.removeRows(0, self.history_root.rowCount())
        
        # Carregar as coleções
        collections = self.storage.get_all_collections()
        
        for collection in collections:
            # Criar item para a coleção
            collection_item = CollectionTreeItem(
                collection.name,
                "collection",
                collection.id
            )
            
            # Adicionar as requisições da coleção
            for request_id in collection.requests:
                request = self.storage.get_request(request_id)
                if request:
                    request_item = CollectionTreeItem(
                        request.name,
                        "request",
                        request.id
                    )
                    collection_item.appendRow(request_item)
            
            # Adicionar as pastas da coleção
            for folder in collection.folders:
                folder_item = self._create_folder_item(folder)
                collection_item.appendRow(folder_item)
            
            # Adicionar a coleção à raiz
            self.collections_root.appendRow(collection_item)
        
        # Carregar o histórico (últimas 10 requisições)
        history_requests = self.storage.get_history(10)
        
        for request in history_requests:
            history_item = CollectionTreeItem(
                request.name,
                "request",
                request.id
            )
            self.history_root.appendRow(history_item)
    
    def _create_folder_item(self, folder: Folder) -> CollectionTreeItem:
        """Cria recursivamente a estrutura de itens para uma pasta"""
        folder_item = CollectionTreeItem(
            folder.name,
            "folder",
            folder.id
        )
        
        # Adicionar as requisições da pasta
        for request_id in folder.requests:
            request = self.storage.get_request(request_id)
            if request:
                request_item = CollectionTreeItem(
                    request.name,
                    "request",
                    request.id
                )
                folder_item.appendRow(request_item)
        
        # Adicionar as subpastas
        for subfolder in folder.subfolders:
            subfolder_item = self._create_folder_item(subfolder)
            folder_item.appendRow(subfolder_item)
        
        return folder_item 