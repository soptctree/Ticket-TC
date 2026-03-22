import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la página (Optimizado para Laptop)
st.set_page_config(page_title="Control Rivas - Pro", layout="wide")

# URL de tu Google Sheets (Asegúrate de que sea esta)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos e inicializar sesión
try:
    # ttl=0 para que siempre lea los datos frescos del Excel
    df_base = conn.read(spreadsheet=URL_SHEET, ttl=0)
    
    # Limpiamos espacios en blanco en los nombres de las columnas
    df_base.columns = df_base.columns.str.strip()
    
    if 'ventas' not in st.session_state:
        # Cargamos los productos y precios del Excel a la memoria de la App
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
        st.session_state.autenticado = False

except Exception as e:
    st.error(f"❌ Error al leer Google Sheets: {e}")
    st.stop()

# 4. FUNCIÓN PARA GUARDAR (Sincronización real)
def guardar_datos():
    try:
        # Preparamos la tabla para subirla
        df_update = pd.DataFrame({
            'PRODUCTO': list(st.session_state.ventas.keys()),
            'CANTIDAD': list(st.session_state.ventas.values()),
            'PRECIO': list(st.session_state.precios.values())
        })
        # El método .create es más estable para evitar el UnsupportedOperationError
        conn.create(spreadsheet=URL_SHEET, data=df_update)
        st.toast("✅ Guardado en la Nube")
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")

# --- DISEÑO DE LA INTERFAZ ---
st.title("🎫 SISTEMA DE REGISTRO - EVENTO RIVAS")
st.info("Presiona '+' para sumar o 'Corr.' para restar. Los cambios se guardan automáticamente.")

# Cuadrícula de productos (4 columnas para laptop)
productos = list(st.session_state.ventas.keys())
cols = st.columns(4)

for i, p in enumerate(productos):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"### {p}")
            cant = st.session_state.ventas[p]
            st.write(f"**Tickets vendidos: {cant}**")
            
            # Botones en paralelo
            c1, c2 = st.columns(2)
            
            if c1.button("➕", key=f"add_{i}", use_container_width=True):
                st.session_state.ventas[p] += 1
                guardar_datos()
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}", use_container_width=True):
                if st.session_state.ventas[p] > 0:
                    st.session_state.ventas[p] -= 1
                    guardar_datos()
                    st.rerun()

# --- SECCIÓN DE ADMINISTRADOR ---
st.markdown("---")
with st.expander("🔐 VER REPORTE DE CAJA"):
    clave = st.text_input("Clave de acceso", type="password")
    if clave == "2802":
        st.success("Acceso Autorizado")
        
        # Crear tabla de arqueo
        resumen = []
        for prod in productos:
            c = st.session_state.ventas[prod]
            pre = st.session_state.precios.get(prod, 0)
            resumen.append({
                "PRODUCTO": prod, 
                "CANTIDAD": c, 
                "PRECIO": pre, 
                "TOTAL": c * pre
            })
        
        df_final = pd.DataFrame(resumen)
        st.table(df_final)
        
        total_plata = df_final["TOTAL"].sum()
        st.metric("RECAUDACIÓN TOTAL", f"C$ {total_plata:,.2f}")
