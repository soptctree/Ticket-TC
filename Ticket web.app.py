import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control Evento Rivas", layout="wide")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos manteniendo el ORDEN ORIGINAL
try:
    # ttl=0 para datos frescos
    df_base = conn.read(spreadsheet=URL_SHEET, ttl=0)
    df_base.columns = df_base.columns.str.strip()
    
    # Creamos una lista con el orden original de los productos
    lista_ordenada = df_base['PRODUCTO'].tolist()

    if 'ventas' not in st.session_state:
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
        st.session_state.autenticado = False

except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

# 4. Función de Guardado Permanente
def guardar_datos():
    try:
        # Reconstruimos el DataFrame respetando el orden de la lista original
        datos_fila = []
        for p in lista_ordenada:
            datos_fila.append({
                'PRODUCTO': p,
                'CANTIDAD': st.session_state.ventas[p],
                'PRECIO': st.session_state.precios[p]
            })
        df_update = pd.DataFrame(datos_fila)
        conn.update(spreadsheet=URL_SHEET, data=df_update)
        st.toast("✅ Guardado en la Nube")
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- INTERFAZ ---
st.title("🎫 REGISTRO DE ENTRADAS - EVENTO")
st.markdown("---")

# Cuadrícula de productos (4 columnas) usando la lista ordenada
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
                guardar_datos()
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}", use_container_width=True):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    guardar_datos()
                    st.rerun()

# --- REPORTE Y EXCEL ---
st.markdown("---")
with st.expander("🔐 PANEL DE ARQUEO Y DESCARGA"):
    clave = st.text_input("Clave Admin", type="password")
    if clave == "2802":
        resumen = []
        for p in lista_ordenada:
            c = st.session_state.ventas[p]
            pre = st.session_state.precios[p]
            resumen.append({"PRODUCTO": p, "CANTIDAD": c, "PRECIO": pre, "TOTAL": c * pre})
        
        df_final = pd.DataFrame(resumen)
        st.table(df_final)
        
        total_recaudado = df_final["TOTAL"].sum()
        st.metric("RECAUDACIÓN TOTAL", f"C$ {total_recaudado:,.2f}")
        
        # --- GENERAR EXCEL PARA DESCARGA ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Arqueo')
        
        st.download_button(
            label="📥 DESCARGAR REPORTE EN EXCEL",
            data=output.getvalue(),
            file_name="Reporte_Evento_Rivas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
