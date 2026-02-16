## **Informe de Análisis Exploratorio y Decisiones de Calidad de Datos**

---
### **1. Contexto y objetivo del documento**

Este documento recoge las **decisiones de calidad de datos** adoptadas tras el análisis exploratorio del dataset de Recursos Humanos (`hr.csv`), con el objetivo de preparar un conjunto de datos consistente, completo y válido para su uso en análisis descriptivo y modelado predictivo de *attrition*.

*Flujo del proyecto:*

1. **EDA (00_EDA.ipynb)**: exploración inicial y detección de problemas
2. **Informe de Análisis Exploratorio (Data_quality_report.ipynb)**: justificación de decisiones de limpieza
3. **Limpieza (01_Limpieza.ipynb)**: implementación reproducible de las transformaciones

**Audiencia:** científicos de datos, analistas y revisores técnicos que necesiten comprender las transformaciones aplicadas al dataset original.


---
### **2. Visión general del dataset original**

#### *2.1 Dimensiones iniciales*

| Métrica | Valor |
|---------|-------|
| **Registros totales** | 1.474 empleados |
| **Variables totales** | 35 columnas |
| **Registros duplicados** | 4 (0,27%) |

#### *2.2 Variable objetivo*

**attrition** → Variable categórica binaria que indica si el empleado abandonó la empresa (`Yes`) o permanece en ella (`No`). Esta variable será el objetivo (*target*) en análisis posteriores.

#### *2.3 Naturaleza de las variables*

El dataset contiene información de múltiples dimensiones:

- **Demográfica**: edad, género, estado civil, distancia al trabajo
- **Laboral**: departamento, rol, nivel, años en la empresa
- **Salarial**: salario mensual, tasas diarias/horarias
- **Satisfacción**: encuestas de ambiente, balance vida-trabajo, relaciones
- **Desempeño**: calificaciones de rendimiento, involucramiento


---
### **3. Problemas identificados en el EDA**

Durante la exploración inicial se detectaron los siguientes problemas de calidad:

#### *3.1 Problemas estructurales*

| Problema | Impacto |
|----------|---------|
| **Duplicados completos** (4 registros) | Sesgo en estimaciones y entrenamiento de modelos |
| **Columnas constantes** (3 variables) | Sin valor predictivo, ruido dimensional |
| **Alta cardinalidad no informativa** (1 variable) | Ruido sin señal útil |
| **Identificador único sin valor analítico** | Riesgo de *data leakage* |

#### *3.2 Problemas de tipado y formato*

| Problema | Variables afectadas |
|----------|---------------------|
| **Tipos incorrectos** | Variables numéricas discretas almacenadas como float o viceversa |
| **Escalas ordinales sin mapeo** | Variables de satisfacción (1-4) sin etiquetas semánticas |
| **Inconsistencias en categorías** | Capitalización errática, espacios extra, errores tipográficos |

#### *3.3 Problemas de completitud*

| Tipo de variable | Variables con nulos |
|------------------|---------------------|
| **Categóricas** | 6 variables |
| **Numéricas** | 4 variables |


---
### **4. Decisiones de limpieza adoptadas**

#### *4.1 Eliminación de registros duplicados*

**Problema:** Se detectaron 4 registros duplicados (0,27% del dataset).

**Decisión:** Eliminar todos los duplicados completos.

**Justificación:**
- Los duplicados no aportan información adicional
- Introducen sesgos en estadísticas descriptivas (media, varianza)
- Afectan negativamente el entrenamiento de modelos predictivos
- Al representar menos del 1% del dataset, su eliminación no compromete el tamaño muestral

**Implementación:** Función `eliminar_filas_duplicadas()` con validación de cambios


---
#### *4.2 Establecimiento de índice único*

**Problema:** La variable `employee_number` actúa como identificador único pero no como índice del DataFrame.

**Decisión:** Establecer `employee_number` como índice y excluirla del modelado.

**Justificación:**
- Permite identificación unívoca de registros
- Facilita operaciones de *join* y *merge*
- Previene *data leakage* al excluirla de variables predictoras

**Implementación:** Función `usar_columna_como_indice()` con validación de cambios


---
#### *4.3 Eliminación de columnas sin valor analítico*

##### 4.3.1 Columnas constantes

**Variables eliminadas:**
- `employee_count` → constante = 1
- `over18` → constante = "Y"
- `standard_hours` → constante = 80.0

