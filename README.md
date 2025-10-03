# Historical Variability Analyzer
## Análisis de Variabilidad Histórica para Datos Mensuales

---

## 📋 **Resumen del Proyecto**

Este proyecto desarrolló una funcionalidad avanzada para analizar la **variabilidad histórica** de datos mensuales, específicamente diseñada para el análisis de llamadas de ServiceTitan. La funcionalidad permite identificar patrones estacionales y calcular desviaciones respecto al promedio histórico.

### **🎯 Objetivo Principal**
Crear una tabla de **25 columnas** que muestre:
1. **Average Mix** (promedio histórico de 12 meses)
2. **12 columnas de meses** (Jan-Dec)
3. **12 columnas de variabilidad** (diferencia de cada mes vs. promedio)

---

## 🧠 **Concepto Técnico**

### **Variabilidad Histórica**
La variabilidad histórica se calcula como la **diferencia entre cada mes y el promedio histórico**:

```
Variabilidad[mes] = Valor[mes] - Promedio_Histórico
```

### **Ejemplo Práctico**
Si una compañía tiene:
- **Promedio histórico**: 8.33%
- **Junio**: 11.11%
- **Diciembre**: 8.33%

Entonces:
- **Variabilidad Junio**: +2.78% (por encima del promedio)
- **Variabilidad Diciembre**: 0.00% (igual al promedio)

---

## 📊 **Estructura de la Tabla (25 Columnas)**

```
| Metric           | Jan | Feb | Mar | ... | Dec | Avg Mix | Jan_var | Feb_var | ... | Dec_var |
|------------------|-----|-----|-----|-----|-----|---------|---------|---------|-----|---------|
| Average Mix (%)  | 8.33|     |     |     |     | 8.33    |         |         |     |         |
| Monthly Values   | 7.64| 9.03| 9.72| ... | 8.33| 8.33    |         |         |     |         |
| Variability      |     |     |     |     |     |         | -0.69   | +0.70   | ... | 0.00    |
```

### **Colores y Formato**
- **🟢 Verde**: Variabilidad positiva (meses por encima del promedio)
- **🔴 Rojo**: Variabilidad negativa (meses por debajo del promedio)
- **⚪ Gris**: Variabilidad cero (igual al promedio)
- **🔵 Azul claro**: Valores mensuales
- **🟡 Amarillo**: Columna Average Mix

---

## 🛠️ **Implementación Técnica**

### **Función Principal**
```python
def create_historical_variability_table(
    monthly_calls: np.ndarray, 
    calls_percentages: np.ndarray, 
    analysis_mode: str = "Percentages",
    company_name: str = "Company",
    company_id: int = 1
) -> Tuple[pd.io.formats.style.Styler, pd.DataFrame]
```

### **Parámetros de Entrada**
- `monthly_calls`: Array con números absolutos de llamadas (12 elementos)
- `calls_percentages`: Array con porcentajes de llamadas (12 elementos)
- `analysis_mode`: "Percentages" o "Absolute"
- `company_name`: Nombre de la compañía
- `company_id`: ID de la compañía

### **Retorno**
- **Tabla con estilos**: Para visualización en Streamlit
- **DataFrame sin estilos**: Para exportación y análisis

---

## 📈 **Casos de Uso Desarrollados**

### **1. Análisis Individual (Implementado)**
- **Una compañía** con datos históricos
- **Vida operativa**: Desde 2015 hasta datos actuales
- **Filtrado**: Excluye meses sin datos (aparecen en gris)

### **2. Análisis Multi-Compañía (Para Implementar)**
- **Todas las compañías** en una sola vista
- **Agrupación**: Por región, industria, tamaño
- **Comparación**: Patrones entre diferentes entidades

---

## 🔢 **Redondeos y Formato**

### **Estándares Implementados**
- **Porcentajes**: 2 decimales (ej: 8.33%)
- **Cantidad de llamadas**: Enteros (ej: 1,234)
- **Promedios**: 2 decimales (ej: 8.33)
- **Variabilidad**: 2 decimales con signo (ej: +2.78, -1.45)

---

## 🌐 **Internacionalización**

### **Traducciones Implementadas**
**Inglés:**
- "Historical Variability"
- "Average Mix"
- "Monthly Values"
- "Variability"

**Español:**
- "Variabilidad Histórica"
- "Promedio General"
- "Valores Mensuales"
- "Variabilidad"

---

## 📤 **Funcionalidades de Exportación**

### **Preparado para:**
- **Google Sheets**: Botón de exportación implementado
- **CSV**: DataFrame exportable
- **PDF**: Tabla con estilos aplicados

---

## 🎨 **Integración Visual**

### **En Dashboard Streamlit**
- **Posicionamiento**: Antes de la tabla anual
- **Separadores**: Líneas divisorias para organización
- **Responsive**: Se adapta al contenedor
- **Interactivo**: Botones de exportación

