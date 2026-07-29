import requests
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import glob
import os

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkY2FzcXVlckB1Y20uZXMiLCJqdGkiOiIzZTFlMDdhZS05NDkzLTQ3NDQtYjNiMS01NzBkZTBiODY1ODAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc3MzY1MjgxNCwidXNlcklkIjoiM2UxZTA3YWUtOTQ5My00NzQ0LWIzYjEtNTcwZGUwYjg2NTgwIiwicm9sZSI6IiJ9.k73ils0yphkkOBNV6o8OETvC1X7eRRWnW8DXGgzyVUk"

HEADERS = {
    "api_key": API_KEY,
    "Accept": "application/json"
}

estacion = 3195 #Madrid Retiro

def peticion_con_reintentos(url):
    """Realiza la petición manejando los límites de carga del servidor."""
    max_reintentos = 5
    for intento in range(max_reintentos):
        try:
            respuesta = requests.get(url, headers=HEADERS, timeout=15)
            
            # Si el servidor nos bloquea temporalmente por exceso de peticiones
            if respuesta.status_code == 429:
                tiempo_espera = 2 ** intento
                print(f"      [!] Servidor saturado (Error 429). Esperando {tiempo_espera}s...")
                time.sleep(tiempo_espera)
                continue
            
            # AEMET devuelve un HTTP 200 incluso cuando el JSON interno indica un error de datos (estado 404)
            if respuesta.status_code == 200:
                return respuesta.json()
                
        except requests.exceptions.RequestException:
            time.sleep(2 ** intento)
            
    return None

def extraer_historico_aemet(estacion, años_historial=30):
    año_actual = datetime.now().year
    año_inicio = año_actual - años_historial

    print(f"Iniciando extracción para la estación {estacion} desde {año_inicio} hasta {año_actual - 1}...")

    for año in range(año_inicio, año_actual):
        print(f"-> Procesando el año {año} en bloques de 15 días...")
        
        fecha_actual = datetime(año, 1, 1)
        fecha_fin_año = datetime(año, 12, 31)
        datos_del_año = []

        # Bucle que divide el año en bloques de 15 días
        while fecha_actual <= fecha_fin_año:
            fecha_bloque_fin = fecha_actual + timedelta(days=14) 
            if fecha_bloque_fin > fecha_fin_año:
                fecha_bloque_fin = fecha_fin_año

            str_ini = fecha_actual.strftime("%Y-%m-%dT00:00:00UTC")
            str_fin = fecha_bloque_fin.strftime("%Y-%m-%dT23:59:59UTC")

            url_api = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{str_ini}/fechafin/{str_fin}/estacion/{estacion}"

            # 1. Llamada de Autodescubrimiento (HATEOAS)
            metadatos = peticion_con_reintentos(url_api)

            # Comprobamos que el estado del JSON interno es 200 (Éxito)
            if metadatos and metadatos.get('estado') == 200:
                url_datos = metadatos.get('datos')
                
                # 2. Descarga de los datos reales
                datos_reales = peticion_con_reintentos(url_datos)
                if datos_reales:
                    datos_del_año.extend(datos_reales)
            
            elif metadatos and metadatos.get('estado') == 429:
                print("      [!] Límite interno de la API alcanzado. Esperando...")
                time.sleep(5) 

            # Avanzamos la fecha para el siguiente bloque y hacemos una pausa cortés
            fecha_actual = fecha_bloque_fin + timedelta(days=1)
            time.sleep(0.5) 

        # Si el array tiene información, guardamos el año completo
        if datos_del_año:
            nombre_archivo = f"raw_data_aemet_{estacion}_{año}.json"
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos_del_año, archivo, ensure_ascii=False, indent=4)
            print(f"    ✓ Año {año} completado y guardado ({len(datos_del_año)} registros diarios).")
        else:
            print(f"    [X] No se encontraron datos históricos disponibles para el año {año}.")

def limpiar_y_transformar_datos(estacion):
    print(f"1. Buscando archivos JSON descargados de la estación {estacion}...")
    # Busca todos los archivos que coincidan con el patrón de la estación indicada
    archivos_json = glob.glob(f'raw_data_aemet_{estacion}_*.json')
    datos_completos = []

    # Leemos y unificamos todos los archivos
    for archivo in archivos_json:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos_anio = json.load(f)
            # AEMET suele devolver una lista de diccionarios
            if isinstance(datos_anio, list):
                datos_completos.extend(datos_anio)
    
    print(f"   -> Se han cargado {len(archivos_json)} archivos con un total de {len(datos_completos)} registros diarios.")

    print("\n2. Convirtiendo a DataFrame de Pandas...")
    df = pd.DataFrame(datos_completos)

    print("\n3. Iniciando limpieza de datos (Data Cleaning)...")
    # AEMET entrega los números como texto y usando comas en lugar de puntos para los decimales.
    # Necesitamos columnas estrictamente numéricas para poder operar o entrenar algoritmos.
    cols_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'dir', 'velmedia', 'racha', 'presMax', 'presMin', 'hrMedia', 'sol']

    for col in cols_numericas:
        if col in df.columns:
            # Reemplazamos comas por puntos y forzamos la conversión a numérico.
            # Los valores erróneos o vacíos se convertirán en nulos (NaN)
            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convertimos la columna de fecha a tipo datetime real y ordenamos cronológicamente
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)

    print("\n4. Manejando valores nulos (Missing Data)...")
    # Para los datos de variables continuas faltantes, aplicamos una interpolación lineal matemática 
    # para deducir el valor basándonos en los días adyacentes.
    cols_interpolacion = ['tmed', 'tmin', 'tmax', 'dir', 'velmedia', 'racha', 'presMax', 'presMin', 'hrMedia', 'sol']
    for col in cols_interpolacion:
        if col in df.columns:
            df[col] = df[col].interpolate(method='linear')

    # Para la precipitación, si un día no hay registro, asumimos que no llovió (0.0)
    if 'prec' in df.columns:
        df['prec'] = df['prec'].fillna(0.0)

    print("\n5. Filtrado de Metadatos...")
    # Conservamos exclusivamente la fecha y las columnas numéricas que existan
    columnas_finales = ['fecha'] + [col for col in cols_numericas if col in df.columns]
    df = df[columnas_finales]
    
    print("\n--- RESUMEN DEL DATASET LIMPIO ---")
    print(df.info())
    
    # Exportamos el resultado final a un archivo estructurado
    nombre_salida = f'dataset_aemet_{estacion}_limpio.csv'
    df.to_csv(nombre_salida, index=False, encoding='utf-8')
    print(f"\n¡Proceso ETL completado! Datos listos y guardados en '{nombre_salida}'")
    
    return df