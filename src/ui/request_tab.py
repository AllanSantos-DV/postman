"""
Componente para a guia de requisição
"""

import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QTabWidget, QTextEdit, 
    QPushButton, QLabel, QSplitter, QToolBar,
    QAction, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QPlainTextEdit, QMenu,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont

from src.models.request import Request, Response
from src.core.http_client import HttpClient
from src.core.storage import Storage


class JsonHighlighter(QSyntaxHighlighter):
    """Realce de sintaxe para JSON"""
    
    def __init__(self, document):
        super().__init__(document)
        
        # Formatos para diferentes elementos
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#ce9178"))
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#b5cea8"))
        
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#9cdcfe"))
        
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#569cd6"))
        
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#569cd6"))
        
        self.brackets_format = QTextCharFormat()
        self.brackets_format.setForeground(QColor("#d4d4d4"))
    
    def highlightBlock(self, text):
        """Aplica o realce de sintaxe a um bloco de texto"""
        # Implementação simplificada de realce de sintaxe JSON
        state = 0  # 0: normal, 1: within string
        i = 0
        length = len(text)
        
        while i < length:
            if state == 0:  # Normal state
                if text[i] == '"':
                    start = i
                    i += 1
                    state = 1  # Within string
                    
                    # Verificar se é uma chave
                    is_key = False
                    j = i
                    while j < length:
                        if text[j] == '"':
                            j += 1
                            while j < length and text[j].isspace():
                                j += 1
                            if j < length and text[j] == ':':
                                is_key = True
                            break
                        j += 1
                    
                    continue
                
                elif text[i].isdigit() or (text[i] == '-' and i + 1 < length and text[i + 1].isdigit()):
                    start = i
                    while i < length and (text[i].isdigit() or text[i] == '.' or text[i] == 'e' or text[i] == 'E' or text[i] == '-' or text[i] == '+'):
                        i += 1
                    self.setFormat(start, i - start, self.number_format)
                    continue
                
                elif text[i:i+4] == "true" or text[i:i+5] == "false":
                    length_word = 4 if text[i:i+4] == "true" else 5
                    self.setFormat(i, length_word, self.boolean_format)
                    i += length_word
                    continue
                
                elif text[i:i+4] == "null":
                    self.setFormat(i, 4, self.null_format)
                    i += 4
                    continue
                
                elif text[i] in "{}[],:":
                    self.setFormat(i, 1, self.brackets_format)
            
            elif state == 1:  # Within string
                if text[i] == '\\' and i + 1 < length:
                    i += 2  # Skip escape character and the next one
                    continue
                
                if text[i] == '"':
                    state = 0  # Back to normal state
                    self.setFormat(start, i - start + 1, self.string_format)
            
            i += 1


