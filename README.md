# FraudLens AI
### AI-Assisted Financial Fraud Detection, AML Screening & Cybersecurity Investigation

FraudLens AI is a portfolio project that combines machine-learning-based transaction risk scoring, rule-based Anti-Money Laundering (AML) screening, cybersecurity event analysis, investigation case management, and cross-domain risk correlation in a Streamlit dashboard.

The project demonstrates how financial transaction indicators and cybersecurity signals can be organized into a unified workflow to support analyst review.

> **Disclaimer:** This project uses synthetic demonstration data and configured detection rules. Its alerts and predictions are for educational purposes and do not establish fraud, money laundering, or a confirmed cyberattack.

## Key Features

- **Machine Learning Fraud Detection:** Uses a Random Forest classifier to estimate transaction fraud probability.
- **Rule-Based Risk Scoring:** Assigns risk levels using configured transaction indicators.
- **AML Screening Agent:** Flags selected patterns of repeated bank transfers for further review.
- **Cybersecurity Analysis Agent:** Evaluates simulated security events for repeated failed logins, unusual hours, and foreign-source indicators.
- **Investigation Summary Agent:** Produces findings and recommendations to assist human investigation.
- **Case Management Agent:** Supports investigation case tracking, status updates, priorities, and analyst notes.
- **Risk Correlation Agent:** Combines transaction and cybersecurity risk signals while preserving uncertainty about any relationship between events.
- **Executive Risk Dashboard:** Summarizes transaction risk and investigation case progress.
- **CSV Reporting:** Exports investigation case information for further analysis.

## Technology Stack

- Python
- Streamlit
- Pandas
- Scikit-learn
- Random Forest classification
- CSV-based data storage
- Git and GitHub

## Project Structure

```text
FraudLens-AI/
├── app.py
├── train_model.py
├── fraud_model.pkl
├── aml_agent.py
├── investigation_agent.py
├── cybersecurity_agent.py
├── case_management_agent.py
├── correlation_agent.py
├── requirements.txt
├── .gitignore
└── data/
    ├── transactions.csv
    └── investigation_cases.csv
```

*The data folder contains local demonstration data. Confirm which CSV files you intend to publish before committing them.*

## Getting Started

### Prerequisites

- Python installed on your system
- Git (optional, for version control)
- A terminal such as PowerShell or the VS Code integrated terminal

### 1. Clone the repository

After publishing this project to GitHub, replace the placeholder URL with your repository URL.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FraudLens-AI
```

Alternatively, open your existing local project folder in VS Code.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell, activate it with:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python executable directly.

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Start the dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Machine Learning Workflow

1. Load the transaction dataset.
2. Prepare the configured model features.
3. Train a Random Forest classifier using the training script.
4. Save the trained model for the dashboard.
5. Estimate fraud probability for transactions.
6. Combine model predictions with rule-based indicators to support risk review.

The model's predictions depend on the training data and features. They should not be interpreted as proof of wrongdoing.

## Agent Overview

| Agent | Purpose |
|---|---|
| AML Monitoring | Screens for configured repeated-transfer patterns |
| Investigation Summary | Generates findings and recommendations |
| Cybersecurity Analysis | Evaluates configured security-event indicators |
| Case Management | Tracks investigation cases and analyst updates |
| Risk Correlation | Combines risk signals without assuming a causal relationship |

## Validation

The prototype has been manually exercised using its synthetic demonstration dataset. Checks performed include:

- Dashboard startup and transaction display
- Investigation summary generation
- AML pattern screening
- Cybersecurity rule evaluation
- Combined transaction and security risk analysis
- Case status and analyst-note updates
- Executive dashboard metrics
- CSV report download

These checks demonstrate basic functional behavior, not production-grade detection performance. The model has been evaluated on a very small sample, so its observed test performance is not evidence of real-world accuracy.

## Limitations and Responsible Use

- Uses synthetic demonstration transactions and simulated security events.
- AML and cybersecurity alerts are rule-based screening results.
- Correlated indicators do not establish a shared identity or causal link.
- The prototype is not a production financial-crime monitoring system.
- It has not been established as compliant with regulatory requirements.
- Real-world deployment would require representative datasets, rigorous validation, security controls, access management, auditability, and human oversight.

## Future Improvements

- Add validated, representative datasets and robust model evaluation.
- Add explainability for model predictions.
- Integrate authorized threat-intelligence feeds.
- Add stronger case persistence and audit logging.
- Implement role-based access control.
- Add automated testing and continuous integration.
- Evaluate secure integrations with SIEM and SOAR platforms.

## Author

**Jyothi Srinivasan**

Portfolio project focused on AI, financial fraud analytics, AML screening, and cybersecurity investigation.

---

*Built for educational and portfolio demonstration purposes.*