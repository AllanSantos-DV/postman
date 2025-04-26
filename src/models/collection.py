"""
Modelo de dados para coleções de requisições
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class Collection:
    """
    Classe que representa uma coleção de requisições
    """
    def __init__(
        self,
        name: str,
        description: str = "",
        requests: Optional[List[str]] = None,
        folders: Optional[List['Folder']] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.requests = requests or []  # Lista de IDs de requisições
        self.folders = folders or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_request(self, request_id: str) -> None:
        """Adiciona uma requisição à coleção"""
        if request_id not in self.requests:
            self.requests.append(request_id)
            self.updated_at = datetime.now()
    
    def remove_request(self, request_id: str) -> None:
        """Remove uma requisição da coleção"""
        if request_id in self.requests:
            self.requests.remove(request_id)
            self.updated_at = datetime.now()
    
    def add_folder(self, folder: 'Folder') -> None:
        """Adiciona uma pasta à coleção"""
        self.folders.append(folder)
        self.updated_at = datetime.now()
    
    def remove_folder(self, folder_id: str) -> None:
        """Remove uma pasta da coleção"""
        self.folders = [f for f in self.folders if f.id != folder_id]
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requests": self.requests,
            "folders": [folder.to_dict() for folder in self.folders],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Collection':
        """Cria um objeto a partir de um dicionário"""
        collection = cls(
            name=data["name"],
            description=data.get("description", ""),
            requests=data.get("requests", []),
        )
        
        collection.id = data["id"]
        collection.created_at = datetime.fromisoformat(data["created_at"])
        collection.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Adiciona as pastas
        for folder_data in data.get("folders", []):
            collection.folders.append(Folder.from_dict(folder_data))
        
        return collection


class Folder:
    """
    Classe que representa uma pasta dentro de uma coleção
    """
    def __init__(
        self,
        name: str,
        description: str = "",
        requests: Optional[List[str]] = None,
        subfolders: Optional[List['Folder']] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.requests = requests or []  # Lista de IDs de requisições
        self.subfolders = subfolders or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_request(self, request_id: str) -> None:
        """Adiciona uma requisição à pasta"""
        if request_id not in self.requests:
            self.requests.append(request_id)
            self.updated_at = datetime.now()
    
    def remove_request(self, request_id: str) -> None:
        """Remove uma requisição da pasta"""
        if request_id in self.requests:
            self.requests.remove(request_id)
            self.updated_at = datetime.now()
    
    def add_subfolder(self, folder: 'Folder') -> None:
        """Adiciona uma subpasta à pasta"""
        self.subfolders.append(folder)
        self.updated_at = datetime.now()
    
    def remove_subfolder(self, folder_id: str) -> None:
        """Remove uma subpasta da pasta"""
        self.subfolders = [f for f in self.subfolders if f.id != folder_id]
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requests": self.requests,
            "subfolders": [subfolder.to_dict() for subfolder in self.subfolders],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Folder':
        """Cria um objeto a partir de um dicionário"""
        folder = cls(
            name=data["name"],
            description=data.get("description", ""),
            requests=data.get("requests", []),
        )
        
        folder.id = data["id"]
        folder.created_at = datetime.fromisoformat(data["created_at"])
        folder.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Adiciona as subpastas
        for subfolder_data in data.get("subfolders", []):
            folder.subfolders.append(Folder.from_dict(subfolder_data))
        
        return folder 