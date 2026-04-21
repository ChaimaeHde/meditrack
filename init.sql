CREATE DATABASE IF NOT EXISTS meditrack;
USE meditrack;

CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE,
    pathologies VARCHAR(255),
    medecin_id INT,
    telephone VARCHAR(20),
    email VARCHAR(100),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    type_mesure VARCHAR(50) NOT NULL,
    valeur FLOAT NOT NULL,
    unite VARCHAR(20),
    contexte VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient (patient_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    rule_id VARCHAR(100),
    severite VARCHAR(20),
    message TEXT,
    statut VARCHAR(20) DEFAULT 'nouvelle',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acquittee_par VARCHAR(100),
    INDEX idx_patient_alert (patient_id)
);

INSERT INTO patients (nom, prenom, date_naissance, pathologies, telephone, email) VALUES
('Benali', 'Ahmed', '1955-03-15', 'diabete,hypertension', '0612345678', 'ahmed.benali@example.com'),
('Alaoui', 'Fatima', '1962-07-22', 'hypertension', '0687654321', 'fatima.alaoui@example.com'),
('Tazi', 'Mohamed', '1948-11-08', 'insuffisance_cardiaque', '0698765432', 'mohamed.tazi@example.com');