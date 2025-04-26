#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyRequestMan - Cliente HTTP em Python

Aplicativo para testes de APIs RESTful similar ao Postman,
desenvolvido inteiramente em Python.
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    """Função principal que inicia a aplicação"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyRequestMan")
    app.setApplicationVersion("0.1.0")
    
    # Criar e exibir a janela principal
    window = MainWindow()
    window.show()
    
    # Iniciar o loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 