import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# 1. Configuración de pantalla
st.set_page_config(page_title="Control Rivas - Pro", layout="wide")

# 2. Intento de Conexión Robusta
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Leemos la hoja. Si falla aquí, el error está en los Secrets o Permisos
    df_base = conn.read(ttl="0") 
    
    if 'ventas' not in st.session_state:
        # Convertimos la columna PRODUCTO en el índice para manejar los datos fácil
        st.session_state.ventas = df_base.set_index('PRODUCTO')['CANTIDAD'].to_dict()
        st.session_state.precios = df_base.set_index('PRODUCTO')['PRECIO'].to_dict()
        st.session_state.autenticado = False

except Exception as e:
    st.error("❌ ERROR DE CONEXIÓN")
    st.info("""
    **Por favor, revisa lo siguiente:**
    1. Que la URL en **Settings > Secrets** sea la correcta.
    2. Que tu Google Sheets tenga permiso de **Editor** para 'Cualquier persona con el enlace'.
    3. Que las columnas se llamen exactamente: **PRODUCTO**, **CANTIDAD** y **PRECIO**.
    """)
    st.stop()

# 3. Función para guardar en la nube
def sincronizar():
    df_update = pd.DataFrame({
        'PRODUCTO': list(st.session_state.ventas.keys()),
        'CANTIDAD': list(st.session_state.ventas.values()),
        'PRECIO': list(st.session_state.precios.values())
    })
    conn.update(data=df_update)
    st.toast("✅ Guardado en Google Sheets")

# --- INTERFAZ DE USUARIO ---
st.title("🚀 SISTEMA DE CONTROL PERMANENTE")
st.write("Los datos se guardan automáticamente en la nube.")

# Cuadrícula de productos (5 columnas)
cols = st.columns(5)
productos_lista = list(st.session_state.ventas.keys())

for i, producto in enumerate(productos_lista):
    with cols[i % 5]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            cant = st.session_state.ventas[producto]
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

# --- SECCIÓN DE ADMINISTRACIÓN ---
st.divider()
with st.expander("🔐 Panel de Arqueo y Reportes"):
    if not st.session_state.autenticado:
        clave = st.text_input("Introduce la clave de acceso", type="password")
        if clave == "2802":
            st.session_state.autenticado = True
            st.rerun()
    else:
        st.success("Acceso concedido")
        # Generar tabla de reporte
        datos_reporte = []
        for p in productos_lista:
            c = st.session_state.ventas[p]
            pre = st.session_state.precios.get(p, 0)
            datos_reporte.append({
                "PRODUCTO": p,
                "CANTIDAD": c,
                "PRECIO": pre,
                "SUBTOTAL": c * pre
            })
        
        df_final = pd.DataFrame(datos_reporte)
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        
        total = df_final["SUBTOTAL"].sum()
        st.metric("TOTAL RECAUDADO", f"C$ {total:,.2f}")
        
        # Botón para descargar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Descargar Reporte Excel",
            data=output.getvalue(),
            file_name=f"Arqueo_{producto}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
