/* ============================================================
   NEXTLEVEL_PEOPLE — SQL "EDA" DE COMPROBACIÓN DE CARGA
   Objetivo:
   - Verificar que la base de datos está cargada correctamente
   - Comprobar: recuentos, nulos, rangos, claves foráneas, duplicados
   - Obtener una “foto” rápida de distribuciones básicas

   Nota:
   - Esto NO es análisis de negocio (no hipótesis ni insights),
     es QA/validación de carga.
   ============================================================ */

USE nextlevel_people;


-- ============================================================
-- 1) RECUENTOS BÁSICOS (¿cuántas filas hay en cada tabla?)
-- ============================================================

SELECT 'employees' 				AS table_name, COUNT(*) AS row_count FROM employees
UNION ALL
SELECT 'departments' 			AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'job_roles' 				AS table_name, COUNT(*) AS row_count FROM job_roles
UNION ALL
SELECT 'education_fields' 		AS table_name, COUNT(*) AS row_count FROM education_fields
UNION ALL
SELECT 'business_travel_types'  AS table_name, COUNT(*) AS row_count FROM business_travel_types
UNION ALL
SELECT 'marital_statuses'       AS table_name, COUNT(*) AS row_count FROM marital_statuses
UNION ALL
SELECT 'genders'                AS table_name, COUNT(*) AS row_count FROM genders;


-- ============================================================
-- 2) COMPROBACIÓN CRÍTICA: ¿employees tiene 1470 filas?
-- ============================================================

SELECT COUNT(*) AS employees_rows
FROM employees;

-- ============================================================
-- 3) ¿HAY DUPLICADOS DEL ID DE ORIGEN (source_employee_id)?
--    (debe ser 0 duplicados)
-- ============================================================
SELECT 
  COUNT(*) - COUNT(DISTINCT source_employee_id) AS duplicated_source_ids
FROM employees;


-- ============================================================
-- 4) COMPROBACIÓN DE NULOS EN EMPLOYEES (debe ser 0 en todo)
-- ============================================================

SELECT
  SUM(source_employee_id IS NULL)        AS null_source_employee_id,
  SUM(department_id IS NULL)             AS null_department_id,
  SUM(job_role_id IS NULL)               AS null_job_role_id,
  SUM(education_field_id IS NULL)        AS null_education_field_id,
  SUM(business_travel_id IS NULL)        AS null_business_travel_id,
  SUM(marital_status_id IS NULL)         AS null_marital_status_id,
  SUM(gender_id IS NULL)                 AS null_gender_id,
  SUM(age IS NULL)                       AS null_age,
  SUM(education_level IS NULL)           AS null_education_level,
  SUM(num_companies_worked IS NULL)      AS null_num_companies_worked,
  SUM(total_years_worked IS NULL)        AS null_total_years_worked,
  SUM(job_level IS NULL)                 AS null_job_level,
  SUM(over_time IS NULL)                 AS null_over_time,
  SUM(training_last_year IS NULL)        AS null_training_last_year,
  SUM(distance_from_home IS NULL)        AS null_distance_from_home,
  SUM(monthly_income IS NULL)            AS null_monthly_income,
  SUM(daily_rate IS NULL)                AS null_daily_rate,
  SUM(hourly_rate IS NULL)               AS null_hourly_rate,
  SUM(salary_hike_pct IS NULL)           AS null_salary_hike_pct,
  SUM(stock_option_level IS NULL)        AS null_stock_option_level,
  SUM(years_at_company IS NULL)          AS null_years_at_company,
  SUM(years_in_current_role IS NULL)     AS null_years_in_current_role,
  SUM(years_since_last_promotion IS NULL)AS null_years_since_last_promotion,
  SUM(years_with_current_manager IS NULL)AS null_years_with_current_manager,
  SUM(attrition IS NULL)                 AS null_attrition
FROM employees;


-- ============================================================
-- 5) RANGOS / CHECKS (validación rápida)
--    Si todo está bien, "bad_rows" debe ser 0 en cada bloque.
-- ============================================================

-- 5.1 Age > 0
SELECT COUNT(*) AS bad_rows_age
FROM employees
WHERE age <= 0;

-- 5.2 education_level 1..5
SELECT COUNT(*) AS bad_rows_education_level
FROM employees
WHERE education_level NOT BETWEEN 1 AND 5;

-- 5.3 job_level 1..5
SELECT COUNT(*) AS bad_rows_job_level
FROM employees
WHERE job_level NOT BETWEEN 1 AND 5;

