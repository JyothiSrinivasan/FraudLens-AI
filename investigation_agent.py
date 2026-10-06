
def generate_investigation_summary(transaction, aml_customer=None):
    """
    Generate an evidence-based investigation summary.
    Findings are preliminary and require human review.
    """

    transaction_id = transaction["transaction_id"]
    customer_id = transaction["customer_id"]
    amount = float(transaction["amount"])
    fraud_probability = float(transaction["fraud_probability"])
    risk_score = int(transaction["risk_score"])
    risk_level = transaction["risk_level"]
    ml_prediction = transaction["ml_prediction"]

    findings = []
    recommendations = []

    # 1. Machine-learning finding
    findings.append(
        f"ML prediction: {ml_prediction} "
        f"({fraud_probability:.1%} predicted fraud probability)."
    )

    # 2. Rule-based risk finding
    findings.append(
        f"Rule-based risk: {risk_level} "
        f"(score: {risk_score}/100)."
    )

    # 3. Risk indicators supplied by the dashboard
    indicators = transaction.get("risk_indicators", [])

    if isinstance(indicators, str):
        indicators = [indicators] if indicators else []

    if indicators:
        findings.append(
            "Risk indicators: " + "; ".join(indicators) + "."
        )
    else:
        findings.append(
            "No rule-based risk indicators were supplied "
            "to the investigation agent."
        )

    # 4. Customer-level AML screening context
    if aml_customer is not None:
        findings.append(
            f"AML screening alert for customer {customer_id}: "
            f"{int(aml_customer['transfer_count'])} bank transfers "
            f"totaling ₹{float(aml_customer['total_amount']):,.2f}. "
            f"Review priority: {aml_customer['aml_review_priority']}."
        )
        recommendations.append(
            "Review the customer's flagged bank-transfer activity."
        )
    else:
        findings.append(
            f"No matching AML alert was found for customer {customer_id} "
            "in the current screening results."
        )

    # 5. Human-review recommendations
    if risk_level == "High" or fraud_probability >= 0.70:
        recommendations.append(
            "Prioritize human review of the transaction and supporting evidence."
        )
    elif risk_level == "Medium" or fraud_probability >= 0.30:
        recommendations.append(
            "Review the transaction and verify the risk indicators."
        )
    else:
        recommendations.append(
            "Continue routine monitoring; this result does not guarantee safety."
        )

    summary = (
        f"Investigation for transaction {transaction_id} "
        f"(customer {customer_id}): amount ₹{amount:,.2f}. "
        + " ".join(findings)
        + " Recommended next actions: "
        + " ".join(recommendations)
        + " These findings are preliminary and require human review."
    )

    return {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "investigation_summary": summary,
        "findings": findings,
        "recommendations": recommendations,
        "review_status": "Requires Human Review",
    }
