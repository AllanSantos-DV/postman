"""
Sistema de armazenamento local para o aplicativo
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from src.models.request import Request
from src.models.collection import Collection, Folder
from src.models.environment import Environment


class Storage:
    """
    Gerencia o armazenamento local de dados do aplicativo
    """
    def __init__(self, base_dir: str = "./data"):
        self.base_dir = Path(base_dir)
        self.collections_dir = self.base_dir / "collections"
        self.requests_dir = self.base_dir / "requests"
        self.history_dir = self.base_dir / "history"
        self.environments_dir = self.base_dir / "environments"
        self.settings_file = self.base_dir / "settings.json"
        
        # Criar diretórios se não existirem
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existam"""
        self.base_dir.mkdir(exist_ok=True)
        self.collections_dir.mkdir(exist_ok=True)
        self.requests_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)
        self.environments_dir.mkdir(exist_ok=True)
    
    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Escreve dados em formato JSON em um arquivo"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _read_json(self, path: Path) -> Dict[str, Any]:
        """Lê dados em formato JSON de um arquivo"""
        if not path.exists():
            return {}
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # === COLEÇÕES ===
    
    def save_collection(self, collection: Collection) -> None:
        """Salva uma coleção no armazenamento local"""
        collection_path = self.collections_dir / f"{collection.id}.json"
        self._write_json(collection_path, collection.to_dict())
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Recupera uma coleção do armazenamento local"""
        collection_path = self.collections_dir / f"{collection_id}.json"
        
        if not collection_path.exists():
            return None
        
        data = self._read_json(collection_path)
        return Collection.from_dict(data)
    
    def delete_collection(self, collection_id: str) -> bool:
        """Remove uma coleção do armazenamento local"""
        collection_path = self.collections_dir / f"{collection_id}.json"
        
        if not collection_path.exists():
            return False
        
        collection_path.unlink()
        return True
    
    def get_all_collections(self) -> List[Collection]:
        """Recupera todas as coleções do armazenamento local"""
        collections = []
        
        for file_path in self.collections_dir.glob("*.json"):
            data = self._read_json(file_path)
            collections.append(Collection.from_dict(data))
        
        return collections
    
    # === REQUISIÇÕES ===
    
    def save_request(self, request: Request) -> None:
        """Salva uma requisição no armazenamento local"""
        request_path = self.requests_dir / f"{request.id}.json"
        self._write_json(request_path, request.to_dict())
    
    def get_request(self, request_id: str) -> Optional[Request]:
        """Recupera uma requisição do armazenamento local"""
        request_path = self.requests_dir / f"{request_id}.json"
        
        if not request_path.exists():
            return None
        
        data = self._read_json(request_path)
        return Request.from_dict(data)
    
    def delete_request(self, request_id: str) -> bool:
        """Remove uma requisição do armazenamento local"""
        request_path = self.requests_dir / f"{request_id}.json"
        
        if not request_path.exists():
            return False
        
        request_path.unlink()
        return True
    
    # === AMBIENTES ===
    
    def save_environment(self, environment: Environment) -> None:
        """Salva um ambiente no armazenamento local"""
        env_path = self.environments_dir / f"{environment.id}.json"
        self._write_json(env_path, environment.to_dict())
    
    def get_environment(self, environment_id: str) -> Optional[Environment]:
        """Recupera um ambiente do armazenamento local"""
        env_path = self.environments_dir / f"{environment_id}.json"
        
        if not env_path.exists():
            return None
        
        data = self._read_json(env_path)
        return Environment.from_dict(data)
    
    def delete_environment(self, environment_id: str) -> bool:
        """Remove um ambiente do armazenamento local"""
        env_path = self.environments_dir / f"{environment_id}.json"
        
        if not env_path.exists():
            return False
        
        env_path.unlink()
        return True
    
    def get_all_environments(self) -> List[Environment]:
        """Recupera todos os ambientes do armazenamento local"""
        environments = []
        
        for file_path in self.environments_dir.glob("*.json"):
            data = self._read_json(file_path)
            environments.append(Environment.from_dict(data))
        
        return environments
    
    # === HISTÓRICO ===
    
    def add_to_history(self, request: Request) -> None:
        """Adiciona uma requisição ao histórico"""
        # Usamos um timestamp como parte do nome do arquivo para ordenação
        history_path = self.history_dir / f"{request.updated_at.timestamp()}-{request.id}.json"
        self._write_json(history_path, request.to_dict())
    
    def get_history(self, limit: int = 50) -> List[Request]:
        """Recupera o histórico de requisições"""
        history_files = list(self.history_dir.glob("*.json"))
        history_files.sort(reverse=True)  # Ordenar do mais recente para o mais antigo
        
        history = []
        for file_path in history_files[:limit]:
            data = self._read_json(file_path)
            history.append(Request.from_dict(data))
        
        return history
    
    def clear_history(self) -> None:
        """Limpa o histórico de requisições"""
        for file_path in self.history_dir.glob("*.json"):
            file_path.unlink()
    
    # === CONFIGURAÇÕES ===
    
    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Salva as configurações do aplicativo"""
        self._write_json(self.settings_file, settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Recupera as configurações do aplicativo"""
        return self._read_json(self.settings_file) 