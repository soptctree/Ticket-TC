# --- SECCIÓN DE REPORTE (SEGURIDAD MEJORADA) ---
st.divider()

with st.expander("🔐 Generar Reporte de Arqueo (Solo Admin)"):
    # Usamos un formulario para evitar que el navegador sugiera claves viejas
    with st.form("admin_access"):
        input_pass = st.text_input(
            "Ingrese Clave de Administrador", 
            type="password", 
            help="La clave no se guardará en el navegador",
            key="password_field",
            autocomplete="new-password" # Esto bloquea las sugerencias del navegador
        )
        
        submit_button = st.form_submit_button("Validar Acceso")

    if submit_button:
        if input_pass == "2802":
            st.success("Acceso Autorizado")
            
            # --- Generación de Datos ---
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
            st.write("### Vista Previa del Arqueo")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # --- Total ---
            total_recaudado = df["SUBTOTAL"].sum()
            st.metric("TOTAL RECAUDADO", f"C$ {total_recaudado:,.2f}")
            
            # --- Descarga de Excel Real ---
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Arqueo')
            
            st.download_button(
                label="📥 DESCARGAR REPORTE EXCEL (.XLSX)",
                data=buffer.getvalue(),
                file_name=f"Arqueo_Rivas_{datetime.now().strftime('%d_%m_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Clave Incorrecta. Intente de nuevo.")
