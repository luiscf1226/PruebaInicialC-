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

def analizar_archivos(carpetas_proyecto):
    resultados = {}
    
    for carpeta in carpetas_proyecto:
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.endswith(('.cpp', '.h')):
                    ruta_completa = os.path.join(raiz, archivo)
                    contenido = leer_archivo(ruta_completa)
                    if contenido is None:
                        continue
                    
                    elementos = extraer_elementos(contenido)
                    complejidad = calcular_complejidad(contenido)
                    
                    resultados[ruta_completa] = {
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
    
    estadisticas_globales = {
        'total_archivos': len(resultados),
        'total_clases': sum(datos['clases']['total'] for datos in resultados.values()),
        'total_funciones': sum(datos['funciones']['total'] for datos in resultados.values()),
        'total_variables': sum(datos['variables']['total'] for datos in resultados.values()),
        'total_librerias': sum(datos['librerias']['total'] for datos in resultados.values()),
        'complejidad_promedio': sum(datos['complejidad']['complejidad_ciclomatica'] for datos in resultados.values()) / len(resultados) if resultados else 0
    }
    
    return {
        'archivos': resultados,
        'estadisticas_globales': estadisticas_globales
    }

def guardar_resultados(resultados, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

def generar_reporte_md(resultados):
    estadisticas = resultados['estadisticas_globales']
    md = f"# 📊 Reporte de Análisis de Código\n\n"
    md += f"📅 Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## 📈 Estadísticas Globales\n\n"
    md += f"- 📁 Total de archivos analizados: **{estadisticas['total_archivos']}**\n"
    md += f"- 🏗️ Total de clases: **{estadisticas['total_clases']}**\n"
    md += f"- 🔧 Total de funciones: **{estadisticas['total_funciones']}**\n"
    md += f"- 📊 Total de variables: **{estadisticas['total_variables']}**\n"
    md += f"- 📚 Total de librerías: **{estadisticas['total_librerias']}**\n"
    md += f"- 🔄 Complejidad ciclomática promedio: **{estadisticas['complejidad_promedio']:.2f}**\n\n"

    md += "## 📑 Detalles por Archivo\n\n"
    for archivo, datos in resultados['archivos'].items():
        md += f"### {os.path.basename(archivo)}\n\n"
        md += f"Ruta: {archivo}\n\n"
        md += f"- Clases: {datos['clases']['total']} ({', '.join(datos['clases']['nombres'][:5])})\n"
        md += f"- Funciones: {datos['funciones']['total']} ({', '.join(datos['funciones']['nombres'][:5])})\n"
        md += f"- Variables: {datos['variables']['total']}\n"
        md += f"- Comentarios: {datos['comentarios']['total']}\n"
        md += f"- Librerías: {datos['librerias']['total']} ({', '.join(datos['librerias']['nombres'])})\n"
        md += f"- Complejidad Ciclomática: {datos['complejidad']['complejidad_ciclomatica']}\n"
        md += f"- Estructuras de Control: {dict(datos['complejidad']['estructuras_control'])}\n"
        md += f"- Operadores Lógicos: {datos['complejidad']['operadores_logicos']}\n"
        md += f"- Llamadas a Funciones: {datos['complejidad']['llamadas_funciones']}\n\n"

    return md

def main():
    print("🔍 Iniciando análisis de código...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_output = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_output, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ruta_resultados = os.path.join(ruta_output, f'analisis_codigo_{timestamp}.json')
    ruta_reporte = os.path.join(ruta_output, f'reporte_analisis_{timestamp}.md')

    print("🔎 Buscando carpetas del proyecto...")
    carpetas_proyecto = buscar_carpetas_proyecto(ruta_src)

    print(f"📂 Carpetas encontradas: {len(carpetas_proyecto)}")
    print("📊 Analizando archivos...")
    resultados = analizar_archivos(carpetas_proyecto)
    
    print("💾 Guardando resultados detallados...")
    guardar_resultados(resultados, ruta_resultados)

    print("📝 Generando reporte resumido...")
    reporte_md = generar_reporte_md(resultados)
    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        f.write(reporte_md)

    print(f"✅ Análisis completado.")
    print(f"📊 Resultados detallados guardados en: {ruta_resultados}")
    print(f"📑 Reporte resumido guardado en: {ruta_reporte}")

if __name__ == "__main__":
    main()
