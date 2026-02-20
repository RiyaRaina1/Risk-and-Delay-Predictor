# 🚀 Real-Time Project Risk & Delay Prediction System

## 📌 Overview

The Real-Time Project Risk & Delay Prediction System is a web-based analytical tool designed to proactively detect potential project delays using real-time performance metrics.

The system continuously evaluates key project KPIs and generates an explainable risk score (0–100) to help managers take preventive action before delays occur.

---

## 🎯 Problem Statement

Project delays are often identified only after major losses occur. Organizations lack a real-time monitoring system that evaluates project health dynamically.

This system solves that problem by providing:
Continuous KPI monitoring
Early risk detection
Explainable risk scoring
Historical trend analysis

---

## 🧠 Core Algorithm

The system uses a *Weighted Multi-Factor Risk Scoring Model* based on Multi-Criteria Decision Making (MCDM).

### Risk Formula:

Risk Score = Σ (Weight_i × Normalized KPI_i)

### KPIs Used:

Completion Rate
Blockers Count
Open Bugs
Scope Change (%)
Average Cycle Time
Velocity Trend (previous vs current progress)

Each KPI is normalized between 0 and 1 and assigned a domain-driven weight.

### Risk Classification:

0 – 39 → Low Risk
40 – 69 → Medium Risk
70 – 100 → High Risk

---

## 📊 Features

Real-Time KPI Dashboard
Automated Risk Score Calculation
Historical Trend Analysis
Explainable Risk Breakdown
CSV Report Export
SQLite Database Storage
Lightweight & Fast Execution

---

## 🏗 Tech Stack

### Backend:
Python
Flask
SQLite

### Frontend:
HTML
CSS
Chart.js

---

## 📂 Project Structure

risk-delay-predictor/
│
├── app.py
├── db.py
├── risk_engine.py
├── requirements.txt
│
└── templates/
    ├── base.html
    ├── index.html
    ├── project_new.html
    ├── project_view.html
    ├── metric_add.html
    └── report.html

---

## ⚙ Installation Guide

### 1️⃣ Clone Repository

git clone <repository-url>
cd risk-delay-predictor

### 2️⃣ Create Virtual Environment

python -m venv .venv

Activate it:

Windows:
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Run the Application

python app.py

Open in browser:
http://127.0.0.1:5000

---

## 📌 How to Use

Create a new project
Add periodic metric snapshots
System calculates real-time risk score
View dashboard and trend charts
Export historical report (CSV)

---

## 🔮 Future Improvements

Machine Learning Integration (Random Forest / Logistic Regression)
Time-Series Forecasting (LSTM)
Email Alert System
Cloud Deployment
Role-Based Authentication

---

## 🏆 Hackathon Value

Demonstrates applied analytics
Fully explainable risk model
Real-time monitoring system
End-to-end working web application

---

## 📜 License

This project is developed for educational and hackathon purposes.