-- 5.4 salary_hike_pct 0..100
SELECT COUNT(*) AS bad_rows_salary_hike_pct
FROM employees
WHERE salary_hike_pct NOT BETWEEN 0 AND 100;

-- 5.5 No negativos donde no deben existir
SELECT COUNT(*) AS bad_rows_negative_values
FROM employees
WHERE
  num_companies_worked < 0 OR
  total_years_worked < 0 OR
  training_last_year < 0 OR
  distance_from_home < 0 OR
  monthly_income < 0 OR
  daily_rate < 0 OR
  hourly_rate < 0 OR
  stock_option_level < 0 OR
  years_at_company < 0 OR
  years_in_current_role < 0 OR
  years_since_last_promotion < 0 OR
  years_with_current_manager < 0;

-- 5.6 Booleans (0/1)
SELECT COUNT(*) AS bad_rows_booleans
FROM employees
WHERE
  over_time NOT IN (0,1) OR
  attrition NOT IN (0,1);


-- ============================================================
-- 6) INTEGRIDAD REFERENCIAL (FKs)
--    Esto detecta "huérfanos" (empleados cuyo FK no existe en la dimensión).
--    Si todo está bien, todas las consultas deben devolver 0.
-- ============================================================

-- 6.1 department_id huérfanos
SELECT COUNT(*) AS orphan_department_fk
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE d.department_id IS NULL;

-- 6.2 job_role_id huérfanos
SELECT COUNT(*) AS orphan_job_role_fk
FROM employees e
LEFT JOIN job_roles jr ON e.job_role_id = jr.job_role_id
WHERE jr.job_role_id IS NULL;

-- 6.3 education_field_id huérfanos
SELECT COUNT(*) AS orphan_education_field_fk
FROM employees e
LEFT JOIN education_fields ef ON e.education_field_id = ef.education_field_id
WHERE ef.education_field_id IS NULL;

-- 6.4 business_travel_id huérfanos
SELECT COUNT(*) AS orphan_business_travel_fk
FROM employees e
LEFT JOIN business_travel_types bt ON e.business_travel_id = bt.business_travel_id
WHERE bt.business_travel_id IS NULL;

-- 6.5 marital_status_id huérfanos
SELECT COUNT(*) AS orphan_marital_status_fk
FROM employees e
LEFT JOIN marital_statuses ms ON e.marital_status_id = ms.marital_status_id
WHERE ms.marital_status_id IS NULL;

-- 6.6 gender_id huérfanos
SELECT COUNT(*) AS orphan_gender_fk
FROM employees e
LEFT JOIN genders g ON e.gender_id = g.gender_id
WHERE g.gender_id IS NULL;


-- ============================================================
-- 7) DISTRIBUCIONES BÁSICAS (para ver que "tiene sentido")
--    Esto no busca conclusiones, solo sanity checks.
-- ============================================================

-- 7.1 Attrition (recuento y %)
SELECT
  attrition,
  COUNT(*) AS n,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM employees), 2) AS pct
FROM employees
GROUP BY attrition
ORDER BY attrition;

-- 7.2 OverTime (recuento y %)
SELECT
  over_time,
  COUNT(*) AS n,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM employees), 2) AS pct
FROM employees
GROUP BY over_time
ORDER BY over_time;

-- 7.3 Empleados por Department
SELECT
  d.department_name,
  COUNT(*) AS n
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY n DESC;

-- 7.4 Empleados por Job Role (top 15)
SELECT
  jr.job_role_name,
  COUNT(*) AS n
FROM employees e
JOIN job_roles jr ON e.job_role_id = jr.job_role_id
GROUP BY jr.job_role_name
ORDER BY n DESC
LIMIT 15;

-- 7.5 Estadísticos rápidos de salario (monthly_income)
SELECT
  MIN(monthly_income) AS min_monthly_income,
  MAX(monthly_income) AS max_monthly_income,
  ROUND(AVG(monthly_income), 2) AS avg_monthly_income
FROM employees;

-- 7.6 Años en la empresa (years_at_company)
SELECT
  MIN(years_at_company) AS min_years_at_company,
  MAX(years_at_company) AS max_years_at_company,
  ROUND(AVG(years_at_company), 2) AS avg_years_at_company
FROM employees;


