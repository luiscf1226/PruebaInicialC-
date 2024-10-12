import os
import re
import json
from collections import Counter
from datetime import datetime

def leer_archivo(ruta_archivo):
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1']
    for encoding in encodings:
        try:
            with open(ruta_archivo, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    print(f"Error: No se pudo leer el archivo {ruta_archivo} con ninguna codificación conocida.")
    return None

def buscar_carpetas_proyecto(ruta_src):
    carpetas_proyecto = []
    for raiz, dirs, archivos in os.walk(ruta_src):
        if any(archivo.endswith(('.cpp', '.h')) for archivo in archivos):
            carpetas_proyecto.append(raiz)
    return carpetas_proyecto

def extraer_elementos(contenido):
    clases = re.findall(r'\bclass\s+(\w+)', contenido)
    funciones = re.findall(r'\b(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:override)?\s*{', contenido)
    variables = re.findall(r'\b(?:int|float|double|char|bool|string|vector)\s+(\w+)', contenido)
    variables += re.findall(r'\bconst\s+\w+\s*&?\s*(\w+)', contenido)
    comentarios = re.findall(r'//.*?$|/\*.*?\*/', contenido, re.DOTALL | re.MULTILINE)
    librerias = re.findall(r'#include\s*[<"]([^>"]+)[>"]', contenido)
    
    return {
        'clases': clases,
        'funciones': funciones,
        'variables': variables,
        'comentarios': [c.strip() for c in comentarios],
        'librerias': librerias
    }

def calcular_complejidad(contenido):
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case)\b', contenido)
    operadores_logicos = re.findall(r'\b(&&|\|\|)\b', contenido)
    llamadas_funciones = re.findall(r'\b\w+\s*\(', contenido)
    
    complejidad = {
        'estructuras_control': Counter(estructuras_control),
        'operadores_logicos': len(operadores_logicos),
        'llamadas_funciones': len(llamadas_funciones),
        'complejidad_ciclomatica': len(estructuras_control) + len(operadores_logicos) + 1
    }
    return complejidad

def analizar_archivo(ruta_completa):
    contenido = leer_archivo(ruta_completa)
    if contenido is None:
        return None
    
    elementos = extraer_elementos(contenido)
    complejidad = calcular_complejidad(contenido)
    
    return {
        'clases': {
            'nombres': elementos['clases'],
            'total': len(elementos['clases']),
            'existe': len(elementos['clases']) > 0
        },
        'funciones': {
            'nombres': elementos['funciones'],
            'total': len(elementos['funciones']),
            'existe': len(elementos['funciones']) > 0
        },
        'variables': {
            'nombres': elementos['variables'],
            'total': len(elementos['variables'])
        },
        'comentarios': {
            'total': len(elementos['comentarios']),
            'contenido': elementos['comentarios']
        },
        'librerias': {
            'nombres': elementos['librerias'],
            'total': len(elementos['librerias'])
        },
        'complejidad': complejidad
    }

def guardar_resultado(resultado, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

def main():
    print("🔍 Iniciando análisis de código...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_output = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_output, exist_ok=True)

    print("🔎 Buscando carpetas del proyecto...")
    carpetas_proyecto = buscar_carpetas_proyecto(ruta_src)

    print(f"📂 Carpetas encontradas: {len(carpetas_proyecto)}")
    print("📊 Analizando archivos...")
    
    for carpeta in carpetas_proyecto:
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.endswith(('.cpp', '.h')):
                    ruta_completa = os.path.join(raiz, archivo)
                    resultado = analizar_archivo(ruta_completa)
                    
                    if resultado:
                        nombre_base = os.path.splitext(archivo)[0]
                        ruta_resultado = os.path.join(ruta_output, f'analisis_{nombre_base}.json')
                        guardar_resultado({archivo: resultado}, ruta_resultado)
                        print(f"✅ Análisis completado para {archivo}")
                        print(f"📊 Resultados guardados en: {ruta_resultado}")

    print("🎉 Análisis de todos los archivos completado.")

if __name__ == "__main__":
    main()
