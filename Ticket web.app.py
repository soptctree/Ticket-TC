import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. Configuración de la aplicación
st.set_page_config(page_title="Sistema de Control", layout="wide")

# 2. Estilo Visual Compacto
st.markdown("""
    <style>
    .stButton button { width: 100%; height: 1.8rem; padding: 0rem; }
    .stMarkdown p { font-size: 0.85rem; margin-bottom: 0rem; }
    [data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Inicialización de Datos
if 'ventas' not in st.session_state:
    productos = [
        "AGUA LUNA VIDRIO", "AGUA GASIFICADA ORIGINA", "AGUA GASIFICA DE LIMÓN",
        "AGUA LUNA GASIFICADA FRESA", "AGUA LUNA SIN GAS", "BORIAL", "CORONA",
        "VICTORIA FROST", "RED BULL", "FDC 12 ANIO", "FDC 18 ANIO", "FDC 5 ANIO",
        "FDC CRISTALINO", "FDC 4 ANIO", "FDC 7 ANIO", "SAGATIBA", "AGUA DE SELTZER",
        "TEQUILA CHARRO BLANCO", "TEQUILA CHARRO REPOSADO", "TONIA",
        "VICTORIA CLÁSICA", "MARGARITA", "SANGRÍA", "LLUVIA PÚRPURA",
        "AGUA LUNA LATA", "NICA HURACÁN", "VITALI", "EXTRA"
    ]
    st.session_state.ventas = {p: 0 for p in productos}
    st.session_state.log = [] 
    
    # Precios fijos (ajústalos según necesites)
    st.session_state.precios = {
        "AGUA LUNA VIDRIO": 30, "AGUA GASIFICADA ORIGINA": 35, "AGUA GASIFICA DE LIMÓN": 35,
        "AGUA LUNA GASIFICADA FRESA": 35, "AGUA LUNA SIN GAS": 25, "BORIAL": 40,
        "CORONA": 60, "VICTORIA FROST": 45, "RED BULL": 80, "FDC 12 ANIO": 150,
        "FDC 18 ANIO": 250, "FDC 5 ANIO": 100, "FDC CRISTALINO": 110, "FDC 4 ANIO": 80,
        "FDC 7 ANIO": 120, "SAGATIBA": 90, "AGUA DE SELTZER": 55, "TEQUILA CHARRO BLANCO": 130,
        "TEQUILA CHARRO REPOSADO": 140, "TONIA": 40, "VICTORIA CLÁSICA": 40,
        "MARGARITA": 120, "SANGRÍA": 100, "LLUVIA PÚRPURA": 120, "AGUA LUNA LATA": 30,
        "NICA HURACÁN": 45, "VITALI": 35, "EXTRA": 40
    }

# CAMBIO DE ENCABEZADO AQUÍ
st.title("🚀 CONTROL DE INVENTARIO - SISTEMA WEB") 

# 4. Interfaz de Botones (5 columnas)
cols = st.columns(5)
for i, producto in enumerate(st.session_state.ventas):
    with cols[i % 5]:
        with st.container(border=True):
            st.markdown(f"**{producto}**")
            st.write(f"Tickets: {st.session_state.ventas[producto]}")
            c1, c2 = st.columns(2)
            
            if c1.button("➕", key=f"add_{i}"):
                st.session_state.ventas[producto] += 1
                st.session_state.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] VENTA: {producto}")
                st.rerun()
                
            if c2.button("Corr.", key=f"corr_{i}"):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    st.session_state.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] CORR: {producto}")
                    st.rerun()

# 5. Reporte y Seguridad
st.divider()
with st.expander("🔐 Generar Reporte de Arqueo (Solo Admin)"):
    with st.form("admin_form", clear_on_submit=True):
        clave = st.text_input("Clave Admin", type="password", autocomplete="new-password")
        validar = st.form_submit_button("Validar Acceso")

    if validar:
        if clave == "2802":
            st.session_state.autenticado = True
            st.success("Acceso Autorizado")
        else:
            st.error("Clave Incorrecta")

    if st.session_state.get('autenticado', False):
        datos = []
        for p, cant in st.session_state.ventas.items():
            precio = st.session_state.precios.get(p, 0)
            datos.append({"PRODUCTO": p, "CANTIDAD": cant, "PRECIO": precio, "SUBTOTAL": cant * precio})
        
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("TOTAL RECAUDADO", f"C$ {df['SUBTOTAL'].sum():,.2f}")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 DESCARGAR EXCEL (.XLSX)",
            data=output.getvalue(),
            file_name=f"Arqueo_Rivas_{datetime.now().strftime('%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
