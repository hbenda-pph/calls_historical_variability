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
from google.cloud import bigquery
import gettext
import locale
import io
import base64
import os
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Historical Variability Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CONFIGURACIÓN DE GETTEXT
# =============================================================================

def get_translation_function():
    """Obtener función de traducción según idioma"""
    
    # Detectar idioma del navegador o parámetro URL
    lang = st.query_params.get("lang", None)
    
    # Si no hay parámetro URL, detectar idioma del sistema
    if lang is None:
        try:
            system_lang = locale.getdefaultlocale()[0][:2]
            if system_lang in ["es", "en"]:
                lang = system_lang
            else:
                lang = "en"  # Fallback a inglés
        except:
            lang = "en"  # Fallback a inglés
    
    # Configurar GETTEXT
    try:
        translation = gettext.translation(
            'messages', 
            'locales', 
            languages=[lang],
            fallback=True
        )
        return translation.gettext
    except Exception as e:
        st.warning(f"Translation error: {e}. Using English.")
        return lambda x: x

# Función de traducción (se llama en cada uso)
def _(text):
    return get_translation_function()(text)

# =============================================================================
# FUNCIONES DE DATOS REALES
# =============================================================================

@st.cache_data
def get_companies_variability_data():
    """
    Extrae datos de variabilidad histórica de todas las compañías desde BigQuery.
    Suma todas las llamadas por mes de todos los años para cada compañía.
    """
    try:
        client = bigquery.Client()
        
        query = f"""
        SELECT c.company_id AS `company_id`
            , c.company_name AS `company_name`
            , EXTRACT(MONTH FROM DATE(cl.lead_call_created_on)) AS `month`
            , COUNT(cl.lead_call_id) AS `calls`
        FROM `pph-central.silver.vw_consolidated_call_inbound_location` cl
        JOIN `pph-central.settings.companies` c ON cl.company_id = c.company_id
        WHERE DATE(cl.lead_call_created_on) < DATE("2025-10-01")
          AND EXTRACT(YEAR FROM DATE(cl.lead_call_created_on)) >= 2015
        GROUP BY c.company_id, c.company_name, EXTRACT(MONTH FROM DATE(cl.lead_call_created_on))
        ORDER BY c.company_id, EXTRACT(MONTH FROM DATE(cl.lead_call_created_on))
        """
        
        df = client.query(query).to_dataframe()
        
        if df.empty:
            return pd.DataFrame()
        
        # Procesar datos por compañía
        companies_data = []
        for company_id in df['company_id'].unique():
            company_df = df[df['company_id'] == company_id]
            company_name = company_df['company_name'].iloc[0]
            
            # Crear arrays de 12 meses (Jan-Dec)
            monthly_calls = np.zeros(12)
            calls_percentages = np.zeros(12)
            
            # Llenar datos por mes (sumando todos los años)
            for _, row in company_df.iterrows():
                month_idx = int(row['month']) - 1  # Convertir a índice 0-11
                if 0 <= month_idx < 12:
                    monthly_calls[month_idx] = row['calls']
            
            # Calcular porcentajes
            total_calls = np.sum(monthly_calls)
            if total_calls > 0:
                calls_percentages = (monthly_calls / total_calls) * 100
            
            companies_data.append({
                'company_name': company_name,
                'company_id': company_id,
                'monthly_calls': monthly_calls,
                'calls_percentages': calls_percentages
            })
        
        return pd.DataFrame(companies_data)
        
    except Exception as e:
        st.error(f"Error al obtener datos de BigQuery: {str(e)}")
        return pd.DataFrame()

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


def export_to_google_sheets(df, sheet_name="Historical_Variability"):
    """Exporta el DataFrame a Google Sheets usando la cuenta de servicio del deploy."""
    
    try:
        # Configuración de credenciales
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Usar credenciales por defecto (cuenta de servicio del deploy)
        # En Cloud Run, las credenciales se configuran automáticamente
        creds = Credentials.from_service_account_info(
            st.secrets.get("google_credentials", {}), 
            scopes=scope
        )
        
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
        st.info("💡 La exportación a Google Sheets requiere configuración de credenciales. Usa la exportación a CSV como alternativa.")
        return None


