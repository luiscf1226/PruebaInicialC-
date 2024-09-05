import os
import json
import re
from datetime import datetime
import subprocess

def analizar_directorio(ruta):
    reporte = {}
    for raiz, directorios, archivos in os.walk(ruta):
        ruta_relativa = os.path.relpath(raiz, ruta)
        reporte[ruta_relativa] = {
            "cantidad_archivos": len(archivos),
            "archivos": archivos,
            "subdirectorios": directorios
        }

        archivos_cpp = [f for f in archivos if f.endswith(('.cpp', '.h', '.hpp'))]
        if archivos_cpp:
            reporte[ruta_relativa]["archivos_cpp"] = archivos_cpp
            reporte[ruta_relativa]["analisis_cpp"] = analizar_archivos_cpp(raiz, archivos_cpp)

    return reporte

def analizar_archivos_cpp(raiz, archivos_cpp):
    analisis = {}
    for archivo in archivos_cpp:
        ruta_archivo = os.path.join(raiz, archivo)
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                clases = analizar_clases(contenido)
                funciones = analizar_funciones(contenido)
                analisis[archivo] = {
                    "cantidad_lineas": len(contenido.split('\n')),
                    "clases": clases,
                    "funciones": funciones,
                    "cantidad_includes": contenido.count("#include"),
                    "cantidad_comentarios": len(re.findall(r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)', contenido)),
                    "cantidad_todos": len(re.findall(r'//\s*TODO:', contenido, re.IGNORECASE)),
                    "complejidad_ciclomatica": calcular_complejidad_ciclomatica(contenido),
                    "funcion_mas_larga": encontrar_funcion_mas_larga(contenido),
                    "cantidad_clases": len(clases),
                    "cantidad_funciones": len(funciones),
                    "librerias_incluidas": analizar_librerias(contenido)
                }
        except Exception as e:
            print(f"Error al analizar el archivo {archivo}: {str(e)}")
            analisis[archivo] = {"error": str(e)}
    return analisis

def analizar_clases(contenido):
    clases = []
    class_pattern = r'class\s+(\w+)\s*(?::\s*(public|private|protected)\s*(\w+))?\s*\{'
    for match in re.finditer(class_pattern, contenido):
        clase = {
            "nombre": match.group(1),
            "herencia": match.group(2) if match.group(2) else "N/A",
            "clase_base": match.group(3) if match.group(3) else "N/A",
            "metodos": analizar_metodos(contenido, match.start())
        }
        clases.append(clase)
    return clases

def analizar_metodos(contenido, start_pos):
    metodos = []
    method_pattern = r'(public|private|protected):\s*([\w\s\*&]+)\s+(\w+)\s*\([^\)]*\)'
    for match in re.finditer(method_pattern, contenido[start_pos:]):
        metodo = {
            "acceso": match.group(1),
            "tipo_retorno": match.group(2).strip(),
            "nombre": match.group(3)
        }
        metodos.append(metodo)
    return metodos

def analizar_funciones(contenido):
    funciones = []
    function_pattern = r'([\w\s\*&]+)\s+(\w+)\s*\(([^\)]*)\)'
    for match in re.finditer(function_pattern, contenido):
        if not re.search(r'\b(if|for|while|switch)\b', match.group(0)):  # Excluir condiciones de control
            funcion = {
                "tipo_retorno": match.group(1).strip(),
                "nombre": match.group(2),
                "parametros": match.group(3).strip()
            }
            funciones.append(funcion)
    return funciones

def calcular_complejidad_ciclomatica(contenido):
    puntos_decision = len(re.findall(r'\b(if|for|while|case|catch|\&\&|\|\|)\b', contenido))
    return puntos_decision + 1

def encontrar_funcion_mas_larga(contenido):
    funciones = re.findall(r'(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*{(?:[^{}]*{[^{}]*})*[^{}]*}', contenido)
    if not funciones:
        return {"nombre": "N/A", "longitud": 0}
    mas_larga = max(funciones, key=lambda f: len(f))
    return {"nombre": mas_larga, "longitud": len(mas_larga.split('\n'))}

def analizar_librerias(contenido):
    librerias = []
    for linea in contenido.split('\n'):
        if linea.strip().startswith('#include'):
            match = re.search(r'#include\s*[<"](.+)[>"]', linea)
            if match:
                librerias.append(match.group(1))
    return librerias

def verificar_estilo_codigo(ruta_archivo):
    try:
        resultado = subprocess.run(['clang-format', '-style=file', '-output-replacements-xml', ruta_archivo],
                                capture_output=True, text=True, check=True)
        reemplazos = resultado.stdout.count('<replacement ')
        return reemplazos
    except Exception:
        return "N/A (clang-format no disponible)"

def generar_reporte(ruta_proyecto):
    reporte = {
        "fecha_hora": datetime.now().isoformat(),
        "estructura_proyecto": analizar_directorio(ruta_proyecto),
        "analisis": {},
        "metricas_generales": {
            "total_archivos": 0,
            "total_archivos_cpp": 0,
            "total_lineas": 0,
            "total_clases": 0,
            "total_funciones": 0,
            "total_comentarios": 0,
            "promedio_complejidad_ciclomatica": 0,
            "violaciones_estilo": 0,
            "librerias_unicas": set()
        },
        "cumplimiento_estructura": {},
        "analisis_detallado": {}
    }

    directorios_esperados = ['src', 'test', 'scripts', '.github/workflows', 'input', 'expected_output', 'output']
    for directorio in directorios_esperados:
        if directorio in reporte["estructura_proyecto"]:
            reporte["cumplimiento_estructura"][f"{directorio}_existe"] = True
        else:
            reporte["cumplimiento_estructura"][f"{directorio}_existe"] = False
            reporte["cumplimiento_estructura"][f"{directorio}_faltante"] = f"La carpeta {directorio} debería existir pero no se encuentra."

    archivos_especificos = {
        'src/main.cpp': 'Archivo principal de C++',
        'README.md': 'Archivo README del proyecto',
        '.gitignore': 'Configuración de Git ignore',
        'scripts/analyze_project.py': 'Script de análisis del proyecto'
    }

    for ruta_archivo, descripcion in archivos_especificos.items():
        if os.path.exists(os.path.join(ruta_proyecto, ruta_archivo)):
            reporte["cumplimiento_estructura"][f"{ruta_archivo}_existe"] = True
        else:
            reporte["cumplimiento_estructura"][f"{ruta_archivo}_existe"] = False
            reporte["cumplimiento_estructura"][f"{ruta_archivo}_faltante"] = f"El archivo {ruta_archivo} ({descripcion}) debería existir pero no se encuentra."

    # Análisis detallado de todos los archivos .cpp
    for ruta, info in reporte["estructura_proyecto"].items():
        if "analisis_cpp" in info:
            reporte["analisis_detallado"][ruta] = info["analisis_cpp"]
            for archivo, analisis in info["analisis_cpp"].items():
                if "error" not in analisis:
                    reporte["metricas_generales"]["total_archivos"] += 1
                    reporte["metricas_generales"]["total_archivos_cpp"] += 1
                    reporte["metricas_generales"]["total_lineas"] += analisis["cantidad_lineas"]
                    reporte["metricas_generales"]["total_clases"] += analisis["cantidad_clases"]
                    reporte["metricas_generales"]["total_funciones"] += analisis["cantidad_funciones"]
                    reporte["metricas_generales"]["total_comentarios"] += analisis["cantidad_comentarios"]
                    reporte["metricas_generales"]["promedio_complejidad_ciclomatica"] += analisis["complejidad_ciclomatica"]
                    reporte["metricas_generales"]["librerias_unicas"].update(analisis["librerias_incluidas"])

    if reporte["metricas_generales"]["total_archivos_cpp"] > 0:
        reporte["metricas_generales"]["promedio_complejidad_ciclomatica"] /= reporte["metricas_generales"]["total_archivos_cpp"]

    reporte["metricas_generales"]["librerias_unicas"] = list(reporte["metricas_generales"]["librerias_unicas"])

    return reporte

def json_a_markdown(reporte):
    md = f"# Reporte de Análisis de Proyecto C++\n\n"
    md += f"Fecha y hora del análisis: {reporte['fecha_hora']}\n\n"

    md += "## Cumplimiento de Estructura del Proyecto\n\n"
    for clave, valor in reporte['cumplimiento_estructura'].items():
        md += f"- {clave}: {'Sí' if valor is True else 'No' if valor is False else valor}\n"

    md += "\n## Métricas Generales\n\n"
    for metrica, valor in reporte['metricas_generales'].items():
        if metrica != "librerias_unicas":
            md += f"- {metrica.replace('_', ' ').title()}: {valor}\n"
    
    md += f"\nLibrerías únicas utilizadas: {', '.join(reporte['metricas_generales']['librerias_unicas'])}\n"

    md += "\n## Análisis Detallado por Archivo\n\n"
    for ruta, archivos in reporte['analisis_detallado'].items():
        md += f"### {ruta}\n\n"
        for archivo, analisis in archivos.items():
            md += f"#### {archivo}\n\n"
            md += f"- Cantidad de líneas: {analisis['cantidad_lineas']}\n"
            md += f"- Complejidad ciclomática: {analisis['complejidad_ciclomatica']}\n"
            md += f"- Cantidad de includes: {analisis['cantidad_includes']}\n"
            md += f"- Cantidad de comentarios: {analisis['cantidad_comentarios']}\n"
            md += f"- Cantidad de TODOs: {analisis['cantidad_todos']}\n"
            md += f"- Cantidad de clases: {analisis['cantidad_clases']}\n"
            md += f"- Cantidad de funciones: {analisis['cantidad_funciones']}\n"
            md += f"- Librerías incluidas: {', '.join(analisis['librerias_incluidas'])}\n"

            md += "\nClases:\n"
            for clase in analisis['clases']:
                md += f"- {clase['nombre']} (Herencia: {clase['herencia']} de {clase['clase_base']})\n"
                for metodo in clase['metodos']:
                    md += f"  - {metodo['acceso']} {metodo['tipo_retorno']} {metodo['nombre']}()\n"

            md += "\nFunciones:\n"
            for funcion in analisis['funciones']:
                md += f"- {funcion['tipo_retorno']} {funcion['nombre']}({funcion['parametros']})\n"

            md += f"\nFunción más larga: {analisis['funcion_mas_larga']['nombre']} ({analisis['funcion_mas_larga']['longitud']} líneas)\n\n"

    return md

def guardar_reporte(reporte, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    # Guardar reporte JSON
    with open(os.path.join(os.path.dirname(ruta_salida), 'reporte.json'), 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    # Guardar reporte Markdown
    markdown_content = json_a_markdown(reporte)
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def obtener_nombre_archivo_reporte():
    ahora = datetime.now()
    return f"reporte_analisis_avanzado_{ahora.strftime('%Y%m%d_%H%M%S')}.md"

def listar_reportes_anteriores(directorio_salida):
    reportes = [f for f in os.listdir(directorio_salida) if f.startswith("reporte_analisis_avanzado_") and f.endswith(".md")]
    return sorted(reportes, reverse=True)

if __name__ == "__main__":
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio_salida = os.path.join(ruta_proyecto, "output")
    nombre_archivo = obtener_nombre_archivo_reporte()
    ruta_salida = os.path.join(directorio_salida, nombre_archivo)

    try:
        reporte = generar_reporte(ruta_proyecto)
        guardar_reporte(reporte, ruta_salida)
        print(f"Reporte avanzado generado y guardado en {ruta_salida}")

        reportes_anteriores = listar_reportes_anteriores(directorio_salida)
        if len(reportes_anteriores) > 1:
            print("\nReportes anteriores:")
            for i, reporte in enumerate(reportes_anteriores[:5], 1):
                print(f"{i}. {reporte}")
            if len(reportes_anteriores) > 5:
                print(f"... y {len(reportes_anteriores) - 5} más.")
    except Exception as e:
        print(f"Error al generar el reporte: {str(e)}")
        print("Estructura del proyecto encontrada:")
        for ruta, contenido in reporte['estructura_proyecto'].items():
            print(f"- {ruta}: {len(contenido.get('archivos', []))} archivos, {len(contenido.get('subdirectorios', []))} subdirectorios")
