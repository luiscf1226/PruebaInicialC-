import os
import re
from datetime import datetime

def analizar_indentacion(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
    except Exception as e:
        return {
            "error": f"No se pudo leer el archivo: {str(e)}",
            "lineas_totales": 0,
            "lineas_correctas": 0,
            "errores": []
        }

    nivel_indentacion = 0
    errores = []
    lineas_correctas = 0
    lineas_totales = 0
    espacios_por_nivel = 4

    for num_linea, linea in enumerate(lineas, 1):
        linea = linea.rstrip('\n\r')
        if linea.strip() == '' or linea.strip().startswith('//'):
            continue

        lineas_totales += 1
        espacios_iniciales = len(linea) - len(linea.lstrip())

        if espacios_iniciales != nivel_indentacion * espacios_por_nivel:
            errores.append(f"Línea {num_linea}: Indentación incorrecta (esperado {nivel_indentacion * espacios_por_nivel}, encontrado {espacios_iniciales})")
        else:
            lineas_correctas += 1

        if linea.strip().endswith('{'):
            nivel_indentacion += 1
        elif linea.strip().startswith('}'):
            nivel_indentacion = max(0, nivel_indentacion - 1)

    return {
        "lineas_totales": lineas_totales,
        "lineas_correctas": lineas_correctas,
        "errores": errores
    }

def analizar_proyecto(ruta_proyecto):
    ruta_src = os.path.join(ruta_proyecto, 'src')
    reporte = {}

    if not os.path.exists(ruta_src):
        return {"error": f"La carpeta 'src' no existe en {ruta_proyecto}"}

    for raiz, _, archivos in os.walk(ruta_src):
        for archivo in archivos:
            if archivo.endswith('.cpp'):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                reporte[ruta_relativa] = analizar_indentacion(ruta_completa)

    return reporte

def generar_reporte_md(reporte):
    md = f"# Reporte de Análisis de Indentación\n\n"
    md += f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    if "error" in reporte:
        md += f"Error: {reporte['error']}\n"
        return md

    total_archivos = len(reporte)
    total_lineas = sum(archivo_info["lineas_totales"] for archivo_info in reporte.values())
    total_lineas_correctas = sum(archivo_info["lineas_correctas"] for archivo_info in reporte.values())

    md += f"## Resumen\n\n"
    md += f"- Total de archivos analizados: {total_archivos}\n"
    md += f"- Total de líneas analizadas: {total_lineas}\n"

    if total_lineas > 0:
        porcentaje_correcto = (total_lineas_correctas / total_lineas) * 100
        md += f"- Porcentaje de líneas con indentación correcta: {porcentaje_correcto:.2f}%\n\n"
    else:
        md += "- No se encontraron líneas para analizar\n\n"

    md += "## Detalles por Archivo\n\n"
    for archivo, info in reporte.items():
        md += f"### {archivo}\n\n"
        if "error" in info:
            md += f"Error: {info['error']}\n"
        else:
            md += f"- Líneas totales: {info['lineas_totales']}\n"
            md += f"- Líneas con indentación correcta: {info['lineas_correctas']}\n"
            if info['lineas_totales'] > 0:
                porcentaje = (info['lineas_correctas'] / info['lineas_totales']) * 100
                md += f"- Porcentaje de indentación correcta: {porcentaje:.2f}%\n"
            if info['errores']:
                md += "- Errores de indentación:\n"
                for error in info['errores']:
                    md += f"  - {error}\n"
        md += "\n"

    return md

def main():
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_salida = os.path.join(ruta_proyecto, "output", "reporte_indentacion.md")

    reporte_indentacion = analizar_proyecto(ruta_proyecto)
    contenido_reporte = generar_reporte_md(reporte_indentacion)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
        archivo_salida.write(contenido_reporte)

    print(f"Reporte de indentación generado en: {ruta_salida}")

if __name__ == "__main__":
    main()
