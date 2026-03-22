import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración compacta
st.set_page_config(page_title="Control Rivas", layout="wide")

# Estilo CSS para que los botones sean más pequeños y la pantalla se ajuste mejor
st.markdown("""
    <style>
    .stButton button { width: 100%; padding: 0.2rem; }
    div[data-testid="stVerticalBlock"] > div { padding: 0.1rem; }
    </style>
    """, unsafe_allow_html=True)

if 'ventas' not in st.session_state:
    # Nombres limpios para evitar errores de símbolos raros
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
    st.session_state.precios = {p: 0 for p in productos} # Aquí puedes poner precios reales
    st.session_state.log = []

st.title("🎫 Registro de Entradas")

# Usamos 4 columnas en lugar de 3 para que se vea menos estirado (ajuste de pantalla)
cols = st.columns(4)

for i, producto in enumerate(st.session_state.ventas):
    with cols[i % 4]:
        with st.container(border=True):
            # Nombre en pequeño para ganar espacio
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

# SECCIÓN DE REPORTE DETALLADO
with st.expander("🔐 Generar Reporte Detallado"):
    clave = st.text_input("Clave Admin", type="password")
    if clave == "2802":
        # Creamos el DataFrame detallado
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
        
        # Mostramos tabla detallada en la web
        st.write("### Vista Previa del Arqueo")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # TOTAL GLOBAL
        total_recaudado = df["SUBTOTAL"].sum()
        st.metric("TOTAL RECAUDADO", f"C$ {total_recaudado:,.2f}")

        # BOTÓN DE DESCARGA EXCEL REAL
        csv = df.to_csv(index=False).encode('utf-8-sig') # El 'utf-8-sig' arregla el problema de Excel
        st.download_button(
            label="📥 DESCARGAR REPORTE DETALLADO (CSV)",
            data=csv,
            file_name=f"Arqueo_Rivas_{datetime.now().strftime('%d_%m_%H%M')}.csv",
            mime='text/csv',
        )
