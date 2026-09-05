# 🩺 Payment State Doctor

> Intelligent payment inconsistency detection, diagnosis & recovery

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://payment-state-doctor-jgudfxvt3k9erdyiva8h9y.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/Akshaya29299/payment-state-doctor)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

## 🚀 Live Demo

### [🩺 Open Payment State Doctor](https://payment-state-doctor-jgudfxvt3k9erdyiva8h9y.streamlit.app/)

---

## 📌 Overview

**Payment State Doctor** is a fintech-focused application designed to detect, analyze, and diagnose inconsistencies in payment transaction states.

In real-world payment systems, the same transaction can pass through multiple systems and states. Temporary failures, delayed updates, inconsistent responses, and reconciliation issues can result in situations where different systems disagree about the actual state of a payment.

Payment State Doctor analyzes transaction information and converts these inconsistencies into actionable diagnostic categories.

The application provides a dashboard that helps identify:

- Healthy transactions
- Payment state mismatches
- Anomalous transactions
- Potentially recoverable transactions
- Uncertain cases
- Revenue at risk

---

## 🎯 Problem Statement

Payment systems can encounter inconsistent transaction states due to failures, delays, retries, or communication issues between different components.

For example:

```text
Payment Gateway → SUCCESS
        ↓
Payment Database → FAILED
        ↓
Merchant System → UNKNOWN
```

A simple `SUCCESS` / `FAILED` status is not always enough to understand what actually happened.

These inconsistencies can result in:

- Failed or delayed payments
- Incorrect transaction records
- Reconciliation problems
- Customer support issues
- Financial losses
- Manual investigation
- Revenue being placed at risk

Payment State Doctor aims to make these inconsistencies easier to detect and understand.

---

## 💡 Solution

The application analyzes payment transaction states and classifies them based on their consistency and available information.

The workflow is:

```text
Transaction Data
       ↓
State Analysis
       ↓
Consistency Checks
       ↓
Issue Detection
       ↓
Issue Classification
       ↓
Diagnosis
       ↓
Recovery Assessment
       ↓
Revenue-at-Risk Calculation
       ↓
Dashboard
```

---

## 📊 Dashboard

The dashboard provides a high-level operational view of the analyzed transactions.

It displays:

### Transactions Analyzed

Total number of payment transactions processed by the system.

### Issues Detected

Number of transactions that require attention.

### Revenue at Risk

The estimated transaction value associated with problematic or uncertain payment states.

### Issue Overview

Transactions are categorized into:

| Category | Description |
|---|---|
| 🟢 **Healthy** | Payment state is consistent and does not require attention |
| 🔴 **Mismatch** | Conflicting payment states are detected |
| 🚨 **Anomaly** | Transaction state or behavior appears unusual |
| 🟠 **Recoverable** | Transaction has a potential recovery path |
| 🟡 **Uncertain** | Available information is insufficient for a confident diagnosis |

---

## 🧠 Key Features

### 🔍 Payment State Detection

Analyzes transaction states and identifies inconsistencies between available payment information.

### 🩺 Transaction Diagnosis

Provides a structured diagnosis for problematic transactions instead of only displaying a failed/successful status.

### 🚨 Issue Classification

Automatically categorizes detected issues into meaningful operational categories.

### 🔄 Recovery Identification

Highlights transactions that may have a possible recovery path.

### 💰 Revenue-at-Risk Analysis

Calculates the monetary value associated with transactions requiring attention.

### 📊 Interactive Dashboard

Presents the analysis in a clean dashboard designed for quick operational understanding.

### 🧪 Scenario-Based Testing

Includes predefined transaction scenarios for testing different payment-state conditions.

---

## 🏗️ Project Structure

```text
payment-state-doctor/
│
├── app.py
├── engine.py
├── database.py
├── scenarios.py
├── ai_explainer.py
├── llm.py
├── test_engine.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    └── ...
```

