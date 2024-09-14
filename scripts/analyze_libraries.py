import os
import re
from datetime import datetime
from collections import Counter

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
        print(f"❌ Error al analizar el archivo {ruta_archivo}: {str(e)}")
    return librerias

def analizar_proyecto(ruta_proyecto):
    reporte = {
        "fecha_hora": datetime.now().isoformat(),
        "librerias_por_archivo": {},
        "estadisticas_generales": {
            "total_archivos": 0,
            "total_librerias_usadas": 0,
            "librerias_unicas": set(),
            "librerias_estandar": set(),
            "librerias_personalizadas": set(),
            "frecuencia_librerias": Counter()
        }
    }

    for carpeta in ['src', 'test']:
        ruta_carpeta = os.path.join(ruta_proyecto, carpeta)
        if not os.path.exists(ruta_carpeta):
            continue
        for raiz, _, archivos in os.walk(ruta_carpeta):
            for archivo in archivos:
                if archivo.endswith(('.cpp', '.h', '.hpp')):
                    ruta_completa = os.path.join(raiz, archivo)
                    ruta_relativa = os.path.relpath(ruta_completa, ruta_proyecto)
                    librerias = analizar_librerias_en_archivo(ruta_completa)
                    reporte["librerias_por_archivo"][ruta_relativa] = librerias
                    reporte["estadisticas_generales"]["total_archivos"] += 1
                    reporte["estadisticas_generales"]["total_librerias_usadas"] += len(librerias)
                    reporte["estadisticas_generales"]["librerias_unicas"].update(librerias)
                    reporte["estadisticas_generales"]["frecuencia_librerias"].update(librerias)

                    for libreria in librerias:
                        if libreria.startswith(('<', 'std')):
                            reporte["estadisticas_generales"]["librerias_estandar"].add(libreria)
                        else:
                            reporte["estadisticas_generales"]["librerias_personalizadas"].add(libreria)

    return reporte

def generar_markdown(reporte):
    md = f"# 📚 Reporte de Análisis de Librerías\n\n"
    md += f"📅 Fecha y hora del análisis: {reporte['fecha_hora']}\n\n"

    md += "## 📊 Estadísticas Generales\n\n"
    stats = reporte['estadisticas_generales']
    md += f"- 📁 Total de archivos analizados: **{stats['total_archivos']}**\n"
    md += f"- 📚 Total de librerías usadas (incluyendo repeticiones): **{stats['total_librerias_usadas']}**\n"
    md += f"- 📈 Promedio de librerías por archivo: **{stats['total_librerias_usadas'] / stats['total_archivos']:.2f}**\n"
    md += f"- 🆕 Número de librerías únicas: **{len(stats['librerias_unicas'])}**\n"
    md += f"- 🏛️ Número de librerías estándar: **{len(stats['librerias_estandar'])}**\n"
    md += f"- 🛠️ Número de librerías personalizadas: **{len(stats['librerias_personalizadas'])}**\n\n"

    md += "### 🔝 Librerías más utilizadas\n\n"
    for libreria, frecuencia in sorted(stats['frecuencia_librerias'].items(), key=lambda x: x[1], reverse=True)[:10]:
        md += f"- `{libreria}`: **{frecuencia}** veces\n"
    md += "\n"

    md += "## 📂 Librerías utilizadas por archivo\n\n"
    for archivo, librerias in reporte['librerias_por_archivo'].items():
        md += f"### 📄 {archivo}\n"
        for libreria in librerias:
            md += f"- `{libreria}`\n"
        md += "\n"

    return md

def guardar_reporte(reporte, ruta_salida_md):
    os.makedirs(os.path.dirname(ruta_salida_md), exist_ok=True)
    markdown_content = generar_markdown(reporte)
    with open(ruta_salida_md, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def obtener_nombre_archivo_reporte():
    ahora = datetime.now()
    return f"REPORTE_ANALISIS_LIBRERIA_{ahora.strftime('%Y%m%d_%H%M%S')}.MD"

def main():
    print("🔍 Iniciando análisis de librerías...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio_salida = os.path.join(ruta_proyecto, "output")
    nombre_archivo = obtener_nombre_archivo_reporte()
    ruta_salida_md = os.path.join(directorio_salida, nombre_archivo)

    try:
        reporte = analizar_proyecto(ruta_proyecto)
        guardar_reporte(reporte, ruta_salida_md)
        print("✅ Análisis completado con éxito.")
        print(f"📄 Reporte generado y guardado en:")
        print(f"   {ruta_salida_md}")
        
        # Mostrar un resumen en la consola
        stats = reporte['estadisticas_generales']
        print("\n📊 Resumen del análisis:")
        print(f"   Total de archivos analizados: {stats['total_archivos']}")
        print(f"   Total de librerías usadas: {stats['total_librerias_usadas']}")
        print(f"   Librerías únicas: {len(stats['librerias_unicas'])}")
        print(f"   Librerías estándar: {len(stats['librerias_estandar'])}")
        print(f"   Librerías personalizadas: {len(stats['librerias_personalizadas'])}")
    except Exception as e:
        print(f"❌ Error al generar el reporte: {str(e)}")

if __name__ == "__main__":
    main()
