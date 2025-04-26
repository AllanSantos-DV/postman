#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar um executável da aplicação PyRequestMan
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()


def build_executable():
    """
    Cria um executável da aplicação usando PyInstaller
    """
    print("Verificando dependências...")
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    print("Criando executável...")
    
    # Configurações do PyInstaller
    pyinstaller_args = [
        "--name=PyRequestMan",
        "--onefile",  # Criar um único arquivo executável
        "--windowed",  # Não mostrar console (modo GUI)
        "--add-data=resources;resources",  # Incluir recursos
        "--add-data=data;data",  # Incluir diretórios de dados
        "--icon=resources/icons/app.ico",  # Ícone do aplicativo (se existir)
        "main.py"  # Script principal
    ]
    
    # Executar o PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller"] + pyinstaller_args
    subprocess.check_call(cmd)
    
    print("Executável criado com sucesso!")
    print("O arquivo está disponível em: dist/PyRequestMan.exe")


def create_portable_zip():
    """
    Cria um pacote ZIP portável com o executável e os recursos necessários
    """
    print("Criando pacote portável...")
    
    # Verificar se o executável foi criado
    exe_path = SCRIPT_DIR / "dist" / "PyRequestMan.exe"
    if not exe_path.exists():
        print("Erro: O executável não foi encontrado. Execute build_executable() primeiro.")
        return
    
    # Criar diretório para o pacote portável
    portable_dir = SCRIPT_DIR / "portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copiar o executável
    shutil.copy(exe_path, portable_dir / "PyRequestMan.exe")
    
    # Criar diretórios de dados
    (portable_dir / "data").mkdir()
    (portable_dir / "data/collections").mkdir()
    (portable_dir / "data/requests").mkdir()
    (portable_dir / "data/history").mkdir()
    
    # Copiar configurações iniciais
    shutil.copy(SCRIPT_DIR / "data/settings.json", portable_dir / "data/settings.json")
    
    # Criar arquivo README
    with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write("""PyRequestMan - Cliente HTTP Portátil

Este é um cliente HTTP portátil similar ao Postman, para testar APIs REST.

Instruções:
1. Execute o arquivo PyRequestMan.exe
2. Todos os dados serão salvos na pasta 'data'
3. Para manter a portabilidade, não mova o executável para fora desta pasta

Desenvolvido com Python e PyQt5.
""")
    
    # Criar ZIP
    shutil.make_archive(SCRIPT_DIR / "PyRequestMan_Portable", "zip", portable_dir)
    
    print("Pacote portável criado com sucesso!")
    print("O arquivo está disponível em: PyRequestMan_Portable.zip")


if __name__ == "__main__":
    print("=== PyRequestMan - Script de Build ===")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--portable":
        build_executable()
        create_portable_zip()
    else:
        build_executable() 