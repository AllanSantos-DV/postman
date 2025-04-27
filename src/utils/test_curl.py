#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar a conversão de comandos cURL
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.curl_converter import curl_to_request

# Comando cURL de teste com múltiplos headers
curl_command = '''curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer my-token-123" -d '{"name": "test", "value": 123}' https://api.example.com/data'''

# Converter para objeto Request
request = curl_to_request(curl_command)

# Imprimir os resultados para verificação
print("URL:", request.url)
print("Método:", request.method)
print("Headers:", request.headers)
print("Body:", request.body)

# Teste com outro formato de comando
curl_command2 = '''curl --request GET --url "https://api.example.org/v1/users" --header "X-API-Key: abcdef123456" --header "Accept: application/json"'''

request2 = curl_to_request(curl_command2)
print("\nTeste 2:")
print("URL:", request2.url)
print("Método:", request2.method)
print("Headers:", request2.headers)

# Teste com headers sem aspas (caso problemático)
curl_command3 = '''curl -X POST -H Content-Type: application/json -H Authorization: products -d '{"title": "products", "price": "13.5", "description": "lorem ipsum set", "image": "https://i.pravatar.cc", "category": "electronic"}' "https://fakestoreapi.com/products"'''

request3 = curl_to_request(curl_command3)
print("\nTeste 3 (Headers sem aspas):")
print("URL:", request3.url)
print("Método:", request3.method)
print("Headers:", request3.headers)
print("Body:", request3.body)

# Teste exato relatado pelo usuário
curl_command4 = '''curl -X POST -H Content-Type: application/json -H Authorization: products -d '{"title": "products", "price": "13.5", "description": "lorem ipsum set", "image": "https://i.pravatar.cc", "category": "electronic"}' https://fakestoreapi.com/products'''

request4 = curl_to_request(curl_command4)
print("\nTeste 4 (Caso exato do usuário):")
print("URL:", request4.url)
print("Método:", request4.method)
print("Headers:", request4.headers)
print("Body:", request4.body) 