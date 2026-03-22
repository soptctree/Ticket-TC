import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control Evento Rivas", layout="wide")

# 2. Conexión a Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl="0" obliga a traer los datos reales de la nube siempre
    df_base = conn.read(ttl="0")
    
    # Limpiar espacios en los nombres de las columnas por si acaso
    df_base.columns = df_base.columns.str.strip()

    if 'ventas' not in st.session_state:
        # Cargamos los datos desde el Excel a la memoria del celular/PC
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
        st.session_state.autenticado = False

except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

# 3. Función para guardar cambios en la nube
def sincronizar():
    try:
        df_update = pd.DataFrame({
            'PRODUCTO': list(st.session_state.ventas.keys()),
            'CANTIDAD': list(st.session_state.ventas.values()),
            'PRECIO': list(st.session_state.precios.values())
        })
        conn.update(data=df_update)
        st.toast("✅ Sincronizado con Google Sheets")
    except:
        st.error("No se pudo guardar en la nube. Revisa el internet.")

# --- INTERFAZ ---
st.title("🚀 REGISTRO DE ENTRADAS - EVENTO RIVAS")

# Mostrar botones en 4 columnas para que se vea bien en celular
cols = st.columns(4)
productos = list(st.session_state.ventas.keys())

for i, producto in enumerate(productos):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            st.write(f"Tickets: {st.session_state.ventas[producto]}")
            
            c1, c2 = st.columns(2)
            if c1.button("➕", key=f"add_{i}"):
                st.session_state.ventas[producto] += 1
                sincronizar()
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}"):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    sincronizar()
                    st.rerun()

# --- REPORTE ---
st.divider()
with st.expander("🔐 Ver Arqueo Total"):
    clave = st.text_input("Clave Admin", type="password")
    if clave == "2802":
        data = []
        for p in productos:
            cant = st.session_state.ventas[p]
            pre = st.session_state.precios.get(p, 0)
            data.append({"PRODUCTO": p, "CANTIDAD": cant, "PRECIO": pre, "TOTAL": cant * pre})
        
        df_final = pd.DataFrame(data)
        st.table(df_final)
        st.metric("RECAUDACIÓN TOTAL", f"C$ {df_final['TOTAL'].sum():,.2f}")
