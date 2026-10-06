
import pandas as pd


def detect_aml_patterns(df):
    """
    Flag customers with repeated bank transfers
    totaling at least ₹50,000.

    Alerts are preliminary screening results,
    not proof of money laundering.
    """

    transfers = df[
        df["transaction_type"] == "bank_transfer"
    ].copy()

    summary = (
        transfers.groupby("customer_id")
        .agg(
            transfer_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            transaction_ids=(
                "transaction_id",
                lambda ids: ", ".join(ids)
            ),
        )
        .reset_index()
    )

    flagged = summary[
        (summary["transfer_count"] > 1)
        & (summary["total_amount"] >= 50000)
    ].copy()

    flagged["aml_reason"] = (
        "Repeated bank transfers with combined "
        "amount of ₹50,000 or more"
    )

    flagged["aml_review_status"] = "Requires Review"
    flagged["aml_review_priority"] = flagged["total_amount"].apply(
    lambda amount: "High" if amount >= 100000 else "Medium"
)

    return flagged
