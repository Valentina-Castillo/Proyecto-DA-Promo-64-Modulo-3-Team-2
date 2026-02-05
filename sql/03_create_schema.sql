/* ============================================================
   PROYECTO HR — CREACIÓN DE BASE DE DATOS (MySQL)
   Objetivo:
   - Crear un esquema en 3FN para almacenar empleados + dimensiones
   - Sin consultas analíticas en SQL
   - Carga de datos mediante SQLAlchemy (ETL en Python)

   Nota importante:
   - Los nulos de variables categóricas se imputan en Python con la categoría 'Unknown' antes de cargar.
   - Aquí SOLO definimos la estructura y las reglas básicas de integridad.
   ============================================================ */

/* 1) Creamos la base de datos.
   - utf8mb4 permite tildes y caracteres especiales sin problemas. */
DROP DATABASE IF EXISTS nextlevel_people;
CREATE DATABASE nextlevel_people
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE nextlevel_people;

/* ------------------------------------------------------------
   2) TABLAS DIMENSIÓN (catálogos)
   - Guardan valores categóricos repetidos.
   - Ventajas: consistencia, menos duplicación y BD en 3FN.
   - Todas tienen:
     * id autoincremental como PK
     * name único para no duplicar categorías
   ------------------------------------------------------------ */

/* Dimensión: Department */
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
  department_id INT AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(50) NOT NULL,
  CONSTRAINT uq_departments_name UNIQUE (department_name)
) ENGINE=InnoDB;

/* Dimensión: Job Role */
DROP TABLE IF EXISTS job_roles;
CREATE TABLE job_roles (
  job_role_id INT AUTO_INCREMENT PRIMARY KEY,
  job_role_name VARCHAR(80) NOT NULL,
  CONSTRAINT uq_job_roles_name UNIQUE (job_role_name)
) ENGINE=InnoDB;

/* Dimensión: Education Field */
DROP TABLE IF EXISTS education_fields;
CREATE TABLE education_fields (
  education_field_id INT AUTO_INCREMENT PRIMARY KEY,
  education_field_name VARCHAR(80) NOT NULL,
  CONSTRAINT uq_education_fields_name UNIQUE (education_field_name)
) ENGINE=InnoDB;

/* Dimensión: Business Travel */
DROP TABLE IF EXISTS business_travel_types;
CREATE TABLE business_travel_types (
  business_travel_id INT AUTO_INCREMENT PRIMARY KEY,
  business_travel_name VARCHAR(30) NOT NULL,
  CONSTRAINT uq_business_travel_name UNIQUE (business_travel_name)
) ENGINE=InnoDB;

/* Dimensión: Marital Status */
DROP TABLE IF EXISTS marital_statuses;
CREATE TABLE marital_statuses (
  marital_status_id INT AUTO_INCREMENT PRIMARY KEY,
  marital_status_name VARCHAR(30) NOT NULL,
  CONSTRAINT uq_marital_status_name UNIQUE (marital_status_name)
) ENGINE=InnoDB;

/* Dimensión: Gender */
DROP TABLE IF EXISTS genders;
CREATE TABLE genders (
  gender_id INT AUTO_INCREMENT PRIMARY KEY,
  gender_name VARCHAR(20) NOT NULL,
  CONSTRAINT uq_genders_name UNIQUE (gender_name)
) ENGINE=InnoDB;


/* ------------------------------------------------------------
   3) TABLA PRINCIPAL: employees
   - Contiene datos numéricos y flags (atributos del empleado).
   - Las columnas categóricas se guardan como IDs (FKs a dimensiones).
   - Como el dataset llega limpio desde Python:
     * usamos NOT NULL en todo lo que debe venir siempre
     * aplicamos CHECKs simples para rangos coherentes
   ------------------------------------------------------------ */

DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
	/* Identificador del empleado
	- No viene del CSV
	- Se genera automáticamente en la base de datos */
    employee_id INT AUTO_INCREMENT PRIMARY KEY,

  /* Claves foráneas a dimensiones (3FN) */
  department_id INT NOT NULL,
  job_role_id INT NOT NULL,
  education_field_id INT NOT NULL,
  business_travel_id INT NOT NULL,
  marital_status_id INT NOT NULL,
  gender_id INT NOT NULL,

  /* Sociodemográficas */
  age SMALLINT NOT NULL,
  education_level SMALLINT NOT NULL,     -- 1..5
  num_companies_worked SMALLINT NOT NULL,
  total_years_worked SMALLINT NOT NULL,

  /* Puesto / condiciones */
  job_level SMALLINT NOT NULL,           -- 1..5
  over_time BOOLEAN NOT NULL,            -- viene de Yes/No en Python
  training_last_year SMALLINT NOT NULL,
  distance_from_home SMALLINT NOT NULL,

  /* Compensación */
  monthly_income INT NOT NULL,
  monthly_rate INT NOT NULL,
  daily_rate INT NOT NULL,
  hourly_rate INT NOT NULL,
  salary_hike_pct SMALLINT NOT NULL,     -- 0..100
  stock_option_level SMALLINT NOT NULL,

  /* Trayectoria interna */
  years_at_company SMALLINT NOT NULL,
  years_in_current_role SMALLINT NOT NULL,
  years_since_last_promotion SMALLINT NOT NULL,
  years_with_current_manager SMALLINT NOT NULL,

  /* Variable objetivo */
  attrition BOOLEAN NOT NULL,            -- viene de Yes/No en Python

  /* --- CHECKS de coherencia (simples) ---
     Nota: en MySQL 8+ los CHECK se aplican. */
  CONSTRAINT chk_age_positive CHECK (age > 0),
  CONSTRAINT chk_education_level CHECK (education_level BETWEEN 1 AND 5),
  CONSTRAINT chk_job_level CHECK (job_level BETWEEN 1 AND 5),

  CONSTRAINT chk_nonneg_num_companies CHECK (num_companies_worked >= 0),
  CONSTRAINT chk_nonneg_total_years CHECK (total_years_worked >= 0),
  CONSTRAINT chk_nonneg_training CHECK (training_last_year >= 0),
  CONSTRAINT chk_nonneg_distance CHECK (distance_from_home >= 0),

  CONSTRAINT chk_nonneg_monthly_income CHECK (monthly_income >= 0),
  CONSTRAINT chk_nonneg_monthly_rate CHECK (monthly_rate >= 0),
  CONSTRAINT chk_nonneg_daily_rate CHECK (daily_rate >= 0),
  CONSTRAINT chk_nonneg_hourly_rate CHECK (hourly_rate >= 0),
  CONSTRAINT chk_salary_hike_pct CHECK (salary_hike_pct BETWEEN 0 AND 100),
  CONSTRAINT chk_nonneg_stock_level CHECK (stock_option_level >= 0),

  CONSTRAINT chk_nonneg_years_company CHECK (years_at_company >= 0),
  CONSTRAINT chk_nonneg_years_role CHECK (years_in_current_role >= 0),
  CONSTRAINT chk_nonneg_years_promo CHECK (years_since_last_promotion >= 0),
  CONSTRAINT chk_nonneg_years_manager CHECK (years_with_current_manager >= 0),

  /* --- FOREIGN KEYS ---
     RESTRICT evita borrar una dimensión si hay empleados que la usan. */
  CONSTRAINT fk_employees_departments
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_employees_job_roles
    FOREIGN KEY (job_role_id) REFERENCES job_roles(job_role_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_employees_education_fields
    FOREIGN KEY (education_field_id) REFERENCES education_fields(education_field_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_employees_business_travel
    FOREIGN KEY (business_travel_id) REFERENCES business_travel_types(business_travel_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_employees_marital_status
    FOREIGN KEY (marital_status_id) REFERENCES marital_statuses(marital_status_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_employees_genders
    FOREIGN KEY (gender_id) REFERENCES genders(gender_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

/* ------------------------------------------------------------
   4) ÍNDICES ÚTILES
   - No son obligatorios, pero ayudan a cargas/joins.
   - Como vais a mapear por FK, indexar FKs es buena práctica.
   ------------------------------------------------------------ */
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_job_role_id ON employees(job_role_id);
CREATE INDEX idx_employees_education_field_id ON employees(education_field_id);
CREATE INDEX idx_employees_business_travel_id ON employees(business_travel_id);
CREATE INDEX idx_employees_marital_status_id ON employees(marital_status_id);
CREATE INDEX idx_employees_gender_id ON employees(gender_id);
