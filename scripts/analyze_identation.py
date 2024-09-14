import os
import re
from datetime import datetime

def analizar_indentacion(contenido):
    lineas = contenido.split('\n')
    errores = []
    nivel_indentacion_esperado = 0
    total_lineas = 0
    dentro_bloque = False

    # Patrones para detectar estructuras de control
    patrones_control = {
        'if': re.compile(r'^\s*if\s*\(.*\)\s*{?\s*$'),
        'else': re.compile(r'^\s*else\s*{?\s*$'),
        'for': re.compile(r'^\s*for\s*\(.*\)\s*{?\s*$'),
        'while': re.compile(r'^\s*while\s*\(.*\)\s*{?\s*$'),
        'do': re.compile(r'^\s*do\s*{?\s*$'),
        'switch': re.compile(r'^\s*switch\s*\(.*\)\s*{?\s*$'),
        'case': re.compile(r'^\s*case\s+.*:\s*$'),
        'default': re.compile(r'^\s*default\s*:\s*$'),
        'llave_apertura': re.compile(r'^\s*\{\s*$'),
        'llave_cierre': re.compile(r'^\s*\}\s*$')
    }

    for numero, linea in enumerate(lineas, 1):
        linea_stripped = linea.strip()
        if not linea_stripped:  # Ignorar líneas vacías
            continue

        total_lineas += 1
        
        # Contar espacios al inicio de la línea
        espacios_iniciales = len(linea) - len(linea.lstrip())
        nivel_actual = espacios_iniciales // 4  # Asumimos que 4 espacios es una indentación

        # Si hay una llave de apertura en la misma línea de una estructura de control
        if any(patron.match(linea_stripped) for patron in [patrones_control['if'], patrones_control['for'], patrones_control['while'], patrones_control['do'], patrones_control['switch']]):
            if '{' in linea_stripped:
                # La llave está en la misma línea que la estructura de control
                if nivel_actual != nivel_indentacion_esperado:
                    errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
                nivel_indentacion_esperado += 1
            elif nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta en estructura de control. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
        
        # Manejar bloques que comienzan con main o funciones
        if re.match(r'^\s*(int|void|char|float|double|bool)\s+main\s*\(.*\)\s*{?\s*$', linea_stripped):
            if '{' in linea_stripped:
                # La llave está en la misma línea que la función main
                if nivel_actual != nivel_indentacion_esperado:
                    errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
                nivel_indentacion_esperado += 1
            elif nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta en función main. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
        
        # Verificar bloques comunes de apertura y cierre de llaves
        elif patrones_control['llave_apertura'].match(linea_stripped):
            if nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
            nivel_indentacion_esperado += 1
        elif patrones_control['llave_cierre'].match(linea_stripped):
            nivel_indentacion_esperado = max(0, nivel_indentacion_esperado - 1)
            if nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
        elif patrones_control['case'].match(linea_stripped) or patrones_control['default'].match(linea_stripped):
            if nivel_actual != nivel_indentacion_esperado:
                errores.append(f"Línea {numero}: Indentación incorrecta en 'case' o 'default'. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
        elif nivel_actual != nivel_indentacion_esperado:
            errores.append(f"Línea {numero}: Indentación incorrecta. Esperado: {nivel_indentacion_esperado * 4} espacios, Encontrado: {espacios_iniciales} espacios")
    
    return errores, total_lineas

def buscar_carpeta_proyecto_visual_studio(ruta_src):
    """
    Busca la carpeta del proyecto de Visual Studio dentro de 'src/'.
    Asume que la carpeta del proyecto contiene archivos .cpp y .h.
    """
    for carpeta in os.listdir(ruta_src):
        ruta_carpeta = os.path.join(ruta_src, carpeta)
        if os.path.isdir(ruta_carpeta):
            # Verifica si dentro de esta carpeta hay archivos .cpp o .h, asumiendo que es un proyecto de Visual Studio
            for archivo in os.listdir(ruta_carpeta):
                if archivo.endswith(('.cpp', '.h', '.hpp')):
                    return ruta_carpeta  # Es la carpeta del proyecto de Visual Studio
    return ruta_src  # Si no se encontró, vuelve a usar 'src'

def analizar_archivo(ruta_archivo):
    try:
        # Intentamos leer el archivo con 'utf-8'
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
        return analizar_indentacion(contenido)
    except UnicodeDecodeError:
        # Si falla, probamos con 'latin-1'
        try:
            with open(ruta_archivo, 'r', encoding='latin-1') as file:
                contenido = file.read()
            return analizar_indentacion(contenido)
        except Exception as e:
            return [f"Error al leer el archivo con 'latin-1': {str(e)}"], 0
    except Exception as e:
        return [f"Error al leer el archivo: {str(e)}"], 0


def analizar_proyecto(ruta_src):
    reporte = {}
    
    # Buscar la carpeta del proyecto Visual Studio en src
    ruta_carpeta_proyecto = buscar_carpeta_proyecto_visual_studio(ruta_src)
    
    for raiz, dirs, archivos in os.walk(ruta_carpeta_proyecto):
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
