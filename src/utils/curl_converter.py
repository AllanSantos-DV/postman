"""
Funções para converter requisições para comandos cURL
"""

import json
import re
import shlex
import urllib.parse
from typing import Dict, Any, List, Optional

from src.models.request import Request


def request_to_curl(request: Request, variables: Optional[Dict[str, str]] = None) -> str:
    """
    Converte um objeto Request para um comando cURL.
    
    Args:
        request (Request): O objeto de requisição a ser convertido
        variables (Optional[Dict[str, str]]): Variáveis de ambiente para substituição de placeholders
        
    Returns:
        str: O comando cURL correspondente
    """
    # Iniciar o comando com curl básico
    command_parts = ["curl"]
    
    # Adicionar a flag -X para o método HTTP (exceto para GET que é o padrão)
    if request.method.upper() != "GET":
        command_parts.extend(["-X", request.method.upper()])
    
    # Construir a URL com parâmetros de consulta
    url = request.url
    
    # Substituir variáveis na URL
    if variables:
        url = _replace_variables(url, variables)
    
    if request.params:
        params = request.params.copy()
        
        # Substituir variáveis nos parâmetros
        if variables:
            params = {k: _replace_variables(v, variables) for k, v in params.items()}
            
        # Verificar se a URL já tem parâmetros
        if "?" in url:
            separator = "&"
        else:
            separator = "?"
            
        # Adicionar os parâmetros à URL
        param_string = separator + "&".join([f"{key}={urllib.parse.quote(value)}" for key, value in params.items()])
        url += param_string
    
    # Adicionar cabeçalhos
    headers = request.headers.copy() if request.headers else {}
    
    # Substituir variáveis nos cabeçalhos
    if variables:
        headers = {k: _replace_variables(v, variables) for k, v in headers.items()}
    
    # Adicionar todos os cabeçalhos ao comando
    for header, value in headers.items():
        command_parts.extend(["-H", f"{header}: {value}"])
    
    # Adicionar o corpo da requisição, se houver
    if request.body:
        body = request.body
        
        # Substituir variáveis no corpo
        if variables and isinstance(body, str):
            body = _replace_variables(body, variables)
        elif variables and isinstance(body, dict):
            body = _replace_variables_in_dict(body, variables)
        
        if isinstance(body, dict):
            # Se for um dicionário, serializar como JSON
            data = json.dumps(body)
            command_parts.extend(["-d", f"'{data}'"])
        elif isinstance(body, str):
            # Se for uma string, usar diretamente
            command_parts.extend(["-d", f"'{body}'"])
    
    # Adicionar a URL (deve ser o último argumento)
    command_parts.append(f'"{url}"')
    
    # Juntar todas as partes do comando
    curl_command = " ".join(command_parts)
    
    return curl_command


def _replace_variables(text: str, variables: Dict[str, str]) -> str:
    """
    Substitui placeholders de variáveis no formato {{nome_var}} pelo seu valor correspondente.
    
    Args:
        text (str): O texto com placeholders
        variables (Dict[str, str]): Dicionário de variáveis
        
    Returns:
        str: O texto com os placeholders substituídos
    """
    # Padrão para encontrar variáveis no formato {{nome_var}}
    pattern = r"{{([^{}]+)}}"
    
    def replace_match(match):
        var_name = match.group(1).strip()
        # Remover @ se estiver presente
        if var_name.startswith('@'):
            var_name = var_name[1:]
        return variables.get(var_name, match.group(0))
    
    return re.sub(pattern, replace_match, text)


