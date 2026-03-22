import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración básica
st.set_page_config(page_title="Control Rivas", layout="wide")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

# 2. Conectar con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos (Sin caché para ver cambios al instante)
try:
    # Usamos ttl=0 para que siempre lea la versión más nueva del Sheets
    df_base = conn.read(spreadsheet=URL_SHEET, ttl=0)
    
    if 'ventas' not in st.session_state:
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
except Exception as e:
    st.error(f"Error de lectura: {e}")
    st.stop()

# 4. FUNCIÓN PARA GUARDAR (Escritura real)
def guardar_en_nube():
    # Creamos la tabla nueva con los datos actuales
    df_nuevo = pd.DataFrame({
        'PRODUCTO': list(st.session_state.ventas.keys()),
        'CANTIDAD': list(st.session_state.ventas.values()),
        'PRECIO': list(st.session_state.precios.values())
    })
    # ENVIAR AL SHEETS (Esto requiere permiso de EDITOR en el enlace)
    conn.update(spreadsheet=URL_SHEET, data=df_nuevo)
    st.toast("✅ Sincronizado en Google Sheets")

# --- INTERFAZ ---
st.title("🚀 REGISTRO DE EVENTO - RIVAS")

cols = st.columns(4)
productos = list(st.session_state.ventas.keys())

for i, p in enumerate(productos):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{p}**")
            st.write(f"Tickets: {st.session_state.ventas[p]}")
            
            if st.button("➕", key=f"btn_{i}"):
                st.session_state.ventas[p] += 1
                guardar_en_nube() # Guardamos primero
                st.rerun()        # Refrescamos la vista

# --- REPORTE ---
st.divider()
if st.checkbox("Ver Arqueo"):
    clave = st.text_input("Clave", type="password")
    if clave == "2802":
        resumen = pd.DataFrame([
            {"Producto": k, "Cant": v, "Total": v * st.session_state.precios[k]} 
            for k, v in st.session_state.ventas.items()
        ])
        st.table(resumen)
        st.metric("TOTAL RECAUDADO", f"C$ {resumen['Total'].sum():,.2f}")
