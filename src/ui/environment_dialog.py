"""
Dialog para gerenciamento de ambientes e variáveis
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QDialogButtonBox, QTabWidget,
    QWidget, QFormLayout, QTextEdit, QListWidget, QListWidgetItem,
    QSplitter, QInputDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from src.models.environment import Environment
from src.core.storage import Storage


class EnvironmentDialog(QDialog):
    """
    Dialog para gerenciamento de ambientes e variáveis
    """
    
    environment_updated = pyqtSignal()
    
    def __init__(self, storage: Storage, parent=None):
        super().__init__(parent)
        
        self.storage = storage
        self.current_environment = None
        
        self.setWindowTitle("Gerenciar Ambientes")
        self.setMinimumSize(800, 500)
        
        self._create_ui()
        self._load_environments()
    
    def _create_ui(self):
        """Cria a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel da lista de ambientes
        environments_panel = QWidget()
        env_layout = QVBoxLayout(environments_panel)
        
        env_label = QLabel("Ambientes:")
        env_layout.addWidget(env_label)
        
        # Lista de ambientes
        self.environments_list = QListWidget()
        self.environments_list.currentItemChanged.connect(self._on_environment_selected)
        env_layout.addWidget(self.environments_list)
        
        # Botões para gerenciar ambientes
        env_buttons_layout = QHBoxLayout()
        
        self.add_env_button = QPushButton("Adicionar")
        self.add_env_button.clicked.connect(self._add_environment)
        env_buttons_layout.addWidget(self.add_env_button)
        
        self.edit_env_button = QPushButton("Renomear")
        self.edit_env_button.clicked.connect(self._rename_environment)
        self.edit_env_button.setEnabled(False)
        env_buttons_layout.addWidget(self.edit_env_button)
        
        self.delete_env_button = QPushButton("Excluir")
        self.delete_env_button.clicked.connect(self._delete_environment)
        self.delete_env_button.setEnabled(False)
        env_buttons_layout.addWidget(self.delete_env_button)
        
        env_layout.addLayout(env_buttons_layout)
        
        # Painel de variáveis
        variables_panel = QWidget()
        var_layout = QVBoxLayout(variables_panel)
        
        var_label = QLabel("Variáveis:")
        var_layout.addWidget(var_label)
        
        # Tabela de variáveis
        self.variables_table = QTableWidget(0, 3)
        self.variables_table.setHorizontalHeaderLabels(["Nome", "Valor", ""])
        self.variables_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.variables_table.horizontalHeader().setDefaultSectionSize(30)
        var_layout.addWidget(self.variables_table)
        
        # Botão para adicionar variável
        add_var_layout = QHBoxLayout()
        self.add_var_button = QPushButton("Adicionar Variável")
        self.add_var_button.clicked.connect(self._add_variable)
        self.add_var_button.setEnabled(False)
        add_var_layout.addWidget(self.add_var_button)
        add_var_layout.addStretch()
        var_layout.addLayout(add_var_layout)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(environments_panel)
        splitter.addWidget(variables_panel)
        
        # Configurar proporções do splitter
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        # Botões de ação
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
    
    def _load_environments(self):
        """Carrega a lista de ambientes do armazenamento"""
        self.environments_list.clear()
        
        environments = self.storage.get_all_environments()
        
        for env in environments:
            item = QListWidgetItem(env.name)
            item.setData(Qt.UserRole, env.id)
            self.environments_list.addItem(item)
    
    def _on_environment_selected(self, current, previous):
        """Manipula a seleção de um ambiente na lista"""
        self.variables_table.setRowCount(0)
        
        if current is None:
            self.current_environment = None
            self.edit_env_button.setEnabled(False)
            self.delete_env_button.setEnabled(False)
            self.add_var_button.setEnabled(False)
            return
        
        env_id = current.data(Qt.UserRole)
        self.current_environment = self.storage.get_environment(env_id)
        
        self.edit_env_button.setEnabled(True)
        self.delete_env_button.setEnabled(True)
        self.add_var_button.setEnabled(True)
        
        # Carregar variáveis
        for name, value in self.current_environment.variables.items():
            self._add_variable_row(name, value)
    
    def _add_environment(self):
        """Adiciona um novo ambiente"""
        name, ok = QInputDialog.getText(
            self, "Novo Ambiente", "Nome do ambiente:", QLineEdit.Normal, ""
        )
        
        if ok and name:
            # Verificar se já existe um ambiente com esse nome
            environments = self.storage.get_all_environments()
            if any(env.name == name for env in environments):
                QMessageBox.warning(
                    self, "Erro", "Já existe um ambiente com esse nome.", QMessageBox.Ok
                )
                return
            
            # Criar e salvar o novo ambiente
            environment = Environment(name=name)
            self.storage.save_environment(environment)
            
            # Atualizar a lista
            self._load_environments()
            
            # Selecionar o novo ambiente
            for i in range(self.environments_list.count()):
                item = self.environments_list.item(i)
                if item.text() == name:
                    self.environments_list.setCurrentItem(item)
                    break
            
            self.environment_updated.emit()
    
    def _rename_environment(self):
        """Renomeia o ambiente selecionado"""
        if not self.current_environment:
            return
        
        name, ok = QInputDialog.getText(
            self, "Renomear Ambiente", "Novo nome:", 
            QLineEdit.Normal, self.current_environment.name
        )
        
        if ok and name and name != self.current_environment.name:
            # Verificar se já existe um ambiente com esse nome
            environments = self.storage.get_all_environments()
            if any(env.name == name and env.id != self.current_environment.id for env in environments):
                QMessageBox.warning(
                    self, "Erro", "Já existe um ambiente com esse nome.", QMessageBox.Ok
                )
                return
            
            # Atualizar e salvar o ambiente
            self.current_environment.name = name
            self.storage.save_environment(self.current_environment)
            
            # Atualizar a lista
            self._load_environments()
            
            # Reselecionar o ambiente
            for i in range(self.environments_list.count()):
                item = self.environments_list.item(i)
                if item.data(Qt.UserRole) == self.current_environment.id:
                    self.environments_list.setCurrentItem(item)
                    break
            
            self.environment_updated.emit()
    
    def _delete_environment(self):
        """Exclui o ambiente selecionado"""
        if not self.current_environment:
            return
        
        result = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o ambiente '{self.current_environment.name}'?\n"
            "Essa ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Excluir o ambiente
            self.storage.delete_environment(self.current_environment.id)
            
            # Atualizar a lista
            self._load_environments()
            
            self.current_environment = None
            self.variables_table.setRowCount(0)
            
            self.environment_updated.emit()
    
    def _add_variable(self):
        """Adiciona uma variável ao ambiente atual"""
        if not self.current_environment:
            return
        
        self._add_variable_row("", "")
    
    def _add_variable_row(self, name="", value=""):
        """Adiciona uma linha à tabela de variáveis"""
        row = self.variables_table.rowCount()
        self.variables_table.insertRow(row)
        
        # Nome da variável
        name_item = QTableWidgetItem(name)
        self.variables_table.setItem(row, 0, name_item)
        
        # Valor da variável
        value_item = QTableWidgetItem(value)
        self.variables_table.setItem(row, 1, value_item)
        
        # Botão para remover
        delete_button = QPushButton("×")
        delete_button.setFixedSize(24, 24)
        delete_button.clicked.connect(lambda _, r=row: self._remove_variable_row(r))
        self.variables_table.setCellWidget(row, 2, delete_button)
        
        # Se for uma nova variável, ativar a célula para edição
        if not name:
            self.variables_table.setCurrentCell(row, 0)
            self.variables_table.editItem(name_item)
        
        # Conectar evento de edição
        self.variables_table.itemChanged.connect(self._on_variable_changed)
    
    def _remove_variable_row(self, row):
        """Remove uma linha da tabela de variáveis"""
        if row < 0 or row >= self.variables_table.rowCount():
            return
        
        # Desconectar o evento para evitar múltiplas chamadas
        self.variables_table.itemChanged.disconnect(self._on_variable_changed)
        
        # Obter o nome da variável a ser removida
        name_item = self.variables_table.item(row, 0)
        if name_item and name_item.text() and self.current_environment:
            var_name = name_item.text()
            if var_name in self.current_environment.variables:
                del self.current_environment.variables[var_name]
                self.storage.save_environment(self.current_environment)
                self.environment_updated.emit()
        
        # Remover a linha
        self.variables_table.removeRow(row)
        
        # Reconectar o evento
        self.variables_table.itemChanged.connect(self._on_variable_changed)
    
    def _on_variable_changed(self, item):
        """Manipula a alteração de uma variável na tabela"""
        if not self.current_environment:
            return
        
        # Obter a linha e coluna do item alterado
        row = item.row()
        col = item.column()
        
        # Obter nome e valor da variável
        name_item = self.variables_table.item(row, 0)
        value_item = self.variables_table.item(row, 1)
        
        if not name_item or not value_item:
            return
        
        name = name_item.text().strip()
        value = value_item.text()
        
        # Ignorar se o nome estiver vazio
        if not name:
            return
        
        # Atualizar o ambiente
        self.current_environment.variables[name] = value
        self.storage.save_environment(self.current_environment)
        
        self.environment_updated.emit()
    
    def accept(self):
        """Manipula o botão OK"""
        super().accept()
    
    def reject(self):
        """Manipula o botão Cancelar"""
        super().reject() 