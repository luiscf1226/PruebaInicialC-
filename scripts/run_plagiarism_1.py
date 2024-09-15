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

def leer_archivo_con_codificacion(ruta_archivo):
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1']
    for encoding in encodings:
        try:
            with open(ruta_archivo, 'r', encoding=encoding) as file:
                return file.read(), None
        except UnicodeDecodeError:
            continue
    return None, f"Error: No se pudo leer el archivo {ruta_archivo} con ninguna codificación conocida."

def buscar_carpeta_proyecto_visual_studio(ruta_src):
    for carpeta in os.listdir(ruta_src):
        ruta_carpeta = os.path.join(ruta_src, carpeta)
        if os.path.isdir(ruta_carpeta):
            for archivo in os.listdir(ruta_carpeta):
                if archivo.endswith(('.cpp', '.h')):
                    return ruta_carpeta
    return ruta_src

def analizar_significado_variable(nombre):
    doc = nlp(nombre)
    significatividad = "No significativo"
    if len(doc) == 0:
        significatividad = "No significativo"
    else:
        for token in doc:
            if token.pos_ in ['NOUN', 'VERB', 'ADJ']:
                significatividad = "Significativo"
                break
    return significatividad

def detectar_anomalias(contenido):
    anomalias = []
    nombres_inusuales = re.findall(r'\b[a-z]+_[0-9]+\b', contenido)
    if nombres_inusuales:
        anomalias.append(f"Nombres inusuales detectados: {', '.join(set(nombres_inusuales))}")
    
    comentarios_sospechosos = re.findall(r'//.*(TODO|FIXME|HACK).*', contenido, re.IGNORECASE)
    if comentarios_sospechosos:
        anomalias.append(f"Comentarios de tareas pendientes detectados: {len(comentarios_sospechosos)}")
    
    gotos = re.findall(r'\bgoto\b', contenido)
    if len(gotos) > 0:
        anomalias.append(f"Uso de 'goto' detectado: {len(gotos)} veces")
    
    return anomalias

def extraer_funciones(contenido):
    patrones_funcion = re.compile(
        r'\b(?:[\w<>]+[\s*&]+)+([\w:~]+)\s*\([^)]*\)\s*(?:const)?\s*{(?:[^{}]*|{[^{}]*})*}',
        re.MULTILINE
    )
    return patrones_funcion.findall(contenido)

