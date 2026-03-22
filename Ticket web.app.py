import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control Evento Rivas", layout="wide")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1d_r4IWEjW1LMiVRlZbddWo1MTvazPS4FY4rXy2wp0Fs/edit?usp=sharing"

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leer datos con TTL=0 (Vital para evitar el reinicio al refrescar)
try:
    # ttl=0 obliga a la app a leer el Excel real en cada refresco, no una copia guardada
    df_base = conn.read(spreadsheet=URL_SHEET, ttl=0)
    df_base.columns = df_base.columns.str.strip()
    lista_ordenada = df_base['PRODUCTO'].tolist()

    if 'ventas' not in st.session_state:
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

# 4. Función de Guardado que "empuja" los datos al Excel inmediatamente
def guardar_y_actualizar():
    try:
        datos_actualizados = []
        for p in lista_ordenada:
            datos_actualizados.append({
                'PRODUCTO': p,
                'CANTIDAD': st.session_state.ventas[p],
                'PRECIO': st.session_state.precios[p]
            })
        df_para_subir = pd.DataFrame(datos_actualizados)
        # Esto sobreescribe el Google Sheets con los nuevos valores
        conn.update(spreadsheet=URL_SHEET, data=df_para_subir)
        st.toast("✅ Guardado en Google Sheets")
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")

# --- INTERFAZ (Tal cual te gusta) ---
st.title("🎫 REGISTRO DE ENTRADAS - EVENTO")
st.markdown("---")

cols = st.columns(4)
for i, producto in enumerate(lista_ordenada):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            # Mostramos el valor actual del Excel/Session State
            cant_actual = st.session_state.ventas[producto]
            st.write(f"Tickets: {cant_actual}")
            
            c1, c2 = st.columns(2)
            if c1.button("➕", key=f"add_{i}", use_container_width=True):
                st.session_state.ventas[producto] += 1
                guardar_y_actualizar() # <--- GUARDADO INSTANTÁNEO
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}", use_container_width=True):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    guardar_y_actualizar() # <--- GUARDADO INSTANTÁNEO
                    st.rerun()

# --- PANEL DE ARQUEO Y EXCEL (Manteniendo tu función de reporte) ---
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
        st.metric("RECAUDACIÓN TOTAL", f"C$ {df_final['TOTAL'].sum():,.2f}")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Arqueo')
        
        st.download_button(
            label="📥 DESCARGAR REPORTE EN EXCEL",
            data=output.getvalue(),
            file_name="Reporte_Evento_Rivas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