def _replace_variables_in_dict(data: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
    """
    Substitui placeholders de variáveis em um dicionário.
    
    Args:
        data (Dict[str, Any]): O dicionário com placeholders
        variables (Dict[str, str]): Dicionário de variáveis
        
    Returns:
        Dict[str, Any]: O dicionário com os placeholders substituídos
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = _replace_variables(value, variables)
        elif isinstance(value, dict):
            result[key] = _replace_variables_in_dict(value, variables)
        elif isinstance(value, list):
            result[key] = [
                _replace_variables_in_dict(item, variables) if isinstance(item, dict)
                else _replace_variables(item, variables) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


def curl_to_request(curl_command: str) -> Request:
    """
    Converte um comando cURL para um objeto Request.
    
    Args:
        curl_command (str): O comando cURL
        
    Returns:
        Request: Um objeto Request correspondente
    """
    # Inicializar valores padrão
    method = "GET"
    url = ""
    headers = {}
    params = {}
    body = None
    
    # Remover 'curl' do início do comando
    if curl_command.lower().startswith("curl "):
        curl_command = curl_command[5:]
    
    # Abordagem mais genérica usando regex para capturar headers no formato -H Header: Value
    # Padrão que identifica qualquer header no formato -H NOME: VALOR
    header_pattern = re.compile(r'-H\s+([^:\s]+):\s+([^\s-][^\s]*(?:\s+[^-][^\s]+)*)', re.IGNORECASE)
    
    # Encontrar todas as ocorrências de headers no comando
    for match in header_pattern.finditer(curl_command):
        header_name = match.group(1).strip()
        header_value = match.group(2).strip()
        
        # Se o valor terminar com aspas, removê-las (pode ser parte de outro token)
        if header_value.endswith("'") or header_value.endswith('"'):
            header_value = header_value[:-1]
        
        # Adicionar ao dicionário de headers
        headers[header_name] = header_value
    
    # Preservar aspas no comando para headers com valores complexos
    # Substituir inicialmente aspas específicas para evitar problemas de parsing
    curl_command = curl_command.replace('\\"', '___DOUBLE_QUOTE___')
    curl_command = curl_command.replace("\\'", "___SINGLE_QUOTE___")
    
    # Separar argumentos do comando cURL
    try:
        args = shlex.split(curl_command)
    except ValueError:
        # Se houver erro no parsing, tenta uma abordagem mais robusta
        # Procura por padrões de argumentos comuns em cURL
        args = []
        parts = re.findall(r'(?:\'[^\']*\'|\"[^\"]*\"|[^\s]+)', curl_command)
        for part in parts:
            # Remover possíveis aspas externas mantendo o conteúdo
            if (part.startswith('"') and part.endswith('"')) or \
               (part.startswith("'") and part.endswith("'")):
                args.append(part[1:-1])
            else:
                args.append(part)
    
    # Restaurar aspas nos argumentos
    args = [arg.replace('___DOUBLE_QUOTE___', '"').replace('___SINGLE_QUOTE___', "'") for arg in args]
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        # Método HTTP
        if arg in ["-X", "--request"]:
            if i + 1 < len(args):
                method = args[i + 1]
                i += 2
                continue
        
        # Headers (processamento normal para headers entre aspas)
        if arg in ["-H", "--header"]:
            if i + 1 < len(args):
                header_line = args[i + 1]
                # Melhor tratamento para encontrar o primeiro separador ":"
                colon_pos = header_line.find(":")
                if colon_pos > 0:  # Garantir que há um nome antes do separador
                    header_name = header_line[:colon_pos].strip()
                    header_value = header_line[colon_pos+1:].strip()
                    
                    # Remover aspas do nome do header se houver
                    if header_name.startswith('"') and header_name.endswith('"'):
                        header_name = header_name[1:-1]
                    elif header_name.startswith("'") and header_name.endswith("'"):
                        header_name = header_name[1:-1]
                    
                    # Adicionar o header (não sobrescreve os já extraídos pelo regex)
                    if header_name not in headers:
                        headers[header_name] = header_value
                i += 2
                continue
        
        # Dados (body)
        if arg in ["-d", "--data", "--data-binary", "--data-raw"]:
            if i + 1 < len(args):
                body_data = args[i + 1]
                
                # Tentar interpretar como JSON
                try:
                    # Remover aspas simples/duplas que possam envolver o JSON string
                    if (body_data.startswith("'") and body_data.endswith("'")) or \
                       (body_data.startswith('"') and body_data.endswith('"')):
                        body_data = body_data[1:-1]
                    body = json.loads(body_data)
                except (ValueError, TypeError):
                    body = body_data
                    
                i += 2
                continue
                
        # Dados de formulário (multipart)
        if arg in ["-F", "--form"]:
            if i + 1 < len(args):
                # Se for o primeiro item de formulário, inicializar o dicionário de corpo
                if not isinstance(body, dict):
                    body = {}
                    
                form_item = args[i + 1]
                if "=" in form_item:
                    form_key, form_value = form_item.split("=", 1)
                    body[form_key] = form_value
                    
                i += 2
                continue
        
        # URL (normalmente é o último argumento sem flag)
        if not arg.startswith("-") and ("://" in arg or arg.startswith("www.")):
            # Limpar aspas da URL se houver
            url = arg.strip("\"'")
            
            # Extrair parâmetros da URL se houver
            if "?" in url:
                url_parts = url.split("?", 1)
                url = url_parts[0]
                query_string = url_parts[1]
                
                for param in query_string.split("&"):
                    if "=" in param:
                        param_name, param_value = param.split("=", 1)
                        params[param_name] = urllib.parse.unquote(param_value)
            
            i += 1
            continue
        
        i += 1
    
    # Criar objeto Request
    request = Request(
        name="Imported from cURL",
        url=url,
        method=method,
        headers=headers,
        params=params,
        body=body
    )
    
    return request 