def obtener_embeddings_para_funciones(funciones):
    embeddings = []
    for funcion in funciones:
        codigo_funcion = funcion
        inputs = tokenizer(codigo_funcion, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(embedding)
    return embeddings

def analizar_similitud_funciones(funciones, umbral=0.8):
    similitudes = []
    embeddings = obtener_embeddings_para_funciones(funciones)
    num_funciones = len(funciones)
    for i in range(num_funciones):
        for j in range(i+1, num_funciones):
            similitud = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if similitud > umbral:
                similitudes.append({
                    'funcion_1': funciones[i],
                    'funcion_2': funciones[j],
                    'similitud': similitud
                })
    return similitudes

def comparar_parafraseo(codigo1, codigo2):
    emb1 = obtener_embeddings(codigo1)
    emb2 = obtener_embeddings(codigo2)
    return cosine_similarity([emb1], [emb2])[0][0]

def extraer_caracteristicas(contenido):
    nombres_var_func = re.findall(r'\b(?:int|float|double|char|bool|void|string)\s+(\w+)', contenido)
    nombres_var_func += re.findall(r'\b(\w+)\s*\(', contenido)
    comentarios = re.findall(r'//.*?$|/\*.*?\*/', contenido, re.DOTALL | re.MULTILINE)
    estructuras_control = re.findall(r'\b(if|else|for|while|switch|case|do)\b', contenido)
    
    return {
        'nombres_var_func': nombres_var_func,
        'comentarios': comentarios,
        'estructuras_control': estructuras_control,
        'contenido_completo': contenido
    }

def detectar_codigo_repetido(contenido):
    lineas = contenido.split('\n')
    bloques_repetidos = {}
    ventana = 5  # Número de líneas a considerar como bloque

    for i in range(len(lineas) - ventana):
        bloque = '\n'.join(lineas[i:i+ventana]).strip()
        if bloque in bloques_repetidos:
            bloques_repetidos[bloque] += 1
        else:
            bloques_repetidos[bloque] = 1

    bloques_frecuentes = [(bloque, count) for bloque, count in bloques_repetidos.items() if count > 1]
    return sorted(bloques_frecuentes, key=lambda x: x[1], reverse=True)

def obtener_embeddings(texto):
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def analizar_complejidad_ciclomatica(contenido):
    estructuras_control = re.findall(r'\b(if|for|while|case|&&|\|\|)\b', contenido)
    return len(estructuras_control) + 1  # Sumar 1 por el flujo básico

def analizar_calidad_comentarios(comentarios, funciones):
    calidad = []
    for comentario in comentarios:
        longitud = len(comentario.strip())
        if longitud < 10:
            calidad.append(('Comentario corto', comentario))
        elif longitud > 200:
            calidad.append(('Comentario muy largo', comentario))
        else:
            calidad.append(('Comentario adecuado', comentario))
    return calidad

def detectar_codigo_muerto(contenido):
    funciones_definidas = re.findall(r'\b[\w:~]+\s*\([^)]*\)\s*{', contenido)
    funciones_llamadas = re.findall(r'\b(\w+)\s*\(', contenido)
    codigo_muerto = set(funciones_definidas) - set(funciones_llamadas)
    return list(codigo_muerto)

def generar_resumen_funciones(funciones):
    resúmenes = {}
    for funcion in funciones:
        doc = nlp(funcion)
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        resumen = ' '.join(tokens[:10])  # Tomar los primeros 10 tokens significativos
        resúmenes[funcion] = resumen
    return resúmenes

def calcular_metricas_codigo(contenido):
    lineas = contenido.split('\n')
    num_lineas = len(lineas)
    num_funciones = len(extraer_funciones(contenido))
    profundidad_anidamiento = contenido.count('{') - contenido.count('}')
    longitud_promedio_funcion = num_lineas / num_funciones if num_funciones > 0 else 0
    return {
        'num_lineas': num_lineas,
        'num_funciones': num_funciones,
        'profundidad_anidamiento': profundidad_anidamiento,
        'longitud_promedio_funcion': longitud_promedio_funcion
    }

def analizar_archivos(ruta_src):
    resultados = {}
    todos_contenidos = []
    nombres_archivos = []

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
                codigo_muerto = detectar_codigo_muerto(contenido)
                resúmenes_funciones = generar_resumen_funciones(caracteristicas['nombres_var_func'])
                calidad_comentarios = analizar_calidad_comentarios(caracteristicas['comentarios'], caracteristicas['nombres_var_func'])
                metricas_codigo = calcular_metricas_codigo(contenido)
                
                funciones = extraer_funciones(contenido)
                similitudes_funciones = analizar_similitud_funciones(funciones)
                embeddings_funciones = obtener_embeddings_para_funciones(funciones)

                analisis_variables = {var: {
                    'significado': analizar_significado_variable(var)
                } for var in caracteristicas['nombres_var_func']}

                complejidad_ciclomatica = analizar_complejidad_ciclomatica(contenido)

                resultados[fichero] = {
                    'ruta': ruta_completa,
                    'caracteristicas': caracteristicas,
                    'codigo_repetido': codigo_repetido,
                    'embedding': embedding,
                    'analisis_variables': analisis_variables,
                    'anomalias': anomalias,
                    'codigo_muerto': codigo_muerto,
                    'resumen_funciones': resúmenes_funciones,
                    'calidad_comentarios': calidad_comentarios,
                    'metricas_codigo': metricas_codigo,
                    'funciones': funciones,
                    'similitudes_funciones': similitudes_funciones,
                    'embeddings_funciones': embeddings_funciones,
                    'complejidad_ciclomatica': complejidad_ciclomatica
                }

                todos_contenidos.append(contenido)
                nombres_archivos.append(fichero)
    
    # Calcular similitud entre archivos
    embeddings_archivos = [datos['embedding'] for datos in resultados.values()]
    similitud_matrix = cosine_similarity(embeddings_archivos)
    
    # Actualizar resultados con similitudes
    for idx, (fichero, datos) in enumerate(resultados.items()):
        datos['similitudes'] = {
            nombres_archivos[j]: similitud
            for j, similitud in enumerate(similitud_matrix[idx])
            if idx != j and similitud > 0.8  # Umbral de similitud
        }
    
    return resultados
def generar_reporte(resultados, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("# Reporte de Análisis de Código y Detección de Posible Plagio\n\n")
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total_archivos = len(resultados)
        total_codigo_repetido = sum(len(datos['codigo_repetido']) for datos in resultados.values())
        total_anomalias = sum(len(datos['anomalias']) for datos in resultados.values())
        complejidad_promedio = sum(datos['complejidad_ciclomatica'] for datos in resultados.values()) / total_archivos
        
        f.write("## Estadísticas Generales\n\n")
        f.write(f"- Total de archivos analizados: {total_archivos}\n")
        f.write(f"- Total de bloques de código repetido detectados: {total_codigo_repetido}\n")
        f.write(f"- Total de anomalías detectadas: {total_anomalias}\n")
        f.write(f"- Complejidad ciclomática promedio: {complejidad_promedio:.2f}\n\n")
        
        for archivo, datos in resultados.items():
            f.write(f"## Archivo: {archivo}\n\n")
            f.write(f"Ruta: {datos['ruta']}\n")
            f.write(f"Complejidad ciclomática: {datos['complejidad_ciclomatica']}\n")
            f.write(f"Métricas del código: {datos['metricas_codigo']}\n\n")
            
            f.write("### Análisis de variables y funciones:\n")
            for var, info in datos['analisis_variables'].items():
                f.write(f"- {var}: {info['significado']}\n")
            
            f.write("\n### Anomalías detectadas:\n")
            for anomalia in datos['anomalias']:
                f.write(f"- {anomalia}\n")
            if not datos['anomalias']:
                f.write("- No se detectaron anomalías.\n")
            
            f.write("\n### Código muerto o inalcanzable:\n")
            if datos['codigo_muerto']:
                for codigo in datos['codigo_muerto']:
                    f.write(f"- {codigo}\n")
            else:
                f.write("- No se detectó código muerto.\n")
            
            f.write("\n### Calidad de comentarios:\n")
            for tipo, comentario in datos['calidad_comentarios']:
                f.write(f"- {tipo}: {comentario.strip()}\n")
            if not datos['calidad_comentarios']:
                f.write("- No se encontraron comentarios.\n")
            
            f.write("\n### Resúmenes de funciones:\n")
            for funcion, resumen in datos['resumen_funciones'].items():
                f.write(f"- {funcion}: {resumen}\n")
            
            f.write("\n### Similitudes entre funciones:\n")
            if datos['similitudes_funciones']:
                for similitud in datos['similitudes_funciones']:
                    f.write(f"- Función 1: {similitud['funcion_1']}\n")
                    f.write(f"  Función 2: {similitud['funcion_2']}\n")
                    f.write(f"  Similitud: {similitud['similitud']:.2f}\n\n")
            else:
                f.write("- No se detectaron similitudes significativas entre funciones.\n")
            
            f.write("\n### Código repetido:\n")
            if datos['codigo_repetido']:
                for bloque, count in datos['codigo_repetido']:
                    f.write(f"- Bloque repetido {count} veces:\n```cpp\n{bloque}\n```\n")
            else:
                f.write("- No se detectó código repetido.\n")
            
            f.write("\n### Similitud con otros archivos:\n")
            if datos['similitudes']:
                for otro_archivo, similitud in datos['similitudes'].items():
                    f.write(f"- Similitud con {otro_archivo}: {similitud:.2f}\n")
            else:
                f.write("- No se detectaron similitudes significativas con otros archivos.\n")
            
            f.write("\n---\n\n")

def main():
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_src = os.path.join(ruta_proyecto, 'src')
    ruta_salida = os.path.join(ruta_proyecto, 'output')
    os.makedirs(ruta_salida, exist_ok=True)

    print("🔍 Iniciando análisis de código...")
    resultados = analizar_archivos(ruta_src)
    
    ruta_reporte = os.path.join(ruta_salida, f"REPORTE_ANALISIS_CODIGO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    generar_reporte(resultados, ruta_reporte)

    print(f"✅ Análisis completado. Reporte guardado en {ruta_reporte}")

if __name__ == "__main__":
    main()