### File Responsibilities

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application and dashboard |
| `engine.py` | Core payment-state analysis and issue detection logic |
| `database.py` | Database-related operations |
| `scenarios.py` | Payment transaction scenarios used by the application |
| `ai_explainer.py` | Explanation/diagnostic support module |
| `llm.py` | Supporting module included in the project |
| `test_engine.py` | Tests for the analysis engine |
| `requirements.txt` | Python dependencies |
| `data/` | Project data and sample transaction information |
| `.gitignore` | Files excluded from version control |

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **SQLite / Database Layer**
- **Rule-based transaction analysis**
- **Git**
- **GitHub**
- **Streamlit Community Cloud**

---

## 🔬 How the Detection Works

Payment State Doctor evaluates transaction information and looks for inconsistencies in payment states.

A simplified example:

```text
Transaction A

Gateway Status:     SUCCESS
Database Status:    SUCCESS
Merchant Status:    SUCCESS

                ↓

             HEALTHY
```

Another example:

```text
Transaction B

Gateway Status:     SUCCESS
Database Status:    FAILED
Merchant Status:    FAILED

                ↓

             MISMATCH
```

The detected condition is then classified and surfaced through the dashboard.

---

## 📈 Example Dashboard Output

The application can summarize a transaction dataset using metrics such as:

```text
Transactions Analyzed     7

Issues Detected           6

Revenue at Risk           ₹40,094
```

Example issue distribution:

```text
🟢 Healthy       1
🔴 Mismatch      2
🚨 Anomaly       2
🟠 Recoverable   1
🟡 Uncertain     1
```

These values depend on the transaction dataset being analyzed.

---

## 💻 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Akshaya29299/payment-state-doctor.git
```

### 2. Navigate into the project

```bash
cd payment-state-doctor
```

### 3. Create a virtual environment

#### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will then be available locally through the Streamlit development server.

---

## 🧪 Running Tests

The project includes tests for the core analysis engine.

Run:

```bash
pytest test_engine.py
```

Alternatively:

```bash
python -m pytest test_engine.py
```

---

## 🔐 Security

Do not commit sensitive information such as:

- API keys
- Passwords
- Database credentials
- Authentication tokens
- `.env` files
- Production secrets

The project includes a `.gitignore` to prevent common local and sensitive files from being committed.

---

## 🌱 Future Enhancements

Potential improvements for future versions include:

- Real-time payment event processing
- Payment gateway integrations
- Automated reconciliation
- Historical transaction analytics
- Advanced anomaly detection
- Automated recovery workflows
- Transaction-level audit trails
- High-risk transaction alerts
- Exportable diagnostic reports
- Recovery success tracking
- Larger and more realistic transaction datasets
- Role-based dashboards for payment operations teams

---

## 🎓 What This Project Demonstrates

This project demonstrates practical application of:

- Python application development
- Data processing
- Payment-state analysis
- Backend/database integration
- Rule-based decision systems
- Exception and inconsistency detection
- Automated classification
- Financial risk analysis
- Dashboard development
- Software testing
- Git/GitHub workflow
- Cloud deployment

---

## 🧩 Project Architecture

```text
                    ┌─────────────────────┐
                    │   Transaction Data  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Database Layer    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Analysis Engine   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             State Detection       Issue Classification
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Diagnosis & Recovery│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘
```

---

## 🌐 Deployment

The application is deployed using **Streamlit Community Cloud**.

### Live Application

**https://payment-state-doctor-jgudfxvt3k9erdyiva8h9y.streamlit.app/**

The deployed application allows users to interact with the dashboard directly without setting up the project locally.

---

## 📂 Repository

GitHub repository:

**https://github.com/Akshaya29299/payment-state-doctor**

---

## 👩‍💻 Author

### Akshaya Reddy

Computer Science Engineering Student

GitHub: **[@Akshaya29299](https://github.com/Akshaya29299)**

---

## ⭐ Support

If you find the project interesting, consider giving the repository a ⭐ on GitHub.

---

<p align="center">
  Built with Python & Streamlit 🩺💳
</p>