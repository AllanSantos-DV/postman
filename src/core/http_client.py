"""
Cliente HTTP para realizar requisições
"""

import time
from typing import Dict, Any, Optional, Union, Tuple

import requests
from requests.exceptions import RequestException

from src.models.request import Request, Response


class HttpClient:
    """
    Cliente HTTP para realizar requisições
    """
    
    @staticmethod
    def send_request(request: Request) -> Tuple[Response, Optional[str]]:
        """
        Envia uma requisição HTTP
        
        Args:
            request (Request): Objeto de requisição
            
        Returns:
            Tuple[Response, Optional[str]]: Resposta e mensagem de erro (se houver)
        """
        start_time = time.time()
        error_message = None
        
        try:
            # Preparar os dados da requisição
            url = request.url
            method = request.method.upper()
            headers = request.headers
            params = request.params
            
            # Determinar o tipo de corpo da requisição
            data = None
            json_data = None
            files = None
            
            if request.body:
                if isinstance(request.body, dict):
                    # Se for um dicionário, assume que é JSON
                    json_data = request.body
                elif isinstance(request.body, str):
                    # Se for uma string, tenta verificar se é JSON
                    try:
                        import json
                        json_data = json.loads(request.body)
                    except (ValueError, TypeError):
                        # Se não for JSON, assume que é um formulário ou dados brutos
                        data = request.body
                
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