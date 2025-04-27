"""
Utilidades para conversão de coleções entre diferentes formatos
Suporta importação e exportação para Postman e Insomnia
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from src.models.collection import Collection, Folder
from src.models.request import Request
from src.core.storage import Storage


def import_collection(file_path: str, storage: Storage) -> Tuple[bool, str, Optional[Collection]]:
    """
    Importa uma coleção a partir de um arquivo.
    Detecta automaticamente se é um formato Postman ou Insomnia.
    
    Args:
        file_path (str): Caminho para o arquivo de coleção
        storage (Storage): Instância do armazenamento para salvar requisições
        
    Returns:
        Tuple[bool, str, Optional[Collection]]: 
            - Sucesso da operação
            - Mensagem descrevendo o resultado
            - Coleção importada (ou None em caso de falha)
    """
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Detectar o formato
        if _is_postman_format(data):
            return _import_postman_collection(data, storage)
        elif _is_insomnia_format(data):
            return _import_insomnia_collection(data, storage)
        else:
            return False, "Formato de arquivo não reconhecido. Suporta apenas Postman ou Insomnia.", None
            
    except Exception as e:
        return False, f"Erro ao importar coleção: {str(e)}", None


def _is_postman_format(data: Dict[str, Any]) -> bool:
    """Verifica se os dados estão no formato do Postman"""
    # Formato do Postman v2.1
    if "info" in data and "schema" in data["info"] and "item" in data:
        return True
    # Formato do Postman mais antigo
    if "id" in data and "name" in data and "order" in data:
        return True
    return False


def _is_insomnia_format(data: Dict[str, Any]) -> bool:
    """Verifica se os dados estão no formato do Insomnia"""
    # Formato do Insomnia Export
    if "_type" in data and data["_type"] == "export" and "resources" in data:
        return True
    return False


def _import_postman_collection(data: Dict[str, Any], storage: Storage) -> Tuple[bool, str, Optional[Collection]]:
    """
    Importa uma coleção do formato Postman.
    
    Args:
        data (Dict[str, Any]): Dados da coleção em formato Postman
        storage (Storage): Instância do armazenamento para salvar requisições
        
    Returns:
        Tuple[bool, str, Optional[Collection]]: 
            - Sucesso da operação
            - Mensagem descrevendo o resultado
            - Coleção importada (ou None em caso de falha)
    """
    try:
        # Extrair informações básicas da coleção
        if "info" in data:  # Formato v2.1
            collection_name = data["info"].get("name", "Coleção Importada")
            collection_description = data.get("description", "")
        else:  # Formato antigo
            collection_name = data.get("name", "Coleção Importada")
            collection_description = data.get("description", "")
        
        # Criar a coleção
        collection = Collection(
            name=collection_name,
            description=collection_description
        )
        
        # Processar os itens da coleção
        if "item" in data:  # Formato v2.1
            _process_postman_items(data["item"], collection, None, storage)
        elif "order" in data and "requests" in data:  # Formato antigo
            for request_id in data["order"]:
                for request_data in data["requests"]:
                    if request_data["id"] == request_id:
                        _process_postman_request(request_data, collection, None, storage)
                        break
        
        # Salvar a coleção
        storage.save_collection(collection)
        
        return True, f"Coleção '{collection_name}' importada com sucesso", collection
        
    except Exception as e:
        return False, f"Erro ao importar coleção Postman: {str(e)}", None


def _process_postman_items(items: List[Dict[str, Any]], collection: Collection, parent_folder: Optional[Folder], storage: Storage):
    """
    Processa recursivamente os itens de uma coleção do Postman.
    
    Args:
        items (List[Dict[str, Any]]): Lista de itens da coleção Postman
        collection (Collection): Coleção a ser populada
        parent_folder (Optional[Folder]): Pasta pai para itens aninhados
        storage (Storage): Instância do armazenamento
    """
    for item in items:
        # Verificar se é uma pasta ou uma requisição
        if "item" in item:  # É uma pasta
            folder = Folder(
                name=item.get("name", "Pasta sem nome"),
                description=item.get("description", "")
            )
            
            # Processar os itens da pasta
            _process_postman_items(item["item"], collection, folder, storage)
            
            # Adicionar a pasta à coleção ou à pasta pai
            if parent_folder is None:
                collection.add_folder(folder)
            else:
                parent_folder.add_subfolder(folder)
                
        elif "request" in item:  # É uma requisição
            _process_postman_request(item, collection, parent_folder, storage)


def _process_postman_request(item: Dict[str, Any], collection: Collection, parent_folder: Optional[Folder], storage: Storage):
    """
    Processa uma requisição do Postman e a adiciona à coleção ou pasta.
    
    Args:
        item (Dict[str, Any]): Dados da requisição no formato Postman
        collection (Collection): Coleção a ser populada
        parent_folder (Optional[Folder]): Pasta pai, se aplicável
        storage (Storage): Instância do armazenamento
    """
    # Formato v2.1
    if isinstance(item["request"], dict):
        request_data = item["request"]
        request_name = item.get("name", "Requisição sem nome")
        
        # Extrair método e URL
        if isinstance(request_data["url"], dict):
            url = request_data["url"].get("raw", "")
        else:
            url = request_data["url"]
            
        method = request_data.get("method", "GET")
        
        # Processar cabeçalhos
        headers = {}
        if "header" in request_data:
            for header in request_data["header"]:
                if not header.get("disabled", False):
                    headers[header["key"]] = header["value"]
        
        # Processar parâmetros de consulta
        params = {}
        if isinstance(request_data["url"], dict) and "query" in request_data["url"]:
            for param in request_data["url"]["query"]:
                if not param.get("disabled", False):
                    params[param["key"]] = param["value"]
        
        # Processar corpo da requisição
        body = None
        if "body" in request_data:
            body_data = request_data["body"]
            body_mode = body_data.get("mode", "")
            
            if body_mode == "raw" and "raw" in body_data:
                # Tentar interpretar como JSON
                try:
                    if "options" in body_data and "raw" in body_data["options"]:
                        if body_data["options"]["raw"].get("language", "") == "json":
                            body = json.loads(body_data["raw"])
                    else:
                        body = body_data["raw"]
                except:
                    body = body_data["raw"]
            elif body_mode == "formdata" and "formdata" in body_data:
                body = {}
                for item in body_data["formdata"]:
                    if not item.get("disabled", False):
                        body[item["key"]] = item["value"]
            elif body_mode == "urlencoded" and "urlencoded" in body_data:
                body = {}
                for item in body_data["urlencoded"]:
                    if not item.get("disabled", False):
                        body[item["key"]] = item["value"]
    
    # Formato antigo
    else:
        request_name = item.get("name", "Requisição sem nome")
        
        # Extrair JSON da requisição
        request_json = json.loads(item["rawModeData"]) if "rawModeData" in item else None
        
        # Extrair método e URL
        url = item.get("url", "")
        method = item.get("method", "GET")
        
        # Processar cabeçalhos
        headers = {}
        for header in item.get("headers", "").split("\n"):
            if header.strip():
                parts = header.split(":", 1)
                if len(parts) == 2:
                    headers[parts[0].strip()] = parts[1].strip()
        
        # Processar parâmetros de consulta
        params = {}
        for param in item.get("parameters", []):
            params[param["key"]] = param["value"]
        
        # Corpo da requisição
        body = request_json
    
    # Criar a requisição
    request = Request(
        name=request_name,
        url=url,
        method=method,
        headers=headers,
        params=params,
        body=body,
        description=item.get("description", "")
    )
    
    # Salvar a requisição
    storage.save_request(request)
    
    # Adicionar à coleção ou pasta
    if parent_folder is None:
        collection.add_request(request.id)
    else:
        parent_folder.add_request(request.id)


def _import_insomnia_collection(data: Dict[str, Any], storage: Storage) -> Tuple[bool, str, Optional[Collection]]:
    """
    Importa uma coleção do formato Insomnia.
    
    Args:
        data (Dict[str, Any]): Dados da coleção em formato Insomnia
        storage (Storage): Instância do armazenamento para salvar requisições
        
    Returns:
        Tuple[bool, str, Optional[Collection]]: 
            - Sucesso da operação
            - Mensagem descrevendo o resultado
            - Coleção importada (ou None em caso de falha)
    """
    try:
        # Mapear recursos por ID
        resources_by_id = {}
        for resource in data["resources"]:
            resources_by_id[resource["_id"]] = resource
        
        # Encontrar pastas e requisições de nível superior
        workspace_id = None
        
        # Encontrar o workspace (coleção principal)
        for resource in data["resources"]:
            if resource["_type"] == "workspace":
                workspace_id = resource["_id"]
                collection_name = resource.get("name", "Coleção Importada")
                collection_description = resource.get("description", "")
                break
        
        if not workspace_id:
            # Se não encontrar um workspace, usar o primeiro recurso como nome da coleção
            collection_name = "Coleção Insomnia"
            collection_description = ""
        
        # Criar a coleção
        collection = Collection(
            name=collection_name,
            description=collection_description
        )
        
        # Mapeamento de pastas para objetos Folder
        folder_map = {}
        
        # Processar pastas
        folders = []
        for resource in data["resources"]:
            if resource["_type"] == "request_group":
                folders.append(resource)
                
                # Criar objeto Folder
                folder = Folder(
                    name=resource.get("name", "Pasta sem nome"),
                    description=resource.get("description", "")
                )
                
                # Armazenar a referência
                folder_map[resource["_id"]] = folder
        
        # Processar hierarquia de pastas
        for resource in folders:
            parent_id = resource.get("parentId")
            
            if parent_id == workspace_id or not parent_id:
                # Pasta de nível superior
                collection.add_folder(folder_map[resource["_id"]])
            elif parent_id in folder_map:
                # Subpasta
                folder_map[parent_id].add_subfolder(folder_map[resource["_id"]])
        
        # Processar requisições
        for resource in data["resources"]:
            if resource["_type"] == "request":
                # Extrair método e URL
                url = resource.get("url", "")
                method = resource.get("method", "GET")
                
                # Processar cabeçalhos
                headers = {}
                for header in resource.get("headers", []):
                    headers[header["name"]] = header["value"]
                
                # Processar parâmetros
                params = {}
                if "parameters" in resource:
                    for param in resource["parameters"]:
                        params[param["name"]] = param["value"]
                
                # Processar corpo da requisição
                body = None
                if "body" in resource:
                    body_data = resource["body"]
                    
                    if resource.get("body", {}).get("mimeType", "") == "application/json":
                        try:
                            body = json.loads(body_data.get("text", "{}"))
                        except:
                            body = body_data.get("text", "")
                    elif "params" in body_data:
                        body = {}
                        for param in body_data["params"]:
                            body[param["name"]] = param["value"]
                    else:
                        body = body_data.get("text", "")
                
                # Criar a requisição
                request = Request(
                    name=resource.get("name", "Requisição sem nome"),
                    url=url,
                    method=method,
                    headers=headers,
                    params=params,
                    body=body,
                    description=resource.get("description", "")
                )
                
                # Salvar a requisição
                storage.save_request(request)
                
                # Adicionar à coleção ou pasta
                parent_id = resource.get("parentId")
                
                if parent_id in folder_map:
                    # Adicionar à pasta
                    folder_map[parent_id].add_request(request.id)
                else:
                    # Adicionar à coleção principal
                    collection.add_request(request.id)
        
        # Salvar a coleção
        storage.save_collection(collection)
        
        return True, f"Coleção '{collection_name}' importada com sucesso", collection
        
    except Exception as e:
        return False, f"Erro ao importar coleção Insomnia: {str(e)}", None


def export_collection(collection: Collection, file_path: str, export_format: str, storage: Storage) -> Tuple[bool, str]:
    """
    Exporta uma coleção para um arquivo no formato especificado.
    
    Args:
        collection (Collection): Coleção a ser exportada
        file_path (str): Caminho para salvar o arquivo exportado
        export_format (str): Formato de exportação ("postman" ou "insomnia")
        storage (Storage): Instância do armazenamento para ler requisições
    
    Returns:
        Tuple[bool, str]: 
            - Sucesso da operação
            - Mensagem descrevendo o resultado
    """
    try:
        if export_format.lower() == "postman":
            data = _export_as_postman(collection, storage)
        elif export_format.lower() == "insomnia":
            data = _export_as_insomnia(collection, storage)
        else:
            return False, f"Formato de exportação não suportado: {export_format}"
        
        # Salvar o arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, f"Coleção '{collection.name}' exportada com sucesso para {file_path}"
    
    except Exception as e:
        return False, f"Erro ao exportar coleção: {str(e)}"


def _export_as_postman(collection: Collection, storage: Storage) -> Dict[str, Any]:
    """
    Exporta uma coleção para o formato Postman v2.1.
    
    Args:
        collection (Collection): Coleção a ser exportada
        storage (Storage): Instância do armazenamento para ler requisições
    
    Returns:
        Dict[str, Any]: Dados da coleção no formato Postman
    """
    # Criar estrutura base do Postman
    postman_data = {
        "info": {
            "_postman_id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Adicionar requisições diretamente na coleção
    for request_id in collection.requests:
        request = storage.get_request(request_id)
        if request:
            postman_data["item"].append(_convert_request_to_postman(request))
    
    # Processar pastas
    for folder in collection.folders:
        postman_data["item"].append(_convert_folder_to_postman(folder, storage))
    
    return postman_data


def _convert_folder_to_postman(folder: Folder, storage: Storage) -> Dict[str, Any]:
    """
    Converte uma pasta para o formato Postman.
    
    Args:
        folder (Folder): Pasta a ser convertida
        storage (Storage): Instância do armazenamento para ler requisições
    
    Returns:
        Dict[str, Any]: Dados da pasta no formato Postman
    """
    folder_data = {
        "name": folder.name,
        "description": folder.description,
        "item": []
    }
    
    # Adicionar requisições na pasta
    for request_id in folder.requests:
        request = storage.get_request(request_id)
        if request:
            folder_data["item"].append(_convert_request_to_postman(request))
    
    # Processar subpastas
    for subfolder in folder.subfolders:
        folder_data["item"].append(_convert_folder_to_postman(subfolder, storage))
    
    return folder_data


def _convert_request_to_postman(request: Request) -> Dict[str, Any]:
    """
    Converte uma requisição para o formato Postman.
    
    Args:
        request (Request): Requisição a ser convertida
    
    Returns:
        Dict[str, Any]: Dados da requisição no formato Postman
    """
    # Criar estrutura base da requisição
    postman_request = {
        "name": request.name,
        "request": {
            "method": request.method,
            "description": request.description,
            "header": [],
            "url": {
                "raw": request.url,
                "query": []
            }
        }
    }
    
    # Adicionar cabeçalhos
    for key, value in request.headers.items():
        postman_request["request"]["header"].append({
            "key": key,
            "value": value,
            "type": "text"
        })
    
    # Adicionar parâmetros de consulta
    for key, value in request.params.items():
        postman_request["request"]["url"]["query"].append({
            "key": key,
            "value": value
        })
    
    # Adicionar corpo da requisição, se houver
    if request.body is not None:
        body = {
            "mode": "raw",
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }
        
        if isinstance(request.body, dict):
            body["raw"] = json.dumps(request.body)
        elif isinstance(request.body, str):
            body["raw"] = request.body
        
        postman_request["request"]["body"] = body
    
    return postman_request


def _export_as_insomnia(collection: Collection, storage: Storage) -> Dict[str, Any]:
    """
    Exporta uma coleção para o formato Insomnia.
    
    Args:
        collection (Collection): Coleção a ser exportada
        storage (Storage): Instância do armazenamento para ler requisições
    
    Returns:
        Dict[str, Any]: Dados da coleção no formato Insomnia
    """
    # Criar estrutura base do Insomnia
    insomnia_data = {
        "_type": "export",
        "__export_format": 4,
        "__export_date": datetime.now().isoformat(),
        "__export_source": "pyrequestman",
        "resources": []
    }
    
    # Criar o workspace (coleção principal)
    workspace = {
        "_id": collection.id,
        "_type": "workspace",
        "name": collection.name,
        "description": collection.description,
        "created": collection.created_at.isoformat(),
        "modified": collection.updated_at.isoformat()
    }
    
    insomnia_data["resources"].append(workspace)
    
    # Mapear pastas e requisições
    _process_insomnia_folders(collection.folders, collection.id, insomnia_data["resources"], storage)
    
    # Adicionar requisições diretamente na coleção
    for request_id in collection.requests:
        request = storage.get_request(request_id)
        if request:
            insomnia_data["resources"].append(_convert_request_to_insomnia(request, collection.id))
    
    return insomnia_data


def _process_insomnia_folders(folders: List[Folder], parent_id: str, resources: List[Dict[str, Any]], storage: Storage):
    """
    Processa recursivamente as pastas para o formato Insomnia.
    
    Args:
        folders (List[Folder]): Lista de pastas
        parent_id (str): ID do pai (coleção ou pasta)
        resources (List[Dict[str, Any]]): Lista de recursos Insomnia
        storage (Storage): Instância do armazenamento para ler requisições
    """
    for folder in folders:
        # Criar pasta no formato Insomnia
        folder_data = {
            "_id": folder.id,
            "_type": "request_group",
            "name": folder.name,
            "description": folder.description,
            "parentId": parent_id,
            "created": folder.created_at.isoformat(),
            "modified": folder.updated_at.isoformat()
        }
        
        resources.append(folder_data)
        
        # Processar requisições da pasta
        for request_id in folder.requests:
            request = storage.get_request(request_id)
            if request:
                resources.append(_convert_request_to_insomnia(request, folder.id))
        
        # Processar subpastas
        _process_insomnia_folders(folder.subfolders, folder.id, resources, storage)


def _convert_request_to_insomnia(request: Request, parent_id: str) -> Dict[str, Any]:
    """
    Converte uma requisição para o formato Insomnia.
    
    Args:
        request (Request): Requisição a ser convertida
        parent_id (str): ID do pai (coleção ou pasta)
    
    Returns:
        Dict[str, Any]: Dados da requisição no formato Insomnia
    """
    # Criar estrutura base da requisição
    insomnia_request = {
        "_id": request.id,
        "_type": "request",
        "name": request.name,
        "parentId": parent_id,
        "method": request.method,
        "url": request.url,
        "description": request.description,
        "headers": [],
        "created": request.created_at.isoformat(),
        "modified": request.updated_at.isoformat()
    }
    
    # Adicionar cabeçalhos
    for key, value in request.headers.items():
        insomnia_request["headers"].append({
            "name": key,
            "value": value
        })
    
    # Adicionar parâmetros de consulta
    if request.params:
        insomnia_request["parameters"] = []
        for key, value in request.params.items():
            insomnia_request["parameters"].append({
                "name": key,
                "value": value
            })
    
    # Adicionar corpo da requisição, se houver
    if request.body is not None:
        body = {}
        
        if isinstance(request.body, dict):
            body["mimeType"] = "application/json"
            body["text"] = json.dumps(request.body)
        elif isinstance(request.body, str):
            if request.headers.get("Content-Type", "").startswith("application/json"):
                body["mimeType"] = "application/json"
            else:
                body["mimeType"] = "text/plain"
            body["text"] = request.body
        
        insomnia_request["body"] = body
    
    return insomnia_request 