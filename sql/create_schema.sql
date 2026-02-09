/* ============================================================
   PROYECTO HR — CREACIÓN DE BASE DE DATOS (MySQL)
   Esquema 3FN: employees + tablas dimensión
   Carga: SQLAlchemy desde Python
   ============================================================ */

DROP DATABASE IF EXISTS nextlevel_people;
CREATE DATABASE nextlevel_people
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE nextlevel_people;

/* ---------------------------
   TABLAS DIMENSIÓN
--------------------------- */

DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
  department_id INT AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(50) NOT NULL,
  CONSTRAINT uq_departments_name UNIQUE (department_name)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS job_roles;
CREATE TABLE job_roles (
  job_role_id INT AUTO_INCREMENT PRIMARY KEY,
  job_role_name VARCHAR(80) NOT NULL,
  CONSTRAINT uq_job_roles_name UNIQUE (job_role_name)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS education_fields;
CREATE TABLE education_fields (
  education_field_id INT AUTO_INCREMENT PRIMARY KEY,
  education_field_name VARCHAR(80) NOT NULL,
  CONSTRAINT uq_education_fields_name UNIQUE (education_field_name)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS business_travel_types;
CREATE TABLE business_travel_types (
  business_travel_id INT AUTO_INCREMENT PRIMARY KEY,
  business_travel_name VARCHAR(30) NOT NULL,
  CONSTRAINT uq_business_travel_name UNIQUE (business_travel_name)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS marital_statuses;
CREATE TABLE marital_statuses (
  marital_status_id INT AUTO_INCREMENT PRIMARY KEY,
  marital_status_name VARCHAR(30) NOT NULL,
  CONSTRAINT uq_marital_status_name UNIQUE (marital_status_name)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS genders;
CREATE TABLE genders (
  gender_id INT AUTO_INCREMENT PRIMARY KEY,
  gender_name VARCHAR(20) NOT NULL,
  CONSTRAINT uq_genders_name UNIQUE (gender_name)
) ENGINE=InnoDB;

/* ---------------------------
   TABLA PRINCIPAL: employees
--------------------------- */

DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
  /* PK interno */
  employee_id INT AUTO_INCREMENT PRIMARY KEY,

  /* ID original del CSV para trazabilidad */
  source_employee_id INT NOT NULL,
  CONSTRAINT uq_employees_source UNIQUE (source_employee_id),

  /* FKs a dimensiones */
  department_id INT NOT NULL,
  job_role_id INT NOT NULL,
  education_field_id INT NOT NULL,
  business_travel_id INT NOT NULL,
  marital_status_id INT NOT NULL,
  gender_id INT NOT NULL,

  /* Datos numéricos */
  age SMALLINT NOT NULL,
  education_level SMALLINT NOT NULL,          /* 1..5 */
  environment_satisfaction SMALLINT NOT NULL, /* 1..4 */
  job_involvement SMALLINT NOT NULL,          /* 1..4 */
  job_level SMALLINT NOT NULL,                /* 1..5 */
  job_satisfaction SMALLINT NOT NULL,         /* 1..4 */
  performance_rating SMALLINT NOT NULL,       /* 1..4 */
  relationship_satisfaction SMALLINT NOT NULL,/* 1..4 */
  work_life_balance SMALLINT NOT NULL,        /* 1..4 */

  num_companies_worked SMALLINT NOT NULL,
  total_years_worked SMALLINT NOT NULL,
  training_last_year SMALLINT NOT NULL,
  distance_from_home SMALLINT NOT NULL,

  monthly_income INT NOT NULL,
  daily_rate INT NOT NULL,
  hourly_rate INT NOT NULL,
  salary_hike_pct SMALLINT NOT NULL,          /* 0..100 */
  stock_option_level SMALLINT NOT NULL,       /* 0..3 */

  years_at_company SMALLINT NOT NULL,
  years_in_current_role SMALLINT NOT NULL,
  years_since_last_promotion SMALLINT NOT NULL,
  years_with_current_manager SMALLINT NOT NULL,

  over_time BOOLEAN NOT NULL,                 /* 0/1 */
  attrition BOOLEAN NOT NULL,                 /* 0/1 */

  /* CHECKS */
  CONSTRAINT chk_age_positive CHECK (age > 0),

  CONSTRAINT chk_education_level CHECK (education_level BETWEEN 1 AND 5),
  CONSTRAINT chk_job_level CHECK (job_level BETWEEN 1 AND 5),

  CONSTRAINT chk_env_sat CHECK (environment_satisfaction BETWEEN 1 AND 4),
  CONSTRAINT chk_job_involvement CHECK (job_involvement BETWEEN 1 AND 4),
  CONSTRAINT chk_job_sat CHECK (job_satisfaction BETWEEN 1 AND 4),
  CONSTRAINT chk_perf_rating CHECK (performance_rating BETWEEN 1 AND 4),
  CONSTRAINT chk_rel_sat CHECK (relationship_satisfaction BETWEEN 1 AND 4),
  CONSTRAINT chk_wlb CHECK (work_life_balance BETWEEN 1 AND 4),

  CONSTRAINT chk_nonneg_num_companies CHECK (num_companies_worked >= 0),
  CONSTRAINT chk_nonneg_total_years CHECK (total_years_worked >= 0),
  CONSTRAINT chk_nonneg_training CHECK (training_last_year >= 0),
  CONSTRAINT chk_nonneg_distance CHECK (distance_from_home >= 0),

  CONSTRAINT chk_nonneg_monthly_income CHECK (monthly_income >= 0),
  CONSTRAINT chk_nonneg_daily_rate CHECK (daily_rate >= 0),
  CONSTRAINT chk_nonneg_hourly_rate CHECK (hourly_rate >= 0),
  CONSTRAINT chk_salary_hike_pct CHECK (salary_hike_pct BETWEEN 0 AND 100),
  CONSTRAINT chk_stock_option CHECK (stock_option_level BETWEEN 0 AND 3),

  CONSTRAINT chk_nonneg_years_company CHECK (years_at_company >= 0),
  CONSTRAINT chk_nonneg_years_role CHECK (years_in_current_role >= 0),
  CONSTRAINT chk_nonneg_years_promo CHECK (years_since_last_promotion >= 0),
  CONSTRAINT chk_nonneg_years_manager CHECK (years_with_current_manager >= 0),

  /* FOREIGN KEYS */
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

/* Índices en FKs */
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_job_role_id ON employees(job_role_id);
CREATE INDEX idx_employees_education_field_id ON employees(education_field_id);
CREATE INDEX idx_employees_business_travel_id ON employees(business_travel_id);
CREATE INDEX idx_employees_marital_status_id ON employees(marital_status_id);
CREATE INDEX idx_employees_gender_id ON employees(gender_id);

