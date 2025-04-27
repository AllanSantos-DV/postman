#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyRequestMan - Cliente HTTP em Python

Aplicativo para testes de APIs RESTful similar ao Postman,
desenvolvido inteiramente em Python.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.ui.main_window import MainWindow

def main():
    """Função principal que inicia a aplicação"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyRequestMan")
    app.setApplicationVersion("0.1.0")
    
    # Definir o ícone da aplicação
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons", "app.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Criar e exibir a janela principal
    window = MainWindow()
    
    # Definir o mesmo ícone para a janela principal
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
        
    window.show()
    
    # Iniciar o loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 