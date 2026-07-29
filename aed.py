import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymannkendall as mk
import matplotlib.colors as mcolors 
from windrose import WindroseAxes
import numpy as np
import pyet

def aed_temperatura(estacion):
    # 1. Cargar los datos limpios de la estación indicada
    nombre_archivo = f'dataset_aemet_{estacion}_limpio.csv'
    print(f"Cargando el dataset limpio: '{nombre_archivo}'...")
    df = pd.read_csv(nombre_archivo)
    
    # Convertimos la fecha al formato adecuado y la usamos como índice
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    df['mes'] = df.index.month
    df['año'] = df.index.year
    # 2. Configurar la estética de los gráficos
    sns.set_theme(style="whitegrid")
    
    # ==========================================
    # EVOLUCIÓN HISTÓRICA MENSUAL CONTINUA
    # ==========================================
    plt.figure(figsize=(16, 6))
    
    # Aplicamos resample mensual ('M' o 'ME') para calcular la media de cada mes de forma secuencial
    df_mensual = df['tmed'].resample('ME').mean()
    
    # Dibujamos la línea de evolución
    plt.plot(df_mensual.index, df_mensual.values, color='#e67e22', linewidth=1.5)
    
    plt.title(f'Evolución Continua de la Temperatura Media Mensual - Estación {estacion}', fontsize=15)
    plt.xlabel('Año', fontsize=12)
    plt.ylabel('Temperatura Media (°C)', fontsize=12)
    
    # Añadimos un pequeño margen y mostramos la gráfica
    plt.tight_layout()
    plt.show()

    # ==========================================
    # GRÁFICA 2: Estacionalidad (Boxplot mensual)
    # ==========================================
    plt.figure(figsize=(12, 6))
    
    # 1. Calculamos la temperatura mediana exacta de cada mes
    medianas_mensuales = df.groupby('mes')['tmed'].median()
    
    # 2. Normalizamos las temperaturas para adaptarlas a una escala matemática de 0 a 1
    norm = mcolors.Normalize(vmin=medianas_mensuales.min(), vmax=medianas_mensuales.max())
    
    # 3. Extraemos el color de la paleta 'coolwarm' que le corresponde a la temperatura de cada mes
    mapa_colores = plt.cm.coolwarm
    paleta_basada_en_temperatura = [mapa_colores(norm(temp)) for temp in medianas_mensuales]

    # 4. Dibujamos el boxplot pasándole nuestra lista de colores exacta
    sns.boxplot(x='mes', y='tmed', data=df, palette=paleta_basada_en_temperatura)
    
    plt.title(f'Distribución y Dispersión de Temperaturas Medias por Mes - Estación {estacion}', fontsize=14)
    plt.xlabel('Mes del Año', fontsize=12)
    plt.ylabel('Temperatura Media (°C)', fontsize=12)
    plt.tight_layout()
    plt.show()

    # ==========================================
    # ANÁLISIS ESTADÍSTICO DE TENDENCIA
    # ==========================================
    print("\n--- TEST ESTADÍSTICO DE MANN-KENDALL ---")
    print("Analizando la tendencia de la temperatura media anual...")
    
    # Agrupamos los datos diarios calculando la media anual para suavizar el ruido
    df_anual = df['tmed'].resample('YE').mean()
    
    # Aplicamos el test original de Mann-Kendall a la serie anual
    tendencia = mk.original_test(df_anual)
    
    print(f"Tendencia detectada: {tendencia.trend}")
    print(f"P-valor: {tendencia.p:.5f}")
    print(f"Pendiente de Sen: {tendencia.slope:.4f} ºC/año")
    print(f"Incremento total estimado: {tendencia.slope * 30:.2f} ºC en 30 años")
    
    if tendencia.p < 0.05:
        print("Conclusión: El p-valor es menor que 0.05. Hay evidencia estadística significativa de una tendencia en los datos.")
    else:
        print("Conclusión: No hay evidencia estadística suficiente para afirmar que existe una tendencia significativa.")

