import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control de Inventario Rivas", layout="wide")

# 2. Conexión a tu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos (ttl=0 para que siempre traiga lo más nuevo)
try:
    df_base = conn.read(ttl="0")
    
    # Inicializar session_state con los datos de la nube
    if 'ventas' not in st.session_state:
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
except Exception as e:
    st.error("Error al conectar con Google Sheets. Revisa los Secrets.")
    st.stop()

# Función para guardar automáticamente
def sincronizar():
    df_update = pd.DataFrame({
        'PRODUCTO': st.session_state.ventas.keys(),
        'CANTIDAD': st.session_state.ventas.values(),
        'PRECIO': st.session_state.precios.values()
    })
    conn.update(data=df_update)
    st.toast("☁️ Sincronizado en Google Sheets")

# --- INTERFAZ ---
st.title("🚀 CONTROL DE INVENTARIO - SISTEMA WEB")

cols = st.columns(5)
for i, (producto, cant) in enumerate(st.session_state.ventas.items()):
    with cols[i % 5]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            st.write(f"Tickets: {cant}")
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
with st.expander("🔐 Reporte de Arqueo"):
    clave = st.text_input("Clave", type="password")
    if clave == "2802":
        datos = []
        for p, c in st.session_state.ventas.items():
            pre = st.session_state.precios.get(p, 0)
            datos.append({"PRODUCTO": p, "CANTIDAD": c, "PRECIO": pre, "SUBTOTAL": c * pre})
        
        df_res = pd.DataFrame(datos)
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        st.metric("TOTAL RECAUDADO", f"C$ {df_res['SUBTOTAL'].sum():,.2f}")
