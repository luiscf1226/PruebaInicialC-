import os
import subprocess
from datetime import datetime

def buscar_carpeta_proyecto(ruta_src):
    for item in os.listdir(ruta_src):
        ruta_item = os.path.join(ruta_src, item)
        if os.path.isdir(ruta_item):
            if any(archivo.endswith(('.cpp', '.h')) for archivo in os.listdir(ruta_item)):
                return ruta_item
    return ruta_src

def ejecutar_cpplint(ruta_archivo):
    try:
        # Ejecutar cpplint y capturar la salida
        resultado = subprocess.run(
            ['cpplint', '--filter=-whitespace/comments', ruta_archivo],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        salida = resultado.stderr  # cpplint escribe los resultados en stderr
        return salida
    except Exception as e:
        return f"Error ejecutando cpplint en {ruta_archivo}: {str(e)}"

def analizar_resultados_cpplint(salida_cpplint):
    errores = []
    lineas = salida_cpplint.strip().split('\n')
    for linea in lineas:
        if 'Total errors found:' in linea:
            continue  # Saltar el resumen final
        if linea:
            errores.append(linea)
    return errores

def analizar_proyecto(ruta_src):
    reporte = {}
    archivos_analizados = []

    ruta_carpeta_proyecto = buscar_carpeta_proyecto(ruta_src)

    for raiz, dirs, archivos in os.walk(ruta_carpeta_proyecto):
        for archivo in archivos:
            if archivo.endswith(('.cpp', '.h', '.hpp')):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                salida_cpplint = ejecutar_cpplint(ruta_completa)
                errores = analizar_resultados_cpplint(salida_cpplint)
                total_lineas = sum(1 for _ in open(ruta_completa, 'r', encoding='utf-8', errors='ignore'))
                reporte[ruta_relativa] = {
                    'errores': errores,
                    'total_lineas': total_lineas,
                    'lineas_correctas': total_lineas - len(errores)
                }
                archivos_analizados.append(ruta_relativa)

    return reporte, archivos_analizados

def generar_reporte_md(reporte, archivos_analizados):
    md = f"# 📊 Reporte de Análisis de Indentación con cpplint\n\n"
    md += f"📅 Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    md += "## 📈 Estadísticas Generales\n\n"
    md += "| Archivo | Líneas Totales | Errores de Indentación |\n"
    md += "|:--------|---------------:|-----------------------:|\n"

    total_lineas_proyecto = 0
    total_errores_proyecto = 0

    for archivo, datos in reporte.items():
        total_lineas = datos['total_lineas']
        errores_indentacion = sum(1 for error in datos['errores'] if 'whitespace/indent' in error)
        md += f"| {archivo} | {total_lineas} | {errores_indentacion} |\n"

        total_lineas_proyecto += total_lineas
        total_errores_proyecto += errores_indentacion

    md += f"\n**Total del Proyecto:** {total_lineas_proyecto} líneas, {total_errores_proyecto} errores de indentación\n\n"

    md += "## 🔍 Detalles por Archivo\n\n"
    for archivo, datos in reporte.items():
        md += f"### 📄 Archivo: {archivo}\n\n"

        errores_indentacion = [error for error in datos['errores'] if 'whitespace/indent' in error]
        if errores_indentacion:
            md += "#### ❌ Errores de indentación encontrados:\n\n"
            for error in errores_indentacion:
                md += f"- 🔴 {error}\n"
            md += "\n"
        else:
            md += "✅ No se encontraron errores de indentación.\n\n"

    md += "\n## 📁 Archivos Analizados\n\n"
    for archivo in archivos_analizados:
        md += f"- {archivo}\n"

    return md

def main():
    print("🔍 Iniciando análisis de indentación con cpplint...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')

    if not os.path.exists(ruta_src):
        print(f"❌ Error: No se encontró la carpeta src en {ruta_src}")
        return

    reporte, archivos_analizados = analizar_proyecto(ruta_src)
    contenido_reporte = generar_reporte_md(reporte, archivos_analizados)

    os.makedirs(ruta_salida, exist_ok=True)
    archivo_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_INDENTACION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(contenido_reporte)

    print(f"✅ Análisis de indentación completado.")
    print(f"📄 Reporte guardado en: {archivo_reporte}")

    # Mostrar un resumen en la consola
    total_archivos = len(reporte)
    total_lineas = sum(datos['total_lineas'] for datos in reporte.values())
    total_errores = sum(len([error for error in datos['errores'] if 'whitespace/indent' in error]) for datos in reporte.values())
    porcentaje_correcto = ((total_lineas - total_errores) / total_lineas * 100) if total_lineas > 0 else 0

    print("\n📊 Resumen del análisis:")
    print(f"   Total de archivos analizados: {total_archivos}")
    print(f"   Archivos analizados: {', '.join(archivos_analizados)}")
    print(f"   Total de líneas analizadas: {total_lineas}")
    print(f"   Total de errores de indentación: {total_errores}")
    print(f"   Porcentaje de líneas correctas: {porcentaje_correcto:.2f}%")

    ruta_carpeta_proyecto = buscar_carpeta_proyecto(ruta_src)
    if ruta_carpeta_proyecto != ruta_src:
        print(f"\n🖥️ Se detectó un proyecto de Visual Studio en: {os.path.relpath(ruta_carpeta_proyecto, ruta_src)}")
    else:
        print("\n🍎 No se detectó una estructura de Visual Studio. Asumiendo proyecto de Mac.")

if __name__ == "__main__":
    main()