def aed_precipitacion(estacion):
    # 1. Cargar datos
    nombre_archivo = f'dataset_aemet_{estacion}_limpio.csv'
    print(f"Cargando el dataset limpio: '{nombre_archivo}'...")
    df = pd.read_csv(nombre_archivo)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    df['mes'] = df.index.month
    df['año'] = df.index.year
    sns.set_theme(style="whitegrid")

    # ==========================================
    # GRÁFICO 1: Precipitación Media Mensual
    # ==========================================
    plt.figure(figsize=(10, 5))
    precip_mensual = df.groupby(['año', 'mes'])['prec'].sum().groupby('mes').mean()
    norm = mcolors.Normalize(vmin=precip_mensual.min(), vmax=precip_mensual.max())
    mapa_colores = plt.cm.Blues
    paleta_precipitacion = [mapa_colores(norm(valor)) for valor in precip_mensual.values]
    sns.barplot(x=precip_mensual.index, y=precip_mensual.values, palette=paleta_precipitacion)
    plt.title(f'Precipitación Acumulada Media por Mes - Estación {estacion}', fontsize=14)
    plt.xlabel('Mes del Año', fontsize=12)
    plt.ylabel('Precipitación (mm)', fontsize=12)
    plt.tight_layout()
    plt.show()

    # ==========================================
    # GRÁFICO 2: Evolución Histórica Anual de Precipitación
    # ==========================================
    plt.figure(figsize=(16, 6))
    df_precip_anual_graf = df['prec'].resample('Y').sum()
    
    norm = mcolors.Normalize(vmin=df_precip_anual_graf.min(), vmax=df_precip_anual_graf.max())
    mapa_colores = plt.cm.Blues
    colores_barras = [mapa_colores(norm(valor)) for valor in df_precip_anual_graf.values]
    
    plt.bar(df_precip_anual_graf.index.year, df_precip_anual_graf.values, color=colores_barras)
    plt.title(f'Evolución de la Precipitación Anual Acumulada - Estación {estacion}', fontsize=15)
    plt.xlabel('Año', fontsize=12)
    plt.ylabel('Precipitación (mm)', fontsize=12)
    plt.tight_layout()
    plt.show()

    # ==========================================
    # ANÁLISIS ESTADÍSTICO DE TENDENCIA - PRECIPITACIÓN
    # ==========================================
    print("\n--- TEST ESTADÍSTICO DE MANN-KENDALL (PRECIPITACIÓN) ---")
    print("Analizando la tendencia de la precipitación anual...")
    df_precip_anual = df['prec'].resample('YE').sum()
    tendencia_precip = mk.original_test(df_precip_anual)
    print(f"Tendencia detectada: {tendencia_precip.trend}")
    print(f"P-valor: {tendencia_precip.p:.5f}")
    if tendencia_precip.p < 0.05:
        print("Conclusión: Hay evidencia estadística significativa de una tendencia en la precipitación.")
    else:
        print("Conclusión: No hay evidencia estadística suficiente para afirmar que existe una tendencia significativa.")