**Justificación:**
- Variables constantes no contienen varianza
- No aportan información discriminatoria
- No pueden contribuir a ningún modelo descriptivo ni predictivo
- Su eliminación reduce dimensionalidad sin pérdida de información

##### 4.3.2 Columnas de alta cardinalidad no informativa

**Variable eliminada:**
- `monthly_rate` → 1.427 valores únicos (97% cardinalidad)

**Justificación:**
- No representa una variable de negocio claramente interpretable
- Potencial fuente de ruido en modelos
- Otras variables salariales (`monthly_income`) son más informativas

**Implementación:** Función `eliminar_columnas_sin_aporte_analítico()` con validación de cambios


---
#### *4.4 Normalización de nombres de columnas*

**Problema:** Nombres de columnas inconsistentes (mayúsculas, sin espacios, etc.).

**Decisión:** Estandarizar todos los nombres a formato `snake_case` minúsculas.

**Ejemplo de transformación:**
- `EmployeeNumber` → `employee_number`
- `JobRole` → `job_role`
- `YearsWithCurrManager` → `years_with_curr_manager`

**Justificación:**
- Facilita el acceso programático a columnas
- Evita errores por inconsistencias en capitalización
- Sigue convenciones estándar de Python/pandas/BD
- Mejora la legibilidad del código

**Implementación:** Función `normalizar_nombres_columnas()` con validación de cambios


---
#### *4.5 Conversión de tipos de datos*

Se identificaron múltiples variables con tipos incorrectos que impedían análisis numérico o categórico apropiado.

##### 4.5.1 Variables numéricas

**Conversiones realizadas:**

| Variable | Tipo original | Tipo objetivo | Justificación |
|----------|---------------|---------------|---------------|
| `age` | float64 | `Int64` | Variable discreta (con nulos) |
| `daily_rate` | int64 | `float64` | Variable continua de tasa salarial |
| `hourly_rate` | int64 | `float64` | Variable continua de tasa salarial |
| `training_times_last_year` | float64 | `Int64` | Conteo discreto |
| `years_with_curr_manager` | float64 | `Int64` | Variable temporal discreta |

**Implementación:** Función `convertir_tipos_columnas()` con validación de cambios

##### 4.5.2 Variables categóricas ordinales

**Variables identificadas con orden semántico inherente:**

| Variable | Escala | Interpretación |
|----------|--------|----------------|
| `education` | 1-5 | Nivel educativo |
| `environment_satisfaction` | 1-4 | Satisfacción con el ambiente |
| `job_involvement` | 1-4 | Nivel de involucramiento |
| `job_level` | 1-5 | Nivel jerárquico |
| `job_satisfaction` | 1-4 | Satisfacción laboral |
| `performance_rating` | 1-4 | Calificación de desempeño |
| `relationship_satisfaction` | 1-4 | Satisfacción con relaciones |
| `stock_option_level` | 0-3 | Nivel de opciones de acciones |
| `work_life_balance` | 1-4 | Balance vida-trabajo |

**Decisión:** Mantener como categóricas ordinales con mapeo semántico explícito.

**Mapeo aplicado a variables de satisfacción (escala 1-4):**

| Valor | Etiqueta |
|-------|----------|
| 1 | Muy Insatisfecho |
| 2 | Insatisfecho |
| 3 | Satisfecho |
| 4 | Muy Satisfecho |

**Justificación:**
- Preserva el orden inherente para análisis
- Mejora interpretabilidad en visualizaciones
- Facilita análisis de tendencias en encuestas
- Permite aplicar técnicas de *ordinal encoding* en modelado


---
#### *4.6 Normalización de variables categóricas*

**Problemas detectados:**
- Inconsistencias en capitalización: `"sALES eXECUTIVE"`, `"rESEARCH sCIENTIST"`
- Espacios extra al inicio o final
- Errores tipográficos: `"Marreid"` → `"Married"`

**Decisión:** Aplicar normalización sistemática.

**Transformaciones realizadas:**

1. **Eliminar espacios extra:** `str.strip()`
2. **Normalizar formato:** `str.title()` para formato Title Case
3. **Corregir errores tipográficos:** mapeo explícito de valores conocidos
4. **Simplificar categorías:** 
   - `"Travel_Rarely"` → `"Rarely"`
   - `"Travel_Frequently"` → `"Frequently"`
   - `"Non-Travel"` → `"Non"`

