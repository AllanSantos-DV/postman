"""
Dialog para gerenciamento de ambientes e variáveis
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QDialogButtonBox, QTabWidget,
    QWidget, QFormLayout, QTextEdit, QListWidget, QListWidgetItem,
    QSplitter, QInputDialog, QToolBar, QAction, QFileDialog
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
        self.setMinimumSize(800, 600)
        
        # Herdar estilo da janela principal
        if parent and parent.styleSheet():
            self.setStyleSheet(parent.styleSheet())
        
        self._create_ui()
        self._load_environments()
    
    def _create_ui(self):
        """Cria a interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo (lista de ambientes)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lista de ambientes
        self.environments_list = QListWidget()
        self.environments_list.itemSelectionChanged.connect(self._on_environment_selected)
        self.environments_list.setToolTip("Lista de ambientes disponíveis")
        left_layout.addWidget(self.environments_list)
        
        # Barra de ferramentas para a lista de ambientes
        env_toolbar = QToolBar()
        
        self.add_env_action = QAction("Adicionar", self)
        self.add_env_action.triggered.connect(self._add_environment)
        self.add_env_action.setToolTip("Adicionar um novo ambiente")
        env_toolbar.addAction(self.add_env_action)
        
        self.rename_env_action = QAction("Renomear", self)
        self.rename_env_action.triggered.connect(self._rename_environment)
        self.rename_env_action.setToolTip("Renomear o ambiente selecionado")
        env_toolbar.addAction(self.rename_env_action)
        
        self.delete_env_action = QAction("Excluir", self)
        self.delete_env_action.triggered.connect(self._delete_environment)
        self.delete_env_action.setToolTip("Excluir o ambiente selecionado")
        env_toolbar.addAction(self.delete_env_action)
        
        left_layout.addWidget(env_toolbar)
        
        # Painel direito (variáveis do ambiente)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Nome do ambiente atual
        self.env_name_label = QLabel("Selecione um ambiente")
        font = self.env_name_label.font()
        font.setBold(True)
        self.env_name_label.setFont(font)
        right_layout.addWidget(self.env_name_label)
        
        # Tabela de variáveis
        self.variables_table = QTableWidget(0, 3)
        self.variables_table.setHorizontalHeaderLabels(["Nome", "Valor", ""])
        self.variables_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.variables_table.setColumnWidth(2, 30)
        self.variables_table.verticalHeader().setVisible(False)
        self.variables_table.setToolTip("Variáveis do ambiente selecionado")
        right_layout.addWidget(self.variables_table)
        
        # Adicionar botão para nova variável
        variable_toolbar = QToolBar()
        
        self.add_var_action = QAction("Adicionar Variável", self)
        self.add_var_action.triggered.connect(self._add_variable)
        self.add_var_action.setToolTip("Adicionar uma nova variável ao ambiente atual")
        variable_toolbar.addAction(self.add_var_action)
        
        self.import_vars_action = QAction("Importar", self)
        self.import_vars_action.triggered.connect(self._import_variables)
        self.import_vars_action.setToolTip("Importar variáveis de um arquivo .env ou JSON")
        variable_toolbar.addAction(self.import_vars_action)
        
        self.export_vars_action = QAction("Exportar", self)
        self.export_vars_action.triggered.connect(self._export_variables)
        self.export_vars_action.setToolTip("Exportar variáveis para um arquivo .env ou JSON")
        variable_toolbar.addAction(self.export_vars_action)
        
        right_layout.addWidget(variable_toolbar)
        
        # Adicionar os painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Definir as proporções do splitter (30% esquerda, 70% direita)
        splitter.setSizes([240, 560])
        
        layout.addWidget(splitter)
        
        # Botões de ação
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
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
            self.env_name_label.setText("Selecione um ambiente")
            self.add_var_action.setEnabled(False)
            self.import_vars_action.setEnabled(False)
            self.export_vars_action.setEnabled(False)
            return
        
        env_id = current.data(Qt.UserRole)
        self.current_environment = self.storage.get_environment(env_id)
        
        self.env_name_label.setText(self.current_environment.name)
        self.add_var_action.setEnabled(True)
        self.import_vars_action.setEnabled(True)
        self.export_vars_action.setEnabled(True)
        
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
    
    def _delete_variable(self, row):
        """Exclui uma variável do ambiente atual"""
        if not self.current_environment:
            return
        
        key_item = self.variables_table.item(row, 0)
        if not key_item:
            return
        
        key = key_item.text()
        
        # Confirmar a exclusão
        reply = QMessageBox.question(
            self,
            "Excluir Variável",
            f"Tem certeza que deseja excluir a variável '{key}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Remover a variável do ambiente
        del self.current_environment.variables[key]
        
        # Atualizar a tabela
        self.variables_table.removeRow(row)
        
        # Salvar o ambiente
        self.storage.save_environment(self.current_environment)
    
    def _import_variables(self):
        """Importa variáveis de um arquivo .env ou JSON"""
        if not self.current_environment:
            QMessageBox.warning(self, "Importar Variáveis", "Selecione um ambiente para importar variáveis.")
            return
        
        # Selecionar o arquivo para importar
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Variáveis",
            "",
            "Arquivos de Variáveis (*.env *.json);;Todos os Arquivos (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Tentar carregar as variáveis do arquivo
            variables = {}
            
            # Verificar o tipo de arquivo
            if file_path.lower().endswith('.json'):
                # Importar de JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    
                    # Verificar se o JSON tem um formato esperado
                    if isinstance(data, dict):
                        variables = data
                    elif isinstance(data, list) and all(isinstance(item, dict) and 'key' in item and 'value' in item for item in data):
                        # Formato com lista de objetos {key: 'nome', value: 'valor'}
                        variables = {item['key']: item['value'] for item in data}
                    else:
                        raise ValueError("Formato JSON não reconhecido.")
            else:
                # Importar de .env
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        
                        # Ignorar comentários e linhas vazias
                        if not line or line.startswith('#'):
                            continue
                        
                        # Extrair chave e valor
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remover aspas se necessário
                            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            
                            variables[key] = value
            
            # Adicionar as variáveis ao ambiente atual
            for key, value in variables.items():
                self.current_environment.variables[key] = value
            
            # Atualizar a tabela
            self._load_variables()
            
            # Salvar o ambiente
            self.storage.save_environment(self.current_environment)
            
            # Mostrar mensagem de sucesso
            QMessageBox.information(
                self,
                "Importar Variáveis",
                f"Foram importadas {len(variables)} variáveis com sucesso."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro na Importação",
                f"Ocorreu um erro ao importar as variáveis: {str(e)}"
            )
    
    def _export_variables(self):
        """Exporta variáveis para um arquivo .env ou JSON"""
        if not self.current_environment:
            QMessageBox.warning(self, "Exportar Variáveis", "Selecione um ambiente para exportar variáveis.")
            return
        
        # Verificar se existem variáveis para exportar
        if not self.current_environment.variables:
            QMessageBox.warning(self, "Exportar Variáveis", "Não há variáveis para exportar.")
            return
        
        # Selecionar o arquivo para exportar
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar Variáveis",
            f"{self.current_environment.name}_variables",
            "Arquivo .env (*.env);;Arquivo JSON (*.json);;Todos os Arquivos (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Determinar o formato de acordo com o filtro selecionado ou extensão
            is_json = selected_filter.startswith("Arquivo JSON") or file_path.lower().endswith('.json')
            
            if is_json:
                # Garantir que o arquivo tenha a extensão .json
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                
                # Exportar para JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(self.current_environment.variables, f, indent=2)
            else:
                # Garantir que o arquivo tenha a extensão .env
                if not file_path.lower().endswith('.env'):
                    file_path += '.env'
                
                # Exportar para .env
                with open(file_path, 'w', encoding='utf-8') as f:
                    for key, value in self.current_environment.variables.items():
                        # Adicionar aspas se o valor contiver espaços
                        if ' ' in value:
                            value = f'"{value}"'
                        f.write(f"{key}={value}\n")
            
            # Mostrar mensagem de sucesso
            QMessageBox.information(
                self,
                "Exportar Variáveis",
                f"As variáveis foram exportadas com sucesso para {file_path}."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro na Exportação",
                f"Ocorreu um erro ao exportar as variáveis: {str(e)}"
            )
    
    def accept(self):
        """Manipula o botão OK"""
        super().accept()
    
    def reject(self):
        """Manipula o botão Cancelar"""
        super().reject() 