def aed_viento_presion(estacion):
    # 1. Cargar datos
    nombre_archivo = f'dataset_aemet_{estacion}_limpio.csv'
    print(f"Cargando el dataset limpio: '{nombre_archivo}'...")
    df = pd.read_csv(nombre_archivo)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    df['mes'] = df.index.month
    df['año'] = df.index.year
    sns.set_theme(style="whitegrid")
    # ==========================================
    # GRÁFICO 2: Viento (Rosa de los Vientos)
    # ==========================================
    print("\nGenerando Rosa de los Vientos...")
    # Verificamos que tengamos dirección y velocidad
    if 'dir' in df.columns and 'velmedia' in df.columns:
        # AEMET a veces da la dirección en decenas de grados (ej. 99=Variable). Filtramos valores válidos.
        df_viento = df.dropna(subset=['dir', 'velmedia'])
        df_viento = df_viento[df_viento['dir'] <= 360] # Asegurar grados válidos
        
        ax = WindroseAxes.from_ax()
        # Generamos el gráfico circular. normed=True lo pasa a porcentajes.
        ax.bar(df_viento['dir'], df_viento['velmedia'], normed=True, opening=0.8, edgecolor='white', cmap=plt.cm.viridis)
        ax.set_legend(title="Velocidad (m/s)", loc='best')
        ax.set_title("Rosa de los Vientos - Estacion " + estacion, fontsize=14, y=1.08)
        plt.show()
    else:
        print("  [!] No se encontraron las columnas de dirección ('dir') o velocidad ('velmedia') para el viento.")
    # ==========================================
    # GRÁFICO 1: Distribución Mensual de Presión (Boxplot)
    # ==========================================
    if 'presMax' in df.columns and 'presMin' in df.columns:
        df['presMedia'] = (df['presMax'] + df['presMin']) / 2
        medianas_presion = df.groupby('mes')['presMedia'].median()
        norm = mcolors.Normalize(vmin=medianas_presion.min(), vmax=medianas_presion.max())
        mapa_colores = plt.cm.coolwarm_r
        paleta_presion = [mapa_colores(norm(val)) for val in medianas_presion]
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='mes', y='presMedia', data=df, palette=paleta_presion)
        plt.title(f'Distribución de la Presión Atmosférica Media por Mes - Estación {estacion}', fontsize=14)
        plt.xlabel('Mes del Año', fontsize=12)
        plt.ylabel('Presión (hPa)', fontsize=12)
        plt.tight_layout()
        plt.show()
        # ==========================================
        # ANÁLISIS ESTADÍSTICO DE TENDENCIA - PRESIÓN
        # ==========================================
        print("\n--- TEST ESTADÍSTICO DE MANN-KENDALL (PRESIÓN) ---")
        print("Analizando la tendencia de la presión atmosférica anual...")
        df_presion_anual = df['presMedia'].resample('Y').mean()
        tendencia_presion = mk.original_test(df_presion_anual)
        print(f"Tendencia detectada: {tendencia_presion.trend}")
        print(f"P-valor: {tendencia_presion.p:.5f}")
        if tendencia_presion.p < 0.05:
            print("Conclusión: Hay evidencia estadística significativa de una tendencia en la presión atmosférica.")
        else:
            print("Conclusión: No hay evidencia estadística suficiente para afirmar que existe una tendencia significativa.")
    else:
        print("\n[!] Aviso: El dataset no contiene columnas de presión atmosférica.")

def analisis_exploratorio(estacion):
    aed_temperatura(estacion)
    aed_precipitacion(estacion)
    aed_viento_presion(estacion)

def enriquecer_datos_con_aridez(estacion):
    nombre_archivo = f'dataset_aemet_{estacion}_limpio.csv'
    print(f"Cargando el dataset limpio: '{nombre_archivo}'...")
    df = pd.read_csv(nombre_archivo)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    
    print("Calculando la Evapotranspiración Potencial (Hargreaves-Samani)...")
    latitud_rad = 40.41 * np.pi / 180
    df['pet'] = pyet.hargreaves(df['tmed'], df['tmax'], df['tmin'], latitud_rad)
    df['pet'] = df['pet'].round(2)
       
    df = df.reset_index()
    nombre_salida = f'dataset_aemet_{estacion}_enriquecido.csv'
    df.to_csv(nombre_salida, index=False, encoding='utf-8')
    print(f"Datos enriquecidos guardados en '{nombre_salida}'")
    
    return df

def graficar_verificacion_aridez(estacion):
    nombre_archivo = f'dataset_aemet_{estacion}_enriquecido.csv'
    df = pd.read_csv(nombre_archivo)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    
    datos_anuales = df.resample('YE').sum()
    datos_anuales['aridez_anual'] = datos_anuales['prec'] / datos_anuales['pet']
    datos_anuales = datos_anuales.replace([np.inf, -np.inf], np.nan).dropna(subset=['aridez_anual'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(datos_anuales.index.year, datos_anuales['aridez_anual'], marker='o', color='darkorange')
    plt.axhspan(0.05, 0.2, color='yellow', alpha=0.2, label='Árido (0.05-0.2)')
    plt.axhspan(0.2, 0.5, color='orange', alpha=0.2, label='Semiárido (0.2-0.5)')
    plt.title(f'Verificación: Evolución del Índice de Aridez - Estación {estacion}')
    plt.xlabel('Año')
    plt.ylabel('Índice de Aridez (P/PET)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('verificacion_aridez.png', dpi=150)
    plt.show()