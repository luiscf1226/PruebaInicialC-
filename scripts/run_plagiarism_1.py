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

# Función para leer archivos con manejo de codificaciones
def leer_archivo_con_codificacion(ruta_archivo):
    """
    Intenta leer el archivo con diferentes codificaciones si UTF-8 falla.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            return file.read(), None
    except UnicodeDecodeError:
        try:
            # Intentar con 'latin-1'
            with open(ruta_archivo, 'r', encoding='latin-1') as file:
                return file.read(), None
        except UnicodeDecodeError:
            try:
                # Intentar con 'ISO-8859-1'
                with open(ruta_archivo, 'r', encoding='ISO-8859-1') as file:
                    return file.read(), None
            except Exception as e:
                return None, f"Error al leer el archivo con otras codificaciones: {str(e)}"
    except Exception as e:
        return None, f"Error general al leer el archivo: {str(e)}"

# Función para buscar la carpeta del proyecto creada por Visual Studio dentro de src
def buscar_carpeta_proyecto_visual_studio(ruta_src):
    """
    Busca la carpeta del proyecto de Visual Studio dentro de 'src/'.
    Asume que la carpeta del proyecto contiene archivos .cpp o .h.
    """
    for carpeta in os.listdir(ruta_src):
        ruta_carpeta = os.path.join(ruta_src, carpeta)
        if os.path.isdir(ruta_carpeta):
            # Verifica si dentro de esta carpeta hay archivos .cpp o .h
            for archivo in os.listdir(ruta_carpeta):
                if archivo.endswith(('.cpp', '.h')):
                    return ruta_carpeta  # Es la carpeta del proyecto de Visual Studio
    return ruta_src  # Si no se encontró, vuelve a usar 'src'

# Definición de detectar_anomalias
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

# Función para extraer funciones de un archivo
def extraer_funciones(contenido):
    """
    Extrae todas las funciones de un archivo de código.
    """
    funciones = re.findall(r'\b\w+\s*\([^)]*\)\s*{(?:[^{}]*|{[^{}]*})*}', contenido)
    return funciones

# Obtener embeddings para las funciones extraídas
def obtener_embeddings_para_funciones(funciones):
    """
    Genera embeddings para cada función utilizando CodeBERT.
    """
    embeddings = []
    for funcion in funciones:
        inputs = tokenizer(funcion, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(embedding)
    return embeddings

# Comparar similitudes entre funciones
def analizar_similitud_funciones(archivo1, archivo2):
    """
    Compara funciones entre dos archivos y muestra las similitudes.
    """
    funciones1 = extraer_funciones(archivo1)
    funciones2 = extraer_funciones(archivo2)
    
    embeddings1 = obtener_embeddings_para_funciones(funciones1)
    embeddings2 = obtener_embeddings_para_funciones(funciones2)

    for i, emb1 in enumerate(embeddings1):
        for j, emb2 in enumerate(embeddings2):
            similitud = cosine_similarity([emb1], [emb2])
            if similitud > 0.7:  # Ajustar el umbral según sea necesario
                print(f"Función {i+1} del archivo 1 es similar a función {j+1} del archivo 2 con una similitud de {similitud[0][0]:.2f}")

# Comparar si dos bloques de código son parafraseos
def comparar_parafraseo(codigo1, codigo2):
    """
    Compara dos bloques de código para determinar si son parafraseos.
    """
    emb1 = obtener_embeddings(codigo1)
    emb2 = obtener_embeddings(codigo2)
    
    similitud = cosine_similarity([emb1], [emb2])
    return similitud[0][0]

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

def analizar_archivos(ruta_src):
    resultados = {}
    todos_contenidos = []

    # Buscar la carpeta del proyecto Visual Studio en src
    ruta_carpeta_proyecto = buscar_carpeta_proyecto_visual_studio(ruta_src)
    
    for raiz, _, ficheros in os.walk(ruta_carpeta_proyecto):
        for fichero in ficheros:
            if fichero.endswith('.cpp'):
                ruta_completa = os.path.join(raiz, fichero)
                contenido, error = leer_archivo_con_codificacion(ruta_completa)
                
                if error:
                    print(f"Error procesando el archivo {ruta_completa}: {error}")
                    continue

                caracteristicas = extraer_caracteristicas(contenido)
                codigo_repetido = detectar_codigo_repetido(contenido)
                embedding = obtener_embeddings(contenido)
                anomalias = detectar_anomalias(contenido)
                
                funciones = extraer_funciones(contenido)
                embeddings_funciones = obtener_embeddings_para_funciones(funciones)

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
                    'anomalias': anomalias,
                    'funciones': funciones,
                    'embeddings_funciones': embeddings_funciones
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
            
            f.write("### Análisis de funciones similares:\n")
            # Comparar funciones dentro del archivo
            for i, funcion1 in enumerate(datos['funciones']):
                for j, funcion2 in enumerate(datos['funciones']):
                    if i != j:
                        similitud = comparar_parafraseo(funcion1, funcion2)
                        f.write(f"- Función {i+1} y función {j+1}: similitud de {similitud:.2f}\n")

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