def main():
    """Función principal del dashboard."""
    
    # Título principal
    st.title(f"📊 {_('Historical Variability Analyzer')}")
    st.markdown("---")
    
    # Panel de control izquierdo
    with st.sidebar:
        st.header(f"🎛️ {_('Control Panel')}")
        
        # Selector de modo de análisis
        analysis_mode = st.selectbox(
            _("Analysis Mode"),
            options=["Percentages", "Absolute"],
            index=0,
            help=_("Select whether to view percentages or absolute call quantities")
        )
        
        st.markdown("---")
        
        # Información del análisis
        st.subheader(f"ℹ️ {_('Analysis Information')}")
        st.info(f"""
        **{_('Current Mode')}**: {analysis_mode}
        
        **{_('Table Structure')}**:
        - {_('Rows')}: {_('Companies')}
        - {_('Columns')}: {_('Average Mix')} + {_('Monthly Values')}/{_('Variability')} alternated
        
        **{_('Colors')}**:
        - 🟡 {_('Yellow')}: {_('Average Mix')}
        - 🔵 {_('Blue')}: {_('Monthly Values')}
        - 🟢 {_('Green')}: {_('Positive Variability')}
        - 🔴 {_('Red')}: {_('Negative Variability')}
        """)
        
        st.markdown("---")
        
        # Botón de exportación
        st.subheader(f"📤 {_('Export')}")
        col1, col2 = st.columns(2)
        
        with col1:
            export_sheets_button = st.button(f"📊 {_('Export to Google Sheets')}", type="primary")
        
        with col2:
            export_csv_button = st.button(f"📄 {_('Export to CSV')}", type="secondary")
    
    # Contenido principal
    st.subheader(f"📈 {_('Historical Variability Table - All Companies')}")
    
    # Obtener datos reales de BigQuery
    with st.spinner(_("Loading data from BigQuery...")):
        companies_data = get_companies_variability_data()
    
    if companies_data.empty:
        st.error(_("No data available. Please check your BigQuery connection."))
        return
    
    # Crear tabla de variabilidad
    styled_table, df_table = create_all_companies_variability_table(
        companies_data,
        grouping_method="by_company",
        analysis_mode=analysis_mode
    )
    
    # Mostrar la tabla normal
    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Información adicional
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(_("Total Companies"), len(companies_data))
    
    with col2:
        if analysis_mode == "Percentages":
            avg_overall = np.mean([np.mean(row['calls_percentages']) for _, row in companies_data.iterrows()])
            st.metric(_("Overall Average"), f"{avg_overall:.2f}%")
        else:
            avg_overall = np.mean([np.mean(row['monthly_calls']) for _, row in companies_data.iterrows()])
            st.metric(_("Overall Average"), f"{avg_overall:,.0f}")
    
    with col3:
        st.metric(_("Period"), f"12 {_('months')}")
    
    # Exportación a Google Sheets
    if export_sheets_button:
        with st.spinner(_("Exporting to Google Sheets...")):
            sheet_url = export_to_google_sheets(df_table, f"Historical_Variability_{analysis_mode}")
            
            if sheet_url:
                st.success(f"✅ {_('Export successful!')}")
                st.markdown(f"**{_('Open sheet')}**: [Abrir hoja]({sheet_url})")
            else:
                st.error(f"❌ {_('Export error. Check credentials configuration.')}")
    
    # Exportación a CSV
    if export_csv_button:
        csv = df_table.to_csv(index=False)
        st.download_button(
            label=f"📄 {_('Download CSV')}",
            data=csv,
            file_name=f"historical_variability_{analysis_mode.lower()}.csv",
            mime="text/csv",
        )
    
    # Footer
    st.markdown("---")
    st.markdown(f"**{_('Developed by')}**: Platform Partners Team | **{_('Version')}**: 1.0")

if __name__ == "__main__":
    main()
