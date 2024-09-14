import os
import re
from datetime import datetime

def analizar_indentacion(contenido):
    lineas = contenido.split('\n')
    errores = []
    nivel_indentacion_esperado = 0
    total_lineas = 0
    
    for numero, linea in enumerate(lineas, 1):
        linea_stripped = linea.strip()
        if not linea_stripped:  # Ignorar líneas vacías
            continue
        
        total_lineas += 1
        
        # Contar espacios al inicio de la línea
        espacios_iniciales = len(linea) - len(linea.lstrip())
        nivel_actual = espacios_iniciales // 4  # Asumimos que 4 espacios es una indentación
        
        # Ajustar el nivel de indentación esperado
        if linea_stripped.endswith('{'):
            if nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
            nivel_indentacion_esperado += 1
        elif linea_stripped.startswith('}'):
            nivel_indentacion_esperado = max(0, nivel_indentacion_esperado - 1)
            if nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
        elif nivel_actual != nivel_indentacion_esperado:
            errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
    
    return errores, total_lineas

def analizar_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
        return analizar_indentacion(contenido)
    except Exception as e:
        return [f"Error al leer el archivo: {str(e)}"], 0

def analizar_proyecto(ruta_src):
    reporte = {}
    for raiz, dirs, archivos in os.walk(ruta_src):
        for archivo in archivos:
            if archivo.endswith('.cpp'):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                errores, total_lineas = analizar_archivo(ruta_completa)
                reporte[ruta_relativa] = {
                    'errores': errores,
                    'total_lineas': total_lineas,
                    'lineas_correctas': total_lineas - len(errores)
                }
    return reporte

def generar_reporte_md(reporte):
    md = f"# 📊 Reporte de Análisis de Indentación\n\n"
    md += f"📅 Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## 📈 Estadísticas Generales\n\n"
    md += "| Archivo | Líneas Totales | Líneas Correctas | Porcentaje Correcto |\n"
    md += "|:--------|---------------:|------------------:|--------------------:|\n"

    total_lineas_proyecto = 0
    total_lineas_correctas_proyecto = 0

    for archivo, datos in reporte.items():
        total_lineas = datos['total_lineas']
        lineas_correctas = datos['lineas_correctas']
        porcentaje_correcto = (lineas_correctas / total_lineas * 100) if total_lineas > 0 else 0
        md += f"| {archivo} | {total_lineas} | {lineas_correctas} | {porcentaje_correcto:.2f}% |\n"
        
        total_lineas_proyecto += total_lineas
        total_lineas_correctas_proyecto += lineas_correctas

    porcentaje_correcto_proyecto = (total_lineas_correctas_proyecto / total_lineas_proyecto * 100) if total_lineas_proyecto > 0 else 0
    md += f"\n**Total del Proyecto:** {total_lineas_proyecto} líneas, {total_lineas_correctas_proyecto} correctas, {porcentaje_correcto_proyecto:.2f}% correcto\n\n"

    md += "## 🔍 Detalles por Archivo\n\n"
    for archivo, datos in reporte.items():
        md += f"### 📄 Archivo: {archivo}\n\n"
        
        if datos['errores']:
            md += "#### ❌ Errores de indentación encontrados:\n\n"
            for error in datos['errores']:
                md += f"- 🔴 {error}\n"
            md += "\n"
        else:
            md += "✅ No se encontraron errores de indentación.\n\n"

    return md

def main():
    print("🔍 Iniciando análisis de indentación...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')

    if not os.path.exists(ruta_src):
        print(f"❌ Error: No se encontró la carpeta src en {ruta_src}")
        return

    reporte = analizar_proyecto(ruta_src)
    contenido_reporte = generar_reporte_md(reporte)

    os.makedirs(ruta_salida, exist_ok=True)
    archivo_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_INDENTACION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(contenido_reporte)

    print(f"✅ Análisis de indentación completado.")
    print(f"📄 Reporte guardado en: {archivo_reporte}")

    # Mostrar un resumen en la consola
    total_archivos = len(reporte)
    total_lineas = sum(datos['total_lineas'] for datos in reporte.values())
    total_errores = sum(len(datos['errores']) for datos in reporte.values())
    porcentaje_correcto = ((total_lineas - total_errores) / total_lineas * 100) if total_lineas > 0 else 0

    print("\n📊 Resumen del análisis:")
    print(f"   Total de archivos analizados: {total_archivos}")
    print(f"   Total de líneas analizadas: {total_lineas}")
    print(f"   Total de errores de indentación: {total_errores}")
    print(f"   Porcentaje de líneas correctas: {porcentaje_correcto:.2f}%")

if __name__ == "__main__":
    main()
