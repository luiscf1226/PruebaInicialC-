import os
import re
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import nltk
from nltk.corpus import wordnet
import spacy

# Descargar recursos de NLTK necesarios
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)

# Cargar el modelo de lenguaje en español y CodeBERT
nlp = spacy.load("es_core_news_sm")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

# Función para intentar leer un archivo con varias codificaciones comunes en América Latina
def leer_archivo_con_codificacion(ruta_archivo):
    codificaciones = ['utf-8', 'latin-1', 'ISO-8859-1']
    for codificacion in codificaciones:
        try:
            with open(ruta_archivo, 'r', encoding=codificacion) as f:
                return f.read(), None
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return None, f"Error: No se pudo leer el archivo {ruta_archivo} con ninguna de las codificaciones conocidas."

# Función para extraer características de un archivo de código
def extraer_caracteristicas(contenido):
    nombres_var_func = re.findall(r'\b(?:int|float|double|char|bool|void)\s+(\w+)', contenido)
    nombres_var_func += re.findall(r'\b(\w+)\s*\(', contenido)  # Extraer nombres de funciones
    comentarios = re.findall(r'//.*?$|/\*.*?\*/', contenido, re.DOTALL | re.MULTILINE)
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case)\b', contenido)
    
    return {
        'nombres_var_func': nombres_var_func,
        'comentarios': comentarios,
        'estructuras_control': estructuras_control,
        'contenido_completo': contenido
    }

# Función para detectar código repetido dentro de un archivo
def detectar_codigo_repetido(contenido):
    lineas = contenido.split('\n')
    bloques = []
    for i in range(len(lineas)):
        for j in range(i+1, len(lineas)):
            bloque = '\n'.join(lineas[i:j])
            if len(bloque) > 50 and contenido.count(bloque) > 1:
                bloques.append((bloque, contenido.count(bloque)))
    return sorted(bloques, key=lambda x: len(x[0]) * x[1], reverse=True)[:5]

# Función para obtener embeddings de CodeBERT para un fragmento de texto
def obtener_embeddings(texto):
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().astype(float)  # Convertir a float

# Función para analizar los nombres de las variables
def analizar_nombre_variable(nombre):
    palabras = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', nombre)
    significativo = len(palabras) > 1 or (len(palabras) == 1 and len(palabras[0]) > 2)
    
    valor_semantico = 0
    for palabra in palabras:
        synsets = wordnet.synsets(palabra.lower())
        if synsets:
            valor_semantico += len(synsets)
    
    return {
        'nombre': nombre,
        'palabras': palabras,
        'significativo': significativo,
        'valor_semantico': valor_semantico
    }

# Función para analizar la significatividad de las variables usando SpaCy
def analizar_significado_variable(nombre):
    doc = nlp(nombre)
    if len(doc) == 0:
        return "No significativo"
    elif len(doc) == 1:
        return "Potencialmente significativo" if doc[0].pos_ in ['NOUN', 'VERB', 'ADJ'] else "Poco significativo"
    else:
        return "Significativo"

# Función para calcular la longitud promedio de las funciones
def calcular_longitud_promedio_funciones(contenido):
    funciones = re.findall(r'\b(\w+)\s*\([^)]*\)\s*{[^}]*}', contenido)  # Encuentra funciones
    lineas = contenido.split('\n')
    total_funciones = len(funciones)
    total_lineas = len(lineas)
    longitud_promedio = total_lineas / total_funciones if total_funciones > 0 else 0
    return longitud_promedio, total_funciones

# Función para analizar los archivos de un proyecto individual
def analizar_archivos(ruta_src):
    resultados = {}
    
    for raiz, _, ficheros in os.walk(ruta_src):
        for fichero in ficheros:
            if fichero.endswith('.cpp'):  # Asumiendo que los archivos de código son C++
                ruta_completa = os.path.join(raiz, fichero)
                contenido, error = leer_archivo_con_codificacion(ruta_completa)
                
                if error:
                    print(f"Error al leer el archivo {ruta_completa}: {error}")
                    continue  # Si hay un error, se omite este archivo
                
                # Extraer características del archivo
                caracteristicas = extraer_caracteristicas(contenido)
                codigo_repetido = detectar_codigo_repetido(contenido)
                embedding = obtener_embeddings(contenido)
                
                # Analizar las variables y funciones
                analisis_variables = {var: {
                    'significado': analizar_significado_variable(var),
                    'analisis': analizar_nombre_variable(var)
                } for var in caracteristicas['nombres_var_func']}
                
                # Calcular la longitud promedio de las funciones
                longitud_promedio, total_funciones = calcular_longitud_promedio_funciones(contenido)
                
                resultados[fichero] = {
                    'ruta': ruta_completa,
                    'caracteristicas': caracteristicas,
                    'codigo_repetido': codigo_repetido,
                    'embedding': embedding.tolist(),  # Convertir a lista de floats
                    'analisis_variables': analisis_variables,
                    'longitud_promedio_funciones': longitud_promedio,
                    'total_funciones': total_funciones
                }
    
    return resultados

# Generar un reporte detallado sobre el análisis de código
def generar_reporte(resultados, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("# Reporte de Análisis de Código\n\n")
        for archivo, datos in resultados.items():
            f.write(f"## Archivo: {archivo}\n\n")
            f.write(f"Ruta: {datos['ruta']}\n\n")
            
            f.write("### Análisis de variables:\n")
            for var, analisis in datos['analisis_variables'].items():
                f.write(f"- {var}: {analisis['significado']}\n")
                f.write(f"  - Significativo: {'Sí' if analisis['analisis']['significativo'] else 'No'}\n")
                f.write(f"  - Valor semántico: {analisis['analisis']['valor_semantico']}\n")
            
            f.write("\n### Estructuras de control:\n")
            for estructura in datos['caracteristicas']['estructuras_control']:
                f.write(f"- {estructura}\n")
            
            f.write("\n### Código repetido:\n")
            for bloque, count in datos['codigo_repetido']:
                f.write(f"- Bloque repetido {count} veces:\n```\n{bloque}\n```\n")
            
            f.write("\n### Longitud promedio de funciones:\n")
            f.write(f"- Longitud promedio de funciones: {datos['longitud_promedio_funciones']:.2f} líneas\n")
            f.write(f"- Total de funciones: {datos['total_funciones']}\n")
            
            f.write("\n---\n\n")

# Función principal para iniciar el análisis de un proyecto
def main():
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_salida, exist_ok=True)

    resultados = analizar_archivos(ruta_src)
    
    # Generar el reporte de análisis
    ruta_reporte = os.path.join(ruta_salida, f"reporte_analisis_codigo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    generar_reporte(resultados, ruta_reporte)

    print(f"Análisis completado. Reporte guardado en {ruta_reporte}")

if __name__ == "__main__":
    main()
