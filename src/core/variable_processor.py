"""
Utilitário para processamento de variáveis de ambiente
"""

import re
from typing import Dict, Optional, Any, List, Match, Tuple


class VariableProcessor:
    """
    Processa variáveis de ambiente em strings
    """
    # Padrão para identificar variáveis no formato {{variavel}}
    VARIABLE_PATTERN = r"{{([^{}]+)}}"
    
    @classmethod
    def process_string(cls, input_string: str, variables: Dict[str, str]) -> str:
        """
        Processa uma string substituindo referências a variáveis
        
        Args:
            input_string: A string contendo referências a variáveis no formato {{variavel}}
            variables: Dicionário com as variáveis disponíveis
            
        Returns:
            String com as variáveis substituídas
        """
        if not input_string:
            return input_string
        
        def replace_var(match: Match) -> str:
            var_name = match.group(1).strip()
            return variables.get(var_name, match.group(0))
        
        # Substitui todas as ocorrências de variáveis
        return re.sub(cls.VARIABLE_PATTERN, replace_var, input_string)
    
    @classmethod
    def process_dict(cls, data: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Processa um dicionário substituindo referências a variáveis em seus valores
        
        Args:
            data: O dicionário a ser processado
            variables: Dicionário com as variáveis disponíveis
            
        Returns:
            Dicionário com as variáveis substituídas
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = cls.process_string(value, variables)
            elif isinstance(value, dict):
                result[key] = cls.process_dict(value, variables)
            elif isinstance(value, list):
                result[key] = cls.process_list(value, variables)
            else:
                result[key] = value
                
        return result
    
    @classmethod
    def process_list(cls, data: List[Any], variables: Dict[str, str]) -> List[Any]:
        """
        Processa uma lista substituindo referências a variáveis em seus valores
        
        Args:
            data: A lista a ser processada
            variables: Dicionário com as variáveis disponíveis
            
        Returns:
            Lista com as variáveis substituídas
        """
        result = []
        
        for item in data:
            if isinstance(item, str):
                result.append(cls.process_string(item, variables))
            elif isinstance(item, dict):
                result.append(cls.process_dict(item, variables))
            elif isinstance(item, list):
                result.append(cls.process_list(item, variables))
            else:
                result.append(item)
                
        return result
    
    @classmethod
    def extract_variables(cls, text: str) -> List[str]:
        """
        Extrai todas as variáveis de uma string
        
        Args:
            text: A string a ser analisada
            
        Returns:
            Lista com os nomes das variáveis encontradas
        """
        if not text:
            return []
            
        matches = re.findall(cls.VARIABLE_PATTERN, text)
        return [match.strip() for match in matches] 