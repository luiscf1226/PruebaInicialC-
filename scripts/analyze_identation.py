import os
import re
from datetime import datetime

def detectar_encoding(ruta_archivo):
    encodings = ['utf-8', 'latin-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(ruta_archivo, 'r', encoding=encoding) as file:
                file.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return None

def remove_strings_and_comments(line):
    result = ''
    i = 0
    in_single_line_comment = False
    in_multi_line_comment = False
    in_string = False
    string_char = ''
    length = len(line)

    while i < length:
        c = line[i]
        if in_single_line_comment:
            break  # Ignorar el resto de la línea
        elif in_multi_line_comment:
            if c == '*' and i + 1 < length and line[i + 1] == '/':
                in_multi_line_comment = False
                i += 1  # Saltar '/'
            # Continuar ignorando caracteres dentro del comentario
        elif in_string:
            if c == '\\':
                i += 1  # Saltar el carácter escapado
            elif c == string_char:
                in_string = False
            # Continuar dentro de la cadena
        else:
            if c == '/' and i + 1 < length:
                next_c = line[i + 1]
                if next_c == '/':
                    in_single_line_comment = True
                    i += 1
                elif next_c == '*':
                    in_multi_line_comment = True
                    i += 1
                else:
                    result += c
            elif c == '"' or c == "'":
                in_string = True
                string_char = c
            else:
                result += c
        i += 1

    return result

def analizar_indentacion(contenido):
    lineas = contenido.split('\n')
    errores = []
    indent_level = 0
    indent_size = 4
    total_lineas = 0

    for numero, linea in enumerate(lineas, 1):
        linea_sin_comentarios = remove_strings_and_comments(linea)
        linea_stripped = linea.strip()
        if not linea_stripped:
            continue

        total_lineas += 1
        espacios_iniciales = len(linea) - len(linea.lstrip())

        # Antes de procesar la línea, ajustar el nivel de indentación según las llaves de cierre
        num_close_braces = linea_sin_comentarios.count('}')
        if num_close_braces > 0:
            indent_level -= num_close_braces
            if indent_level < 0:
                indent_level = 0

        # Verificar la indentación
        expected_indentation = indent_level * indent_size
        if espacios_iniciales != expected_indentation:
            errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {expected_indentation} espacios, Encontrado: {espacios_iniciales} espacios")

        # Después de procesar la línea, ajustar el nivel de indentación según las llaves de apertura
        num_open_braces = linea_sin_comentarios.count('{')
        indent_level += num_open_braces

    return errores, total_lineas

def buscar_carpeta_proyecto(ruta_src):
    for item in os.listdir(ruta_src):
        ruta_item = os.path.join(ruta_src, item)
        if os.path.isdir(ruta_item):
            if any(archivo.endswith(('.cpp', '.h')) for archivo in os.listdir(ruta_item)):
                return ruta_item
    return ruta_src

def analizar_archivo(ruta_archivo):
    encoding = detectar_encoding(ruta_archivo)
    if encoding:
        with open(ruta_archivo, 'r', encoding=encoding) as file:
            contenido = file.read()
        return analizar_indentacion(contenido)
    else:
        return [f"No se pudo determinar el encoding del archivo: {ruta_archivo}"], 0

def analizar_proyecto(ruta_src):
    reporte = {}
    archivos_analizados = []
    
    ruta_carpeta_proyecto = buscar_carpeta_proyecto(ruta_src)
    
    for raiz, dirs, archivos in os.walk(ruta_carpeta_proyecto):
        for archivo in archivos:
            if archivo.endswith(('.cpp', '.h', '.hpp')):
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_src)
                errores, total_lineas = analizar_archivo(ruta_completa)
                reporte[ruta_relativa] = {
                    'errores': errores,
                    'total_lineas': total_lineas,
                    'lineas_correctas': total_lineas - len(errores)
                }
                archivos_analizados.append(ruta_relativa)
    
    return reporte, archivos_analizados

def generar_reporte_md(reporte, archivos_analizados):
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

    md += "\n## 📁 Archivos Analizados\n\n"
    for archivo in archivos_analizados:
        md += f"- {archivo}\n"

    return md

def main():
    print("🔍 Iniciando análisis de indentación...")
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
    total_errores = sum(len(datos['errores']) for datos in reporte.values())
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
