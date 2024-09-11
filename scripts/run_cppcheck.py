import os
import subprocess
import re
import json
from datetime import datetime

# Define directories
SRC_DIR = "../src"
OUTPUT_DIR = "../output"
INPUT_DIR = "../input"
EXPECTED_OUTPUT_DIR = "../expected_output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.md")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_visual_studio_solution():
    sln_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.sln')]
    if sln_files:
        return f"Se ha detectado un archivo de solución (.sln) de Visual Studio: {sln_files[0]}"
    else:
        return "No se ha encontrado ningún archivo de solución (.sln) en el directorio 'src'."

def run_cppcheck():
    try:
        cppcheck_command = [
            "cppcheck", "--enable=all", "--inconclusive", "--std=c++11",
            "--language=c++", "--output-file=cppcheck_raw_output.txt",
            "--xml", SRC_DIR
        ]
        subprocess.run(cppcheck_command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Cppcheck: {e}")
        return False

def count_lines_of_code():
    total_lines = 0
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                with open(os.path.join(root, file), 'r') as f:
                    total_lines += sum(1 for line in f if line.strip())
    return total_lines

def analyze_complexity():
    complexity_results = {}
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.cpp'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Simple cyclomatic complexity estimation
                    complexity = content.count('if') + content.count('for') + content.count('while') + content.count('&&') + content.count('||')
                    complexity_results[file] = complexity
    return complexity_results

def check_naming_conventions():
    naming_issues = []
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    # Check for camelCase function names
                    functions = re.findall(r'\b\w+\s+(\w+)\s*\(', content)
                    for func in functions:
                        if not func[0].islower() or '_' in func:
                            naming_issues.append(f"Función '{func}' en {file} no sigue camelCase")
                    # Check for PascalCase class names
                    classes = re.findall(r'\bclass\s+(\w+)', content)
                    for cls in classes:
                        if not cls[0].isupper() or '_' in cls:
                            naming_issues.append(f"Clase '{cls}' en {file} no sigue PascalCase")
    return naming_issues

def analyze_input_output():
    try:
        with open(os.path.join(INPUT_DIR, 'input.json'), 'r') as f:
            input_data = json.load(f)
        with open(os.path.join(EXPECTED_OUTPUT_DIR, 'expected_steps.json'), 'r') as f:
            expected_steps = json.load(f)
        with open(os.path.join(EXPECTED_OUTPUT_DIR, 'expected_final_output.json'), 'r') as f:
            expected_final = json.load(f)
        return len(input_data['steps']), len(expected_steps['steps']), expected_final['final_output']
    except FileNotFoundError:
        return 0, 0, "No se encontraron archivos de entrada/salida esperada"

def generate_markdown_report(cppcheck_results, loc, complexity_results, naming_issues, io_analysis):
    with open(OUTPUT_FILE, "w") as md_file:
        md_file.write("# Reporte de Análisis - Proyecto C++\n\n")
        md_file.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        md_file.write("## 1. Estructura del Proyecto\n")
        md_file.write(f"{check_visual_studio_solution()}\n\n")

        md_file.write("## 2. Métricas de Código\n")
        md_file.write(f"- **Líneas de Código**: {loc}\n")
        md_file.write("- **Complejidad Ciclomática**:\n")
        for file, complexity in complexity_results.items():
            md_file.write(f"  - {file}: {complexity}\n")
        md_file.write("\n")

        md_file.write("## 3. Calidad del Código\n")
        md_file.write("### 3.1 Resultados de Cppcheck\n")
        if cppcheck_results:
            errors = len([line for line in open("cppcheck_raw_output.txt") if "error" in line])
            warnings = len([line for line in open("cppcheck_raw_output.txt") if "warning" in line])
            md_file.write(f"- **Errores**: {errors}\n")
            md_file.write(f"- **Advertencias**: {warnings}\n")
        else:
            md_file.write("No se pudo ejecutar Cppcheck\n")
        
        md_file.write("\n### 3.2 Convenciones de Nomenclatura\n")
        if naming_issues:
            for issue in naming_issues:
                md_file.write(f"- {issue}\n")
        else:
            md_file.write("No se encontraron problemas de nomenclatura\n")
        
        md_file.write("\n## 4. Análisis de Entrada/Salida\n")
        input_steps, expected_steps, expected_final = io_analysis
        md_file.write(f"- **Pasos de entrada**: {input_steps}\n")
        md_file.write(f"- **Pasos de salida esperados**: {expected_steps}\n")
        md_file.write(f"- **Salida final esperada**: {expected_final}\n")

        md_file.write("\n## 5. Recomendaciones\n")
        md_file.write("1. Revisar y corregir los errores y advertencias reportados por Cppcheck.\n")
        md_file.write("2. Asegurar que todas las funciones y clases sigan las convenciones de nomenclatura adecuadas.\n")
        md_file.write("3. Considerar refactorizar funciones con alta complejidad ciclomática.\n")
        md_file.write("4. Verificar que el programa maneje correctamente todos los pasos de entrada y produzca las salidas esperadas.\n")

    print(f"Reporte generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    cppcheck_results = run_cppcheck()
    loc = count_lines_of_code()
    complexity_results = analyze_complexity()
    naming_issues = check_naming_conventions()
    io_analysis = analyze_input_output()
    generate_markdown_report(cppcheck_results, loc, complexity_results, naming_issues, io_analysis)