class RequestTab(QWidget):
    """
    Componente para a guia de requisição
    """
    # Sinal emitido quando uma requisição é salva
    request_saved = pyqtSignal(Request)
    # Sinal para solicitar salvar na coleção
    save_to_collection = pyqtSignal()
    
    def __init__(self, request: Request, storage: Storage):
        super().__init__()
        
        self.request = request
        self.storage = storage
        self.response = None
        self._has_unsaved_changes = False
        
        # Criar a interface
        self._create_ui()
        
        # Preencher os campos com os dados da requisição
        self._populate_fields()
    
    def _create_ui(self):
        """Cria a interface do usuário"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Botão para enviar a requisição
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self._send_request)
        toolbar.addWidget(self.send_button)
        
        # Botão para salvar a requisição
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_request)
        toolbar.addWidget(self.save_button)
        
        # Botão para salvar na coleção
        self.save_to_collection_button = QPushButton("Salvar na Coleção")
        self.save_to_collection_button.clicked.connect(self._on_save_to_collection)
        toolbar.addWidget(self.save_to_collection_button)
        
        main_layout.addWidget(toolbar)
        
        # Área principal (dividida em duas partes: requisição e resposta)
        main_splitter = QSplitter(Qt.Vertical)
        
        # === Área da Requisição ===
        request_widget = QWidget()
        request_layout = QVBoxLayout(request_widget)
        
        # URL e método
        url_layout = QHBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        self.method_combo.currentTextChanged.connect(self._on_field_changed)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://api.example.com/endpoint")
        self.url_edit.textChanged.connect(self._on_field_changed)
        
        url_layout.addWidget(self.method_combo)
        url_layout.addWidget(self.url_edit, 1)
        
        request_layout.addLayout(url_layout)
        
        # Nome da requisição
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome:"))
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nome da requisição")
        self.name_edit.textChanged.connect(self._on_field_changed)
        
        name_layout.addWidget(self.name_edit, 1)
        request_layout.addLayout(name_layout)
        
        # Guias para parâmetros, cabeçalhos, corpo
        self.request_tabs = QTabWidget()
        
        # Guia de parâmetros
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        
        self.params_table = QTableWidget(0, 3)
        self.params_table.setHorizontalHeaderLabels(["Chave", "Valor", ""])
        self.params_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.params_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.params_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.params_table.horizontalHeader().setDefaultSectionSize(30)
        self.params_table.itemChanged.connect(self._on_table_changed)
        
        params_layout.addWidget(self.params_table)
        
        # Botão para adicionar parâmetro
        add_param_button = QPushButton("Adicionar Parâmetro")
        add_param_button.clicked.connect(lambda: self._add_table_row(self.params_table))
        params_layout.addWidget(add_param_button)
        
        self.request_tabs.addTab(params_widget, "Parâmetros")
        
        # Guia de cabeçalhos
        headers_widget = QWidget()
        headers_layout = QVBoxLayout(headers_widget)
        
        self.headers_table = QTableWidget(0, 3)
        self.headers_table.setHorizontalHeaderLabels(["Chave", "Valor", ""])
        self.headers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.headers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.headers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.headers_table.horizontalHeader().setDefaultSectionSize(30)
        self.headers_table.itemChanged.connect(self._on_table_changed)
        
        headers_layout.addWidget(self.headers_table)
        
        # Botão para adicionar cabeçalho
        add_header_button = QPushButton("Adicionar Cabeçalho")
        add_header_button.clicked.connect(lambda: self._add_table_row(self.headers_table))
        headers_layout.addWidget(add_header_button)
        
        self.request_tabs.addTab(headers_widget, "Cabeçalhos")
        
        # Guia de corpo
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        
        body_type_layout = QHBoxLayout()
        body_type_layout.addWidget(QLabel("Tipo:"))
        
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(["none", "raw", "form-data", "x-www-form-urlencoded"])
        self.body_type_combo.currentTextChanged.connect(self._on_body_type_changed)
        
        body_type_layout.addWidget(self.body_type_combo)
        body_type_layout.addStretch()
        
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["application/json", "text/plain", "application/xml", "text/html"])
        self.content_type_combo.setVisible(False)
        self.content_type_combo.currentTextChanged.connect(self._on_content_type_changed)
        
        body_type_layout.addWidget(QLabel("Content-Type:"))
        body_type_layout.addWidget(self.content_type_combo)
        
        body_layout.addLayout(body_type_layout)
        
        # Editor de corpo
        editor_layout = QVBoxLayout()
        
        # Barra de ferramentas do editor
        editor_toolbar = QHBoxLayout()
        
        # Botão para formatar JSON
        self.format_json_button = QPushButton("Formatar JSON")
        self.format_json_button.clicked.connect(self._format_json)
        self.format_json_button.setVisible(False)
        editor_toolbar.addWidget(self.format_json_button)
        
        editor_toolbar.addStretch()
        editor_layout.addLayout(editor_toolbar)
        
        # Editor de texto
        self.body_editor = QPlainTextEdit()
        self.body_editor.setPlaceholderText("Corpo da requisição")
        self.body_editor.textChanged.connect(self._on_field_changed)
        
        # Realce de sintaxe para JSON
        self.json_highlighter = JsonHighlighter(self.body_editor.document())
        
        editor_layout.addWidget(self.body_editor)
        body_layout.addLayout(editor_layout)
        
        # Tabela para form-data/url-encoded
        self.body_table = QTableWidget(0, 3)
        self.body_table.setHorizontalHeaderLabels(["Chave", "Valor", ""])
        self.body_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.body_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.body_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.body_table.horizontalHeader().setDefaultSectionSize(30)
        self.body_table.setVisible(False)
        self.body_table.itemChanged.connect(self._on_table_changed)
        
        body_layout.addWidget(self.body_table)
        
        # Botão para adicionar item de formulário
        self.add_form_button = QPushButton("Adicionar Item")
        self.add_form_button.clicked.connect(lambda: self._add_table_row(self.body_table))
        self.add_form_button.setVisible(False)
        
        body_layout.addWidget(self.add_form_button)
        
        self.request_tabs.addTab(body_widget, "Corpo")
        
        request_layout.addWidget(self.request_tabs)
        
        # === Área da Resposta ===
        response_widget = QWidget()
        response_layout = QVBoxLayout(response_widget)
        
        # Informações da resposta
        self.response_info = QLabel("Nenhuma resposta")
        response_layout.addWidget(self.response_info)
        
        # Guias para diferentes visualizações da resposta
        self.response_tabs = QTabWidget()
        
        # Guia para visualização da resposta como texto
        self.response_text = QPlainTextEdit()
        self.response_text.setReadOnly(True)
        self.response_tabs.addTab(self.response_text, "Resposta")
        
        # Guia para cabeçalhos da resposta
        self.response_headers = QTableWidget(0, 2)
        self.response_headers.setHorizontalHeaderLabels(["Chave", "Valor"])
        self.response_headers.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.response_headers.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.response_tabs.addTab(self.response_headers, "Cabeçalhos")
        
        response_layout.addWidget(self.response_tabs)
        
        # Adicionar os componentes ao splitter principal
        main_splitter.addWidget(request_widget)
        main_splitter.addWidget(response_widget)
        
        # Configurar o tamanho relativo dos painéis (40% requisição, 60% resposta)
        main_splitter.setSizes([400, 600])
        
        main_layout.addWidget(main_splitter)
    
    def _populate_fields(self):
        """Preenche os campos com os dados da requisição"""
        # Definir método e URL
        index = self.method_combo.findText(self.request.method.upper())
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        self.url_edit.setText(self.request.url)
        self.name_edit.setText(self.request.name)
        
        # Parâmetros
        for key, value in self.request.params.items():
            row = self.params_table.rowCount()
            self._add_table_row(self.params_table)
            self.params_table.item(row, 0).setText(key)
            self.params_table.item(row, 1).setText(value)
        
        # Cabeçalhos
        for key, value in self.request.headers.items():
            row = self.headers_table.rowCount()
            self._add_table_row(self.headers_table)
            self.headers_table.item(row, 0).setText(key)
            self.headers_table.item(row, 1).setText(value)
        
        # Corpo
        if self.request.body:
            if isinstance(self.request.body, dict):
                # Se for um dicionário, exibir como JSON
                self.body_type_combo.setCurrentText("raw")
                self.content_type_combo.setCurrentText("application/json")
                self.body_editor.setPlainText(json.dumps(self.request.body, indent=2))
                self.format_json_button.setVisible(True)
            elif isinstance(self.request.body, str):
                # Se for uma string, exibir como texto
                self.body_type_combo.setCurrentText("raw")
                self.content_type_combo.setCurrentText("text/plain")
                self.body_editor.setPlainText(self.request.body)
                
                # Verificar se parece ser JSON
                try:
                    json.loads(self.request.body)
                    # Se passou no parse, é JSON
                    self.content_type_combo.setCurrentText("application/json")
                    self.format_json_button.setVisible(True)
                except (ValueError, TypeError):
                    # Não é JSON, manter como texto plano
                    pass
        
        # Limpar o flag de alterações não salvas
        self._has_unsaved_changes = False
    
    def _add_table_row(self, table):
        """Adiciona uma nova linha a uma tabela"""
        row = table.rowCount()
        table.insertRow(row)
        
        # Coluna para a chave
        key_item = QTableWidgetItem("")
        table.setItem(row, 0, key_item)
        
        # Coluna para o valor
        value_item = QTableWidgetItem("")
        table.setItem(row, 1, value_item)
        
        # Coluna para o botão de exclusão
        delete_button = QPushButton("X")
        delete_button.clicked.connect(lambda: self._remove_table_row(table, row))
        table.setCellWidget(row, 2, delete_button)
    
    def _remove_table_row(self, table, row):
        """Remove uma linha da tabela"""
        table.removeRow(row)
        self._on_field_changed()
    
    def _on_body_type_changed(self, body_type):
        """Atualiza a interface quando o tipo de corpo muda"""
        # Ocultar todos os componentes específicos de tipo de corpo
        self.body_editor.setVisible(False)
        self.body_table.setVisible(False)
        self.add_form_button.setVisible(False)
        self.content_type_combo.setVisible(False)
        self.format_json_button.setVisible(False)
        
        if body_type == "none":
            # Nenhum corpo
            pass
        
        elif body_type == "raw":
            # Corpo como texto
            self.body_editor.setVisible(True)
            self.content_type_combo.setVisible(True)
            
            # Verificar se o tipo de conteúdo é JSON para mostrar o botão de formatação
            if self.content_type_combo.currentText() == "application/json":
                self.format_json_button.setVisible(True)
        
        elif body_type == "form-data" or body_type == "x-www-form-urlencoded":
            # Corpo como formulário
            self.body_table.setVisible(True)
            self.add_form_button.setVisible(True)
        
        self._on_field_changed()
    
    def _on_field_changed(self):
        """Chamado quando um campo é alterado"""
        self._has_unsaved_changes = True
    
    def _on_table_changed(self, item):
        """Chamado quando uma tabela é alterada"""
        self._has_unsaved_changes = True
    
    def has_unsaved_changes(self) -> bool:
        """Verifica se há alterações não salvas"""
        return self._has_unsaved_changes
    
    def _update_request_from_fields(self):
        """Atualiza o objeto de requisição com os valores dos campos"""
        # Atualizar dados básicos
        self.request.method = self.method_combo.currentText()
        self.request.url = self.url_edit.text()
        self.request.name = self.name_edit.text()
        
        # Atualizar parâmetros
        params = {}
        for row in range(self.params_table.rowCount()):
            key_item = self.params_table.item(row, 0)
            value_item = self.params_table.item(row, 1)
            
            if key_item and key_item.text() and value_item:
                params[key_item.text()] = value_item.text()
        
        self.request.params = params
        
        # Atualizar cabeçalhos
        headers = {}
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            
            if key_item and key_item.text() and value_item:
                headers[key_item.text()] = value_item.text()
        
        self.request.headers = headers
        
        # Atualizar corpo
        body_type = self.body_type_combo.currentText()
        
        if body_type == "none":
            self.request.body = None
        
        elif body_type == "raw":
            # Adicionar o cabeçalho Content-Type
            content_type = self.content_type_combo.currentText()
            if content_type:
                self.request.headers["Content-Type"] = content_type
            
            # Se for JSON, tentar converter para objeto
            body_text = self.body_editor.toPlainText()
            
            if content_type == "application/json" and body_text:
                try:
                    self.request.body = json.loads(body_text)
                except json.JSONDecodeError:
                    # Se falhar, manter como texto
                    self.request.body = body_text
            else:
                self.request.body = body_text
        
        elif body_type == "form-data" or body_type == "x-www-form-urlencoded":
            # Criar um dicionário com os dados do formulário
            form_data = {}
            
            for row in range(self.body_table.rowCount()):
                key_item = self.body_table.item(row, 0)
                value_item = self.body_table.item(row, 1)
                
                if key_item and key_item.text() and value_item:
                    form_data[key_item.text()] = value_item.text()
            
            self.request.body = form_data
            
            # Definir o cabeçalho adequado
            if body_type == "form-data":
                self.request.headers["Content-Type"] = "multipart/form-data"
            else:
                self.request.headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    def save_request(self):
        """Salva a requisição"""
        self._update_request_from_fields()
        
        # Salvar no armazenamento
        self.storage.save_request(self.request)
        
        # Limpar flag de alterações não salvas
        self._has_unsaved_changes = False
        
        # Emitir sinal
        self.request_saved.emit(self.request)
    
    def _on_save_to_collection(self):
        """Emite sinal para salvar na coleção"""
        # Primeiro salvamos a requisição
        self.save_request()
        
        # Emitir sinal para a janela principal
        self.save_to_collection.emit()
    
    def _send_request(self):
        """Envia a requisição"""
        # Atualizar os dados da requisição
        self._update_request_from_fields()
        
        # Enviar a requisição
        response, error = HttpClient.send_request(self.request)
        self.response = response
        
        # Adicionar ao histórico
        self.storage.add_to_history(self.request)
        
        # Exibir a resposta
        self._display_response(response, error)
    
    def _display_response(self, response: Response, error: str = None):
        """Exibe a resposta na interface"""
        if error:
            # Exibir mensagem de erro
            self.response_info.setText(f"Erro: {error}")
            self.response_text.setPlainText("")
            self.response_headers.setRowCount(0)
            return
        
        # Exibir informações da resposta
        self.response_info.setText(
            f"Status: {response.status_code} | Tempo: {response.elapsed_time:.2f}s | Tamanho: {len(response.content)} bytes"
        )
        
        # Exibir o conteúdo da resposta
        try:
            if response.is_json:
                # Formatar o JSON
                json_data = response.get_content_as_json()
                self.response_text.setPlainText(json.dumps(json_data, indent=2))
            else:
                # Exibir como texto
                self.response_text.setPlainText(response.get_content_as_text())
        except Exception as e:
            # Em caso de erro, exibir o conteúdo bruto
            self.response_text.setPlainText(f"Erro ao exibir resposta: {str(e)}\n\nConteúdo bruto:\n{response.content}")
        
        # Exibir os cabeçalhos da resposta
        self.response_headers.setRowCount(0)
        for key, value in response.headers.items():
            row = self.response_headers.rowCount()
            self.response_headers.insertRow(row)
            self.response_headers.setItem(row, 0, QTableWidgetItem(key))
            self.response_headers.setItem(row, 1, QTableWidgetItem(value))
    
    def _on_content_type_changed(self, content_type):
        """Atualiza a interface quando o tipo de conteúdo muda"""
        # Mostrar ou esconder o botão de formatação JSON
        is_json = content_type == "application/json"
        self.format_json_button.setVisible(is_json)
        
        if is_json:
            # Verificar o texto do JSON para determinar o texto do botão
            text = self.body_editor.toPlainText().strip()
            if text:
                try:
                    # Verificar se já está formatado (tem quebras de linha)
                    is_formatted = '\n' in text
                    
                    if is_formatted:
                        self.format_json_button.setText("Minificar JSON")
                    else:
                        self.format_json_button.setText("Formatar JSON")
                except Exception:
                    # Em caso de erro, usar o texto padrão
                    self.format_json_button.setText("Formatar JSON")
            else:
                # Se não há texto, usar o texto padrão
                self.format_json_button.setText("Formatar JSON")
    
    def _format_json(self):
        """Formata o JSON no editor de corpo"""
        text = self.body_editor.toPlainText().strip()
        if not text:
            return
        
        try:
            # Carregar o JSON
            parsed_json = json.loads(text)
            
            # Verificar se já está formatado (tem quebras de linha)
            is_formatted = '\n' in text
            
            if is_formatted:
                # Se já está formatado, minificar
                formatted_json = json.dumps(parsed_json, separators=(',', ':'))
                message = "JSON minificado com sucesso!"
            else:
                # Se está minificado, formatar
                formatted_json = json.dumps(parsed_json, indent=2)
                message = "JSON formatado com sucesso!"
            
            # Atualizar o editor
            self.body_editor.setPlainText(formatted_json)
            
            # Atualizar o texto do botão
            if is_formatted:
                self.format_json_button.setText("Formatar JSON")
            else:
                self.format_json_button.setText("Minificar JSON")
            
            # Mostrar mensagem discreta na barra de status se disponível
            parent = self.window()
            if hasattr(parent, 'statusBar'):
                parent.statusBar().showMessage(message, 3000)
            
        except json.JSONDecodeError as e:
            # Informar ao usuário sobre o erro
            QMessageBox.warning(
                self,
                "Erro de formatação",
                f"Não foi possível processar o JSON. Erro: {str(e)}",
                QMessageBox.Ok
            ) 