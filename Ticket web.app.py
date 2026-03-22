import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de pantalla
st.set_page_config(page_title="Control de Tickets Rivas", layout="wide")

# --- LÓGICA DE ESTADO (Base de datos temporal) ---
if 'ventas' not in st.session_state:
    productos = [
        "AGUA LUNA VIDRIO", "AGUA GASIFICADA ORIGINA", "AGUA GASIFICA DE LIMON",
        "AGUA LUNA GASIFICADA FRESA", "AGUA LUNA SIN GAS", "BORIAL", "CORONA",
        "VICTORIA FROST", "RED BULL", "FDC 12 AÑO", "FDC 18 AÑO", "FDC 5 AÑO",
        "FDC CRISTALINO", "FDC 4 AÑO", "FDC 7 AÑO", "SAGATIBA", "SELTZER",
        "TEQUILA CHARRO BLANCO", "TEQUILA CHARRO REPOSADO", "TOÑA",
        "VICTORIA CLASICA", "MARGARITA", "SANGRIA", "PURPLE RAIN",
        "AGUA LUNA LATA", "NICA HURRACAN", "VITALI", "EXTRA"
    ]
    # En una implementación real, aquí cargaríamos desde Google Sheets
    st.session_state.ventas = {p: 0 for p in productos}
    st.session_state.log = []
    # Precios (Igual que en el Excel)
    st.session_state.precios = {p: 50 for p in productos} # Ejemplo: todos a 50

st.title("🎫 Registro de Tickets - Evento")

# --- INTERFAZ DEL OPERADOR (3 Columnas para Celular/Web) ---
cols = st.columns(3)

for i, producto in enumerate(st.session_state.ventas):
    with cols[i % 3]:
        with st.container(border=True):
            st.write(f"**{producto}**")
            st.write(f"Tickets: {st.session_state.ventas[producto]}")
            
            c1, c2 = st.columns(2)
            if c1.button(f"➕", key=f"add_{producto}", use_container_width=True):
                st.session_state.ventas[producto] += 1
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M:%S')} - VENTA: {producto}")
                st.rerun()
                
            if c2.button(f"Corr.", key=f"corr_{producto}", use_container_width=True):
                if st.session_state.ventas[producto] > 0:
                    st.session_state.ventas[producto] -= 1
                    st.session_state.log.append(f"{datetime.now().strftime('%H:%M:%S')} - CORRECCIÓN: {producto}")
                    st.rerun()

# --- SECCIÓN DE ADMINISTRADOR (PROTEGIDA) ---
st.divider()
with st.expander("🔐 Generar Reporte de Arqueo (Solo Admin)"):
    clave = st.text_input("Ingrese Clave 2802", type="password")
    
    if clave == "2802":
        st.success("Acceso Autorizado")
        
        # Crear tabla de arqueo
        datos = []
        for p, cant in st.session_state.ventas.items():
            precio = st.session_state.precios.get(p, 0)
            datos.append({"Producto": p, "Tickets": cant, "Precio": precio, "Subtotal": cant * precio})
        
        df = pd.DataFrame(datos)
        total_dinero = df["Subtotal"].sum()
        
        st.metric("TOTAL RECAUDADO", f"C$ {total_dinero:,.2f}")
        st.dataframe(df, use_container_width=True)
        
        # Botón para descargar
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Excel (CSV)", csv, "arqueo_final.csv", "text/csv")
        
        st.write("### Auditoría de Movimientos")
        st.write(st.session_state.log[::-1]) # Muestra el log del más reciente al más viejo
    elif clave != "":
        st.error("Clave Incorrecta")