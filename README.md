# Machine Learning for Quantum Machine Calibration Forecasting

> Master's Research Project — M1 Data Science  
> University of Lille / Centrale Lille / IMT Nord Europe  
> Supervisor: Dr. Zakaria Abdelmoiz DAHI (INRIA Bonus)

---

## Overview

Quantum computers in their current **NISQ (Noisy Intermediate-Scale Quantum)** era are highly sensitive to environmental noise, causing frequent calibration drift and elevated error rates. This project builds an end-to-end pipeline to **forecast the temporal evolution of IBM quantum machine calibration metrics**, with the goal of predicting optimal computation windows and reducing wasted time and money on cloud-based quantum platforms.

The pipeline covers automated data extraction, storage, exploratory analysis, and time-series forecasting using multiple model families (LSTM, GRU, SARIMAX, NeuralProphet).

---

## Repository Structure

```

|-- dataset/
|   |- complete_data.jsonl          # Complete (Gates + Qubits) dataset
│   |- gates_data.jsonl          # Gate-level calibration metrics
│   |- qubits_data.jsonl        # Qubit-level calibration metrics
|-- etl/
│   ├── collecte_extract_jsonl.py   # IBM calibration metrics scraper
|-- eda/
│   |- analysis.ipynb   # Exploratory Data Analysis notebook
|-- modeling/
│   |-- model.
│   |-- neuralprophet.py # NeuralProphet model
└── README.md
```

---

## Data

### Sources

Calibration data is scraped from **3 real IBM superconducting quantum backends** via the Qiskit SDK:

| Backend | Qubits | Provider |
|---|---|---|
| ibm_fez | 156 | IBM Quantum |
| ibm_torino | 133 | IBM Quantum |
| ibm_marrakesh | 156 | IBM Quantum |

Data is collected **hourly** (validated by calibration stability analysis) from October 29, 2025 to March 03, 2026 — **126 days / 3,025 hours** of data per backend.

### Features

After EDA-driven feature selection, 9 features are retained for modeling:

| Feature | Level | Description |
|---|---|---|
| `t1` | Qubit | Relaxation time |
| `t2` | Qubit | Dephasing time |
| `readout_error` | Qubit | Mean readout assignment error |
| `prob_meas0_prep1` | Qubit | P(measure 0 \| prepared 1) |
| `prob_meas1_prep0` | Qubit | P(measure 1 \| prepared 0) |
| `single_gate_error` | Gate | Single-qubit gate error rate |
| `cz_error` | Gate | CZ two-qubit gate error |
| `rzz_error` | Gate | RZZ two-qubit gate error |

Features excluded: constant durations, `rz_error` (always 0), `frequency`/`anharmonicity` (always NaN), `reset_error` (always 0).

### Storage

Raw data is stored in **JSONL** format for incremental appending without full file reloads, versioned via **GitHub Actions + Git LFS**.

---

Unique record identifier format: `{backend_name}_{scraping_timestamp}`

---

## Models

| Model | Type | Notes |
|---|---|---|
| Linear Regression | Baseline | Strong naive baseline | t̂ = t-1 pattern |
| GRU | Recurrent Neural Network | Fewer params than LSTM, slightly better on daily data |
| LSTM | Recurrent Neural Network | Best on hourly data for stable features |
| SARIMAX | Statistical | Best with exogenous variables; poor standalone |
| NeuralProphet | Hybrid | Most promising overall; better pattern extraction |

All RNN models trained with PyTorch, 80/20 train/test split, standardized features, Adam optimizer, MSE loss.

---

## Results Summary

### Hourly data (median per feature)

Most models achieve **R² > 0.9** on stable features (T1, T2, gate errors), but converge to a **naive approach** (ŷ_t = y_{t-1}). Readout-related features are significantly harder to predict (R² < 0).

| Model | T1 MAE | T1 R² |
|---|---|---|
| LSTM | 0.051 | 0.933 |
| GRU | 0.061 | 0.933 |
| Linear | 0.054 | 0.929 |

### Daily data (median per day)

All models struggle — R² is often negative, close to or worse than predicting the mean. Likely caused by insufficient data volume and over-smoothing via repeated medians.

### Key findings

- Calibration metrics update on average every **2–3.5 hours** depending on the backend
- Most of the feature express a correlation between each others
- Most series are **stationary** (ADF test, p < 0.05) with **no significant seasonality**
- Time series behave close to **white noise / random walk**, making prediction inherently difficult
- NeuralProphet outperforms RNNs and SARIMAX but still does not beat the naive baseline

---

## Installation

```bash
git clone https://github.com/GwennGrs/Projet_M1_Garrigues-Journaud_ULIlle_2025-2026
cd Projet_M1_Garrigues-Journaud_ULIlle_2025-2026
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- `qiskit`, `qiskit-ibm-runtime`
- `torch`, `neuralprophet`, `statsmodels`
- `pandas`, `numpy`, `scikit-learn`, `matplotlib`

### IBM API Key

To run the scraper, set your IBM Quantum API key:

```bash
export IBM_QUANTUM_API_KEY="your_key_here"
```

---

## Future Work

- **Qubit-wise modeling** — study individual qubit behavior instead of backend-level medians
- **Longer collection period** — more data to improve daily forecasting
- **Multi-provider extension** — generalize to IQM and Quantum Inspire once metric standardization is resolved
- 
---

## References

- Dahi et al., *Optimising Quantum Calculations Reliability via Machine Learning: The IBM Case Study*, IEEE QAI 2025
- Saghafi & Mili, *Predictive Time-Series Analysis of Single-Qubit Quantum Circuit Outcomes*, IEEE Access 2025
- Triebe et al., *NeuralProphet: Explainable Forecasting at Scale*, arXiv 2021
- Krantz et al., *A Quantum Engineer's Guide to Superconducting Qubits*, Applied Physics Reviews 2019

---

## Acknowledgments

Special thanks to **Dr. Zakaria Abdelmoiz DAHI** (INRIA Bonus) for his guidance and support throughout this project.Master's research project in Data Science
