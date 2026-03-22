import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Intentamos importar openpyxl, si no está, Streamlit avisará en el log
try:
    import openpyxl
except ImportError:
    st.error("Error: Falta la librería 'openpyxl'. Asegúrate de que aparezca en tu archivo requirements.txt")

# 1. Configuración de pantalla (Ancha y compacta)
st.set_page_config(page_title="Control Rivas", layout="wide")

# 2. Ajuste Visual (CSS) para que los botones sean pequeños y entren más en pantalla
st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        padding: 0rem !important;
        margin-bottom: -1rem !important;
    }
    .st-emotion-cache-1r6slb0 {
        padding: 0.5rem !important;
        margin-bottom: 0.2rem !important;
    }
    .stButton button {
        width: 100%;
        padding: 0rem !important;
        height: 1.8rem !important;
        min-height: 1.8rem !important;
    }
    .stMarkdown p {
        font-size: 0.85rem !important;
        margin-bottom: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Inicialización de datos
if 'ventas' not in st.session_state:
    productos = [
        "AGUA LUNA VIDRIO", "AGUA GASIFICADA ORIGINA", "AGUA GASIFICA DE LIMON",
        "AGUA LUNA GASIFICADA FRESA", "AGUA LUNA SIN GAS", "BORIAL", "CORONA",
        "VICTORIA FROST", "RED BULL", "FDC 12 ANIO", "FDC 18 ANIO", "FDC 5 ANIO",
        "FDC CRISTALINO", "FDC 4 ANIO", "FDC 7 ANIO", "SAGATIBA", "SELTZER",
        "TEQUILA CHARRO BLANCO", "TEQUILA CHARRO REPOSADO", "TONIA",
        "VICTORIA CLASICA", "MARGARITA", "SANGRIA", "PURPLE RAIN",
        "AGUA LUNA LATA", "NICA HURRACAN", "VITALI", "EXTRA"
    ]
    st.session_state.ventas = {p: 0 for p in productos}
    # Precios base (puedes editarlos aquí)
    st.session_state.precios = {p: 0 for p in productos} 
    st.session_state.log = []

st.title("🎫 Registro de Entradas - Evento Rivas")

# 4. Cuadrícula de productos (5 columnas para aprovechar el ancho)
cols = st.columns(5)

for i, producto in enumerate(st.session_state.ventas):
    with cols[i % 5]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            cant = st.session_state.ventas[producto]
            st.write(f"Tickets: {cant}")
            
            c1, c2 = st.columns(2)
            if c1.button("➕", key=f"add_{i}"):
                st.session_state.ventas[producto] += 1
                st.session_state.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] VENTA: {producto}")
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}"):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    st.session_state.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] CORRECCION: {producto}")
                    st.rerun()

st.divider()

# 5. Sección de Reporte con Seguridad Mejorada
with st.expander("🔐 Generar Reporte de Arqueo (Solo Admin)"):
    # Formulario para evitar sugerencias automáticas del navegador
    with st.form("seguridad_admin", clear_on_submit=True):
        input_pass = st.text_input(
            "Ingrese Clave de Administrador", 
            type="password", 
            autocomplete="new-password"
        )
        submit_button = st.form_submit_button("Validar y Mostrar Arqueo")

    if submit_button:
        if input_pass == "2802":
            st.session_state.acceso_autorizado = True
            st.success("Acceso Concedido")
        else:
            st.session_state.acceso_autorizado = False
            st.error("Clave Incorrecta")
            st.session_state.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INTENTO FALLIDO DE CLAVE")

    # Si la clave fue correcta, mostramos los datos
    if st.session_state.get('acceso_autorizado', False):
        datos_reporte = []
        for p, cant in st.session_state.ventas.items():
            precio = st.session_state.precios.get(p, 0)
            datos_reporte.append({
                "PRODUCTO": p,
                "CANTIDAD": cant,
                "PRECIO": precio,
                "SUBTOTAL": cant * precio
            })
        
        df = pd.DataFrame(datos_reporte)
        st.write("### Vista Previa del Arqueo")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        total = df["SUBTOTAL"].sum()
        st.metric("TOTAL RECAUDADO", f"C$ {total:,.2f}")

        # Generar Excel real en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Arqueo')
        
        st.download_button(
            label="📥 DESCARGAR REPORTE EXCEL (.XLSX)",
            data=output.getvalue(),
            file_name=f"Arqueo_Rivas_{datetime.now().strftime('%d%m_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Auditoría visible para el admin
        if st.checkbox("Ver Log de Auditoría"):
            st.write(st.session_state.log[::-1])
