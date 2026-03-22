import streamlit as st
import pandas as pd
from datetime import datetime
import io # Necesario para generar el Excel real

# Configuración compacta y ancha
st.set_page_config(page_title="Control Rivas", layout="wide")

# --- CSS MEJORADO PARA PANTALLA AJUSTABLE ---
st.markdown("""
    <style>
    /* Hace los contenedores de productos más bajos y compactos */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        padding: 0rem !important;
        margin-bottom: -1rem !important;
    }
    /* Reduce márgenes y espacios internos de los cuadros (border=True) */
    .st-emotion-cache-1r6slb0 {
        padding: 0.5rem !important;
        margin-bottom: 0.2rem !important;
    }
    /* Botones más pequeños y compactos */
    .stButton button {
        width: 100%;
        padding: 0rem !important;
        height: 1.8rem !important;
        min-height: 1.8rem !important;
    }
    /* Reduce tamaño del texto del producto */
    .stMarkdown p {
        font-size: 0.85rem !important;
        margin-bottom: 0rem !important;
    }
    /* Reduce espacio entre el nombre y los botones */
    .stHorizontalBlock {
        gap: 0.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
    # He puesto precios de ejemplo para que el reporte salga con datos
    st.session_state.precios = {p: 100 for p in productos} 
    st.session_state.log = []

st.title("🎫 Registro de Entradas - Flujo Ágil")

# --- AHORA USAMOS 5 COLUMNAS PARA MÁS AJUSTE ---
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
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M:%S')} - VENTA: {producto}")
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}"):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    st.session_state.log.append(f"{datetime.now().strftime('%H:%M:%S')} - CORR: {producto}")
                    st.rerun()

st.divider()

# SECCIÓN DE REPORTE (Sin el monto recaudado en pantalla)
with st.expander("🔐 Generar Reporte de Arqueo (Solo Admin)"):
    clave = st.text_input("Clave Admin", type="password")
    if clave == "2802":
        st.write("### Vista Previa del Arqueo")
        
        datos_reporte = []
        for p, cant in st.session_state.ventas.items():
            precio = st.session_state.precios.get(p, 0)
            datos_reporte.append({
                "PRODUCTO": p,
                "CANTIDAD VENDIDA": cant,
                "PRECIO UNITARIO": precio,
                "SUBTOTAL": cant * precio
            })
        
        df = pd.DataFrame(datos_reporte)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # --- LÓGICA PARA DESCARGAR EXCEL REAL (.XLSX) ---
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Arqueo')
        
        st.download_button(
            label="📥 DESCARGAR REPORTE DETALLADO (EXCEL)",
            data=buffer.getvalue(),
            file_name=f"Arqueo_Rivas_{datetime.now().strftime('%d_%m_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
