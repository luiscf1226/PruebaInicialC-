import os
import re
from datetime import datetime
from spellchecker import SpellChecker
import unicodedata

def extraer_couts(contenido):
    patron_cout = r'cout\s*<<\s*"([^"]*)"(?:\s*<<\s*endl\s*)?;'
    return re.findall(patron_cout, contenido)

def verificar_ortografia(texto, spell):
    palabras = re.findall(r'\b\w+\b', texto.lower())
    errores = spell.unknown(palabras)
    return [f"Posible error en '{palabra}': {spell.correction(palabra)}" for palabra in errores]

def verificar_acentos(texto):
    palabras = re.findall(r'\b\w+\b', texto)
    errores = []
    for palabra in palabras:
        if any(c in 'áéíóúÁÉÍÓÚ' for c in palabra):
            sin_acentos = ''.join(c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn')
            if sin_acentos != palabra and sin_acentos in spell:
                errores.append(f"Posible acento incorrecto en '{palabra}', podría ser '{sin_acentos}'")
    return errores

def analizar_archivo(ruta_archivo, spell):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
    except Exception as e:
        return [], [f"Error al leer el archivo: {str(e)}"]
    
    salidas = extraer_couts(contenido)
    errores = []
    
    for salida in salidas:
        errores_ortografia = verificar_ortografia(salida, spell)
        errores_acentos = verificar_acentos(salida)
        if errores_ortografia or errores_acentos:
            errores.append({"texto": salida, "errores": errores_ortografia + errores_acentos})
    
    return salidas, errores

def analizar_proyecto(ruta_src, spell):
    reporte = {
        "archivos_analizados": 0,
        "total_salidas": 0,
        "salidas_con_errores": 0,
        "total_errores": 0,
        "detalles": {}
    }
    for raiz, dirs, archivos in os.walk(ruta_src):
        for archivo in archivos:
            if archivo.endswith('.cpp'):
                reporte["archivos_analizados"] += 1
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                salidas, errores = analizar_archivo(ruta_completa, spell)
                reporte["total_salidas"] += len(salidas)
                reporte["salidas_con_errores"] += len(errores)
                reporte["total_errores"] += sum(len(e["errores"]) for e in errores)
                if salidas or errores:
                    reporte["detalles"][ruta_relativa] = {'salidas': salidas, 'errores': errores}
    return reporte

def generar_reporte_md(reporte):
    md = f"# Reporte de Análisis de Salidas cout y Revisión Ortográfica\n\n"
    md += f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## Estadísticas Generales\n\n"
    md += f"- Archivos analizados: {reporte['archivos_analizados']}\n"
    md += f"- Total de salidas encontradas: {reporte['total_salidas']}\n"
    md += f"- Salidas con errores: {reporte['salidas_con_errores']}\n"
    md += f"- Total de errores detectados: {reporte['total_errores']}\n"
    if reporte['total_salidas'] > 0:
        md += f"- Porcentaje de salidas con errores: {(reporte['salidas_con_errores'] / reporte['total_salidas']) * 100:.2f}%\n\n"

    md += "## Detalles por Archivo\n\n"
    for archivo, datos in reporte["detalles"].items():
        md += f"### Archivo: {archivo}\n\n"
        
        if datos['salidas']:
            md += "#### Salidas encontradas:\n\n"
            for salida in datos['salidas']:
                md += f"- `{salida}`\n"
            md += "\n"
        
        if datos['errores']:
            md += "#### Posibles errores ortográficos y de acentuación:\n\n"
            for error in datos['errores']:
                md += f"- Texto: `{error['texto']}`\n"
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

    spell = SpellChecker(language='es')
    reporte = analizar_proyecto(ruta_src, spell)
    contenido_reporte = generar_reporte_md(reporte)

    os.makedirs(ruta_salida, exist_ok=True)
    archivo_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_ORTOGRAFIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(contenido_reporte)

    print(f"Análisis completado. Reporte guardado en {archivo_reporte}")

if __name__ == "__main__":
    main()
