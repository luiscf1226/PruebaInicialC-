import os
import re
from datetime import datetime
from spellchecker import SpellChecker
import unicodedata

# Función para extraer las salidas cout
def extraer_couts(contenido):
    patron_cout = r'cout\s*<<\s*"([^"]*)"(?:\s*<<\s*endl\s*)?;'
    return re.findall(patron_cout, contenido)

# Verifica palabras que tienen acentos incorrectos o que deberían llevar acento
def verificar_acentos_faltantes(texto, spell):
    palabras = re.findall(r'\b\w+\b', texto)
    errores = []

    for palabra in palabras:
        # Normalizamos la palabra para separar acentos
        palabra_normalizada = unicodedata.normalize('NFD', palabra)
        sin_acentos = ''.join(c for c in palabra_normalizada if unicodedata.category(c) != 'Mn')

        # Verificamos si la palabra original es distinta a la normalizada sin acentos
        if sin_acentos != palabra:
            # La palabra tiene acentos, verificamos si existe en el diccionario
            if sin_acentos.lower() not in spell:
                errores.append(f"Posible acento incorrecto en '{palabra}', sugerencia: '{sin_acentos}'")
        else:
            # La palabra no tiene acentos, verificamos si debería tener uno
            if palabra.lower() not in spell:
                correccion = spell.correction(palabra.lower())
                if correccion != palabra.lower():
                    errores.append(f"Posible acento faltante en '{palabra}', sugerencia: '{correccion}'")
    
    return errores

# Analiza el archivo .cpp para encontrar posibles errores de acentuación
def analizar_archivo(ruta_archivo, spell):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
    except Exception as e:
        return [], [f"Error al leer el archivo: {str(e)}"]

    salidas = extraer_couts(contenido)
    errores = []

    for salida in salidas:
        errores_acentos = verificar_acentos_faltantes(salida, spell)
        if errores_acentos:
            errores.append({"texto": salida, "errores": errores_acentos})

    return salidas, errores

# Analiza todos los archivos .cpp en el directorio src
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

# Genera el reporte en formato Markdown
def generar_reporte_md(reporte):
    md = f"# 📝 Reporte de Análisis de Acentos y Ortografía en Salidas cout\n\n"
    md += f"📅 Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## 📊 Estadísticas Generales\n\n"
    md += f"- 📁 Archivos analizados: **{reporte['archivos_analizados']}**\n"
    md += f"- 💬 Total de salidas encontradas: **{reporte['total_salidas']}**\n"
    md += f"- ⚠️ Salidas con errores: **{reporte['salidas_con_errores']}**\n"
    md += f"- 🚫 Total de errores detectados: **{reporte['total_errores']}**\n"
    if reporte['total_salidas'] > 0:
        md += f"- 📊 Porcentaje de salidas con errores: **{(reporte['salidas_con_errores'] / reporte['total_salidas']) * 100:.2f}%**\n\n"

    md += "## 📄 Detalles por Archivo\n\n"
    for archivo, datos in reporte["detalles"].items():
        md += f"### 📎 Archivo: `{archivo}`\n\n"
        
        if datos['salidas']:
            md += "#### 💬 Salidas encontradas:\n\n"
            for salida in datos['salidas']:
                md += f"- ```{salida}```\n"
            md += "\n"
        
        if datos['errores']:
            md += "#### ⚠️ Posibles errores ortográficos y de acentuación:\n\n"
            for error in datos['errores']:
                md += f"- Texto: ```{error['texto']}```\n"
                for e in error['errores']:
                    md += f"  - 🔍 {e}\n"
                md += "\n"

    return md

# Función principal
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
