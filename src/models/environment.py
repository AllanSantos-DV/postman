"""
Modelo de dados para ambientes e variáveis de ambiente
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class Environment:
    """
    Classe que representa um ambiente com variáveis
    """
    def __init__(
        self,
        name: str,
        variables: Optional[Dict[str, str]] = None,
        description: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.variables = variables or {}
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "variables": self.variables,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Environment':
        """Cria um objeto a partir de um dicionário"""
        environment = cls(
            name=data["name"],
            variables=data.get("variables", {}),
            description=data.get("description", "")
        )
        
        environment.id = data["id"]
        environment.created_at = datetime.fromisoformat(data["created_at"])
        environment.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return environment 