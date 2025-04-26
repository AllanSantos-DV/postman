"""
Modelo de dados para requisições HTTP
"""

from typing import Dict, List, Optional, Any
import json
import uuid
from datetime import datetime


class Request:
    """
    Classe que representa uma requisição HTTP
    """
    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        description: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.params = params or {}
        self.body = body
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Request':
        """Cria um objeto a partir de um dicionário"""
        request = cls(
            name=data["name"],
            url=data["url"],
            method=data["method"],
            headers=data.get("headers", {}),
            params=data.get("params", {}),
            body=data.get("body"),
            description=data.get("description", "")
        )
        
        request.id = data["id"]
        request.created_at = datetime.fromisoformat(data["created_at"])
        request.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return request


class Response:
    """
    Classe que representa uma resposta HTTP
    """
    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        elapsed_time: float
    ):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.elapsed_time = elapsed_time
        self.timestamp = datetime.now()
    
    @property
    def is_json(self) -> bool:
        """Verifica se o conteúdo é um JSON"""
        content_type = self.headers.get("Content-Type", "")
        return "application/json" in content_type
    
    @property
    def is_html(self) -> bool:
        """Verifica se o conteúdo é HTML"""
        content_type = self.headers.get("Content-Type", "")
        return "text/html" in content_type
    
    @property
    def is_xml(self) -> bool:
        """Verifica se o conteúdo é XML"""
        content_type = self.headers.get("Content-Type", "")
        return "application/xml" in content_type or "text/xml" in content_type
    
    def get_content_as_text(self) -> str:
        """Retorna o conteúdo como texto"""
        return self.content.decode("utf-8")
    
    def get_content_as_json(self) -> Any:
        """Retorna o conteúdo como JSON"""
        if not self.is_json:
            raise ValueError("O conteúdo não é um JSON")
        
        return json.loads(self.get_content_as_text()) 