-- ============================================================
-- 8) MUESTRA DE DATOS (para inspección visual rápida)
-- ============================================================
SELECT
  e.employee_id,
  e.source_employee_id,
  d.department_name,
  jr.job_role_name,
  ef.education_field_name,
  bt.business_travel_name,
  ms.marital_status_name,
  g.gender_name,
  e.age,
  e.education_level,
  e.job_level,
  e.monthly_income,
  e.over_time,
  e.attrition
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_roles jr ON e.job_role_id = jr.job_role_id
JOIN education_fields ef ON e.education_field_id = ef.education_field_id
JOIN business_travel_types bt ON e.business_travel_id = bt.business_travel_id
JOIN marital_statuses ms ON e.marital_status_id = ms.marital_status_id
JOIN genders g ON e.gender_id = g.gender_id
ORDER BY e.employee_id
LIMIT 20;


-- ============================================================
-- 9) COMPROBACIÓN: ¿hay categorías "Unknown" en dimensiones?
--    Esto sirve para validar que la imputación se cargó.
-- ============================================================

SELECT 'departments' AS dim, COUNT(*) AS unknown_rows
FROM departments
WHERE department_name = 'Unknown'
UNION ALL
SELECT 'job_roles', COUNT(*)
FROM job_roles
WHERE job_role_name = 'Unknown'
UNION ALL
SELECT 'education_fields', COUNT(*)
FROM education_fields
WHERE education_field_name = 'Unknown'
UNION ALL
SELECT 'business_travel_types', COUNT(*)
FROM business_travel_types
WHERE business_travel_name = 'Unknown'
UNION ALL
SELECT 'marital_statuses', COUNT(*)
FROM marital_statuses
WHERE marital_status_name = 'Unknown'
UNION ALL
SELECT 'genders', COUNT(*)
FROM genders
WHERE gender_name = 'Unknown';

/* ============================================================
   10) CATÁLOGOS DE DIMENSIONES (VALIDACIÓN DE DECISIONES)
   Objetivo:
   - Confirmar que las dimensiones contienen exactamente las categorías esperadas
   - Dejar evidencia reproducible de decisiones de limpieza/modelado
   ============================================================ */

-- 10.1 Business Travel (decisión: "Non" = no viaja)
SELECT 
  business_travel_id,
  business_travel_name
FROM business_travel_types
ORDER BY business_travel_id;

-- 10.2 Marital Status (incluye categoría "Unknown" por imputación)
SELECT 
  marital_status_id,
  marital_status_name
FROM marital_statuses
ORDER BY marital_status_id;

-- 10.3 Education Field (incluye categoría "Unknown" por imputación)
SELECT 
  education_field_id,
  education_field_name
FROM education_fields
ORDER BY education_field_id;

-- 10.4 Departments
SELECT 
  department_id,
  department_name
FROM departments
ORDER BY department_id;

-- 10.5 Job Roles
SELECT 
  job_role_id,
  job_role_name
FROM job_roles
ORDER BY job_role_id;

-- 10.6 Genders
SELECT 
  gender_id,
  gender_name
FROM genders
ORDER BY gender_id;


/* ============================================================
   11) VALIDACIÓN ESPECÍFICA DE CATEGORÍAS "SPECIAL CASES"
   Objetivo:
   - Confirmar que "Unknown" existe y cuántos empleados caen en esa categoría
   - Confirmar cuántos empleados están en business_travel = 'Non'
   ============================================================ */

-- 11.1 ¿Cuántos empleados tienen Education Field = 'Unknown'?
SELECT
  ef.education_field_name,
  COUNT(*) AS n_employees
FROM employees e
JOIN education_fields ef ON e.education_field_id = ef.education_field_id
WHERE ef.education_field_name = 'Unknown'
GROUP BY ef.education_field_name;

-- 11.2 ¿Cuántos empleados tienen Marital Status = 'Unknown'?
SELECT
  ms.marital_status_name,
  COUNT(*) AS n_employees
FROM employees e
JOIN marital_statuses ms ON e.marital_status_id = ms.marital_status_id
WHERE ms.marital_status_name = 'Unknown'
GROUP BY ms.marital_status_name;

-- 11.3 ¿Cuántos empleados tienen Business Travel = 'Non' (no viaja)?
SELECT
  bt.business_travel_name,
  COUNT(*) AS n_employees
FROM employees e
JOIN business_travel_types bt ON e.business_travel_id = bt.business_travel_id
WHERE bt.business_travel_name = 'Non'
GROUP BY bt.business_travel_name;

-- 11.4 Distribución completa de Business Travel (sanity check)
SELECT
  bt.business_travel_name,
  COUNT(*) AS n_employees,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM employees), 2) AS pct
FROM employees e
JOIN business_travel_types bt ON e.business_travel_id = bt.business_travel_id
GROUP BY bt.business_travel_name
ORDER BY n_employees DESC;



