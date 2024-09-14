import os
import re
import json
import hashlib
from collections import Counter
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

def extraer_elementos(contenido):
    variables = re.findall(r'\b(?:int|float|double|char|bool|string)\s+(\w+)', contenido)
    variables += re.findall(r'\bthis->(\w+)', contenido)
    funciones = re.findall(r'\b(\w+)\s*\([^)]*\)\s*{', contenido)
    clases = re.findall(r'\bclass\s+(\w+)', contenido)
    comentarios = re.findall(r'//.*?$|/\*.*?\*/', contenido, re.DOTALL | re.MULTILINE)
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case)\b', contenido)
    llamadas_funciones = re.findall(r'\b(\w+)\s*\(', contenido)
    tipos_datos = re.findall(r'\b(int|float|double|char|bool|string|auto)\b', contenido)
    operadores = re.findall(r'[+\-*/%=<>!&|^~]', contenido)
    
    return {
        'variables': variables,
        'funciones': funciones,
        'clases': clases,
        'comentarios': [c.strip() for c in comentarios],
        'estructuras_control': estructuras_control,
        'llamadas_funciones': llamadas_funciones,
        'tipos_datos': tipos_datos,
        'operadores': operadores
    }

def calcular_hash(texto):
    return hashlib.md5(texto.encode()).hexdigest()

def calcular_metricas_codigo(contenido):
    lineas = contenido.split('\n')
    return {
        'total_lineas': len(lineas),
        'lineas_codigo': len([l for l in lineas if l.strip() and not l.strip().startswith('//')]),
        'lineas_comentarios': len([l for l in lineas if l.strip().startswith('//')]),
        'lineas_vacias': len([l for l in lineas if not l.strip()]),
    }

def analizar_complejidad(contenido):
    return len(re.findall(r'\b(if|for|while|switch)\b', contenido))

def extraer_secuencias(contenido, longitud=3):
    tokens = re.findall(r'\b\w+\b|[+\-*/%=<>!&|^~;{}()\[\]]', contenido)
    return [' '.join(tokens[i:i+longitud]) for i in range(len(tokens) - longitud + 1)]

def analizar_archivos(ruta_src):
    resultados = {}
    todos_elementos = []
    todos_secuencias = []
    
    for raiz, _, ficheros in os.walk(ruta_src):
        for fichero in ficheros:
            if fichero.endswith(('.cpp', '.h')):
                ruta_completa = os.path.join(raiz, fichero)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                elementos = extraer_elementos(contenido)
                todos_elementos.append(' '.join(elementos['variables'] + elementos['funciones'] +
                                                elementos['clases'] + elementos['comentarios']))
                
                secuencias = extraer_secuencias(contenido)
                todos_secuencias.extend(secuencias)
                
                metricas = calcular_metricas_codigo(contenido)
                complejidad = analizar_complejidad(contenido)
                
                resultados[fichero] = {
                    'elementos': elementos,
                    'hash_contenido': calcular_hash(contenido),
                    'metricas': metricas,
                    'complejidad': complejidad,
                    'estadisticas': {
                        'num_variables': len(elementos['variables']),
                        'num_funciones': len(elementos['funciones']),
                        'num_clases': len(elementos['clases']),
                        'num_comentarios': len(elementos['comentarios']),
                        'freq_estructuras_control': dict(Counter(elementos['estructuras_control'])),
                        'freq_llamadas_funciones': dict(Counter(elementos['llamadas_funciones'])),
                        'freq_tipos_datos': dict(Counter(elementos['tipos_datos'])),
                        'freq_operadores': dict(Counter(elementos['operadores']))
                    },
                    'secuencias_comunes': Counter(secuencias).most_common(10)
                }
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(todos_elementos)
    
    for i, (fichero, datos) in enumerate(resultados.items()):
        datos['vector_tfidf'] = tfidf_matrix[i].toarray()[0].tolist()
    
    estadisticas_globales = {
        'total_archivos': len(resultados),
        'total_lineas': sum(datos['metricas']['total_lineas'] for datos in resultados.values()),
        'total_funciones': sum(datos['estadisticas']['num_funciones'] for datos in resultados.values()),
        'total_clases': sum(datos['estadisticas']['num_clases'] for datos in resultados.values()),
        'complejidad_promedio': sum(datos['complejidad'] for datos in resultados.values()) / len(resultados) if resultados else 0,
        'secuencias_mas_comunes': Counter(todos_secuencias).most_common(20)
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
    md += f"- 📝 Total de líneas de código: **{estadisticas['total_lineas']}**\n"
    md += f"- 🔧 Total de funciones: **{estadisticas['total_funciones']}**\n"
    md += f"- 🏗️ Total de clases: **{estadisticas['total_clases']}**\n"
    md += f"- 🔄 Complejidad promedio: **{estadisticas['complejidad_promedio']:.2f}**\n\n"

    md += "### 🔁 Secuencias más comunes\n\n"
    for seq, count in estadisticas['secuencias_mas_comunes'][:5]:
        md += f"- `{seq}`: {count} veces\n"

    return md

def main():
    print("🔍 Iniciando análisis de código...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_output = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_output, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ruta_resultados = os.path.join(ruta_output, f'caracteristicas_a_comparar_{timestamp}.json')
    ruta_reporte = os.path.join(ruta_output, f'reporte_analisis_{timestamp}.md')

    print("📊 Analizando archivos...")
    resultados = analizar_archivos(ruta_src)
    
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