**Variables afectadas:**
- `business_travel`
- `job_role`
- `marital_status`

**Implementación:** Función `normalizar_columnas_texto()` con validación de cambios

**Beneficios:**
- Reduce cardinalidad artificial
- Previene fragmentación de categorías similares
- Mejora consistencia semántica
- Facilita análisis comparativo


---
#### *4.7 Tratamiento de valores nulos*

Se adoptó una estrategia diferenciada según tipo de variable y porcentaje de nulos.

##### 4.7.1 Estrategia para variables categóricas

**Criterio de decisión:**

| % Nulos | Estrategia | Justificación |
|---------|------------|---------------|
| **Bajo** (≤5%) | Imputar con **moda** | Solo si hay categoría verdaderamente dominante, sino imputa Unkown |
| **Medio** (5-20%) | Crear categoría **"Unknown"** | Solo si hay categoría verdaderamente dominante, sino imputa Unkown |
| **Alto** (>20%) | Crear categoría **"Unknown"** | Con muchos nulos, imputar por moda distorsiona demasiada información |

**Variables categóricas afectadas:**

| Variable | % Nulos | Estrategia aplicada |
|----------|---------|---------------------|
| `business_travel` | 7,96% | Moda |
| `department` | 1,97% | Moda |
| `education_field` | 3,95% | Categoría "Unknown" |
| `job_satisfaction` | 1,97% | Categoría "Unknown" |
| `marital_status` | 8,98% | Categoría "Unknown" |
| `over_time` | 2,99% | Moda |

**Implementación:** Función `imputar_categoricas()` con lógica condicional por umbral

##### 4.7.2 Estrategia para variables numéricas

**Criterio de decisión:**

| % Nulos | Estrategia | Justificación |
|---------|------------|---------------|
| **Bajo** (≤5%) | **Mediana** con `SimpleImputer` | Robusta frente a outliers, preserva distribución central |
| **Medio** (5-20%) | **KNNImputer** (k=5) con escalado | Preserva estructura multivariable, contexto de registros similares |
| **Alto** (>20%) | **KNN/Mediana** + **indicador de missingness** | Captura señal estructural del patrón de nulos |

**Variables afectadas:**

| Variable | % Nulos | Estrategia aplicada |
|----------|---------|---------------------|
| `age` | 4,97% | Mediana |
| `monthly_income` | 0,95% | Mediana |
| `training_times_last_year` | 5,99% | KNN (k=5) |
| `years_with_curr_manager` | 10,00% | KNN (k=5) |

**Detalles de implementación KNN:**

1. Selección de variables contextuales numéricas relacionadas
2. Escalado previo con `StandardScaler` (requisito de KNN)
3. Imputación con `KNNImputer(n_neighbors=5)`
4. Inversión del escalado para restaurar escala original
5. Redondeo y conversión a `Int64` para variables discretas

**Implementación:** Función `imputar_numericas()` con lógica condicional por umbral


---
#### *4.8 Tratamiento de outliers*

**Método de detección:** Rango Intercuartílico (IQR) con factor 1.5x

**Fórmula:**
- Límite inferior = Q1 - 1.5 × IQR
- Límite superior = Q3 + 1.5 × IQR

**Variables con outliers detectados:**

| Variable | % outliers |
|----------|------------|
| `num_companies_worked` | 3,53% |
| `monthly_income` | 7,67% |
| `performance_rating` | 15,33% |
| `stock_option_level` | 5,77% |
| `total_working_years` | 4,27% |
| `training_times_last_year` | 15,40% |
| `years_at_company` | 7,06% |
| `years_in_current_role` | 1,42% |
| `years_since_last_promotion` | 7,26% |
| `years_with_curr_manager` | 0,81% |

**Decisión:** **NO eliminar ni transformar outliers**

**Justificación:**
1. **Plausibilidad contextual:** Los valores extremos son realistas en un contexto empresarial real
2. **Representación de diversidad:** Capturan casos reales de ejecutivos de alto nivel, empleados remotos, etc.
3. **Baja frecuencia:** Representan <5% del dataset, no dominan la distribución
4. **Relevancia predictiva:** Pueden tener señal importante para attrition (ej: salarios muy altos/bajos, distancias extremas)
5. **Prevención de sesgo:** Eliminarlos podría artificialmente homogeneizar el dataset


