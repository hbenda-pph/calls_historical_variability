"""
Dashboard de Análisis de Variabilidad Histórica
==============================================

Dashboard de Streamlit para analizar la variabilidad histórica de llamadas
de todas las compañías con funcionalidades de exportación y visualización avanzada.

Desarrollado para: Platform Partners - ServiceTitan Call Analysis
Fecha: Octubre 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
from historical_variability_analyzer import create_all_companies_variability_table
import gspread
from google.oauth2.service_account import Credentials
import io
import base64

# Configuración de la página
st.set_page_config(
    page_title="Historical Variability Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el encabezado con doble fila
st.markdown("""
<style>
    .multi-level-header {
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        font-weight: bold;
    }
    
    .month-header {
        background-color: #e8f4f8;
        border: 1px solid #ddd;
        padding: 4px;
        text-align: center;
        font-weight: bold;
        font-size: 12px;
    }
    
    .value-header {
        background-color: #e8f4f8;
        border: 1px solid #ddd;
        padding: 4px;
        text-align: center;
        font-size: 10px;
    }
    
    .variability-header {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        padding: 4px;
        text-align: center;
        font-size: 10px;
    }
</style>
""", unsafe_allow_html=True)

def create_multi_level_header():
    """Crea el encabezado con doble fila para la tabla."""
    
    # Primera fila: Meses agrupados
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    header_html = """
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
        <tr>
            <td class="multi-level-header" style="width: 15%;">Company</td>
            <td class="multi-level-header" style="width: 10%;">Average Mix</td>
    """
    
    # Crear celdas agrupadas para cada mes (2 columnas por mes)
    for month in months:
        header_html += f'<td class="month-header" colspan="2" style="width: 6.25%;">{month}</td>'
    
    header_html += """
        </tr>
        <tr>
            <td class="value-header"></td>
            <td class="value-header"></td>
    """
    
    # Segunda fila: Valores y Variabilidad
    for month in months:
        header_html += f'<td class="value-header">{month}</td>'
        header_html += f'<td class="variability-header">{month}_var</td>'
    
    header_html += """
        </tr>
    </table>
    """
    
    return header_html

def export_to_google_sheets(df, sheet_name="Historical_Variability"):
    """Exporta el DataFrame a Google Sheets."""
    
    try:
        # Configuración de credenciales
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Intentar obtener credenciales del entorno o usar credenciales por defecto
        try:
            # Para Streamlit Cloud o entorno con secrets configurado
            creds = Credentials.from_service_account_info(
                st.secrets["google_credentials"], 
                scopes=scope
            )
        except:
            # Para desarrollo local o sin configuración de secrets
            st.warning("⚠️ Credenciales de Google Sheets no configuradas. Configura las credenciales para habilitar la exportación.")
            return None
        
        client = gspread.authorize(creds)
        
        # Crear nueva hoja de cálculo
        spreadsheet = client.create(sheet_name)
        worksheet = spreadsheet.sheet1
        
        # Escribir datos
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        # Hacer la hoja pública para lectura
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        return spreadsheet.url
        
    except Exception as e:
        st.error(f"Error al exportar a Google Sheets: {str(e)}")
        return None

def create_sample_data():
    """Crea datos de ejemplo para demostración."""
    
    companies_info = [
        {
            'company_name': 'Monarch HVAC',
            'company_id': 1,
            'monthly_calls': np.array([1200, 1100, 1300, 1400, 1500, 1600, 1700, 1600, 1500, 1400, 1300, 1200]),
            'calls_percentages': np.array([8.33, 7.64, 9.03, 9.72, 10.42, 11.11, 11.81, 11.11, 10.42, 9.72, 9.03, 8.33])
        },
        {
            'company_name': 'Elite Plumbing',
            'company_id': 2,
            'monthly_calls': np.array([1000, 900, 1100, 1200, 1300, 1400, 1500, 1400, 1300, 1200, 1100, 1000]),
            'calls_percentages': np.array([7.89, 7.12, 8.45, 9.18, 9.91, 10.64, 11.37, 10.64, 9.91, 9.18, 8.45, 7.89])
        },
        {
            'company_name': 'Premium Electric',
            'company_id': 3,
            'monthly_calls': np.array([1100, 1000, 1200, 1300, 1400, 1500, 1600, 1500, 1400, 1300, 1200, 1100]),
            'calls_percentages': np.array([8.76, 8.12, 9.38, 10.04, 10.70, 11.36, 12.02, 11.36, 10.70, 10.04, 9.38, 8.76])
        },
        {
            'company_name': 'Advanced HVAC',
            'company_id': 4,
            'monthly_calls': np.array([1300, 1200, 1400, 1500, 1600, 1700, 1800, 1700, 1600, 1500, 1400, 1300]),
            'calls_percentages': np.array([8.67, 8.00, 9.33, 10.00, 10.67, 11.33, 12.00, 11.33, 10.67, 10.00, 9.33, 8.67])
        },
        {
            'company_name': 'Pro Plumbing',
            'company_id': 5,
            'monthly_calls': np.array([900, 800, 1000, 1100, 1200, 1300, 1400, 1300, 1200, 1100, 1000, 900]),
            'calls_percentages': np.array([7.50, 6.67, 8.33, 9.17, 10.00, 10.83, 11.67, 10.83, 10.00, 9.17, 8.33, 7.50])
        }
    ]
    
    return pd.DataFrame(companies_info)

def main():
    """Función principal del dashboard."""
    
    # Título principal
    st.title("📊 Historical Variability Analyzer")
    st.markdown("---")
    
    # Panel de control izquierdo
    with st.sidebar:
        st.header("🎛️ Panel de Control")
        
        # Selector de modo de análisis
        analysis_mode = st.selectbox(
            "Modo de Análisis",
            options=["Percentages", "Absolute"],
            index=0,
            help="Selecciona si deseas ver porcentajes o cantidades absolutas de llamadas"
        )
        
        st.markdown("---")
        
        # Información del análisis
        st.subheader("ℹ️ Información")
        st.info(f"""
        **Modo actual**: {analysis_mode}
        
        **Estructura de la tabla**:
        - Filas: Compañías
        - Columnas: Average Mix + Valores/Variabilidad alternados
        
        **Colores**:
        - 🟡 Amarillo: Average Mix
        - 🔵 Azul: Valores mensuales
        - 🟢 Verde: Variabilidad positiva
        - 🔴 Rojo: Variabilidad negativa
        """)
        
        st.markdown("---")
        
        # Botón de exportación
        st.subheader("📤 Exportación")
        export_button = st.button("📊 Exportar a Google Sheets", type="primary")
    
    # Contenido principal
    st.subheader("📈 Tabla de Variabilidad Histórica - Todas las Compañías")
    
    # Crear datos de ejemplo
    companies_data = create_sample_data()
    
    # Crear tabla de variabilidad
    styled_table, df_table = create_all_companies_variability_table(
        companies_data,
        grouping_method="by_company",
        analysis_mode=analysis_mode
    )
    
    # Mostrar encabezado con doble fila
    st.markdown(create_multi_level_header(), unsafe_allow_html=True)
    
    # Mostrar la tabla
    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Información adicional
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Compañías", len(companies_data))
    
    with col2:
        if analysis_mode == "Percentages":
            avg_overall = np.mean([np.mean(row['calls_percentages']) for _, row in companies_data.iterrows()])
            st.metric("Promedio General", f"{avg_overall:.2f}%")
        else:
            avg_overall = np.mean([np.mean(row['monthly_calls']) for _, row in companies_data.iterrows()])
            st.metric("Promedio General", f"{avg_overall:,.0f}")
    
    with col3:
        st.metric("Período", "12 meses")
    
    # Exportación a Google Sheets
    if export_button:
        with st.spinner("Exportando a Google Sheets..."):
            sheet_url = export_to_google_sheets(df_table, f"Historical_Variability_{analysis_mode}")
            
            if sheet_url:
                st.success("✅ Exportación exitosa!")
                st.markdown(f"**Enlace a Google Sheets**: [Abrir hoja]({sheet_url})")
            else:
                st.error("❌ Error en la exportación. Verifica la configuración de credenciales.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Desarrollado por**: Platform Partners Team | **Versión**: 1.0")

if __name__ == "__main__":
    main()
