"""
Cliente HTTP para realizar requisições
"""

import time
import json as json_lib
from typing import Dict, Any, Optional, Union, Tuple

import requests
from requests.exceptions import RequestException

from src.models.request import Request, Response
from src.core.variable_processor import VariableProcessor


class HttpClient:
    """
    Cliente HTTP para realizar requisições
    """
    
    @staticmethod
    def send_request(request: Request, variables: Optional[Dict[str, str]] = None) -> Tuple[Response, Optional[str]]:
        """
        Envia uma requisição HTTP
        
        Args:
            request (Request): Objeto de requisição
            variables (Optional[Dict[str, str]]): Variáveis para substituição
            
        Returns:
            Tuple[Response, Optional[str]]: Resposta e mensagem de erro (se houver)
        """
        start_time = time.time()
        error_message = None
        
        # Clonar a requisição para não modificar a original
        processed_request = HttpClient._process_request_variables(request, variables or {})
        
        try:
            # Preparar os dados da requisição
            url = processed_request.url
            method = processed_request.method.upper()
            headers = processed_request.headers
            params = processed_request.params
            
            # Determinar o tipo de corpo da requisição
            data = None
            json_data = None
            files = None
            
            if processed_request.body:
                if isinstance(processed_request.body, dict):
                    # Se for um dicionário, assume que é JSON
                    json_data = processed_request.body
                elif isinstance(processed_request.body, str):
                    # Se for uma string, tenta verificar se é JSON
                    try:
                        json_data = json_lib.loads(processed_request.body)
                    except (ValueError, TypeError):
                        # Se não for JSON, assume que é um formulário ou dados brutos
                        data = processed_request.body
                
            # Enviar a requisição
            http_response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                files=files,
                timeout=30  # Timeout de 30 segundos
            )
            
            # Calcular o tempo decorrido
            elapsed_time = time.time() - start_time
            
            # Criar objeto de resposta
            response = Response(
                status_code=http_response.status_code,
                headers=dict(http_response.headers),
                content=http_response.content,
                elapsed_time=elapsed_time
            )
            
            return response, error_message
            
        except RequestException as e:
            # Calcular o tempo decorrido mesmo em caso de erro
            elapsed_time = time.time() - start_time
            
            # Criar uma resposta vazia
            response = Response(
                status_code=0,
                headers={},
                content=b"",
                elapsed_time=elapsed_time
            )
            
            error_message = f"Erro ao realizar requisição: {str(e)}"
            
            return response, error_message
        
        except Exception as e:
            # Calcular o tempo decorrido mesmo em caso de erro
            elapsed_time = time.time() - start_time
            
            # Criar uma resposta vazia
            response = Response(
                status_code=0,
                headers={},
                content=b"",
                elapsed_time=elapsed_time
            )
            
            error_message = f"Erro inesperado: {str(e)}"
            
            return response, error_message
    
    @staticmethod
    def _process_request_variables(request: Request, variables: Dict[str, str]) -> Request:
        """
        Processa as variáveis em uma requisição
        
        Args:
            request (Request): A requisição original
            variables (Dict[str, str]): As variáveis para substituição
            
        Returns:
            Request: Uma nova requisição com as variáveis substituídas
        """
        # Criar uma cópia da requisição
        processed_request = Request(
            name=request.name,
            url=request.url,
            method=request.method,
            headers=request.headers.copy() if request.headers else {},
            params=request.params.copy() if request.params else {},
            body=request.body,
            description=request.description
        )
        processed_request.id = request.id
        processed_request.created_at = request.created_at
        processed_request.updated_at = request.updated_at
        
        # Processar URL
        processed_request.url = VariableProcessor.process_string(processed_request.url, variables)
        
        # Processar nome
        processed_request.name = VariableProcessor.process_string(processed_request.name, variables)
        
        # Processar cabeçalhos
        processed_request.headers = VariableProcessor.process_dict(processed_request.headers, variables)
        
        # Processar parâmetros
        processed_request.params = VariableProcessor.process_dict(processed_request.params, variables)
        
        # Processar corpo
        if isinstance(processed_request.body, str):
            processed_request.body = VariableProcessor.process_string(processed_request.body, variables)
        elif isinstance(processed_request.body, dict):
            processed_request.body = VariableProcessor.process_dict(processed_request.body, variables)
        
        return processed_request 