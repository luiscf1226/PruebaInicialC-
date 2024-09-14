import os
import json
import subprocess
import sys
from datetime import datetime
import glob

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_cpp_program(program_path, inputs):
    process = subprocess.Popen(
        [program_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    output = ""
    for input_step in inputs:
        process.stdin.write(input_step['input'] + '\n')
        process.stdin.flush()
        
    stdout, stderr = process.communicate()
    return stdout, stderr

def compare_output(actual_output, expected_steps):
    actual_lines = [line.strip() for line in actual_output.strip().split('\n') if line.strip()]
    expected_lines = [step['output'].strip() for step in expected_steps]
    results = []
    passed = 0
    total = len(expected_lines)
    
    for i, expected in enumerate(expected_lines):
        if i >= len(actual_lines):
            results.append(f"❌ Paso {i+1}: Falta salida esperada\n   Esperado: {expected}")
        elif expected not in actual_lines[i]:
            results.append(f"❌ Paso {i+1}: Discrepancia detectada\n   Esperado: {expected}\n   Obtenido: {actual_lines[i]}")
        else:
            results.append(f"✅ Paso {i+1}: Prueba exitosa")
            passed += 1
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    return results, passed, total, success_rate

def generate_markdown_report(results, passed, total, success_rate, output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"reporte_pruebas_{timestamp}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 Reporte de Pruebas del Programa C++\n\n")
        f.write(f"📅 Fecha y hora de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📈 Estadísticas\n\n")
        f.write(f"- Total de pruebas: {total}\n")
        f.write(f"- Pruebas exitosas: {passed}\n")
        f.write(f"- Tasa de éxito: {success_rate:.2f}%\n\n")
        
        f.write("## 🔍 Resultados Detallados\n\n")
        for result in results:
            f.write(f"{result}\n\n")
        
        if success_rate == 100:
            f.write("## 🎉 ¡Felicidades!\n\n")
            f.write("Todas las pruebas han pasado exitosamente.\n")
        else:
            f.write("## 💡 Recomendaciones\n\n")
            f.write("1. Revisa las discrepancias reportadas y corrige el código según sea necesario.\n")
            f.write("2. Asegúrate de que todas las salidas esperadas estén correctamente definidas.\n")
            f.write("3. Ejecuta las pruebas nuevamente después de realizar los cambios.\n")
    
    print(f"Reporte generado: {report_file}")

def find_cpp_files(src_dir):
    cpp_files = []
    for ext in ['*.cpp', '*.h', '*.hpp']:
        cpp_files.extend(glob.glob(os.path.join(src_dir, '**', ext), recursive=True))
    return cpp_files

def compile_cpp_program(src_dir, output_dir):
    cpp_files = find_cpp_files(src_dir)
    if not cpp_files:
        return None, "No se encontraron archivos C++ en el directorio src."
    
    executable = os.path.join(output_dir, 'program.exe' if sys.platform == "win32" else 'program')
    
    if sys.platform == "win32":  # Windows
        compile_command = ['cl', '/EHsc', '/Fe:', executable] + cpp_files
    else:  # Unix-like
        compile_command = ['g++', '-std=c++11', '-o', executable] + cpp_files
    
    compile_result = subprocess.run(compile_command, capture_output=True, text=True)
    if compile_result.returncode != 0:
        return None, f"La compilación falló:\n{compile_result.stderr}"
    
    return executable, None

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, 'src')
    input_file = os.path.join(project_root, 'input', 'input.json')
    expected_output_file = os.path.join(project_root, 'expected_output', 'expected_steps.json')
    output_dir = os.path.join(project_root, 'output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    executable, compile_error = compile_cpp_program(src_dir, output_dir)
    if compile_error:
        generate_markdown_report([f"❌ Error de compilación: {compile_error}"], 0, 1, 0, output_dir)
        return
    
    try:
        input_data = load_json(input_file)
        expected_output_data = load_json(expected_output_file)
        
        actual_output, error_output = run_cpp_program(executable, input_data['steps'])
        
        results, passed, total, success_rate = compare_output(actual_output, expected_output_data['steps'])
        
        generate_markdown_report(results, passed, total, success_rate, output_dir)
        
    except Exception as e:
        generate_markdown_report([f"❌ Error inesperado: {str(e)}"], 0, 1, 0, output_dir)
    
    finally:
        if executable and os.path.exists(executable):
            os.remove(executable)

if __name__ == "__main__":
    main()
