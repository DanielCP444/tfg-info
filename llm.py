import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from fpdf import FPDF

gemini_key = ""
chatgpt_key = ""
claude_key = ""

# 1. Configurar la clave de la API (Necesitarás generar una clave gratuita en Google AI Studio)
os.environ["GEMINI_API_KEY"] = gemini_key
os.environ["OPENAI_API_KEY"] = chatgpt_key
os.environ["CLAUDE_API_KEY"] = claude_key

def generar_informe_gemini(prompt_texto):
    print("1. Conectando con la Inteligencia Artificial...")
    
    # 2. Inicializar el Modelo de Lenguaje
    # Configuramos una 'temperature' baja (0.2) para que la IA sea analítica y rigurosa, reduciendo alucinaciones
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    print("2. Enviando los datos de AEMET al modelo...")
    # 3. Enviar el prompt estructurado a la IA
    mensaje = [HumanMessage(content=prompt_texto)]
    respuesta = llm.invoke(mensaje)
    
    # 4. Guardar el informe generado
    informe_gemini = respuesta.content
    
    nombre_archivo = "informe_aridez_madrid_gemini.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(informe_gemini)
        
    print(f"\n¡Informe generado y guardado con éxito en '{nombre_archivo}'!")
    print("=" * 60)
    print(informe_gemini)
    print("=" * 60)
    return informe_gemini

def generar_informe_chatgpt(prompt_texto):
    print("1. Conectando con la Inteligencia Artificial...")
    
    # 2. Inicializar el Modelo de Lenguaje
    # Configuramos una 'temperature' baja (0.2) para que la IA sea analítica y rigurosa, reduciendo alucinaciones
    llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    print("2. Enviando los datos de AEMET al modelo...")
    # 3. Enviar el prompt estructurado a la IA
    mensaje = [HumanMessage(content=prompt_texto)]
    respuesta = llm_openai.invoke(mensaje)
    
    # 4. Guardar el informe generado
    informe_chatgpt = respuesta.content
    
    nombre_archivo = "informe_aridez_madrid_chatgpt.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(informe_chatgpt)
        
    print(f"\n¡Informe generado y guardado con éxito en '{nombre_archivo}'!")
    print("=" * 60)
    print(informe_chatgpt)
    print("=" * 60)

def generar_informe_claude(prompt_texto):
    print("1. Conectando con la Inteligencia Artificial...")
    
    # 2. Inicializar el Modelo de Lenguaje
    # Configuramos una 'temperature' baja (0.2) para que la IA sea analítica y rigurosa, reduciendo alucinaciones
    llm_claude = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.2)
    
    print("2. Enviando los datos de AEMET al modelo...")
    # 3. Enviar el prompt estructurado a la IA
    mensaje = [HumanMessage(content=prompt_texto)]
    respuesta = llm_claude.invoke(mensaje)
    
    # 4. Guardar el informe generado
    informe_claude = respuesta.content
    
    nombre_archivo = "informe_aridez_madrid_claude.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(informe_claude)
        
    print(f"\n¡Informe generado por claude y guardado con éxito en '{nombre_archivo}'!")
    print("=" * 60)
    print(informe_claude)
    print("=" * 60)

def compilar_informe_pdf(texto_llm, ruta_imagen):
    print("1. Inicializando documento PDF...")
    # Creamos un documento en formato A4 vertical con medidas en milímetros
    pdf = FPDF(orientation='P', unit='mm', format='A4') 
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # --- AÑADIR TÍTULO ---
    pdf.set_font("helvetica", "B", 14)
    pdf.set_margins(10, 20, 10)
    # Escribimos el título centrado
    pdf.ln(6)
    pdf.cell(0, 0, "Informe de la Evolución de la Aridez y Riesgo de Desertificación en Madrid", align="C", ln=1)
    pdf.ln(10) # Añadimos un salto de línea de 10mm
    pdf.set_margins(20, 20, 20)
    pdf.set_x(20)
    # --- AÑADIR EL TEXTO DEL LLM ---
    print("2. Redactando el análisis de la Inteligencia Artificial...")
    pdf.set_font("helvetica", "", 10)
    # multi_cell se encarga de hacer los saltos de línea automáticos cuando el párrafo es muy largo
    pdf.multi_cell(0, 5, texto_llm)
    pdf.ln(10)
    
    # --- AÑADIR LA GRÁFICA ---
    print("3. Incrustando la evidencia visual...")
    # Insertamos la imagen. 'x=10' le da un margen izquierdo y 'w=190' la ajusta al ancho del A4
    pdf.image(ruta_imagen, x=20, w=170)
    
    # --- GUARDAR DOCUMENTO ---
    nombre_salida = "Informe_Meteorologico_Gemini.pdf"
    pdf.output(nombre_salida)
    
    print(f"¡Completado! El reporte final se ha exportado con éxito como '{nombre_salida}'.")

