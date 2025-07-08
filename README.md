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
- **Docker**: Easy environment setup and deployment.
- **PostgreSQL**: Backend for MLflow metadata.
- **MinIO**: S3-compatible storage for ML artifacts (models, environments, etc.).
- **Airflow** *(To-do)*: Automated model retraining pipeline.

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

### ✅ **First Experiment**:  
**Two separate WGAN-GP models** for normal and fraud data:

- Trained on:  
  1. All data  
  2. Only validation data  

- ❌ Issue: Classifier achieved **perfect metrics (100%)**, indicating:
  - Synthetic data is **too clean/separable**.
  - Models produce **non-overlapping distributions** for each class.

---

### ✅ **Second Experiment**:  
**Conditional WGAN-GP** for both classes:

- Trained only on **validation set**
- Observations:
  - SMOTE with large fraud ratio → **skewed distribution**
  - SMOTE with **10% fraud** seems more reasonable → **still under evaluation**

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

### Evaluation Strategy:

- **Round 1**: On original imbalanced data  
- **Round 2**: On SMOTE-upsampled data  
  - Result: Best F1 for fraud class ≈ **0.78 (XGBoost)**
- **Fine-tuning** led to slight improvements.

---

## 🔪 Experiments Summary

### 🔪 **First Attempt**:
- Train/test split on all data.
- Synthesizer trained on same data.
- ❌ Result: **Data leakage** → **perfect scores**

---

### 🔪 **Second Attempt**:
- Train/test split as before.
- Synthesizer trained **only on test set**.
- ❌ Still overfitting: synthetic data too recognizable → perfect classifier scores

---

### 🔪 **Third Attempt**:
- Proper `train/val/test` split.
- Synthesizer trained on `val`, classifiers trained on `train` and tested on `test`.
- ✅ Most reasonable setup.
- ❌ However:  
  - **Distribution mismatch** between synthetic and real test data  
  - Many **false positives**, classifiers perform poorly → **still under testing**

---

## 📊 Conclusion

- SMOTE helps but may cause classifier overfit in fraud detection.
- Conditional WGAN-GP has potential but needs careful tuning and **distribution matching**.
- Real-time fraud detection needs **realistic synthetic data** to generalize well.
- Next step: Integrate **Airflow** for retraining pipeline.

---