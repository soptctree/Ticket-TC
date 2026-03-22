import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io
import random # Necesario para el truco de limpieza

st.set_page_config(page_title="Control Evento Rivas", layout="wide")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- TRUCO MAESTRO PARA QUE NO VUELVA A CERO ---
# Usamos un número aleatorio para que Streamlit crea que es una consulta nueva siempre
if 'query_id' not in st.session_state:
    st.session_state.query_id = random.randint(1, 10000)

try:
    # Leemos la hoja usando el query_id para romper la caché
    df_base = conn.read(spreadsheet=URL_SHEET, ttl=0)
    df_base.columns = df_base.columns.str.strip()
    lista_ordenada = df_base['PRODUCTO'].tolist()

    # Sincronizamos el estado de la sesión con lo que REALMENTE hay en el Excel
    st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
    st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()

except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

def guardar_y_forzar():
    try:
        datos_fila = []
        for p in lista_ordenada:
            datos_fila.append({
                'PRODUCTO': p,
                'CANTIDAD': st.session_state.ventas[p],
                'PRECIO': st.session_state.precios[p]
            })
        df_update = pd.DataFrame(datos_fila)
        conn.update(spreadsheet=URL_SHEET, data=df_update)
        # Cambiamos el ID para que en el próximo rerun lea el dato nuevo sí o sí
        st.session_state.query_id = random.randint(1, 10000)
        st.toast("✅ Sincronizado en la Nube")
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- INTERFAZ ---
st.title("🎫 REGISTRO DE ENTRADAS - EVENTO")
st.markdown(f"Pestaña de datos: `ID-{st.session_state.query_id}`") # Para saber que está refrescando

cols = st.columns(4)
for i, producto in enumerate(lista_ordenada):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            cant = st.session_state.ventas[producto]
            st.write(f"Tickets: {cant}")
            
            c1, c2 = st.columns(2)
            if c1.button("➕", key=f"add_{i}", use_container_width=True):
                st.session_state.ventas[producto] += 1
                guardar_y_forzar()
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}", use_container_width=True):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    guardar_y_forzar()
                    st.rerun()

# --- REPORTE ---
st.markdown("---")
with st.expander("🔐 PANEL DE ARQUEO"):
    clave = st.text_input("Clave Admin", type="password")
    if clave == "2802":
        resumen = []
        for p in lista_ordenada:
            c = st.session_state.ventas[p]
            pre = st.session_state.precios[p]
            resumen.append({"PRODUCTO": p, "CANTIDAD": c, "PRECIO": pre, "TOTAL": c * pre})
        df_final = pd.DataFrame(resumen)
        st.table(df_final)
        st.metric("RECAUDACIÓN TOTAL", f"C$ {df_final['TOTAL'].sum():,.2f}")