---

## 🔧 **Dependencias**

### **Librerías Requeridas**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from typing import Tuple, Optional, Dict, List
```

---

## 📝 **Historial de Desarrollo**

### **Fase 1: Concepto (Chat Original)**
- ✅ Identificación de necesidad de análisis de variabilidad
- ✅ Diseño de estructura de tabla (25 columnas)
- ✅ Implementación de función principal

### **Fase 2: Integración**
- ✅ Integración en dashboard Streamlit
- ✅ Aplicación de estilos y colores
- ✅ Corrección de redondeos

### **Fase 3: Preparación Multi-Proyecto**
- ✅ Extracción a script independiente
- ✅ Documentación completa
- ✅ Ejemplos de uso

---

## 🚀 **Dashboard de Streamlit Implementado**

### **✅ Funcionalidades Completadas**
1. **Panel de control**: Selector de porcentajes vs. cantidades absolutas
2. **Visualización multi-compañía**: Todas las compañías en una tabla
3. **Encabezado con doble fila**: Meses agrupados + Valores/Variabilidad
4. **Exportación**: A Google Sheets con un click
5. **Estilos avanzados**: Colores intuitivos para diferentes tipos de datos

### **📊 Estructura del Dashboard**
- **Filas**: Compañías (una por fila)
- **Columnas**: Average Mix + columnas alternadas (Valor del mes + Variabilidad)
- **Colores**: Amarillo (Average Mix), Azul (Valores), Verde/Rojo (Variabilidad)

### **🛠️ Archivos del Proyecto**
- `dashboard.py` - Dashboard principal de Streamlit
- `historical_variability_analyzer.py` - Funciones de análisis
- `requirements.txt` - Dependencias
- `Dockerfile` - Configuración de contenedor
- `.dockerignore` - Archivos a ignorar en Docker

### **🚀 Instrucciones de Uso**

#### **Ejecución Local**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
streamlit run dashboard.py
```

#### **Ejecución con Docker**
```bash
# Construir imagen
docker build -t historical-variability-dashboard .

# Ejecutar contenedor
docker run -p 8501:8501 historical-variability-dashboard
```

#### **Deploy a Google Cloud Run**
```bash
# Ejecutar script de build & deploy
./build_deploy.sh

# O manualmente:
gcloud builds submit --tag gcr.io/platform-partners-qua/historical-variability-analyzer
gcloud run deploy historical-variability-analyzer --image gcr.io/platform-partners-qua/historical-variability-analyzer --platform managed --region us-east1 --allow-unauthenticated --port 8501
```

#### **Configuración de Google Sheets (Opcional)**
Para habilitar la exportación a Google Sheets:
1. Crear proyecto en Google Cloud Console
2. Habilitar APIs de Google Sheets y Google Drive
3. Crear cuenta de servicio y descargar credenciales JSON
4. Configurar en Streamlit Cloud o localmente como secrets

---

## 💡 **Insights Generados**

### **Patrones Identificados**
- **Estacionalidad**: Picos en verano (Jun-Jul), valles en invierno (Dec-Jan)
- **Variabilidad**: Meses con mayor desviación del promedio histórico
- **Consistencia**: Compañías con patrones similares vs. atípicas

### **Valor de Negocio**
- **Planificación**: Identificar meses de alta/baja demanda
- **Recursos**: Optimizar asignación de personal
- **Predicción**: Base para modelos predictivos

---

## 📞 **Contexto del Proyecto Original**

### **Plataforma**: ServiceTitan
### **Datos**: Llamadas de marketing y servicio
### **Período**: 2015 - Presente
### **Filtros**: Solo llamadas entrantes (Inbound)
### **Granularidad**: Mensual por compañía

### **Tabla Original**: `pph-central.silver.vw_consolidated_call_inbound_location`
### **Compañías**: `pph-central.settings.companies`

---

## 🔗 **Archivos del Proyecto**

### **Script Principal**
- `historical_variability_analyzer.py` - Función principal extraída

### **Documentación**
- `README_HISTORICAL_VARIABILITY.md` - Este archivo

### **Proyecto Original**
- `calls_analysis_dashboard/dashboard.py` - Implementación completa
- `calls_analysis_dashboard/locales/` - Traducciones

---

## ✅ **Estado del Desarrollo**

- ✅ **Función principal**: Completamente funcional
- ✅ **Integración**: Probada en dashboard
- ✅ **Estilos**: Aplicados correctamente
- ✅ **Redondeos**: Corregidos según estándares
- ✅ **Traducciones**: Inglés y español
- ✅ **Documentación**: Completa
- 🔄 **Multi-compañía**: Para implementar en nuevo proyecto

---

**Desarrollado por**: Assistant AI + Platform Partners Team  
**Fecha**: Octubre 2025  
**Versión**: 1.0  
**Estado**: Listo para nuevo proyecto
