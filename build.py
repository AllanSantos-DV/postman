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


def clean_build_directories():
    """
    Limpa os diretórios de build e dist caso existam
    """
    print("Limpando diretórios de build anteriores...")
    
    # Limpar diretório build
    build_dir = SCRIPT_DIR / "build"
    if build_dir.exists():
        print(f"Removendo diretório: {build_dir}")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Erro ao remover diretório build: {e}")
    
    # Limpar diretório dist
    dist_dir = SCRIPT_DIR / "dist"
    if dist_dir.exists():
        print(f"Removendo diretório: {dist_dir}")
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"Erro ao remover diretório dist: {e}")
    
    # Limpar arquivos .spec
    for spec_file in SCRIPT_DIR.glob("*.spec"):
        print(f"Removendo arquivo spec: {spec_file}")
        try:
            spec_file.unlink()
        except Exception as e:
            print(f"Erro ao remover arquivo spec: {e}")
    
    print("Limpeza concluída.")


def build_executable():
    """
    Cria um executável da aplicação usando PyInstaller
    """
    # Limpar diretórios anteriores
    clean_build_directories()
    
    print("Verificando dependências...")
    pyinstaller_installed = False
    
    # Verificar se o PyInstaller já está instalado
    try:
        import PyInstaller
        print(f"PyInstaller versão: {PyInstaller.__version__}")
        pyinstaller_installed = True
    except ImportError:
        print("PyInstaller não encontrado, tentando instalar...")
    
    # Tentar instalar PyInstaller se necessário
    if not pyinstaller_installed:
        try:
            print("Instalando PyInstaller com a flag --user...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "PyInstaller"])
            print("PyInstaller instalado com sucesso.")
            
            # Verificar se foi instalado corretamente
            try:
                import PyInstaller
                print(f"PyInstaller versão: {PyInstaller.__version__}")
                pyinstaller_installed = True
            except ImportError:
                # Se ainda não conseguir importar, o pip pode ter adicionado em um local não presente no PATH
                print("Aviso: PyInstaller instalado, mas não está no PYTHONPATH.")
                print("Tentando localizar o executável diretamente...")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar PyInstaller: {e}")
            print("\nSugestões para resolver problemas de instalação:")
            print("1. Execute este script como administrador")
            print("2. Instale o PyInstaller manualmente: pip install --user PyInstaller")
            print("3. Adicione o diretório de scripts do usuário ao PATH")
            return False
    
    # Se chegou até aqui sem PyInstaller, não prosseguir
    if not pyinstaller_installed:
        print("Erro: Não foi possível instalar ou encontrar o PyInstaller.")
        print("Por favor, instale-o manualmente com:")
        print("pip install --user PyInstaller")
        return False
    
    print("Criando executável...")
    
    # Verificar existência dos diretórios de recursos
    data_paths = []
    if os.path.exists("resources"):
        data_paths.append("--add-data=resources;resources")
    else:
        print("Aviso: Diretório 'resources' não encontrado.")
    
    if os.path.exists("data"):
        data_paths.append("--add-data=data;data")
    else:
        print("Aviso: Diretório 'data' não encontrado.")
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/collections", exist_ok=True) 
        os.makedirs("data/requests", exist_ok=True)
        os.makedirs("data/history", exist_ok=True)
        os.makedirs("data/environments", exist_ok=True)
        
        # Criar um settings.json vazio
        with open("data/settings.json", "w", encoding="utf-8") as f:
            f.write("{}")
            
        print("Diretórios 'data' criados.")
        data_paths.append("--add-data=data;data")
        
    icon_path = "--icon=resources/icons/app.ico" if os.path.exists("resources/icons/app.ico") else ""
    
    # Configurações do PyInstaller
    pyinstaller_args = [
        "--name=PyRequestMan",
        "--onefile",  # Criar um único arquivo executável
        "--windowed",  # Não mostrar console (modo GUI)
    ]
    
    # Adicionar caminhos de dados apenas se existirem
    pyinstaller_args.extend(data_paths)
    
    # Adicionar ícone apenas se existir
    if icon_path:
        pyinstaller_args.append(icon_path)
    
    # Adicionar o script principal
    pyinstaller_args.append("main.py")
    
    print("Executando PyInstaller com argumentos:")
    print(" ".join(pyinstaller_args))
    
    try:
        # Executar o PyInstaller diretamente em vez de como módulo
        cmd = [sys.executable, "-m", "PyInstaller"] + pyinstaller_args
        subprocess.check_call(cmd)
        print("Executável criado com sucesso!")
        print("O arquivo está disponível em: dist/PyRequestMan.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar executável: {e}")
        print("Tentando método alternativo...")
        
        try:
            # Método alternativo usando arquivos .spec
            with open("PyRequestMan.spec", "w", encoding="utf-8") as spec_file:
                spec_file.write(f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[{repr(str(SCRIPT_DIR))}],
    binaries=[],
    datas=[{'[("resources", "resources"), ("data", "data")]' if os.path.exists("resources") and os.path.exists("data") else '[]'}],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PyRequestMan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {'icon="resources/icons/app.ico"' if os.path.exists("resources/icons/app.ico") else ''},
)
""")
            
            # Executar o PyInstaller com o arquivo .spec
            cmd = [sys.executable, "-m", "PyInstaller", "PyRequestMan.spec"]
            subprocess.check_call(cmd)
            print("Executável criado com sucesso usando método alternativo!")
            print("O arquivo está disponível em: dist/PyRequestMan.exe")
            return True
        except Exception as e2:
            print(f"Falha também no método alternativo: {e2}")
            print("\nSugestões para resolver o problema:")
            print("1. Verifique se você tem permissões de administrador")
            print("2. Tente desinstalar e reinstalar o PyInstaller: pip uninstall pyinstaller && pip install --user pyinstaller")
            print("3. Verifique se há conflitos com antivírus ou firewall")
            print("4. Verifique se há espaço em disco suficiente")
            return False


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
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--portable":
            if build_executable():
                create_portable_zip()
            else:
                print("Não foi possível criar o executável. A criação do pacote portável foi cancelada.")
                sys.exit(1)
        else:
            if not build_executable():
                print("Falha ao criar o executável.")
                sys.exit(1)
    except Exception as e:
        print(f"Erro não tratado durante o processo de build: {e}")
        sys.exit(1) 