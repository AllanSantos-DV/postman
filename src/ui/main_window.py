"""
Janela principal do aplicativo
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QSplitter, QTreeView, QVBoxLayout, 
    QHBoxLayout, QWidget, QAction, QToolBar, QStatusBar, QMessageBox,
    QMenu, QInputDialog, QLineEdit, QDialog, QDialogButtonBox, QComboBox,
    QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from src.core.storage import Storage
from src.ui.request_tab import RequestTab
from src.ui.collection_tree_model import CollectionTreeModel
from src.models.collection import Collection, Folder
from src.models.request import Request


class SelectCollectionDialog(QDialog):
    """
    Diálogo para selecionar uma coleção
    """
    def __init__(self, collections, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Salvar na Coleção")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Combobox para selecionar a coleção
        self.collection_combo = QComboBox()
        for collection in collections:
            self.collection_combo.addItem(collection.name, collection.id)
        
        layout.addWidget(QLabel("Selecione a coleção:"))
        layout.addWidget(self.collection_combo)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_selected_collection_id(self):
        """Retorna o ID da coleção selecionada"""
        return self.collection_combo.currentData()


class MainWindow(QMainWindow):
    """
    Janela principal do aplicativo
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyRequestMan")
        self.setMinimumSize(1200, 800)
        
        # Inicializar o armazenamento
        self.storage = Storage()
        
        # Criar os componentes da interface
        self._create_ui()
        
        # Carregar dados
        self._load_data()
    
    def _create_ui(self):
        """Cria a interface do usuário"""
        # Criar o layout principal (splitter horizontal)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Painel esquerdo para coleções e histórico
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Árvore de coleções
        self.collection_tree = QTreeView()
        self.collection_tree.setHeaderHidden(True)
        self.collection_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.collection_tree.customContextMenuRequested.connect(self._show_collection_context_menu)
        self.collection_tree.doubleClicked.connect(self._on_collection_item_double_clicked)
        
        # Modelo para a árvore de coleções
        self.collection_model = CollectionTreeModel(self.storage)
        self.collection_tree.setModel(self.collection_model)
        
        self.left_layout.addWidget(self.collection_tree)
        self.main_splitter.addWidget(self.left_panel)
        
        # Painel direito para as requisições
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Guias para múltiplas requisições
        self.request_tabs = QTabWidget()
        self.request_tabs.setTabsClosable(True)
        self.request_tabs.tabCloseRequested.connect(self._close_tab)
        
        self.right_layout.addWidget(self.request_tabs)
        self.main_splitter.addWidget(self.right_panel)
        
        # Definir as proporções do splitter (30% esquerda, 70% direita)
        self.main_splitter.setSizes([300, 700])
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")
        
        # Criar as ações da interface
        self._create_actions()
        
        # Criar a barra de ferramentas
        self._create_toolbar()
        
        # Criar o menu principal
        self._create_menu()
    
    def _create_actions(self):
        """Cria as ações da interface"""
        # Ação para nova requisição
        self.new_request_action = QAction("Nova Requisição", self)
        self.new_request_action.setStatusTip("Criar uma nova requisição")
        self.new_request_action.triggered.connect(self._create_new_request)
        
        # Ação para nova coleção
        self.new_collection_action = QAction("Nova Coleção", self)
        self.new_collection_action.setStatusTip("Criar uma nova coleção")
        self.new_collection_action.triggered.connect(self._create_new_collection)
        
        # Ação para importar coleção
        self.import_action = QAction("Importar", self)
        self.import_action.setStatusTip("Importar coleção")
        
        # Ação para exportar coleção
        self.export_action = QAction("Exportar", self)
        self.export_action.setStatusTip("Exportar coleção")
        
        # Ação para sair
        self.exit_action = QAction("Sair", self)
        self.exit_action.setStatusTip("Sair do aplicativo")
        self.exit_action.triggered.connect(self.close)
        
        # Ação para salvar requisição na coleção
        self.save_to_collection_action = QAction("Salvar na Coleção", self)
        self.save_to_collection_action.setStatusTip("Salvar requisição em uma coleção")
        self.save_to_collection_action.triggered.connect(self._save_current_request_to_collection)
    
    def _create_toolbar(self):
        """Cria a barra de ferramentas"""
        self.toolbar = QToolBar("Barra de Ferramentas Principal")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Adicionar ações à barra de ferramentas
        self.toolbar.addAction(self.new_request_action)
        self.toolbar.addAction(self.new_collection_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_to_collection_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.import_action)
        self.toolbar.addAction(self.export_action)
    
    def _create_menu(self):
        """Cria o menu principal"""
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        file_menu.addAction(self.new_request_action)
        file_menu.addAction(self.new_collection_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_to_collection_action)
        file_menu.addSeparator()
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Menu Editar
        edit_menu = menu_bar.addMenu("Editar")
        # Adicionar ações posteriormente
        
        # Menu Visualizar
        view_menu = menu_bar.addMenu("Visualizar")
        # Adicionar ações posteriormente
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        about_action = QAction("Sobre", self)
        help_menu.addAction(about_action)
    
    def _load_data(self):
        """Carrega os dados do armazenamento"""
        # Atualizar o modelo de coleções
        self.collection_model.load_collections()
    
    def _create_new_request(self):
        """Cria uma nova requisição em uma nova guia"""
        # Criar um novo objeto de requisição
        request = Request(
            name="Nova Requisição",
            url="https://",
            method="GET"
        )
        
        # Criar uma nova guia de requisição
        self._add_request_tab(request)
    
    def _add_request_tab(self, request):
        """Adiciona uma nova guia com uma requisição"""
        request_tab = RequestTab(request, self.storage)
        
        # Conectar sinais
        request_tab.request_saved.connect(self._on_request_saved)
        request_tab.save_to_collection.connect(self._save_current_request_to_collection)
        
        # Adicionar à guia e selecionar
        index = self.request_tabs.addTab(request_tab, request.name)
        self.request_tabs.setCurrentIndex(index)
    
    def _close_tab(self, index):
        """Fecha uma guia"""
        widget = self.request_tabs.widget(index)
        
        # Verificar se há alterações não salvas
        if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
            reply = QMessageBox.question(
                self, 
                "Alterações não salvas", 
                "Há alterações não salvas. Deseja salvar antes de fechar?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                # Salvar alterações
                widget.save_request()
            elif reply == QMessageBox.Cancel:
                # Cancelar fechamento
                return
        
        # Remover a guia
        self.request_tabs.removeTab(index)
    
    def _create_new_collection(self):
        """Cria uma nova coleção"""
        name, ok = QInputDialog.getText(
            self, 
            "Nova Coleção", 
            "Nome da coleção:",
            QLineEdit.Normal
        )
        
        if ok and name:
            # Criar nova coleção
            collection = Collection(name=name)
            
            # Salvar no armazenamento
            self.storage.save_collection(collection)
            
            # Atualizar o modelo
            self.collection_model.load_collections()
    
    def _show_collection_context_menu(self, position):
        """Exibe o menu de contexto para a árvore de coleções"""
        # Obter o índice do item clicado
        index = self.collection_tree.indexAt(position)
        
        if not index.isValid():
            # Se não houver item válido, exibir menu para adicionar coleção
            menu = QMenu()
            menu.addAction("Nova Coleção", self._create_new_collection)
            menu.exec_(self.collection_tree.viewport().mapToGlobal(position))
            return
        
        # Obter o item do modelo
        item = self.collection_model.itemFromIndex(index)
        item_type = getattr(item, "item_type", None)
        
        # Criar o menu de contexto
        menu = QMenu()
        
        if item_type == "collection":
            # Menu para coleções
            menu.addAction("Nova Requisição", lambda: self._add_request_to_collection(item.data))
            menu.addAction("Nova Pasta", lambda: self._add_folder_to_collection(item.data))
            menu.addSeparator()
            menu.addAction("Renomear", lambda: self._rename_collection(item.data))
            menu.addAction("Excluir", lambda: self._delete_collection(item.data))
        
        elif item_type == "folder":
            # Menu para pastas
            menu.addAction("Nova Requisição", lambda: self._add_request_to_folder(item.data))
            menu.addAction("Nova Subpasta", lambda: self._add_subfolder(item.data))
            menu.addSeparator()
            menu.addAction("Renomear", lambda: self._rename_folder(item.data))
            menu.addAction("Excluir", lambda: self._delete_folder(item.data))
        
        elif item_type == "request":
            # Menu para requisições
            menu.addAction("Abrir", lambda: self._open_request(item.data))
            menu.addAction("Duplicar", lambda: self._duplicate_request(item.data))
            menu.addSeparator()
            menu.addAction("Renomear", lambda: self._rename_request(item.data))
            menu.addAction("Excluir", lambda: self._delete_request(item.data))
        
        # Exibir o menu
        menu.exec_(self.collection_tree.viewport().mapToGlobal(position))
    
    def _on_collection_item_double_clicked(self, index):
        """Ação quando um item da árvore de coleções é clicado duplamente"""
        # Obter o item do modelo
        item = self.collection_model.itemFromIndex(index)
        item_type = getattr(item, "item_type", None)
        
        if item_type == "request":
            # Abrir a requisição em uma nova guia
            self._open_request(item.data)
    
    def _open_request(self, request_id):
        """Abre uma requisição em uma nova guia"""
        # Carregar a requisição do armazenamento
        request = self.storage.get_request(request_id)
        
        if request:
            # Verificar se a requisição já está aberta
            for i in range(self.request_tabs.count()):
                tab = self.request_tabs.widget(i)
                if hasattr(tab, 'request') and tab.request.id == request.id:
                    # Se já estiver aberta, apenas selecionar a guia
                    self.request_tabs.setCurrentIndex(i)
                    return
            
            # Se não estiver aberta, criar uma nova guia
            self._add_request_tab(request)
    
    def _on_request_saved(self, request):
        """Atualiza a interface quando uma requisição é salva"""
        # Atualizar o nome da guia
        for i in range(self.request_tabs.count()):
            tab = self.request_tabs.widget(i)
            if hasattr(tab, 'request') and tab.request.id == request.id:
                self.request_tabs.setTabText(i, request.name)
                break
        
        # Atualizar o modelo de coleções
        self.collection_model.load_collections()
    
    def _save_current_request_to_collection(self):
        """Salva a requisição atual em uma coleção"""
        # Obter a guia atual
        current_index = self.request_tabs.currentIndex()
        if current_index < 0:
            return
        
        tab = self.request_tabs.widget(current_index)
        if not hasattr(tab, 'request'):
            return
        
        # Salvar a requisição atual
        tab.save_request()
        
        # Obter todas as coleções
        collections = self.storage.get_all_collections()
        if not collections:
            QMessageBox.warning(
                self,
                "Sem Coleções",
                "Não há coleções disponíveis. Crie uma coleção primeiro."
            )
            return
        
        # Mostrar diálogo para selecionar a coleção
        dialog = SelectCollectionDialog(collections, self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # Obter a coleção selecionada
        collection_id = dialog.get_selected_collection_id()
        collection = self.storage.get_collection(collection_id)
        
        if not collection:
            return
        
        # Adicionar a requisição à coleção
        collection.add_request(tab.request.id)
        
        # Salvar a coleção
        self.storage.save_collection(collection)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
        
        # Exibir mensagem de sucesso
        self.status_bar.showMessage(f"Requisição '{tab.request.name}' adicionada à coleção '{collection.name}'", 3000)
        
    def _add_request_to_collection(self, collection_id):
        """Adiciona uma nova requisição a uma coleção"""
        # Carregar a coleção
        collection = self.storage.get_collection(collection_id)
        if not collection:
            return
        
        # Criar uma nova requisição
        request = Request(
            name="Nova Requisição",
            url="https://",
            method="GET"
        )
        
        # Salvar a requisição
        self.storage.save_request(request)
        
        # Adicionar à coleção
        collection.add_request(request.id)
        self.storage.save_collection(collection)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
        
        # Abrir a requisição em uma nova guia
        self._add_request_tab(request)
    
    def _add_folder_to_collection(self, collection_id):
        """Adiciona uma nova pasta a uma coleção"""
        # Carregar a coleção
        collection = self.storage.get_collection(collection_id)
        if not collection:
            return
        
        # Solicitar o nome da pasta
        name, ok = QInputDialog.getText(
            self,
            "Nova Pasta",
            "Nome da pasta:",
            QLineEdit.Normal
        )
        
        if not (ok and name):
            return
        
        # Criar uma nova pasta
        folder = Folder(name=name)
        
        # Adicionar à coleção
        collection.add_folder(folder)
        self.storage.save_collection(collection)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
    
    def _rename_collection(self, collection_id):
        """Renomeia uma coleção"""
        # Carregar a coleção
        collection = self.storage.get_collection(collection_id)
        if not collection:
            return
        
        # Solicitar o novo nome
        name, ok = QInputDialog.getText(
            self,
            "Renomear Coleção",
            "Novo nome:",
            QLineEdit.Normal,
            collection.name
        )
        
        if not (ok and name):
            return
        
        # Atualizar o nome
        collection.name = name
        self.storage.save_collection(collection)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
    
    def _delete_collection(self, collection_id):
        """Exclui uma coleção"""
        # Carregar a coleção
        collection = self.storage.get_collection(collection_id)
        if not collection:
            return
        
        # Confirmar a exclusão
        reply = QMessageBox.question(
            self,
            "Excluir Coleção",
            f"Deseja realmente excluir a coleção '{collection.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Excluir a coleção
        self.storage.delete_collection(collection_id)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
    
    def _add_request_to_folder(self, folder_id):
        """Adiciona uma requisição a uma pasta"""
        # Encontrar a pasta
        for collection in self.storage.get_all_collections():
            folder = self._find_folder_in_collection(collection, folder_id)
            if folder:
                # Criar uma nova requisição
                request = Request(
                    name="Nova Requisição",
                    url="https://",
                    method="GET"
                )
                
                # Salvar a requisição
                self.storage.save_request(request)
                
                # Adicionar à pasta
                folder.add_request(request.id)
                self.storage.save_collection(collection)
                
                # Atualizar o modelo
                self.collection_model.load_collections()
                
                # Abrir a requisição em uma nova guia
                self._add_request_tab(request)
                return
    
    def _find_folder_in_collection(self, collection, folder_id):
        """Encontra uma pasta em uma coleção (busca recursiva)"""
        # Verificar as pastas diretamente na coleção
        for folder in collection.folders:
            if folder.id == folder_id:
                return folder
            
            # Verificar subpastas
            subfolder = self._find_folder_in_subfolders(folder, folder_id)
            if subfolder:
                return subfolder
        
        return None
    
    def _find_folder_in_subfolders(self, parent_folder, folder_id):
        """Busca recursivamente uma pasta dentro de subpastas"""
        for subfolder in parent_folder.subfolders:
            if subfolder.id == folder_id:
                return subfolder
            
            # Verificar níveis mais profundos
            result = self._find_folder_in_subfolders(subfolder, folder_id)
            if result:
                return result
        
        return None
    
    def _add_subfolder(self, parent_folder_id):
        """Adiciona uma subpasta a uma pasta"""
        # Encontrar a pasta pai
        for collection in self.storage.get_all_collections():
            parent_folder = self._find_folder_in_collection(collection, parent_folder_id)
            if parent_folder:
                # Solicitar o nome da pasta
                name, ok = QInputDialog.getText(
                    self,
                    "Nova Subpasta",
                    "Nome da subpasta:",
                    QLineEdit.Normal
                )
                
                if not (ok and name):
                    return
                
                # Criar uma nova pasta
                subfolder = Folder(name=name)
                
                # Adicionar à pasta pai
                parent_folder.add_subfolder(subfolder)
                self.storage.save_collection(collection)
                
                # Atualizar o modelo
                self.collection_model.load_collections()
                return
    
    def _rename_folder(self, folder_id):
        """Renomeia uma pasta"""
        # Encontrar a pasta
        for collection in self.storage.get_all_collections():
            folder = self._find_folder_in_collection(collection, folder_id)
            if folder:
                # Solicitar o novo nome
                name, ok = QInputDialog.getText(
                    self,
                    "Renomear Pasta",
                    "Novo nome:",
                    QLineEdit.Normal,
                    folder.name
                )
                
                if not (ok and name):
                    return
                
                # Atualizar o nome
                folder.name = name
                self.storage.save_collection(collection)
                
                # Atualizar o modelo
                self.collection_model.load_collections()
                return
    
    def _delete_folder(self, folder_id):
        """Exclui uma pasta"""
        # Encontrar a pasta e sua coleção
        for collection in self.storage.get_all_collections():
            # Verificar se a pasta está diretamente na coleção
            for folder in collection.folders:
                if folder.id == folder_id:
                    # Confirmar a exclusão
                    reply = QMessageBox.question(
                        self,
                        "Excluir Pasta",
                        f"Deseja realmente excluir a pasta '{folder.name}'?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply != QMessageBox.Yes:
                        return
                    
                    # Excluir a pasta
                    collection.remove_folder(folder_id)
                    self.storage.save_collection(collection)
                    
                    # Atualizar o modelo
                    self.collection_model.load_collections()
                    return
            
            # Verificar pastas aninhadas
            if self._delete_folder_from_subfolders(collection, folder_id):
                return
    
    def _delete_folder_from_subfolders(self, collection, folder_id):
        """Remove uma pasta de subpastas recursivamente"""
        for folder in collection.folders:
            if self._delete_subfolder(folder, folder_id):
                self.storage.save_collection(collection)
                self.collection_model.load_collections()
                return True
        
        return False
    
    def _delete_subfolder(self, parent_folder, folder_id):
        """Busca e remove uma subpasta recursivamente"""
        # Verificar se a pasta está nas subpastas diretas
        for subfolder in parent_folder.subfolders:
            if subfolder.id == folder_id:
                # Confirmar a exclusão
                reply = QMessageBox.question(
                    self,
                    "Excluir Pasta",
                    f"Deseja realmente excluir a pasta '{subfolder.name}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return False
                
                # Excluir a pasta
                parent_folder.remove_subfolder(folder_id)
                return True
            
            # Verificar níveis mais profundos
            if self._delete_subfolder(subfolder, folder_id):
                return True
        
        return False
    
    def _duplicate_request(self, request_id):
        """Duplica uma requisição"""
        # Carregar a requisição original
        original_request = self.storage.get_request(request_id)
        if not original_request:
            return
        
        # Criar uma nova requisição com dados copiados
        request_data = original_request.to_dict()
        
        # Modificar para uma nova requisição
        del request_data["id"]
        request_data["name"] = f"{original_request.name} (Cópia)"
        
        # Criar a nova requisição
        new_request = Request.from_dict(request_data)
        
        # Salvar a nova requisição
        self.storage.save_request(new_request)
        
        # Abrir a nova requisição
        self._add_request_tab(new_request)
    
    def _rename_request(self, request_id):
        """Renomeia uma requisição"""
        # Carregar a requisição
        request = self.storage.get_request(request_id)
        if not request:
            return
        
        # Solicitar o novo nome
        name, ok = QInputDialog.getText(
            self,
            "Renomear Requisição",
            "Novo nome:",
            QLineEdit.Normal,
            request.name
        )
        
        if not (ok and name):
            return
        
        # Atualizar o nome
        request.name = name
        self.storage.save_request(request)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
        
        # Atualizar as guias abertas com esta requisição
        for i in range(self.request_tabs.count()):
            tab = self.request_tabs.widget(i)
            if hasattr(tab, 'request') and tab.request.id == request.id:
                tab.request.name = name
                self.request_tabs.setTabText(i, name)
                break
    
    def _delete_request(self, request_id):
        """Exclui uma requisição"""
        # Carregar a requisição
        request = self.storage.get_request(request_id)
        if not request:
            return
        
        # Confirmar a exclusão
        reply = QMessageBox.question(
            self,
            "Excluir Requisição",
            f"Deseja realmente excluir a requisição '{request.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Fechar guias abertas com esta requisição
        for i in range(self.request_tabs.count()-1, -1, -1):
            tab = self.request_tabs.widget(i)
            if hasattr(tab, 'request') and tab.request.id == request.id:
                self.request_tabs.removeTab(i)
        
        # Remover de todas as coleções
        for collection in self.storage.get_all_collections():
            # Remover da coleção principal
            if request_id in collection.requests:
                collection.remove_request(request_id)
                self.storage.save_collection(collection)
            
            # Remover de pastas
            self._remove_request_from_folders(collection, request_id)
        
        # Excluir a requisição
        self.storage.delete_request(request_id)
        
        # Atualizar o modelo
        self.collection_model.load_collections()
    
    def _remove_request_from_folders(self, collection, request_id):
        """Remove uma requisição de todas as pastas em uma coleção"""
        # Verificar todas as pastas na coleção
        for folder in collection.folders:
            # Remover da pasta atual
            if request_id in folder.requests:
                folder.remove_request(request_id)
                self.storage.save_collection(collection)
            
            # Verificar subpastas recursivamente
            self._remove_request_from_subfolders(folder, request_id, collection)
    
    def _remove_request_from_subfolders(self, folder, request_id, collection):
        """Remove uma requisição de subpastas recursivamente"""
        for subfolder in folder.subfolders:
            # Remover da subpasta atual
            if request_id in subfolder.requests:
                subfolder.remove_request(request_id)
                self.storage.save_collection(collection)
            
            # Verificar níveis mais profundos
            self._remove_request_from_subfolders(subfolder, request_id, collection) 