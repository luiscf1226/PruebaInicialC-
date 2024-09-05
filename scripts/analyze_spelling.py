import os
import re
from datetime import datetime
from spellchecker import SpellChecker

def extraer_couts(contenido):
    patron_cout = r'cout\s*<<\s*(.*?)(?:<<\s*endl\s*)?;'
    matches = re.findall(patron_cout, contenido, re.DOTALL)
    salidas = []
    for match in matches:
        partes = re.split(r'\s*<<\s*', match)
        salida = ' '.join(parte.strip('" ') for parte in partes if parte.strip('" '))
        if salida:
            salidas.append(salida)
    return salidas

def verificar_ortografia(texto, spell):
    palabras = re.findall(r'\b\w+\b', texto.lower())
    errores = spell.unknown(palabras)
    return [f"Posible error en '{palabra}': {spell.correction(palabra)}" for palabra in errores]

def analizar_archivo(ruta_archivo, spell):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
    except Exception as e:
        return [], [f"Error al leer el archivo: {str(e)}"]
    
    salidas = extraer_couts(contenido)
    errores = []
    
    for salida in salidas:
        errores_salida = verificar_ortografia(salida, spell)
        if errores_salida:
            errores.append({"texto": salida, "errores": errores_salida})
    
    return salidas, errores

def analizar_proyecto(ruta_src, spell):
    reporte = {}
    for raiz, dirs, archivos in os.walk(ruta_src):
        for archivo in archivos:
            if archivo.endswith('.cpp'):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                salidas, errores = analizar_archivo(ruta_completa, spell)
                if salidas or errores:
                    reporte[ruta_relativa] = {'salidas': salidas, 'errores': errores}
    return reporte

def generar_reporte_md(reporte):
    md = f"# Reporte de Análisis de Salidas cout y Revisión Ortográfica\n\n"
    md += f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for archivo, datos in reporte.items():
        md += f"## Archivo: {archivo}\n\n"
        
        if datos['salidas']:
            md += "### Salidas encontradas:\n\n"
            for salida in datos['salidas']:
                md += f"- `{salida}`\n"
            md += "\n"
        
        if datos['errores']:
            md += "### Posibles errores ortográficos:\n\n"
            for error in datos['errores']:
                md += f"- Texto: `{error['texto']}`\n"
                for e in error['errores']:
                    md += f"  - {e}\n"
                md += "\n"
        
        if not datos['salidas'] and not datos['errores']:
            md += "No se encontraron salidas cout ni errores ortográficos.\n\n"

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
    archivo_reporte = os.path.join(ruta_salida, f"reporte_couts_ortografia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(contenido_reporte)

    print(f"Análisis completado. Reporte guardado en {archivo_reporte}")

if __name__ == "__main__":
    main()
