"""
Historical Variability Analyzer
==============================

Este script analiza la variabilidad histórica de datos mensuales para identificar
patrones estacionales y desviaciones respecto al promedio histórico.

Desarrollado para: Platform Partners - ServiceTitan Call Analysis
Fecha: Octubre 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from typing import Tuple, Optional, Dict, List, Any


def create_historical_variability_table(
    monthly_calls: np.ndarray, 
    calls_percentages: np.ndarray, 
    analysis_mode: str = "Percentages",
    company_name: str = "Company",
    company_id: int = 1
) -> Tuple[Any, pd.DataFrame]:
    """
    Crea la tabla de variabilidad histórica con promedio y variabilidad por mes.
    
    Esta función analiza la variabilidad de datos mensuales calculando:
    1. El promedio histórico de los 12 meses
    2. La variabilidad (diferencia) de cada mes respecto al promedio
    3. Presenta los datos en formato de tabla con 25 columnas
    
    Parámetros:
    -----------
    monthly_calls : np.ndarray
        Array con los números absolutos de llamadas por mes (12 elementos)
    calls_percentages : np.ndarray  
        Array con los porcentajes de llamadas por mes (12 elementos)
    analysis_mode : str, opcional
        Modo de análisis: "Percentages" o "Absolute" (default: "Percentages")
    company_name : str, opcional
        Nombre de la compañía para títulos (default: "Company")
    company_id : int, opcional
        ID de la compañía para referencia (default: 1)
    
    Retorna:
    --------
    Tuple[pd.io.formats.style.Styler, pd.DataFrame]
        Tupla con (tabla con estilos aplicados, DataFrame sin estilos)
    
    Ejemplos:
    ---------
    >>> # Para análisis de porcentajes
    >>> monthly_calls = np.array([1200, 1100, 1300, 1400, 1500, 1600, 1700, 1600, 1500, 1400, 1300, 1200])
    >>> calls_percentages = np.array([8.33, 7.64, 9.03, 9.72, 10.42, 11.11, 11.81, 11.11, 10.42, 9.72, 9.03, 8.33])
    >>> styled_table, df = create_historical_variability_table(monthly_calls, calls_percentages, "Percentages")
    
    >>> # Para análisis de números absolutos
    >>> styled_table, df = create_historical_variability_table(monthly_calls, calls_percentages, "Absolute")
    """
    
    # Calcular el promedio de los 12 meses
    if analysis_mode == "Percentages":
        # Para porcentajes, usar los valores de calls_percentages
        average_mix = round(np.mean(calls_percentages), 2)
        monthly_values = calls_percentages
        avg_unit = "%"
        var_unit = "pp"  # percentage points
    else:
        # Para números absolutos, usar monthly_calls
        average_mix = round(np.mean(monthly_calls), 2)
        monthly_values = monthly_calls
        avg_unit = "calls"
        var_unit = "calls"
    
    # Crear datos para la tabla
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Calcular variabilidad (diferencia respecto al promedio)
    variability = [round(monthly_values[i] - average_mix, 2) for i in range(12)]
    
    # Crear DataFrame
    table_data = []
    
    # Primera fila: Average Mix
    row_avg = [f"Average Mix ({avg_unit})"]
    row_avg.extend([f"{average_mix:.2f}" if analysis_mode == "Percentages" else f"{average_mix:,.2f}"])
    for _ in range(11):
        row_avg.append("")
    row_avg.extend([f"Avg Mix ({avg_unit})"])
    for _ in range(11):
        row_avg.append("")
    table_data.append(row_avg)
    
    # Segunda fila: Valores mensuales
    row_values = ["Monthly Values"]
    for i, month in enumerate(months):
        if analysis_mode == "Percentages":
            row_values.append(f"{monthly_values[i]:.2f}%")
        else:
            row_values.append(f"{monthly_values[i]:,.0f}")
    row_values.extend([f"Monthly Values ({avg_unit})"])
    for _ in range(11):
        row_values.append("")
    table_data.append(row_values)
    
    # Tercera fila: Variabilidad
    row_var = ["Variability"]
    for _ in range(12):
        row_var.append("")
    row_var.extend([f"Variability ({var_unit})"])
    for i, month in enumerate(months):
        if variability[i] >= 0:
            row_var.append(f"+{variability[i]:.2f}" if analysis_mode == "Percentages" else f"+{variability[i]:,.2f}")
        else:
            row_var.append(f"{variability[i]:.2f}" if analysis_mode == "Percentages" else f"{variability[i]:,.2f}")
    table_data.append(row_var)
    
    # Crear columnas
    columns = ['Metric'] + months + ['Avg Mix'] + [f'{month}_var' for month in months]
    
    # Crear DataFrame
    df = pd.DataFrame(table_data, columns=columns)
    
    # Aplicar estilos
    def highlight_variability(row):
        styles = ['font-weight: bold']  # Primera columna en negrita
        
        # Columnas de valores mensuales (2-13)
        for i in range(1, 13):
            if row.index[i] in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                styles.append('background-color: #e8f4f8')
            else:
                styles.append('')
        
        # Columna Average Mix (14)
        styles.append('background-color: #fff2cc; font-weight: bold')
        
        # Columnas de variabilidad (15-26)
        for i in range(14, 26):
            if row.index[i].endswith('_var'):
                # Aplicar colores según el signo de la variabilidad
                if i >= 15:  # Primera fila de variabilidad
                    var_idx = i - 15
                    if var_idx < len(variability):
                        if variability[var_idx] > 0:
                            styles.append('background-color: #d4edda; color: #155724')  # Verde para positivo
                        elif variability[var_idx] < 0:
                            styles.append('background-color: #f8d7da; color: #721c24')  # Rojo para negativo
                        else:
                            styles.append('background-color: #f8f9fa')  # Gris para cero
                    else:
                        styles.append('')
                else:
                    styles.append('')
            else:
                styles.append('')
        
        return styles
    
    styled_df = df.style.apply(highlight_variability, axis=1)
    
    return styled_df, df


def calculate_historical_statistics(monthly_data: Dict[str, List[float]]) -> Dict[str, float]:
    """
    Calcula estadísticas históricas para múltiples compañías o períodos.
    
    Parámetros:
    -----------
    monthly_data : Dict[str, List[float]]
        Diccionario donde las claves son identificadores (compañía, región, etc.)
        y los valores son listas de 12 elementos con datos mensuales
        
    Retorna:
    --------
    Dict[str, float]
        Diccionario con estadísticas calculadas:
        - 'overall_average': Promedio general de todos los datos
        - 'monthly_averages': Promedio por mes de todas las entidades
        - 'total_variability': Variabilidad total del sistema
    """
    
    all_values = []
    monthly_totals = [0] * 12
    
    # Recopilar todos los datos
    for entity, data in monthly_data.items():
        all_values.extend(data)
        for i, value in enumerate(data):
            monthly_totals[i] += value
    
    # Calcular estadísticas
    overall_average = np.mean(all_values)
    monthly_averages = [total / len(monthly_data) for total in monthly_totals]
    
    # Calcular variabilidad total
    total_variability = np.std(all_values)
    
    return {
        'overall_average': overall_average,
        'monthly_averages': monthly_averages,
        'total_variability': total_variability,
        'entities_count': len(monthly_data)
    }


def create_all_companies_variability_table(
    all_companies_data: pd.DataFrame,
    grouping_method: str = "by_company",
    analysis_mode: str = "Percentages"
) -> Tuple[Any, pd.DataFrame]:
    """
    Crea tabla de variabilidad histórica para todas las compañías.
    
    Estructura de la tabla:
    - Filas: Compañías (una por fila)
    - Columnas: Average Mix + columnas alternadas (Valor del mes + Variabilidad del mes)
    
    Parámetros:
    -----------
    all_companies_data : pd.DataFrame
        DataFrame con datos de todas las compañías. Debe tener columnas:
        - 'company_name': Nombre de la compañía
        - 'company_id': ID de la compañía
        - 'monthly_calls': Array con números absolutos de llamadas (12 elementos)
        - 'calls_percentages': Array con porcentajes de llamadas (12 elementos)
    grouping_method : str
        Método de agrupación: "by_company", "by_region", "by_industry", "total"
    analysis_mode : str
        Modo de análisis: "Percentages" o "Absolute"
        
    Retorna:
    --------
    Tuple[pd.io.formats.style.Styler, pd.DataFrame]
        Tupla con (tabla con estilos, DataFrame sin estilos)
    """
    
    # Validar que tenemos datos
    if all_companies_data.empty:
        # Crear DataFrame vacío con estructura correcta
        empty_df = pd.DataFrame(columns=['Company', 'Average Mix'])
        return empty_df.style, empty_df
    
    # Preparar datos para la tabla
    table_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Crear columnas de la tabla
    columns = ['Company', 'Average Mix']
    for month in months:
        columns.extend([f'{month}', f'{month}_var'])
    
    # Procesar cada compañía
    for _, company_row in all_companies_data.iterrows():
        company_name = company_row.get('company_name', 'Unknown Company')
        company_id = company_row.get('company_id', 0)
        
        # Obtener datos mensuales
        monthly_calls = company_row.get('monthly_calls', np.zeros(12))
        calls_percentages = company_row.get('calls_percentages', np.zeros(12))
        
        # Convertir a arrays numpy si no lo son
        if not isinstance(monthly_calls, np.ndarray):
            monthly_calls = np.array(monthly_calls)
        if not isinstance(calls_percentages, np.ndarray):
            calls_percentages = np.array(calls_percentages)
        
        # Calcular promedio histórico
        if analysis_mode == "Percentages":
            average_mix = round(np.mean(calls_percentages), 2)
            monthly_values = calls_percentages
            avg_unit = "%"
            var_unit = "pp"
        else:
            average_mix = round(np.mean(monthly_calls), 2)
            monthly_values = monthly_calls
            avg_unit = "calls"
            var_unit = "calls"
        
        # Calcular variabilidad
        variability = [round(monthly_values[i] - average_mix, 2) for i in range(12)]
        
        # Crear fila para esta compañía
        row_data = [company_name]
        
        # Average Mix
        if analysis_mode == "Percentages":
            row_data.append(f"{average_mix:.2f}%")
        else:
            row_data.append(f"{average_mix:,.2f}")
        
        # Valores mensuales y variabilidad alternados
        for i, month in enumerate(months):
            # Valor del mes
            if analysis_mode == "Percentages":
                row_data.append(f"{monthly_values[i]:.2f}%")
            else:
                row_data.append(f"{monthly_values[i]:,.0f}")
            
            # Variabilidad del mes
            if variability[i] >= 0:
                if analysis_mode == "Percentages":
                    row_data.append(f"+{variability[i]:.2f}")
                else:
                    row_data.append(f"+{variability[i]:,.2f}")
            else:
                if analysis_mode == "Percentages":
                    row_data.append(f"{variability[i]:.2f}")
                else:
                    row_data.append(f"{variability[i]:,.2f}")
        
        table_data.append(row_data)
    
    # Crear DataFrame sin encabezado duplicado
    df = pd.DataFrame(table_data, columns=columns)
    
    # Aplicar estilos
    def highlight_variability_table(row):
        styles = []
        
        # Primera columna (Company) - negrita
        styles.append('font-weight: bold; background-color: #f8f9fa')
        
        # Segunda columna (Average Mix) - amarillo
        styles.append('background-color: #fff2cc; font-weight: bold')
        
        # Columnas alternadas (Valor del mes + Variabilidad)
        for i in range(2, len(row)):
            col_name = row.index[i]
            
            if col_name.endswith('_var'):
                # Columna de variabilidad
                var_value = row.iloc[i]
                if isinstance(var_value, str):
                    if var_value.startswith('+'):
                        styles.append('background-color: #d4edda; color: #155724')  # Verde para positivo
                    elif var_value.startswith('-'):
                        styles.append('background-color: #f8d7da; color: #721c24')  # Rojo para negativo
                    else:
                        styles.append('background-color: #f8f9fa')  # Gris para cero
                else:
                    styles.append('background-color: #f8f9fa')
            else:
                # Columna de valor mensual
                styles.append('background-color: #e8f4f8')  # Azul claro
        
        return styles
    
    styled_df = df.style.apply(highlight_variability_table, axis=1)
    
    return styled_df, df


# =============================================================================
# EJEMPLOS DE USO
# =============================================================================

def example_single_company():
    """Ejemplo de uso para una sola compañía."""
    
    # Datos de ejemplo
    monthly_calls = np.array([1200, 1100, 1300, 1400, 1500, 1600, 1700, 1600, 1500, 1400, 1300, 1200])
    calls_percentages = np.array([8.33, 7.64, 9.03, 9.72, 10.42, 11.11, 11.81, 11.11, 10.42, 9.72, 9.03, 8.33])
    
    # Crear tabla de variabilidad
    styled_table, df = create_historical_variability_table(
        monthly_calls, 
        calls_percentages, 
        analysis_mode="Percentages",
        company_name="Monarch HVAC",
        company_id=1
    )
    
    print("Tabla de Variabilidad Histórica - Monarch HVAC")
    print("=" * 50)
    print(styled_table)
    
    return styled_table, df


def example_multiple_companies():
    """Ejemplo de uso para múltiples compañías."""
    
    # Datos de ejemplo para múltiples compañías
    companies_data = {
        'Monarch HVAC': [8.33, 7.64, 9.03, 9.72, 10.42, 11.11, 11.81, 11.11, 10.42, 9.72, 9.03, 8.33],
        'Elite Plumbing': [7.89, 7.12, 8.45, 9.18, 9.91, 10.64, 11.37, 10.64, 9.91, 9.18, 8.45, 7.89],
        'Premium Electric': [8.76, 8.12, 9.38, 10.04, 10.70, 11.36, 12.02, 11.36, 10.70, 10.04, 9.38, 8.76]
    }
    
    # Calcular estadísticas
    stats = calculate_historical_statistics(companies_data)
    
    print("Estadísticas Históricas - Múltiples Compañías")
    print("=" * 50)
    print(f"Promedio General: {stats['overall_average']:.2f}%")
    print(f"Variabilidad Total: {stats['total_variability']:.2f}%")
    print(f"Número de Entidades: {stats['entities_count']}")
    print(f"Promedios Mensuales: {[f'{x:.2f}%' for x in stats['monthly_averages']]}")
    
    return stats




if __name__ == "__main__":
    print("Historical Variability Analyzer")
    print("=" * 40)
    
    # Ejecutar ejemplos
    print("\n1. Ejemplo - Una Compañía:")
    example_single_company()
    
    print("\n2. Ejemplo - Múltiples Compañías (Estadísticas):")
    example_multiple_companies()
    
    print("\n✅ Script ejecutado exitosamente")
