"""
Janela principal do aplicativo
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QSplitter, QTreeView, QVBoxLayout, 
    QHBoxLayout, QWidget, QAction, QToolBar, QStatusBar, QMessageBox,
    QMenu, QInputDialog, QLineEdit, QDialog, QDialogButtonBox, QComboBox,
    QLabel, QActionGroup, QAbstractItemView, QFileDialog, QRadioButton,
    QTextBrowser, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon, QPixmap

from src.core.storage import Storage
from src.ui.request_tab import RequestTab
from src.ui.collection_tree_model import CollectionTreeModel, CollectionTreeItem
from src.ui.environment_dialog import EnvironmentDialog
from src.models.collection import Collection, Folder
from src.models.request import Request
from src.models.environment import Environment
from src.ui.styles import LIGHT_STYLE, DARK_STYLE


class SelectCollectionDialog(QDialog):
    """
    Diálogo para selecionar uma coleção
    """
    def __init__(self, collections, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Salvar na Coleção")
        self.setMinimumWidth(400)
        
        # Herdar estilo da janela principal
        if parent and parent.styleSheet():
            self.setStyleSheet(parent.styleSheet())
        
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


class AboutDialog(QDialog):
    """
    Diálogo Sobre com informações do aplicativo
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Sobre PyRequestMan")
        self.setMinimumSize(900, 700)
        
        # Herdar estilo da janela principal
        if parent and parent.styleSheet():
            self.setStyleSheet(parent.styleSheet())
        
        layout = QVBoxLayout(self)
        
        # Área com scroll para o conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Título
        title_label = QLabel("PyRequestMan")
        title_label.setAlignment(Qt.AlignCenter)
        font = title_label.font()
        font.setPointSize(font.pointSize() + 10)
        font.setBold(True)
        title_label.setFont(font)
        content_layout.addWidget(title_label)
        
        # Versão
        version_label = QLabel("Versão 0.1.0")
        version_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(version_label)
        
        # Espaçamento
        content_layout.addSpacing(20)
        
        # Screenshot da aplicação
        screenshot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "resources", "screenshots", "main.png")
        
        if os.path.exists(screenshot_path):
            screenshot_label = QLabel()
            pixmap = QPixmap(screenshot_path)
            pixmap = pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            screenshot_label.setPixmap(pixmap)
            screenshot_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(screenshot_label)
        
        content_layout.addSpacing(20)
        
        # Descrição do aplicativo
        description = """
        <h3>Descrição</h3>
        <p>O PyRequestMan é um cliente HTTP similar ao Postman e Insomnia, desenvolvido inteiramente em Python.
        Esta aplicação permite testar APIs REST de forma simples e intuitiva, sem necessidade de conexão com serviços externos.</p>
        
        <h3>Principais Funcionalidades</h3>
        <ul>
            <li>Suporte para todos os métodos HTTP (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)</li>
            <li>Organização de requisições em coleções e pastas</li>
            <li>Ambientes e variáveis para facilitar diferentes configurações</li>
            <li>Formatação automática de respostas JSON</li>
            <li>Histórico de requisições enviadas</li>
            <li>Importação e exportação de coleções no formato Postman</li>
            <li>Tema claro e escuro</li>
        </ul>
        
        <h3>Como Utilizar</h3>
        <h4>Criando uma Nova Requisição</h4>
        <ol>
            <li>Clique no botão "Nova Requisição" na barra de ferramentas ou no menu Arquivo</li>
            <li>Escolha o método HTTP desejado (GET, POST, etc.)</li>
            <li>Digite a URL da API que deseja acessar</li>
            <li>Configure cabeçalhos, parâmetros ou corpo da requisição conforme necessário</li>
            <li>Clique no botão "Enviar" para executar a requisição</li>
            <li>A resposta será exibida abaixo com formatação adequada</li>
        </ol>
        
        <h4>Trabalhando com Coleções</h4>
        <ol>
            <li>Crie uma nova coleção clicando com o botão direito no painel esquerdo</li>
            <li>Adicione requisições à coleção usando o botão "Salvar na Coleção"</li>
            <li>Organize suas requisições em pastas para melhor organização</li>
            <li>Clique duas vezes em qualquer requisição na coleção para abri-la</li>
            <li>Exporte suas coleções para compartilhar com outros usuários</li>
        </ol>
        
        <h4>Utilizando Ambientes e Variáveis</h4>
        <ol>
            <li>Crie ambientes (dev, homologação, produção) no menu Ambientes</li>
            <li>Defina variáveis para cada ambiente (como URL base, tokens, etc.)</li>
            <li>Selecione o ambiente ativo na barra de ferramentas</li>
            <li>Use variáveis nas suas requisições com a sintaxe {{nome_da_variavel}}</li>
            <li>Alterne entre ambientes facilmente para testar diferentes configurações</li>
        </ol>
        """
        
        description_browser = QTextBrowser()
        description_browser.setHtml(description)
        description_browser.setOpenExternalLinks(True)
        content_layout.addWidget(description_browser)
        
        # Adicionar informações de copyright
        copyright_label = QLabel("© 2025 - Desenvolvido com Python e PyQt5")
        copyright_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(copyright_label)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


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
        
        # Ambiente selecionado
        self.current_environment = None
        self.current_variables = {}
        
        # Configurações de tema
        self.is_dark_theme = False
        self._load_settings()
        
        # Criar os componentes da interface
        self._create_ui()
        
        # Carregar dados
        self._load_data()
        
        # Aplicar tema inicial
        self._apply_theme()
    
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
        
        # Permitir edição in-place dos itens da árvore
        self.collection_tree.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.DoubleClicked)
        
        # Modelo para a árvore de coleções
        self.collection_model = CollectionTreeModel(self.storage)
        self.collection_tree.setModel(self.collection_model)
        
        # Conectar o sinal de edição de item
        self.collection_model.itemChanged.connect(self._on_collection_item_changed)
        
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
        self.import_action.triggered.connect(self._import_collection)
        
        # Ação para exportar coleção
        self.export_action = QAction("Exportar", self)
        self.export_action.setStatusTip("Exportar coleção")
        self.export_action.triggered.connect(self._export_collection)
        
        # Ação para sair
        self.exit_action = QAction("Sair", self)
        self.exit_action.setStatusTip("Sair do aplicativo")
        self.exit_action.triggered.connect(self.close)
        
        # Ação para salvar requisição na coleção
        self.save_to_collection_action = QAction("Salvar na Coleção", self)
        self.save_to_collection_action.setStatusTip("Salvar requisição em uma coleção")
        self.save_to_collection_action.triggered.connect(self._save_current_request_to_collection)
        
        # Ação para gerenciar ambientes
        self.manage_environments_action = QAction("Gerenciar Ambientes", self)
        self.manage_environments_action.setStatusTip("Gerenciar ambientes e variáveis")
        self.manage_environments_action.triggered.connect(self._show_environments_dialog)
        
        # Ações para alternar tema
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        self.light_theme_action = QAction("Tema Claro", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.setChecked(not self.is_dark_theme)
        self.light_theme_action.triggered.connect(lambda: self._toggle_theme(False))
        self.theme_group.addAction(self.light_theme_action)
        
        self.dark_theme_action = QAction("Tema Escuro", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(self.is_dark_theme)
        self.dark_theme_action.triggered.connect(lambda: self._toggle_theme(True))
        self.theme_group.addAction(self.dark_theme_action)
        
        # Ações para o menu Editar
        self.rename_action = QAction("Renomear", self)
        self.rename_action.setStatusTip("Renomear item selecionado")
        self.rename_action.triggered.connect(self._rename_selected_item)
        
        self.delete_action = QAction("Excluir", self)
        self.delete_action.setStatusTip("Excluir item selecionado")
        self.delete_action.triggered.connect(self._delete_selected_item)
        
        # Ação para limpar histórico
        self.clear_history_action = QAction("Limpar Histórico", self)
        self.clear_history_action.setStatusTip("Limpar histórico de requisições")
        self.clear_history_action.triggered.connect(self._clear_history)
    
    def _create_toolbar(self):
        """Cria a barra de ferramentas"""
        self.toolbar = QToolBar("Barra de Ferramentas Principal")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Adicionar ações à barra de ferramentas
        self.toolbar.addAction(self.new_request_action)
        self.new_request_action.setToolTip("Criar uma nova requisição")
        
        self.toolbar.addAction(self.new_collection_action)
        self.new_collection_action.setToolTip("Criar uma nova coleção de requisições")
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_to_collection_action)
        self.save_to_collection_action.setToolTip("Salvar a requisição atual em uma coleção")
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.import_action)
        self.import_action.setToolTip("Importar uma coleção de requisições")
        
        self.toolbar.addAction(self.export_action)
        self.export_action.setToolTip("Exportar uma coleção de requisições")
        
        # Adicionar seletor de ambiente
        self.toolbar.addSeparator()
        env_label = QLabel("Ambiente: ")
        env_label.setToolTip("Selecione o ambiente de variáveis a ser utilizado")
        self.toolbar.addWidget(env_label)
        
        self.environment_combo = QComboBox()
        self.environment_combo.setMinimumWidth(150)
        self.environment_combo.addItem("Nenhum", None)
        self.environment_combo.currentIndexChanged.connect(self._on_environment_changed)
        self.environment_combo.setToolTip("Selecione o ambiente de variáveis para substituição nas requisições")
        self.toolbar.addWidget(self.environment_combo)
        
        # Botão para gerenciar ambientes
        self.toolbar.addAction(self.manage_environments_action)
        self.manage_environments_action.setToolTip("Gerenciar ambientes e suas variáveis")
    
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
        edit_menu.addAction(self.rename_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.clear_history_action)
        
        # Menu Visualizar
        view_menu = menu_bar.addMenu("Visualizar")
        
        # Submenu de temas
        theme_menu = view_menu.addMenu("Tema")
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)
        
        # Menu Ambientes
        environment_menu = menu_bar.addMenu("Ambientes")
        environment_menu.addAction(self.manage_environments_action)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        self.about_action = QAction("Sobre", self)
        self.about_action.setStatusTip("Informações sobre o aplicativo")
        self.about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(self.about_action)
    
    def _load_data(self):
        """Carrega os dados do armazenamento"""
        # Atualizar o modelo de coleções
        self.collection_model.load_collections()
        
        # Carregar ambientes
        self._load_environments()
    
    def _load_environments(self):
        """Carrega os ambientes do armazenamento"""
        # Salvar o ambiente atual selecionado
        current_env_id = self.environment_combo.currentData()
        
        # Limpar combobox
        self.environment_combo.clear()
        self.environment_combo.addItem("Nenhum", None)
        
        # Carregar ambientes
        environments = self.storage.get_all_environments()
        
        for env in environments:
            self.environment_combo.addItem(env.name, env.id)
        
        # Restaurar a seleção anterior, se possível
        if current_env_id:
            index = self.environment_combo.findData(current_env_id)
            if index >= 0:
                self.environment_combo.setCurrentIndex(index)
    
    def _on_environment_changed(self, index):
        """Manipula a mudança de ambiente selecionado"""
        env_id = self.environment_combo.currentData()
        
        if env_id:
            self.current_environment = self.storage.get_environment(env_id)
            self.current_variables = self.current_environment.variables.copy() if self.current_environment else {}
        else:
            self.current_environment = None
            self.current_variables = {}
        
        # Atualizar as variáveis disponíveis em todas as guias abertas
        for i in range(self.request_tabs.count()):
            tab = self.request_tabs.widget(i)
            if hasattr(tab, 'set_available_variables'):
                tab.set_available_variables(self.current_variables)
        
        self.status_bar.showMessage(f"Ambiente atual: {self.environment_combo.currentText()}")
    
    def _show_environments_dialog(self):
        """Mostra o diálogo de gerenciamento de ambientes"""
        dialog = EnvironmentDialog(self.storage, self)
        dialog.environment_updated.connect(self._load_environments)
        
        # Se o diálogo for aceito, atualizar as variáveis em todas as guias
        if dialog.exec_() == EnvironmentDialog.Accepted:
            # Recarregar o ambiente atual
            env_id = self.environment_combo.currentData()
            if env_id:
                self.current_environment = self.storage.get_environment(env_id)
                self.current_variables = self.current_environment.variables.copy() if self.current_environment else {}
                
                # Atualizar as variáveis disponíveis em todas as guias abertas
                for i in range(self.request_tabs.count()):
                    tab = self.request_tabs.widget(i)
                    if hasattr(tab, 'set_available_variables'):
                        tab.set_available_variables(self.current_variables)
    
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
        
        # Definir as variáveis disponíveis
        if hasattr(request_tab, 'set_available_variables'):
            request_tab.set_available_variables(self.current_variables)
        
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
    
    def _get_current_request_tab(self):
        """Retorna a guia de requisição atual"""
        index = self.request_tabs.currentIndex()
        if index >= 0:
            return self.request_tabs.widget(index)
        return None
    
    def _on_request_saved(self, request):
        """Chamado quando uma requisição é salva"""
        # Atualizar o título da guia
        index = self.request_tabs.currentIndex()
        if index >= 0:
            self.request_tabs.setTabText(index, request.name)
    
    def _send_request(self):
        """Envia a requisição da guia atual usando o ambiente selecionado"""
        tab = self._get_current_request_tab()
        if not tab:
            return
            
        # Usar o método de envio com ambiente se estiver implementado
        if hasattr(tab, '_send_request_with_environment'):
            tab._send_request_with_environment(self.current_variables)
        else:
            # Fallback para método existente se não implementamos a versão com ambiente
            tab._send_request()
    
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
        elif item_type in ["collection", "folder"]:
            # Para coleções e pastas, permitir a edição in-place
            # (não fazemos nada explicitamente, a QTreeView já cuidará disso
            # com as configurações de EditTriggers que definimos)
            pass
    
    def _on_collection_item_changed(self, item):
        """Chamado quando um item na árvore de coleções é editado"""
        # Verificar se o item possui tipo e dados
        item_type = getattr(item, "item_type", None)
        item_data = getattr(item, "data", None)
        
        if not (item_type and item_data):
            return
        
        # Pegar o novo nome do item
        new_name = item.text()
        
        # Atualizar o nome de acordo com o tipo
        if item_type == "collection":
            self._update_collection_name(item_data, new_name)
        elif item_type == "folder":
            self._update_folder_name(item_data, new_name)
        elif item_type == "request":
            self._update_request_name(item_data, new_name)
    
    def _update_collection_name(self, collection_id, new_name):
        """Atualiza o nome de uma coleção"""
        collection = self.storage.get_collection(collection_id)
        if collection and new_name:
            collection.name = new_name
            self.storage.save_collection(collection)
            # Não precisamos recarregar o modelo completo, pois apenas o nome foi alterado
            # e isso já está refletido no item da árvore
    
    def _update_folder_name(self, folder_id, new_name):
        """Atualiza o nome de uma pasta"""
        # Buscamos a pasta em todas as coleções
        for collection in self.storage.get_all_collections():
            folder = self._find_folder_in_collection(collection, folder_id)
            if folder and new_name:
                folder.name = new_name
                self.storage.save_collection(collection)
                return
    
    def _update_request_name(self, request_id, new_name):
        """Atualiza o nome de uma requisição"""
        request = self.storage.get_request(request_id)
        if request and new_name:
            request.name = new_name
            self.storage.save_request(request)
            
            # Atualizar também o nome na aba da requisição se estiver aberta
            for i in range(self.request_tabs.count()):
                tab = self.request_tabs.widget(i)
                if hasattr(tab, 'request') and tab.request.id == request_id:
                    self.request_tabs.setTabText(i, new_name)
                    # Se a requisição está aberta, atualizar também o campo de nome
                    if hasattr(tab, 'name_edit'):
                        tab.name_edit.setText(new_name)
                    break
    
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
    
    def _toggle_theme(self, dark_mode):
        """Alterna entre os temas claro e escuro"""
        if dark_mode != self.is_dark_theme:
            self.is_dark_theme = dark_mode
            self._apply_theme()
            self._save_settings()
    
    def _apply_theme(self):
        """Aplica o tema atual à interface"""
        style = DARK_STYLE if self.is_dark_theme else LIGHT_STYLE
        self.setStyleSheet(style)
    
    def _load_settings(self):
        """Carrega as configurações do armazenamento"""
        settings = self.storage.get_settings()
        
        if 'theme' in settings:
            self.is_dark_theme = settings['theme'] == 'dark'
    
    def _save_settings(self):
        """Salva as configurações no armazenamento"""
        settings = self.storage.get_settings()
        settings['theme'] = 'dark' if self.is_dark_theme else 'light'
        self.storage.save_settings(settings)

    def _import_collection(self):
        """Importa uma coleção de um arquivo Postman ou Insomnia"""
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Importar Coleção")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Arquivos de Coleção (*.json)")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            
            # Importar a coleção usando o conversor
            from src.utils.collection_converter import import_collection
            success, message, collection = import_collection(file_path, self.storage)
            
            if success:
                # Atualizar a árvore de coleções
                self.collection_model.load_collections()
                QMessageBox.information(self, "Importação Concluída", message)
            else:
                QMessageBox.warning(self, "Erro na Importação", message)

    def _export_collection(self):
        """Exporta uma coleção selecionada para um arquivo Postman ou Insomnia"""
        # Obter o item selecionado
        index = self.collection_tree.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Erro", "Selecione uma coleção para exportar")
            return
        
        # Verificar se é uma coleção (não pasta ou requisição)
        item = self.collection_model.itemFromIndex(index)
        if not hasattr(item, 'item_type') or item.item_type != "collection":
            QMessageBox.warning(self, "Erro", "Selecione uma coleção para exportar")
            return
        
        # Obter a coleção
        collection_id = item.data
        collection = self.storage.get_collection(collection_id)
        
        if not collection:
            QMessageBox.warning(self, "Erro", "Coleção não encontrada")
            return
        
        # Escolher o formato de exportação
        format_dialog = QDialog(self)
        format_dialog.setWindowTitle("Formato de Exportação")
        format_dialog.resize(300, 150)
        
        layout = QVBoxLayout()
        
        format_label = QLabel("Escolha o formato de exportação:")
        layout.addWidget(format_label)
        
        postman_radio = QRadioButton("Postman")
        postman_radio.setChecked(True)
        layout.addWidget(postman_radio)
        
        insomnia_radio = QRadioButton("Insomnia")
        layout.addWidget(insomnia_radio)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(format_dialog.accept)
        button_box.rejected.connect(format_dialog.reject)
        layout.addWidget(button_box)
        
        format_dialog.setLayout(layout)
        
        if format_dialog.exec_() != QDialog.Accepted:
            return
        
        # Determinar o formato selecionado
        export_format = "postman" if postman_radio.isChecked() else "insomnia"
        
        # Selecionar o arquivo de destino
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Exportar Coleção")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("Arquivos JSON (*.json)")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            
            # Exportar a coleção usando o conversor
            from src.utils.collection_converter import export_collection
            success, message = export_collection(collection, file_path, export_format, self.storage)
            
            if success:
                QMessageBox.information(self, "Exportação Concluída", message)
            else:
                QMessageBox.warning(self, "Erro na Exportação", message)

    def _rename_selected_item(self):
        """Renomeia o item selecionado na árvore de coleções"""
        index = self.collection_tree.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Renomear", "Selecione um item para renomear")
            return
        
        item = self.collection_model.itemFromIndex(index)
        if not hasattr(item, 'item_type'):
            return
        
        if item.item_type == "collection":
            self._rename_collection(item.data)
        elif item.item_type == "folder":
            self._rename_folder(item.data)
        elif item.item_type == "request":
            self._rename_request(item.data)
    
    def _delete_selected_item(self):
        """Exclui o item selecionado na árvore de coleções"""
        index = self.collection_tree.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Excluir", "Selecione um item para excluir")
            return
        
        item = self.collection_model.itemFromIndex(index)
        if not hasattr(item, 'item_type'):
            return
        
        if item.item_type == "collection":
            self._delete_collection(item.data)
        elif item.item_type == "folder":
            self._delete_folder(item.data)
        elif item.item_type == "request":
            self._delete_request(item.data)
    
    def _clear_history(self):
        """Limpa o histórico de requisições"""
        # Confirmar a ação com o usuário
        reply = QMessageBox.question(
            self,
            "Limpar Histórico",
            "Deseja realmente limpar todo o histórico de requisições?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Limpar o histórico
        self.storage.clear_history()
        
        # Atualizar a árvore de coleções
        self.collection_model.load_collections()
        
        # Exibir mensagem de sucesso
        self.status_bar.showMessage("Histórico de requisições limpo com sucesso", 3000)

    def _show_about_dialog(self):
        """Mostra o diálogo Sobre"""
        dialog = AboutDialog(self)
        dialog.exec_() 