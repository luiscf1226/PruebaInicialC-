import os
import re
import json
import subprocess
from collections import Counter
from datetime import datetime
import hashlib

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

def calcular_complejidad_funcion(contenido_funcion):
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case)\b', contenido_funcion)
    operadores_logicos = re.findall(r'\b(&&|\|\|)\b', contenido_funcion)
    llamadas_funciones = re.findall(r'\b\w+\s*\(', contenido_funcion)
    
    complejidad = {
        'estructuras_control': Counter(estructuras_control),
        'operadores_logicos': len(operadores_logicos),
        'llamadas_funciones': len(llamadas_funciones),
        'complejidad_ciclomatica': len(estructuras_control) + len(operadores_logicos) + 1
    }
    return complejidad

def extraer_funciones_con_complejidad(contenido):
    patron_funcion = r'\b(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:override)?\s*{([^}]*)}'
    funciones = re.findall(patron_funcion, contenido, re.DOTALL)
    funciones_con_complejidad = {}
    for nombre_funcion, contenido_funcion in funciones:
        complejidad = calcular_complejidad_funcion(contenido_funcion)
        funciones_con_complejidad[nombre_funcion] = complejidad
    return funciones_con_complejidad

def ejecutar_cpplint(ruta_archivo):
    try:
        resultado = subprocess.run(
            ['cpplint', '--filter=-whitespace/comments', ruta_archivo],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return resultado.stderr
    except Exception as e:
        return f"Error ejecutando cpplint en {ruta_archivo}: {str(e)}"

def analizar_indentacion(salida_cpplint):
    errores_indentacion = [error for error in salida_cpplint.split('\n') if 'whitespace/indent' in error]
    return len(errores_indentacion) == 0

def calcular_hash_contenido(contenido):
    return hashlib.md5(contenido.encode()).hexdigest()

def analizar_archivo(ruta_completa):
    contenido = leer_archivo(ruta_completa)
    if contenido is None:
        return None
    
    elementos = extraer_elementos(contenido)
    funciones_con_complejidad = extraer_funciones_con_complejidad(contenido)
    salida_cpplint = ejecutar_cpplint(ruta_completa)
    indentacion_correcta = analizar_indentacion(salida_cpplint)
    hash_contenido = calcular_hash_contenido(contenido)
    
    return {
        'clases': {
            'nombres': elementos['clases'],
            'total': len(elementos['clases']),
            'existe': len(elementos['clases']) > 0
        },
        'funciones': {
            'nombres': elementos['funciones'],
            'total': len(elementos['funciones']),
            'existe': len(elementos['funciones']) > 0,
            'complejidad': funciones_con_complejidad
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
        'indentacion_correcta': indentacion_correcta,
        'hash_contenido': hash_contenido
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
    
    resultados_globales = {}
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
                        resultados_globales[archivo] = resultado
                        print(f"✅ Análisis completado para {archivo}")
                        print(f"📊 Resultados guardados en: {ruta_resultado}")

    # Análisis de posible plagio
    hashes_unicos = set()
    archivos_duplicados = []
    for archivo, resultado in resultados_globales.items():
        if resultado['hash_contenido'] in hashes_unicos:
            archivos_duplicados.append(archivo)
        else:
            hashes_unicos.add(resultado['hash_contenido'])

    if archivos_duplicados:
        print("\n⚠️ Posible plagio detectado en los siguientes archivos:")
        for archivo in archivos_duplicados:
            print(f"  - {archivo}")
    else:
        print("\n✅ No se detectaron archivos duplicados.")

    print("\n🎉 Análisis de todos los archivos completado.")

if __name__ == "__main__":
    main()
