import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import io

# 1. Configuración y Conexión
st.set_page_config(page_title="Control Permanente", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Leer datos desde Google Sheets
# Nota: La hoja debe tener columnas: PRODUCTO, CANTIDAD, PRECIO
df_base = conn.read(ttl="0") 

# Sincronizamos con session_state para que la app sea fluida
if 'ventas' not in st.session_state:
    st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
    st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
    st.session_state.log = []

# 3. Función para Guardar Cambios en Sheets
def guardar_cambios():
    # Convertimos el estado actual a un DataFrame
    df_actualizado = pd.DataFrame({
        'PRODUCTO': st.session_state.ventas.keys(),
        'CANTIDAD': st.session_state.ventas.values(),
        'PRECIO': st.session_state.precios.values()
    })
    # Subimos a Google Sheets
    conn.update(data=df_actualizado)
    st.toast("✅ Sincronizado con la nube")

# --- ENCABEZADO PERSONALIZADO ---
st.title("🚀 CONTROL DE INVENTARIO - SISTEMA WEB")

# 4. Interfaz de Botones (Igual que antes pero con autoguardado)
cols = st.columns(5)
for i, (producto, cant) in enumerate(st.session_state.ventas.items()):
    with cols[i % 5]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            st.write(f"Tickets: {cant}")
            c1, c2 = st.columns(2)
            
            if c1.button("➕", key=f"add_{i}"):
                st.session_state.ventas[producto] += 1
                guardar_cambios() # Guarda en Sheets al instante
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}"):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    guardar_cambios() # Guarda en Sheets al instante
                    st.rerun()

# 5. Reporte de Administrador (Bloqueado con clave)
st.divider()
with st.expander("🔐 Generar Reporte de Arqueo"):
    with st.form("admin_form"):
        clave = st.text_input("Clave Admin", type="password")
        if st.form_submit_button("Validar"):
            if clave == "2802":
                st.session_state.autenticado = True
            else:
                st.error("Clave incorrecta")

    if st.session_state.get('autenticado', False):
        # Crear tabla final
        datos = []
        for p, cant in st.session_state.ventas.items():
            precio = st.session_state.precios.get(p, 0)
            datos.append({"PRODUCTO": p, "CANTIDAD": cant, "PRECIO": precio, "SUBTOTAL": cant * precio})
        
        df_reporte = pd.DataFrame(datos)
        st.dataframe(df_reporte, use_container_width=True, hide_index=True)
        st.metric("TOTAL RECAUDADO", f"C$ {df_reporte['SUBTOTAL'].sum():,.2f}")
