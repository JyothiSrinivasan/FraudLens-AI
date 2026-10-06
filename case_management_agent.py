
from datetime import datetime
from pathlib import Path
import pandas as pd


CASE_FILE = Path(__file__).parent / "data" / "investigation_cases.csv"

CASE_COLUMNS = [
    "case_id",
    "source_type",
    "source_id",
    "customer_id",
    "priority",
    "status",
    "case_summary",
    "analyst_notes",
    "created_at",
    "updated_at",
]


def load_cases():
    """Load saved investigation cases, creating the CSV if needed."""

    CASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CASE_FILE.exists():
        pd.DataFrame(columns=CASE_COLUMNS).to_csv(
            CASE_FILE, index=False
        )

    return pd.read_csv(CASE_FILE, dtype=str)



def find_case_by_source(source_type, source_id):
    """Find an existing case by its source type and source ID."""
    cases = load_cases()

    if cases.empty:
        return None

    matches = cases[
        (cases["source_type"] == str(source_type))
        & (cases["source_id"] == str(source_id))
    ]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()




def create_case(
    source_type,
    source_id,
    customer_id,
    priority,
    case_summary,
):
    """Create and save a new investigation case."""

    cases = load_cases()

    if not cases.empty and (
        (cases["source_type"] == source_type)
        & (cases["source_id"] == source_id)
    ).any():
        raise ValueError(
            "A case already exists for this source and source ID."
        )

    now = datetime.now().isoformat(timespec="seconds")

    case_number = len(cases) + 1
    case_id = f"CASE-{datetime.now():%Y%m%d}-{case_number:04d}"

    new_case = {
        "case_id": case_id,
        "source_type": source_type,
        "source_id": source_id,
        "customer_id": customer_id,
        "priority": priority,
        "status": "Open",
        "case_summary": case_summary,
        "analyst_notes": "",
        "created_at": now,
        "updated_at": now,
    }

    updated_cases = pd.concat(
        [cases, pd.DataFrame([new_case])],
        ignore_index=True,
    )

    updated_cases.to_csv(CASE_FILE, index=False)

    return new_case


def update_case(case_id, status, priority, analyst_notes):
    """Update the status, priority, and notes of an existing case."""

    cases = load_cases()
    matches = cases.index[cases["case_id"] == case_id].tolist()

    if not matches:
        raise ValueError(f"Case {case_id} was not found.")

    if status not in ["Open", "Under Review", "Closed"]:
        raise ValueError("Invalid case status.")

    if priority not in ["Low", "Medium", "High"]:
        raise ValueError("Invalid case priority.")

    index = matches[0]

    cases.loc[index, "status"] = status
    cases.loc[index, "priority"] = priority
    cases.loc[index, "analyst_notes"] = analyst_notes
    cases.loc[index, "updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    cases.to_csv(CASE_FILE, index=False)

    return cases.loc[index].to_dict()


def prepare_transaction_case(transaction):
    """
    Prepare a case from an analyzed transaction.
    The analyst can review it before saving.
    """

    transaction_id = str(transaction["transaction_id"])
    customer_id = str(transaction.get("customer_id", "Unknown"))

    risk_level = str(transaction.get("risk_level", "Medium"))
    fraud_probability = float(
        transaction.get("fraud_probability", 0)
    )
    risk_score = transaction.get("risk_score", "N/A")
    ml_prediction = str(
        transaction.get("ml_prediction", "Not available")
    )

    if risk_level not in ["High", "Medium", "Low"]:
        risk_level = "Medium"

    case_summary = (
        f"Transaction {transaction_id} requires review. "
        f"Customer: {customer_id}. "
        f"Rule-based risk: {risk_level}. "
        f"Risk score: {risk_score}/100. "
        f"ML prediction: {ml_prediction}. "
        f"Predicted fraud probability: {fraud_probability:.1%}. "
        "Review the underlying evidence before making a decision."
    )

    return {
        "source_type": "Transaction",
        "source_id": transaction_id,
        "customer_id": customer_id,
        "priority": risk_level,
        "case_summary": case_summary,
    }
