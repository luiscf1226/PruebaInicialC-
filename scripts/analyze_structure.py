import os
from datetime import datetime

def identificar_archivo_cpp_principal(ruta_src):
    """
    Identifica la carpeta dentro de 'src/' que contiene el archivo .cpp principal
    con el mismo nombre de la carpeta (como lo haría Visual Studio).
    """
    for carpeta in os.listdir(ruta_src):
        ruta_carpeta = os.path.join(ruta_src, carpeta)
        if os.path.isdir(ruta_carpeta):
            # Buscar el archivo .cpp con el mismo nombre que la carpeta
            archivo_cpp = os.path.join(ruta_carpeta, f"{carpeta}.cpp")
            if os.path.isfile(archivo_cpp):
                return archivo_cpp
    return None

def analizar_estructura(ruta_proyecto):
    estructura_esperada = {
        'src': 'Carpeta',
        'test': 'Carpeta',
        'scripts': 'Carpeta',
        '.github/workflows': 'Carpeta',
        'input': 'Carpeta',
        'expected_output': 'Carpeta',
        'output': 'Carpeta',
        'README.md': 'Archivo',
        '.gitignore': 'Archivo',
        'scripts/analyze_structure.py': 'Archivo'
    }
#
    # Inicializamos el reporte
    reporte = {
        "fecha_hora": datetime.now().isoformat(),
        "cumplimiento_estructura": {},
        "estadisticas": {
            "total_elementos": len(estructura_esperada),
            "elementos_presentes": 0,
            "elementos_faltantes": 0
        }
    }

    # Ruta del proyecto
    ruta_src = os.path.join(ruta_proyecto, 'src')

    # Buscar archivo principal .cpp dentro de la carpeta src
    archivo_cpp_principal = identificar_archivo_cpp_principal(ruta_src)
    if archivo_cpp_principal:
        estructura_esperada[archivo_cpp_principal] = 'Archivo'
        reporte["estadisticas"]["total_elementos"] += 1

    # Comenzamos a verificar si los elementos existen
    for ruta, tipo in estructura_esperada.items():
        ruta_completa = os.path.join(ruta_proyecto, ruta)
        if tipo == 'Carpeta' and os.path.isdir(ruta_completa):
            reporte["cumplimiento_estructura"][ruta] = True
            reporte["estadisticas"]["elementos_presentes"] += 1
        elif tipo == 'Archivo' and os.path.isfile(ruta_completa):
            reporte["cumplimiento_estructura"][ruta] = True
            reporte["estadisticas"]["elementos_presentes"] += 1
        else:
            reporte["cumplimiento_estructura"][ruta] = False
            reporte["estadisticas"]["elementos_faltantes"] += 1

    # Calcular el porcentaje de cumplimiento y ajustarlo a 100% máximo
    total_elementos = max(reporte["estadisticas"]["total_elementos"], 1)  # Evita división por cero
    reporte["estadisticas"]["porcentaje_cumplimiento"] = min((reporte["estadisticas"]["elementos_presentes"] / total_elementos) * 100, 100)

    return reporte

def generar_markdown(reporte):
    md = f"# 📊 Reporte de Análisis de Estructura del Proyecto\n\n"
    md += f"📅 Fecha y hora del análisis: {reporte['fecha_hora']}\n\n"

    md += "## 📈 Estadísticas Generales\n\n"
    stats = reporte['estadisticas']
    md += f"- 🔢 Total de elementos esperados: **{stats['total_elementos']}**\n"
    md += f"- ✅ Elementos presentes: **{stats['elementos_presentes']}**\n"
    md += f"- ❌ Elementos faltantes: **{stats['elementos_faltantes']}**\n"
    md += f"- 📊 Porcentaje de cumplimiento: **{stats['porcentaje_cumplimiento']:.2f}%**\n\n"

    md += "## 🔍 Detalle de Cumplimiento\n\n"
    for ruta, cumple in reporte['cumplimiento_estructura'].items():
        emoji = "✅" if cumple else "❌"
        md += f"- {emoji} {ruta}: **{'Presente' if cumple else 'Faltante'}**\n"

    return md

def guardar_reporte(contenido, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(contenido)

def obtener_nombre_archivo_reporte():
    ahora = datetime.now()
    return f"REPORTE_ANALISIS_ESTRUCTURA_{ahora.strftime('%Y%m%d_%H%M%S')}.md"

def main():
    print("🔍 Iniciando análisis de estructura del proyecto...")
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio_salida = os.path.join(ruta_proyecto, "output")
    nombre_archivo = obtener_nombre_archivo_reporte()
    ruta_salida = os.path.join(directorio_salida, nombre_archivo)

    try:
        reporte = analizar_estructura(ruta_proyecto)
        contenido_markdown = generar_markdown(reporte)
        guardar_reporte(contenido_markdown, ruta_salida)
        print("✅ Análisis completado con éxito.")
        print(f"📄 Reporte generado y guardado en:")
        print(f"   {ruta_salida}")
        
        # Mostrar un resumen en la consola
        print("\n📊 Resumen del análisis:")
        print(f"   Total de elementos esperados: {reporte['estadisticas']['total_elementos']}")
        print(f"   Elementos presentes: {reporte['estadisticas']['elementos_presentes']}")
        print(f"   Elementos faltantes: {reporte['estadisticas']['elementos_faltantes']}")
        print(f"   Porcentaje de cumplimiento: {reporte['estadisticas']['porcentaje_cumplimiento']:.2f}%")
    except Exception as e:
        print(f"❌ Error al generar el reporte: {str(e)}")

if __name__ == "__main__":
    main()
