"""
Componente de autocompletar para variáveis de ambiente
"""

from PyQt5.QtWidgets import QCompleter, QLineEdit, QTextEdit, QPlainTextEdit
from PyQt5.QtCore import Qt, QStringListModel, pyqtSignal, QObject

from src.core.variable_processor import VariableProcessor


class VariableCompleter(QObject):
    """
    Classe para fornecer autocompletar de variáveis de ambiente em campos de texto.
    """
    
    # Sinal emitido quando uma variável é selecionada
    variable_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Lista de variáveis
        self.variables = []
        
        # Modelo para o completer
        self.model = QStringListModel()
        
        # Completer
        self.completer = QCompleter()
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchContains)
        
        self.completer.activated.connect(self._on_completion_selected)
        
        # Editor de texto atual
        self.current_widget = None
        
        # Posição atual no texto
        self.current_pos = 0
        
        # Estado do autocompletar
        self.completion_active = False
        
        # Tooltip para informar sobre o uso de variáveis
        self.variable_tooltip = "Digite {{ para acessar o autopreenchimento de variáveis"
    
    def set_variables(self, variables):
        """
        Define a lista de variáveis disponíveis para autocompletar.
        
        Args:
            variables (dict): Dicionário com as variáveis disponíveis
        """
        self.variables = list(variables.keys())
        self._update_model()
    
    def _update_model(self):
        """Atualiza o modelo com as variáveis disponíveis"""
        self.model.setStringList(self.variables)
    
    def _on_completion_selected(self, text):
        """
        Chamado quando uma variável é selecionada no completer.
        
        Args:
            text (str): O texto selecionado
        """
        try:
            if not self.current_widget or not self.completion_active:
                return
            
            # Obtém o texto atual
            if isinstance(self.current_widget, QLineEdit):
                current_text = self.current_widget.text()
            elif isinstance(self.current_widget, (QTextEdit, QPlainTextEdit)):
                current_text = self.current_widget.toPlainText()
            else:
                return
            
            # Encontra a posição do início da variável
            cursor_pos = self.current_pos
            start_pos = cursor_pos
            
            # Procura pelo início da variável ({{)
            found_opening = False
            while start_pos > 0:
                if start_pos >= 2 and current_text[start_pos-2:start_pos] == "{{":
                    found_opening = True
                    break
                start_pos -= 1
            
            # Se não encontramos {{ antes, usamos a posição atual
            if not found_opening:
                start_pos = cursor_pos
            
            # Insere a variável no formato correto
            if isinstance(self.current_widget, QLineEdit):
                # Remove a parte do texto onde estava digitando
                prefix = "" if found_opening else "{{"
                # Adiciona apenas a variável entre {{ e }}
                new_text = current_text[:start_pos] + prefix + text + "}}" + current_text[cursor_pos:]
                self.current_widget.setText(new_text)
                # Posiciona o cursor após a variável inserida
                new_cursor_pos = start_pos + len(prefix) + len(text) + 2
                self.current_widget.setCursorPosition(new_cursor_pos)
            elif isinstance(self.current_widget, QPlainTextEdit):
                cursor = self.current_widget.textCursor()
                cursor.setPosition(start_pos)
                cursor.setPosition(cursor_pos, cursor.KeepAnchor)
                prefix = "" if found_opening else "{{"
                cursor.insertText(prefix + text + "}}")
            elif isinstance(self.current_widget, QTextEdit):
                cursor = self.current_widget.textCursor()
                cursor.setPosition(start_pos)
                cursor.setPosition(cursor_pos, cursor.KeepAnchor)
                prefix = "" if found_opening else "{{"
                cursor.insertText(prefix + text + "}}")
            
            # Emite o sinal de variável selecionada
            self.variable_selected.emit(text)
            
            # Desativa o modo de autocompletar
            self.completion_active = False
        except Exception as e:
            print(f"Erro ao selecionar variável: {str(e)}")
    
    def connect_to_lineedit(self, widget):
        """
        Conecta o completer a um QLineEdit.
        
        Args:
            widget (QLineEdit): O widget a ser conectado
        """
        widget.textEdited.connect(lambda text: self._handle_text_edited(widget, text))
        widget.setToolTip(self.variable_tooltip)
    
    def connect_to_textedit(self, widget):
        """
        Conecta o completer a um QTextEdit ou QPlainTextEdit.
        
        Args:
            widget (QTextEdit/QPlainTextEdit): O widget a ser conectado
        """
        if isinstance(widget, QPlainTextEdit):
            widget.textChanged.connect(lambda: self._handle_textedit_changed(widget))
        else:
            widget.textChanged.connect(lambda: self._handle_textedit_changed(widget))
        
        widget.setToolTip(self.variable_tooltip)
    
    def _handle_text_edited(self, widget, text):
        """
        Manipula a edição de texto em um QLineEdit.
        
        Args:
            widget (QLineEdit): O widget sendo editado
            text (str): O texto atual
        """
        try:
            self.current_widget = widget
            cursor_pos = widget.cursorPosition()
            self.current_pos = cursor_pos
            
            # Verifica se está em um contexto de variável
            if cursor_pos >= 2 and text[cursor_pos-2:cursor_pos] == "{{":
                # Ativa o autocompletar
                self.completion_active = True
                self.completer.setCompletionPrefix("")
                
                # Garante que temos pelo menos um item para exibir
                if not self.variables:
                    self.model.setStringList(["nova_variavel"])
                else:
                    self._update_model()
                
                # Configura o completer para o widget atual
                self.completer.setWidget(widget)
                self.completer.complete()
            elif self._is_in_variable_context(text, cursor_pos):
                # Obtém o texto da variável até o cursor
                var_text = self._get_variable_text(text, cursor_pos)
                
                # Ativa o autocompletar com o prefixo
                self.completion_active = True
                self.completer.setCompletionPrefix(var_text)
                
                # Configura o completer para o widget atual
                self.completer.setWidget(widget)
                self.completer.complete()
            else:
                # Desativa o autocompletar
                self.completion_active = False
        except Exception as e:
            print(f"Erro ao manipular texto editado: {str(e)}")
    
    def _handle_textedit_changed(self, widget):
        """
        Manipula a mudança de texto em um QTextEdit ou QPlainTextEdit.
        
        Args:
            widget (QTextEdit/QPlainTextEdit): O widget sendo editado
        """
        try:
            self.current_widget = widget
            cursor = widget.textCursor()
            cursor_pos = cursor.position()
            self.current_pos = cursor_pos
            
            # Obtém o texto atual
            text = widget.toPlainText()
            
            # Verifica se está em um contexto de variável
            if cursor_pos >= 2 and text[cursor_pos-2:cursor_pos] == "{{":
                # Ativa o autocompletar
                self.completion_active = True
                self.completer.setCompletionPrefix("")
                
                # Garante que temos pelo menos um item para exibir
                if not self.variables:
                    self.model.setStringList(["nova_variavel"])
                else:
                    self._update_model()
                
                # Configura o completer para o widget atual
                self.completer.setWidget(widget)
                
                # Exibe o popup de autocompletar em uma posição padrão
                self.completer.complete()
            elif self._is_in_variable_context(text, cursor_pos):
                # Obtém o texto da variável até o cursor
                var_text = self._get_variable_text(text, cursor_pos)
                
                # Ativa o autocompletar com o prefixo
                self.completion_active = True
                self.completer.setCompletionPrefix(var_text)
                
                # Configura o completer para o widget atual
                self.completer.setWidget(widget)
                
                # Exibe o popup de autocompletar
                self.completer.complete()
            else:
                # Desativa o autocompletar
                self.completion_active = False
        except Exception as e:
            print(f"Erro ao manipular texto alterado: {str(e)}")
    
    def _is_in_variable_context(self, text, cursor_pos):
        """
        Verifica se o cursor está dentro de um contexto de variável.
        
        Args:
            text (str): O texto atual
            cursor_pos (int): A posição do cursor
            
        Returns:
            bool: True se o cursor estiver dentro de um contexto de variável, False caso contrário
        """
        # Se o texto for muito curto, não pode estar em um contexto de variável
        if len(text) < 2 or cursor_pos < 2:
            return False
        
        # Procura pelo início da variável ({{)
        start_pos = cursor_pos - 1
        while start_pos > 0:
            if text[start_pos-1:start_pos+1] == "{{":
                # Verifica se tem um fechamento "}}" antes da posição atual
                for i in range(start_pos+1, cursor_pos):
                    if i < len(text) - 1 and text[i:i+2] == "}}":
                        return False
                return True
            start_pos -= 1
        
        return False
    
    def _get_variable_text(self, text, cursor_pos):
        """
        Obtém o texto da variável até o cursor.
        
        Args:
            text (str): O texto atual
            cursor_pos (int): A posição do cursor
            
        Returns:
            str: O texto da variável até o cursor
        """
        # Procura pelo início da variável ({{)
        start_pos = cursor_pos - 1
        while start_pos > 0:
            if text[start_pos-1:start_pos+1] == "{{":
                return text[start_pos+1:cursor_pos]
            start_pos -= 1
        
        return ""
    
    def find_variables_in_text(self, text):
        """
        Encontra todas as variáveis usadas em um texto.
        
        Args:
            text (str): O texto a ser analisado
            
        Returns:
            list: Lista com os nomes das variáveis encontradas
        """
        return VariableProcessor.extract_variables(text) 