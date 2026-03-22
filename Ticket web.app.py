import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control Evento Rivas", layout="wide")

# URL de tu Google Sheets (Ya verificada)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

# 2. Conexión Robusta
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Forzamos la URL directamente en el código para evitar errores de conexión
    df_base = conn.read(spreadsheet=URL_SHEET, ttl="0")
    
    # Limpiamos nombres de columnas por si hay espacios invisibles
    df_base.columns = df_base.columns.str.strip()

    if 'ventas' not in st.session_state:
        # Cargamos los datos de la nube a la memoria de la App
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
        st.session_state.autenticado = False

except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.info("Asegúrate de que el archivo requirements.txt tenga: st-gsheets-connection")
    st.stop()

# 3. Función para guardar cambios en Google Sheets
def sincronizar():
    try:
        df_update = pd.DataFrame({
            'PRODUCTO': list(st.session_state.ventas.keys()),
            'CANTIDAD': list(st.session_state.ventas.values()),
            'PRECIO': list(st.session_state.precios.values())
        })
        conn.update(spreadsheet=URL_SHEET, data=df_update)
        st.toast("✅ Sincronizado en la Nube")
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")

# --- DISEÑO DE LA INTERFAZ ---
st.title("🎫 REGISTRO DE ENTRADAS - EVENTO")
st.markdown("---")

# Cuadrícula de 4 columnas para botones
cols = st.columns(4)
productos = list(st.session_state.ventas.keys())

for i, producto in enumerate(productos):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            cantidad = st.session_state.ventas[producto]
            st.write(f"Tickets: {cantidad}")
            
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

# --- SECCIÓN DE REPORTES ---
st.markdown("---")
with st.expander("🔐 VER ARQUEO DE CAJA (ADMIN)"):
    clave = st.text_input("Introduce Clave", type="password")
    if clave == "2802":
        st.session_state.autenticado = True
        
    if st.session_state.get('autenticado', False):
        resumen = []
        for p in productos:
            cant = st.session_state.ventas[p]
            pre = st.session_state.precios.get(p, 0)
            resumen.append({"PRODUCTO": p, "CANTIDAD": cant, "PRECIO": pre, "TOTAL": cant * pre})
        
        df_final = pd.DataFrame(resumen)
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        
        total_plata = df_final["TOTAL"].sum()
        st.metric("RECAUDACIÓN TOTAL", f"C$ {total_plata:,.2f}")
        
        # Botón para descargar Excel por si necesitas enviarlo por WhatsApp
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 DESCARGAR EXCEL",
            data=output.getvalue(),
            file_name="Reporte_Ventas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