---
#### *4.9 Análisis de correlación*

**Objetivo:** Identificar variables numéricas altamente correlacionadas que puedan causar multicolinealidad.

**Pares de variables con alta correlación detectados:**

| Variable 1 | Variable 2 | Correlación (r) | Relación conceptual |
|------------|------------|-----------------|---------------------|
| `job_level` | `monthly_income` | >0.90 | Nivel jerárquico determina salario |
| `job_level` | `total_working_years` | >0.75 | Nivel jerárquico correlaciona con experiencia total |
| `montly_income` | `total_working_years` | >0.75 | Nivel salarial correlaciona con experiencia total |
| `percent_salary_hike` | `performance_rating` | >0.75 | Subida salarial correlaciona con rendimiento |
| `years_at_company` | `years_with_curr_manager` | >0.75 | Antigüedad en la empresa correlaciona con años con el manager actual |
| `years_at_company` | `years_in_current_role` | >0.75 | Antigüedad en la empresa correlaciona con años en el rol actual  |
| `years_in_current_role` | `years_with_curr_manager` | >0.70 | Años en el rol actual correlaciona con años con el manager actual |

**Decisión:** Mantener todas las variables, relaciones coherentes.

**Justificación de mantenerlas:**
- Algunas representan conceptos distintos aunque correlacionen
- La correlación no implica total redundancia
- Diferentes modelos tienen distinta sensibilidad a multicolinealidad
- Permiten análisis descriptivo más rico


---
### **5. Estado final del dataset**

#### *5.1 Dimensiones finales*

| Métrica | Valor inicial | Valor final | Cambio |
|---------|---------------|-------------|--------|
| **Registros** | 1.474 | 1.470 | -4 (duplicados eliminados) |
| **Variables** | 35 | 30 | -5 (columnas sin valor eliminadas) |
| **Valores nulos** | 732 | 0 | -732 (100% imputados) |

#### *5.2 Calidad del dataset resultante*

✅ **Integridad:** 0% de valores nulos, 0% duplicados  
✅ **Consistencia:** Tipos de datos correctos, categorías normalizadas  
✅ **Validez:** Valores dentro de rangos esperados, escalas ordinales mapeadas  
✅ **Unicidad:** Índice único por empleado  
✅ **Relevancia:** Variables sin valor analítico eliminadas  


---
### **6. Validación y trazabilidad**

#### *6.1 Reproducibilidad*

Todas las decisiones documentadas en este informe han sido implementadas mediante funciones reutilizables y parametrizables en el notebook `01_Limpieza.ipynb`.

**Beneficios:**
- Reproducibilidad completa del pipeline de limpieza
- Consistencia entre entornos de desarrollo/producción
- Facilidad para reentrenar modelos con datos nuevos
- Auditoría completa del procesamiento

#### *6.2 Exportación de datos limpios*

**Ubicación:** `../data/processed/hr_processed.csv`


---
### **7. Conclusiones**

Este proceso de limpieza y preparación de datos ha transformado el dataset original en un conjunto de datos de **alta calidad**, **consistente** y **analíticamente válido**, listo para soportar análisis descriptivo robusto y modelado predictivo confiable.

**Logros principales:**

1. ✅ **Eliminación de inconsistencias:** Duplicados, tipos incorrectos, categorías fragmentadas
2. ✅ **Completitud total:** 0% de valores nulos mediante imputación inteligente
3. ✅ **Estandarización:** Nombres de columnas, formato de categorías, escalas ordinales
4. ✅ **Reducción de ruido:** Eliminación de variables sin valor analítico
5. ✅ **Trazabilidad:** Código reproducible y documentado

**Criterios de calidad cumplidos:**

| Dimensión | Estado |
|-----------|--------|
| **Exactitud** | ✅ Valores dentro de rangos válidos |
| **Completitud** | ✅ 0% valores nulos |
| **Consistencia** | ✅ Formatos y tipos estandarizados |
| **Oportunidad** | ✅ Dataset actualizado y relevante |
| **Validez** | ✅ Cumple reglas de negocio y restricciones semánticas |
| **Unicidad** | ✅ 0% duplicados, índice único establecido |

El dataset resultante constituye la **base oficial** para todas las fases posteriores del proyecto de análisis de attrition.

---
