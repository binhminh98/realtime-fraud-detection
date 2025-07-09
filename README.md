# 🕵️ Realtime Fraud Detection Pipeline

## 🚀 Project Overview

This project implements a **real-time fraud detection pipeline** using a Kafka-based streaming setup, GAN-based synthetic data generation, and ML model training and deployment, all containerized with Docker.

---

## 🛠️ Tech Stack

- **Kafka**: Real-time transaction data simulation via producer/consumer pattern.
- **Python**:
  - Synthetic data generation using `Conditional WGAN-GP`
  - FastAPI for serving models via REST API
  - Plotly Dash for UI and model monitoring
  - ML classifiers: baseline `DecisionTree` ➔ `Bagging (RandomForest)` ➔ `Boosting (XGBoost, CatBoost, LightGBM)`
- **MLFlow**: Model logging and performance monitoring.
- **MinIO**: S3-compatible storage for MLFlow artifacts (models, environments, etc.).
- **PostgreSQL**: Backend for MLflow metadata.
- **Docker**: Easy environment setup and deployment.
- **Airflow** *(To-do)*: Automated model retraining pipeline.

![System Design](images/realtime_fraud_detection.png "System design")

---

## 🧪 Dataset Setup

- The dataset is split into: `train`, `validation`, `test`.
- **Classifier**: Trained on `train` set, evaluated on `test` set.
- **Synthesizer**: Trained only on the `validation` set (to avoid data leakage).

---

## 🧬 Synthetic Data Generation Insights

### ❗ Issues with SMOTE:

- SMOTE preserves the feature space structure, aiding classifiers on imbalanced datasets.
- However, it introduces **overfitting**—especially in small datasets with minority fraud samples.

### ❗ Issues with WGAN-GP:

- WGAN-GP struggles on **small datasets** (overfits easily).
- Even with SMOTE-upsampled data, it generates synthetic samples that are **too easy to separate**, leading to unreliable classifiers.
- **Needs scaled input** → `MinMaxScaler` is used for better performance.
- Recommended: **SMOTE with 10% more fraud data** (vs. full oversampling) to reduce overfit.

---

## 🔬 Experiments with Synthesizer

### **First Experiment**:  
**Two separate WGAN-GP models** for normal and fraud data:

- Trained on:  
  1. All data  
  2. Only validation data  

- ❌ Issue: Classifier achieved **perfect metrics (100%)**, indicating:
  - Synthetic data is **too clean/separable**.
  - Models produce **non-overlapping distributions** for each class.

### **Second Experiment**:  
**Conditional WGAN-GP** for both classes:

- Trained only on **validation set**
- Observations:
  - SMOTE with large fraud ratio → **skewed distribution**
  - SMOTE with **10% fraud** seems more reasonable → but **distribution drift**

### **Third/Last Experiment**:  
**WGAN-GP** for only fraud transactions:

- Trained only on **validation set**
- Observations:
  - SMOTE with **10% fraud** seems more reasonable -> data looks reasonable on TSNE plot.

![Fraud vs real transactions](images/synthetic_vs_real_fraud.png "Fraud vs real transactions")

---

## 🧠 Classifier Development

- Tree-based classifiers were chosen due to:
  - Interpretability
  - Handling of mixed feature types
  - Good performance on tabular data with class imbalance

### Models Used:

| Model               | Notes |
|--------------------|-------|
| `DecisionTree`     | Baseline – underperformed |
| `RandomForest`     | Bagging approach – slower training, decent performance |
| `XGBoost` / `CatBoost` / `LightGBM` | Boosting models – fast, regularized, auto feature selection |