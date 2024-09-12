import os
import re
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import nltk
from nltk.corpus import wordnet
import spacy

# Descargar recursos de NLTK necesarios
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)

# Cargar el modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

# Inicializar el modelo y tokenizador de CodeBERT
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

def extraer_caracteristicas(contenido):
    nombres_var_func = re.findall(r'\b(?:int|float|double|char|bool|void)\s+(\w+)', contenido)
    nombres_var_func += re.findall(r'\b(\w+)\s*\(', contenido)
    comentarios = re.findall(r'//.*?$|/\*.*?\*/', contenido, re.DOTALL | re.MULTILINE)
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case)\b', contenido)
    
    return {
        'nombres_var_func': nombres_var_func,
        'comentarios': comentarios,
        'estructuras_control': estructuras_control,
        'contenido_completo': contenido
    }

def detectar_codigo_repetido(contenido):
    lineas = contenido.split('\n')
    bloques = []
    for i in range(len(lineas)):
        for j in range(i+1, len(lineas)):
            bloque = '\n'.join(lineas[i:j])
            if len(bloque) > 50 and contenido.count(bloque) > 1:
                bloques.append((bloque, contenido.count(bloque)))
    return sorted(bloques, key=lambda x: len(x[0]) * x[1], reverse=True)[:5]

def obtener_embeddings(texto):
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

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

def analizar_significado_variable(nombre):
    doc = nlp(nombre)
    if len(doc) == 0:
        return "No significativo"
    elif len(doc) == 1:
        return "Potencialmente significativo" if doc[0].pos_ in ['NOUN', 'VERB', 'ADJ'] else "Poco significativo"
    else:
        return "Significativo"

def detectar_anomalias(contenido):
    anomalias = []
    # Detectar nombres de variables o funciones inusuales
    nombres_inusuales = re.findall(r'\b[a-z]+_[0-9]+\b', contenido)
    if nombres_inusuales:
        anomalias.append(f"Nombres inusuales detectados: {', '.join(nombres_inusuales)}")
    
    # Detectar comentarios sospechosos
    comentarios_sospechosos = re.findall(r'//.*TODO.*|//.*FIXME.*|//.*HACK.*', contenido)
    if comentarios_sospechosos:
        anomalias.append(f"Comentarios sospechosos detectados: {len(comentarios_sospechosos)}")
    
    # Detectar uso excesivo de goto
    gotos = re.findall(r'\bgoto\b', contenido)
    if len(gotos) > 2:
        anomalias.append(f"Uso excesivo de 'goto': {len(gotos)} veces")
    
    return anomalias

def analizar_archivos(ruta_src):
    resultados = {}
    todos_contenidos = []
    
    for raiz, _, ficheros in os.walk(ruta_src):
        for fichero in ficheros:
            if fichero.endswith('.cpp'):
                ruta_completa = os.path.join(raiz, fichero)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                caracteristicas = extraer_caracteristicas(contenido)
                codigo_repetido = detectar_codigo_repetido(contenido)
                embedding = obtener_embeddings(contenido)
                anomalias = detectar_anomalias(contenido)
                
                analisis_variables = {var: {
                    'significado': analizar_significado_variable(var),
                    'analisis': analizar_nombre_variable(var)
                } for var in caracteristicas['nombres_var_func']}
                
                resultados[fichero] = {
                    'ruta': ruta_completa,
                    'caracteristicas': caracteristicas,
                    'codigo_repetido': codigo_repetido,
                    'embedding': embedding,
                    'analisis_variables': analisis_variables,
                    'anomalias': anomalias
                }
                
                todos_contenidos.append(contenido)
    
    # TF-IDF y similitud coseno
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(todos_contenidos)
    similitud_matrix = cosine_similarity(tfidf_matrix)
    
    for i, (fichero, datos) in enumerate(resultados.items()):
        datos['similitudes'] = {
            otro_fichero: similitud
            for j, (otro_fichero, similitud) in enumerate(zip(resultados.keys(), similitud_matrix[i]))
            if i != j and similitud > 0.7  # Solo mostramos similitudes altas
        }
    
    return resultados

def generar_reporte(resultados, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("# Reporte de Análisis de Código y Detección de Posible Plagio\n\n")
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Estadísticas generales
        total_archivos = len(resultados)
        total_codigo_repetido = sum(len(datos['codigo_repetido']) for datos in resultados.values())
        total_anomalias = sum(len(datos['anomalias']) for datos in resultados.values())
        
        f.write("## Estadísticas Generales\n\n")
        f.write(f"- Total de archivos analizados: {total_archivos}\n")
        f.write(f"- Total de bloques de código repetido detectados: {total_codigo_repetido}\n")
        f.write(f"- Total de anomalías detectadas: {total_anomalias}\n\n")
        
        for archivo, datos in resultados.items():
            f.write(f"## Archivo: {archivo}\n\n")
            f.write(f"Ruta: {datos['ruta']}\n\n")
            
            f.write("### Análisis de variables:\n")
            for var, analisis in datos['analisis_variables'].items():
                f.write(f"- {var}: {analisis['significado']}\n")
            
            f.write("\n### Estructuras de control:\n")
            for estructura in datos['caracteristicas']['estructuras_control']:
                f.write(f"- {estructura}\n")
            
            f.write("\n### Código repetido:\n")
            for bloque, count in datos['codigo_repetido']:
                f.write(f"- Bloque repetido {count} veces:\n```\n{bloque[:100]}...\n```\n")
            
            f.write("\n### Anomalías detectadas:\n")
            for anomalia in datos['anomalias']:
                f.write(f"- {anomalia}\n")
            
            f.write("\n### Similitudes con otros archivos:\n")
            for otro_archivo, similitud in datos['similitudes'].items():
                f.write(f"- {otro_archivo}: {similitud:.2f}\n")
            
            f.write("\n---\n\n")

def main():
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_salida, exist_ok=True)

    resultados = analizar_archivos(ruta_src)
    
    # Generar reporte
    ruta_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_CODIGO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    generar_reporte(resultados, ruta_reporte)

    print(f"Análisis completado. Reporte guardado en {ruta_reporte}")

if __name__ == "__main__":
    main()
