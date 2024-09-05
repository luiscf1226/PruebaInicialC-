
import os
import json
import re
from datetime import datetime

def analizar_librerias_en_archivo(ruta_archivo):
    librerias = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            for linea in contenido.split('\n'):
                if linea.strip().startswith('#include'):
                    match = re.search(r'#include\s*[<"](.+)[>"]', linea)
                    if match:
                        librerias.append(match.group(1))
    except Exception as e:
        print(f"Error al analizar el archivo {ruta_archivo}: {str(e)}")
    return librerias

def analizar_proyecto(ruta_proyecto):
    reporte = {
        "fecha_hora": datetime.now().isoformat(),
        "librerias_por_archivo": {},
        "librerias_unicas": set(),
        "librerias_estandar": set(),
        "librerias_personalizadas": set(),
        "estadisticas": {
            "total_archivos_cpp": 0,
            "total_librerias_usadas": 0,
            "promedio_librerias_por_archivo": 0
        }
    }

    ruta_src = os.path.join(ruta_proyecto, 'src')
    for raiz, directorios, archivos in os.walk(ruta_src):
        for archivo in archivos:
            if archivo.endswith(('.cpp', '.h', '.hpp')):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                librerias = analizar_librerias_en_archivo(ruta_completa)
                reporte["librerias_por_archivo"][ruta_relativa] = librerias
                reporte["librerias_unicas"].update(librerias)
                reporte["estadisticas"]["total_archivos_cpp"] += 1
                reporte["estadisticas"]["total_librerias_usadas"] += len(librerias)

                for libreria in librerias:
                    if libreria.startswith(('<', 'std')):
                        reporte["librerias_estandar"].add(libreria)
                    else:
                        reporte["librerias_personalizadas"].add(libreria)

    if reporte["estadisticas"]["total_archivos_cpp"] > 0:
        reporte["estadisticas"]["promedio_librerias_por_archivo"] = (
            reporte["estadisticas"]["total_librerias_usadas"] / reporte["estadisticas"]["total_archivos_cpp"]
        )

    reporte["librerias_unicas"] = list(reporte["librerias_unicas"])
    reporte["librerias_estandar"] = list(reporte["librerias_estandar"])
    reporte["librerias_personalizadas"] = list(reporte["librerias_personalizadas"])

    return reporte

def generar_markdown(reporte):
    md = f"# Reporte de Análisis de Librerías\n\n"
    md += f"Fecha y hora del análisis: {reporte['fecha_hora']}\n\n"

    md += "## Librerías utilizadas por archivo\n\n"
    for archivo, librerias in reporte['librerias_por_archivo'].items():
        md += f"### {archivo}\n"
        for libreria in librerias:
            md += f"- {libreria}\n"
        md += "\n"

    md += "## Librerías únicas utilizadas en el proyecto\n\n"
    for libreria in reporte['librerias_unicas']:
        md += f"- {libreria}\n"

    md += "\n## Librerías estándar utilizadas\n\n"
    for libreria in reporte['librerias_estandar']:
        md += f"- {libreria}\n"

    md += "\n## Librerías personalizadas utilizadas\n\n"
    for libreria in reporte['librerias_personalizadas']:
        md += f"- {libreria}\n"

    md += "\n## Estadísticas\n\n"
    md += f"- Total de archivos analizados: {reporte['estadisticas']['total_archivos_cpp']}\n"
    md += f"- Total de librerías usadas (incluyendo repeticiones): {reporte['estadisticas']['total_librerias_usadas']}\n"
    md += f"- Promedio de librerías por archivo: {reporte['estadisticas']['promedio_librerias_por_archivo']:.2f}\n"
    md += f"- Número de librerías únicas: {len(reporte['librerias_unicas'])}\n"
    md += f"- Número de librerías estándar: {len(reporte['librerias_estandar'])}\n"
    md += f"- Número de librerías personalizadas: {len(reporte['librerias_personalizadas'])}\n"

    return md

def guardar_reporte(reporte, ruta_salida_json, ruta_salida_md):
    os.makedirs(os.path.dirname(ruta_salida_json), exist_ok=True)

    # Guardar reporte JSON
    with open(ruta_salida_json, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    # Guardar reporte Markdown
    markdown_content = generar_markdown(reporte)
    with open(ruta_salida_md, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def obtener_nombre_archivo_reporte():
    ahora = datetime.now()
    return f"reporte_analisis_librerias_{ahora.strftime('%Y%m%d_%H%M%S')}"

if __name__ == "__main__":
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio_salida = os.path.join(ruta_proyecto, "output")
    nombre_archivo = obtener_nombre_archivo_reporte()
    ruta_salida_json = os.path.join(directorio_salida, f"{nombre_archivo}.json")
    ruta_salida_md = os.path.join(directorio_salida, f"{nombre_archivo}.md")

    try:
        reporte = analizar_proyecto(ruta_proyecto)
        guardar_reporte(reporte, ruta_salida_json, ruta_salida_md)
        print(f"Reporte de análisis de librerías generado y guardado en:")
        print(f"- JSON: {ruta_salida_json}")
        print(f"- Markdown: {ruta_salida_md}")
    except Exception as e:
        print(f"Error al generar el reporte: {str(e)}")
