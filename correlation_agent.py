
def correlate_risk_signals(transaction, security_event):
    """
    Correlate transaction risk and cybersecurity signals.

    This prototype compares two supplied records.
    It does not establish that they belong to the same person.
    """

    transaction_id = str(
        transaction.get("transaction_id", "UNKNOWN")
    )
    customer_id = str(
        transaction.get("customer_id", "Unknown")
    )

    risk_level = str(
        transaction.get("risk_level", "Low")
    )
    fraud_probability = float(
        transaction.get("fraud_probability", 0.0)
    )

    event_id = str(
        security_event.get("event_id", "UNKNOWN")
    )
    failed_attempts = int(
        security_event.get("failed_attempts", 0)
    )
    event_hour = int(
        security_event.get("hour", 12)
    )
    is_foreign = int(
        security_event.get("is_foreign", 0)
    )

    findings = []

    # Transaction risk signals
    if risk_level == "High" or fraud_probability >= 0.70:
        findings.append(
            f"Transaction {transaction_id} has elevated fraud risk."
        )
    elif risk_level == "Medium" or fraud_probability >= 0.30:
        findings.append(
            f"Transaction {transaction_id} has moderate fraud risk."
        )

    # Cybersecurity signals
    if failed_attempts >= 5:
        findings.append(
            f"Security event {event_id} has "
            f"{failed_attempts} failed login attempts."
        )

    if 0 <= event_hour <= 4:
        findings.append(
            f"Security event {event_id} occurred during "
            f"an unusual hour ({event_hour}:00)."
        )

    if is_foreign == 1:
        findings.append(
            f"Security event {event_id} has a "
            f"foreign-source activity indicator."
        )

    # Combined assessment
    transaction_elevated = (
        risk_level == "High" or fraud_probability >= 0.70
    )
    security_elevated = (
        failed_attempts >= 5
        and (is_foreign == 1 or 0 <= event_hour <= 4)
    )

    if transaction_elevated and security_elevated:
        combined_risk = "High"
        recommendation = (
            "Prioritize analyst review of both records and verify "
            "whether reliable evidence links them."
        )
    elif transaction_elevated or security_elevated:
        combined_risk = "Medium"
        recommendation = (
            "Review the elevated-risk record and validate its "
            "supporting evidence."
        )
    else:
        combined_risk = "Low"
        recommendation = (
            "Continue routine monitoring; this assessment "
            "does not guarantee that either record is safe."
        )

    if not findings:
        findings.append(
            "No configured elevated-risk signals were detected."
        )

    return {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "security_event_id": event_id,
        "combined_risk": combined_risk,
        "findings": findings,
        "recommendation": recommendation,
        "correlation_status": (
            "Unverified association: shared identity or causal link "
            "has not been established."
        ),
    }
