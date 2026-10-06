
def analyze_security_event(event):
    """
    Analyze a simulated cybersecurity event using
    transparent, rule-based detection.

    Alerts indicate activity for review, not confirmed attacks.
    """

    event_id = event.get("event_id", "UNKNOWN")
    source_ip = event.get("source_ip", "Unknown")
    failed_attempts = int(event.get("failed_attempts", 0))
    hour = int(event.get("hour", 12))
    is_foreign = int(event.get("is_foreign", 0))

    findings = []
    recommendations = []

    # Rule 1: Potential brute-force activity
    if failed_attempts >= 5:
        findings.append(
            f"Multiple failed login attempts detected: "
            f"{failed_attempts} attempts."
        )
        recommendations.append(
            "Review authentication logs for possible brute-force activity."
        )

    # Rule 2: Login during unusual hours
    if 0 <= hour <= 4:
        findings.append(
            f"Login activity occurred during an unusual hour: {hour}:00."
        )
        recommendations.append(
            "Verify whether the login time matches expected user activity."
        )

    # Rule 3: Foreign-source indicator
    if is_foreign == 1:
        findings.append(
            "The event has a foreign-source activity indicator."
        )
        recommendations.append(
            "Verify the source location and whether the access was expected."
        )

    if findings:
        status = "Requires Review"
        risk_level = (
            "High" if failed_attempts >= 5 and
            (is_foreign == 1 or 0 <= hour <= 4)
            else "Medium"
        )
    else:
        status = "No Rule Triggered"
        risk_level = "Low"
        findings.append(
            "No configured cybersecurity detection rules were triggered."
        )
        recommendations.append(
            "Continue routine security monitoring."
        )

    return {
        "event_id": event_id,
        "source_ip": source_ip,
        "risk_level": risk_level,
        "status": status,
        "findings": findings,
        "recommendations": recommendations,
    }
