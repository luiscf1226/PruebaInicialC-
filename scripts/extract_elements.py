import os
import re
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

def buscar_carpeta_proyecto(ruta_src):
    for carpeta in os.listdir(ruta_src):
        ruta_carpeta = os.path.join(ruta_src, carpeta)
        if os.path.isdir(ruta_carpeta):
            for archivo in os.listdir(ruta_carpeta):
                if archivo.endswith('.cpp'):
                    return ruta_carpeta
    return ruta_src

def extraer_couts(contenido):
    patron_cout = r'cout\s*<<\s*"([^"]*)"(?:\s*<<\s*endl\s*)?;'
    return re.findall(patron_cout, contenido)

def verificar_acentos(texto):
    palabras_con_acento = re.findall(r'\b\w*[áéíóúÁÉÍÓÚ]\w*\b', texto)
    return [f"Posible acento en '{palabra}'" for palabra in palabras_con_acento]

def analizar_archivo(ruta_archivo):
    contenido = leer_archivo(ruta_archivo)
    if contenido is None:
        return [], []

    salidas = extraer_couts(contenido)
    errores = []

    for salida in salidas:
        errores_acentos = verificar_acentos(salida)
        if errores_acentos:
            errores.append({"texto": salida, "errores": errores_acentos})

    return salidas, errores

def analizar_proyecto(ruta_src):
    reporte = {
        "archivos_analizados": 0,
        "total_salidas": 0,
        "salidas_con_errores": 0,
        "total_errores": 0,
        "detalles": {}
    }

    ruta_carpeta_proyecto = buscar_carpeta_proyecto(ruta_src)

    for raiz, dirs, archivos in os.walk(ruta_carpeta_proyecto):
        for archivo in archivos:
            if archivo.endswith('.cpp'):
                reporte["archivos_analizados"] += 1
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                salidas, errores = analizar_archivo(ruta_completa)
                reporte["total_salidas"] += len(salidas)
                reporte["salidas_con_errores"] += len(errores)
                reporte["total_errores"] += sum(len(e["errores"]) for e in errores)
                if salidas or errores:
                    reporte["detalles"][ruta_relativa] = {'salidas': salidas, 'errores': errores}
    return reporte

def generar_reporte_md(reporte):
    md = f"# Reporte de Análisis de Acentos en Salidas cout\n\n"
    md += f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## Estadísticas Generales\n\n"
    md += f"- Archivos analizados: {reporte['archivos_analizados']}\n"
    md += f"- Total de salidas encontradas: {reporte['total_salidas']}\n"
    md += f"- Salidas con posibles errores: {reporte['salidas_con_errores']}\n"
    md += f"- Total de posibles errores detectados: {reporte['total_errores']}\n"
    if reporte['total_salidas'] > 0:
        md += f"- Porcentaje de salidas con posibles errores: {(reporte['salidas_con_errores'] / reporte['total_salidas']) * 100:.2f}%\n\n"

    md += "## Detalles por Archivo\n\n"
    for archivo, datos in reporte["detalles"].items():
        md += f"### Archivo: `{archivo}`\n\n"
        
        if datos['salidas']:
            md += "#### Salidas encontradas:\n\n"
            for salida in datos['salidas']:
                md += f"- ```{salida}```\n"
            md += "\n"
        
        if datos['errores']:
            md += "#### Posibles errores de acentuación:\n\n"
            for error in datos['errores']:
                md += f"- Texto: ```{error['texto']}```\n"
                for e in error['errores']:
                    md += f"  - {e}\n"
                md += "\n"

    return md

def main():
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')

    if not os.path.exists(ruta_src):
        print(f"Error: No se encontró la carpeta src en {ruta_src}")
        return

    reporte = analizar_proyecto(ruta_src)
    contenido_reporte = generar_reporte_md(reporte)

    os.makedirs(ruta_salida, exist_ok=True)
    archivo_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_ACENTOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(contenido_reporte)

    print(f"Análisis completado. Reporte guardado en {archivo_reporte}")

if __name__ == "__main__":
    main()
