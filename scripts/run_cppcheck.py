import os
import re
import subprocess
from datetime import datetime
from collections import defaultdict

SRC_DIR = "../src"
OUTPUT_DIR = "../output"

def count_lines_of_code():
    loc = defaultdict(int)
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    loc['total'] += len(content.splitlines())
                    loc['code'] += sum(1 for line in content.splitlines() if line.strip() and not line.strip().startswith('//'))
                    loc['comment'] += sum(1 for line in content.splitlines() if line.strip().startswith('//'))
                    loc['blank'] += sum(1 for line in content.splitlines() if not line.strip())
    return loc

def analyze_complexity():
    complexity = defaultdict(int)
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.cpp'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    complexity['cyclomatic'] += content.count('if') + content.count('for') + content.count('while') + content.count('case')
                    complexity['cognitive'] += content.count('if') + content.count('for') + content.count('while') + content.count('switch')
    return complexity

def count_functions():
    function_count = 0
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    function_count += len(re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*{', content))
    return function_count

def analyze_duplications():
    duplications = 0
    all_code_blocks = []
    
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    code_blocks = re.findall(r'\{[^{}]*\}', content)
                    all_code_blocks.extend(code_blocks)
    
    for i, block in enumerate(all_code_blocks):
        for j in range(i + 1, len(all_code_blocks)):
            if len(block) > 50 and block == all_code_blocks[j]:
                duplications += 1
    
    return duplications

def run_cppcheck():
    try:
        result = subprocess.run(['cppcheck', '--enable=all', '--inconclusive', '--xml', SRC_DIR],
                                capture_output=True, text=True, check=True)
        errors = len(re.findall(r'severity="error"', result.stdout))
        warnings = len(re.findall(r'severity="warning"', result.stdout))
        return {'errors': errors, 'warnings': warnings}
    except subprocess.CalledProcessError:
        return {'errors': "N/A", 'warnings': "N/A"}
    except FileNotFoundError:
        print("Cppcheck no está instalado o no se encuentra en el PATH del sistema.")
        return {'errors': "N/A", 'warnings': "N/A"}

def generate_report(loc, complexity, function_count, duplications, cppcheck_results):
    report = f"# 📊 Reporte de Análisis de Métricas - Proyecto C++\n\n"
    report += f"📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += "## 📈 Métricas de Código\n\n"
    report += "### 📝 Líneas de Código\n\n"
    report += f"- 📏 Líneas totales: **{loc['total']}**\n"
    report += f"- 💻 Líneas de código efectivas: **{loc['code']}**\n"
    report += f"- 💬 Líneas de comentarios: **{loc['comment']}**\n"
    report += f"- ⚪ Líneas en blanco: **{loc['blank']}**\n"
    report += f"- 📊 Densidad de comentarios: **{loc['comment'] / loc['code']:.2%}**\n\n"

    report += "### 🧮 Complejidad y Funciones\n\n"
    report += f"- 🔢 Número de funciones: **{function_count}**\n"
    report += f"- 🔄 Complejidad ciclomática total: **{complexity['cyclomatic']}**\n"
    report += f"- 🧠 Complejidad cognitiva total: **{complexity['cognitive']}**\n"
    report += f"- 📊 Complejidad ciclomática promedio por función: **{complexity['cyclomatic'] / function_count:.2f}**\n"
    report += f"- 📊 Complejidad cognitiva promedio por función: **{complexity['cognitive'] / function_count:.2f}**\n\n"

    report += f"### 🔄 Duplicaciones\n\n"
    report += f"- 🔁 Duplicaciones detectadas: **{duplications}**\n\n"

    report += "## 🚨 Problemas de Calidad\n\n"
    report += f"- ❌ Errores detectados por Cppcheck: **{cppcheck_results['errors']}**\n"
    report += f"- ⚠️ Advertencias detectadas por Cppcheck: **{cppcheck_results['warnings']}**\n\n"

    report += "## 💡 Recomendaciones\n\n"
    report += "1. 🔍 Revisar y corregir los errores y advertencias reportados por Cppcheck.\n"
    report += "2. 🔧 Considerar refactorizar funciones con alta complejidad.\n"
    report += "3. 🗑️ Revisar y eliminar código duplicado.\n"
    report += "4. 📝 Aumentar la cobertura de comentarios si es necesario.\n"

    return report

def save_report(content):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"REPORTE_ANALISIS_METRICAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Reporte generado: {filepath}")

if __name__ == "__main__":
    loc = count_lines_of_code()
    complexity = analyze_complexity()
    function_count = count_functions()
    duplications = analyze_duplications()
    cppcheck_results = run_cppcheck()
    
    report_content = generate_report(loc, complexity, function_count, duplications, cppcheck_results)
    save_report(report_content)
