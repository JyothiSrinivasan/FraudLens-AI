
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from aml_agent import detect_aml_patterns
from investigation_agent import generate_investigation_summary
from cybersecurity_agent import analyze_security_event
from case_management_agent import (
    create_case,
    load_cases,
    update_case,
    find_case_by_source,
)
from case_management_agent import prepare_transaction_case
from correlation_agent import correlate_risk_signals



# Project paths
PROJECT_DIR = Path(__file__).parent
MODEL_PATH = PROJECT_DIR / "fraud_model.pkl"

# Load the trained machine-learning model
saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]
FEATURES = saved_model["features"]



st.set_page_config(
    page_title="FraudLens AI",
    page_icon="🔎",
    layout="wide"
)

# Project title
st.title("🔎 FraudLens AI")
st.subheader(
    "Financial Fraud Detection & Cybersecurity Investigation"
)

st.write(
    "Analyze financial transactions and explore "
    "potentially suspicious activity using synthetic data."
)

st.divider()

# Load transaction data

# Rule-based transaction risk scoring
def calculate_risk_score(transaction):
    score = 0

    if transaction["amount"] >= 30000:
        score += 30
    elif transaction["amount"] >= 10000:
        score += 15

    if transaction["hour"] <= 4:
        score += 20

    if transaction["is_foreign"] == 1:
        score += 20

    if transaction["failed_attempts"] >= 3:
        score += 30
    elif transaction["failed_attempts"] >= 1:
        score += 10

    return min(score, 100)



data_path = Path(__file__).parent / "data" / "transactions.csv"

try:
    df = pd.read_csv(data_path)
    df["risk_score"] = df.apply(calculate_risk_score, axis=1)

    df["risk_level"] = df["risk_score"].apply(
    lambda score: (
        "High" if score >= 70
        else "Medium" if score >= 40
        else "Low"
        )
    )

    # Generate machine-learning fraud predictions
    X = df[FEATURES]

    df["fraud_probability"] = model.predict_proba(X)[:, 1]

    df["ml_prediction"] = df["fraud_probability"].apply(
        lambda probability: (
            "Potential Fraud" if probability >= 0.5
            else "Likely Legitimate"
        )
    )



    # Dashboard metrics
    total_transactions = len(df)
    suspicious_transactions = int(df["is_fraud"].sum())
    critical_alerts = int(
        (
            (df["is_fraud"] == 1)
            & (df["amount"] >= 30000)
        ).sum()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Transactions Analyzed", total_transactions)
    col2.metric("Flagged Fraud Examples", suspicious_transactions)
    col3.metric("High-Value Fraud Examples", critical_alerts)

    st.divider()

    # Transaction table
    
    # Risk-level summary
    st.header("🎯 Transaction Risk Summary")

    low_risk = int((df["risk_level"] == "Low").sum())
    medium_risk = int((df["risk_level"] == "Medium").sum())
    high_risk = int((df["risk_level"] == "High").sum())

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    risk_col1.metric("Low Risk", low_risk)
    risk_col2.metric("Medium Risk", medium_risk)
    risk_col3.metric("High Risk", high_risk)

    st.divider()
    
    # Risk distribution chart
    st.subheader("📊 Risk Distribution")

    risk_chart_data = pd.DataFrame({
        "Risk Level": ["Low", "Medium", "High"],
        "Transactions": [low_risk, medium_risk, high_risk]
    })

    st.plotly_chart(
        __import__("plotly.express", fromlist=["pie"]).pie(
            risk_chart_data,
            names="Risk Level",
            values="Transactions",
            title="Transaction Risk Breakdown",
            hole=0.4
        ),
        use_container_width=True
    )

    st.header("📊 Transaction Explorer")
    

    selected_risk = st.selectbox(
        "Filter transactions by risk level",
        ["All", "Low", "Medium", "High"]
    )

    if selected_risk == "All":
        filtered_df = df
    else:
        filtered_df = df[df["risk_level"] == selected_risk]

    st.metric(
        f"{selected_risk} Risk Transactions",
        len(filtered_df)
    )
    
    st.metric(
        "ML-Predicted Fraud",
        int((df["ml_prediction"] == "Potential Fraud").sum())
    )

    st.metric(
        "Average Fraud Probability",
        f"{df['fraud_probability'].mean():.1%}"
    )


    

    st.write("Browse the synthetic financial transaction records.")

    st.dataframe(df, use_container_width=True)
    
    # ML Fraud Investigation Table
    st.subheader("🔍 ML Fraud Investigation")

    investigation_df = df[
        [
            "transaction_id",
            "amount",
            "fraud_probability",
            "ml_prediction",
            "risk_level",
        ]
    ].copy()

    investigation_df["fraud_probability"] = (
        investigation_df["fraud_probability"].map(
            lambda probability: f"{probability:.1%}"
        )
    )

    
    # Filter investigation results
    prediction_filter = st.selectbox(
        "Filter by ML prediction",
        ["All", "Potential Fraud", "Likely Legitimate"],
        key="ml_prediction_filter",
    )

    if prediction_filter != "All":
        display_df = investigation_df[
            investigation_df["ml_prediction"] == prediction_filter
        ]
    else:
        display_df = investigation_df

    st.dataframe(
        display_df.sort_values(
            "fraud_probability",
            ascending=False,
            key=lambda column: column.map(
                lambda value: float(value.rstrip("%"))
            ) if column.dtype == "object" else column,
        ),
        use_container_width=True,
        hide_index=True,
    )
    
    # Individual transaction investigation
    st.subheader("🕵️ Investigate Individual Transaction")

    transaction_ids = df["transaction_id"].tolist()

    selected_transaction_id = st.selectbox(
        "Select a transaction ID",
        transaction_ids,
        key="investigation_transaction",
    )

    selected_transaction = df[
        df["transaction_id"] == selected_transaction_id
    ].iloc[0]
    
    # Display selected transaction details
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Transaction Amount",
            f"₹{selected_transaction['amount']:,.0f}"
        )

    with col2:
        st.metric(
            "Fraud Probability",
            f"{selected_transaction['fraud_probability']:.1%}"
        )

    with col3:
        st.metric(
            "Rule-Based Risk Level",
            selected_transaction["risk_level"]
        )

    st.write(
        "ML Prediction:",
        selected_transaction["ml_prediction"]
    )
    
    st.subheader("🚩 Risk Indicators")

    indicators = []

    if selected_transaction["amount"] >= 30000:
        indicators.append("High transaction amount: ₹30,000 or more")
    elif selected_transaction["amount"] >= 10000:
        indicators.append("Elevated transaction amount: ₹10,000 or more")

    if selected_transaction["hour"] <= 4:
        indicators.append("Transaction occurred during a late-night/early-morning hour")

    if selected_transaction["is_foreign"] == 1:
        indicators.append("Foreign transaction")

    if selected_transaction["failed_attempts"] >= 3:
        indicators.append("Three or more failed attempts")
    elif selected_transaction["failed_attempts"] >= 1:
        indicators.append("One or more failed attempts")

    if indicators:
        for indicator in indicators:
            st.warning(indicator)
    else:
        st.success("No indicators from the current rules were triggered.")

    
    st.divider()
    st.header("🏦 AML Monitoring Agent")

    aml_results = detect_aml_patterns(df)

    if aml_results.empty:
        st.success("No customers matched the current AML screening rule.")
    else:
        st.warning(
            f"{len(aml_results)} customer(s) require AML review "
            "under the current screening rule."
        )




        st.dataframe(
            aml_results,
            use_container_width=True,
            hide_index=True,
        )





    st.caption(
        "AML alerts are preliminary screening results from synthetic data. "
        "They do not establish money laundering or other wrongdoing."
    )




    aml_customer = None

    if not aml_results.empty:
        matching_aml = aml_results[
            aml_results["customer_id"]
            == selected_transaction["customer_id"]
        ]

        if not matching_aml.empty:
            aml_customer = matching_aml.iloc[0]

    investigation_input = selected_transaction.copy()

    investigation_input["risk_indicators"] = indicators

    investigation_result = generate_investigation_summary(
        investigation_input,
        aml_customer
    )
    st.subheader("📋 Investigation Summary")

    st.write(
        investigation_result["investigation_summary"]
    )

    st.caption(
        "This summary is generated from synthetic data. "
        "Predictions and risk indicators require human review "
        "and do not confirm fraudulent activity. "
        "AML alerts are preliminary screening results, not "
        "proof of money laundering."
    )
   

    
    # Export the selected transaction's investigation report
    from datetime import datetime

 

    report_df = pd.DataFrame([{
        "Transaction ID": selected_transaction_id,
        "Transaction Amount": selected_transaction["amount"],
        "Fraud Probability": selected_transaction["fraud_probability"],
        "ML Prediction": selected_transaction["ml_prediction"],
        "Rule-Based Risk Score": selected_transaction["risk_score"],
        "Rule-Based Risk Level": selected_transaction["risk_level"],
        "Risk Indicators": "; ".join(indicators),
        "Investigation Summary": investigation_result["investigation_summary"],
        "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Disclaimer": (
            "Synthetic-data prototype. Predictions require human review "
            "and do not confirm fraudulent activity."
        )
    }])

    st.download_button(
        label="📥 Download Investigation Report (CSV)",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name=f"FraudLens_Report_{selected_transaction_id}.csv",
        mime="text/csv",
    )



    # Display flagged examples
    
    # Transaction amount analysis
    st.subheader("💰 Transaction Amount Analysis")

    st.bar_chart(
        df,
        x="transaction_id",
        y="amount",
        x_label="Transaction ID",
        y_label="Transaction Amount"
    )
    
    # Suspicious Transaction Investigation
    st.header("🔍 Suspicious Transaction Investigation")

    investigation_df = df[df["risk_level"] == "High"]

    if not investigation_df.empty:
        selected_transaction = st.selectbox(
            "Select a high-risk transaction",
            investigation_df["transaction_id"].tolist()
        )

        transaction = investigation_df[
            investigation_df["transaction_id"] == selected_transaction
        ].iloc[0]

        st.subheader(f"Investigation: {selected_transaction}")
        
        # Explain the risk factors
        st.subheader("🧠 Why Was This Transaction Flagged?")

        risk_reasons = []

        if transaction["amount"] >= 30000:
            risk_reasons.append("High transaction amount: ₹30,000 or more")
        elif transaction["amount"] >= 10000:
            risk_reasons.append("Elevated transaction amount: ₹10,000 or more")

        if transaction["hour"] <= 4:
            risk_reasons.append("Transaction occurred during the early morning (12 AM–4 AM)")

        if transaction["is_foreign"] == 1:
            risk_reasons.append("Foreign activity indicator is enabled")

        if transaction["failed_attempts"] >= 3:
            risk_reasons.append("Multiple failed attempts: 3 or more")
        elif transaction["failed_attempts"] >= 1:
            risk_reasons.append("At least one failed attempt was recorded")

        if risk_reasons:
            for reason in risk_reasons:
                st.warning(reason)
        else:
            st.success("No risk factors from the current rules were triggered.")


        detail1, detail2, detail3 = st.columns(3)
        detail1.metric("Transaction Amount", f"₹{transaction['amount']:,.2f}")
        detail2.metric("Risk Score", f"{transaction['risk_score']}/100")
        detail3.metric("Risk Level", transaction["risk_level"])

        st.write("**Customer ID:**", transaction["customer_id"])
        st.write("**Transaction Type:**", transaction["transaction_type"])
        st.write("**Location:**", transaction["location"])
        st.write("**Transaction Hour:**", transaction["hour"])
        st.write("**Foreign Activity Indicator:**", transaction["is_foreign"])
        st.write("**Failed Attempts:**", transaction["failed_attempts"])

    else:
        st.info("No high-risk transactions are available to investigate.")

    st.header("🚨 Flagged Transaction Examples")

    flagged_df = df[df["is_fraud"] == 1]

    if not flagged_df.empty:
        st.dataframe(flagged_df, use_container_width=True)
    else:
        st.success("No transactions are labelled as fraudulent.")

    st.caption(
        "Educational demo using synthetic data. "
        "Fraud labels are preassigned example labels, "
        "not predictions from a trained machine-learning model."
    )

except FileNotFoundError:
    st.error(
        "Transaction file not found. Please check that "
        "data/transactions.csv exists inside your project folder."
    )
except (KeyError, pd.errors.ParserError) as error:
    st.error(f"Please check the transaction CSV file: {error}")


st.divider()

st.header("🛡️ Cybersecurity Threat Analysis")

st.write(
    "Analyze a simulated security event for suspicious "
    "login patterns and potential brute-force activity."
)

with st.expander("Analyze a sample security event", expanded=True):
    event_id = st.text_input(
        "Security Event ID",
        value="SEC001"
    )

    source_ip = st.text_input(
        "Source IP (simulated)",
        value="203.0.113.10"
    )

    failed_attempts = st.number_input(
        "Failed Login Attempts",
        min_value=0,
        max_value=100,
        value=7,
        step=1
    )

    event_hour = st.slider(
        "Event Hour (24-hour format)",
        min_value=0,
        max_value=23,
        value=2
    )

    foreign_activity = st.checkbox(
        "Foreign-source activity indicator",
        value=True
    )

    if st.button("Analyze Security Event"):
        security_event = {
            "event_id": event_id,
            "source_ip": source_ip,
            "failed_attempts": failed_attempts,
            "hour": event_hour,
            "is_foreign": int(foreign_activity),
        }

        security_result = analyze_security_event(security_event)

        st.subheader("Security Analysis Results")

        st.write("**Event ID:**", security_result["event_id"])
        st.write("**Source IP:**", security_result["source_ip"])
        st.write("**Risk Level:**", security_result["risk_level"])
        st.write("**Status:**", security_result["status"])

        st.write("**Findings**")
        for finding in security_result["findings"]:
            st.write(f"- {finding}")

        st.write("**Recommended Actions**")
        for recommendation in security_result["recommendations"]:
            st.write(f"- {recommendation}")

        st.caption(
            "This prototype analyzes simulated events using "
            "rule-based logic. Alerts require human review and "
            "do not establish that an attack occurred."
        )


# ==================================================
# CASE MANAGEMENT DASHBOARD
# ==================================================

st.divider()
st.header("📁 Case Management Dashboard")

st.write(
    "Create investigation cases, track review status, "
    "manage priorities, and record analyst notes."
)

# Create a new investigation case
with st.expander("➕ Create New Investigation Case", expanded=True):
    with st.form("create_case_form"):
        source_type = st.selectbox(
            "Case Source",
            ["Transaction", "Cybersecurity Event", "AML Alert"]
        )

        source_id = st.text_input(
            "Transaction / Event ID",
            placeholder="Example: TXN004"
        )

        customer_id = st.text_input(
            "Customer ID (optional)",
            placeholder="Example: CUST101"
        )

        priority = st.selectbox(
            "Review Priority",
            ["High", "Medium", "Low"]
        )

        case_summary = st.text_area(
            "Investigation Summary",
            placeholder="Describe why this case requires review..."
        )

        create_button = st.form_submit_button(
            "Create Investigation Case"
        )

        if create_button:
            if not source_id.strip() or not case_summary.strip():
                st.error("Please enter a source ID and investigation summary.")
            else:
                try:
                    new_case = create_case(
                        source_type,
                        source_id.strip(),
                        customer_id.strip(),
                        priority,
                        case_summary.strip(),
                    )
                    st.success(
                        f"Case {new_case['case_id']} created successfully!"
                    )
                except ValueError as error:
                    st.warning(str(error))


# Load and display saved cases
cases = load_cases()

st.subheader("📋 Investigation Case Register")

if not cases.empty:
    st.dataframe(cases, use_container_width=True)

    # Update an existing case
    with st.expander("✏️ Update Case Status and Analyst Notes"):
        case_ids = cases["case_id"].tolist()

        selected_case_id = st.selectbox(
            "Select Case",
            case_ids,
            key="case_to_update"
        )

        selected_case = cases[
            cases["case_id"] == selected_case_id
        ].iloc[0]

        with st.form("update_case_form"):
            new_status = st.selectbox(
                "Case Status",
                ["Open", "Under Review", "Closed"],
                index=["Open", "Under Review", "Closed"].index(
                    selected_case["status"]
                ),
            )

            new_priority = st.selectbox(
                "Review Priority",
                ["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(
                    selected_case["priority"]
                ),
            )

            analyst_notes = st.text_area(
                "Analyst Notes",
                value=selected_case["analyst_notes"],
            )

            update_button = st.form_submit_button("Save Case Updates")

            if update_button:
                update_case(
                    selected_case_id,
                    new_status,
                    new_priority,
                    analyst_notes,
                )
                st.success(f"Case {selected_case_id} updated successfully!")
                st.rerun()

    # Export saved cases
    st.download_button(
        label="📥 Download Case Register (CSV)",
        data=cases.to_csv(index=False).encode("utf-8"),
        file_name="fraudlens_investigation_cases.csv",
        mime="text/csv",
    )

else:
    st.info(
        "No investigation cases yet. Create your first case above."
    )

st.caption(
    "FraudLens AI case management is a prototype. "
    "Analysts must review alerts and approve consequential actions."
)


# ==================================================
# AGENT 7: AUTOMATED CASE CREATION
# ==================================================

st.divider()
st.header("🤖 Automated Case Creation")

st.write(
    "Prepare investigation cases from analyzed transactions. "
    "Review the draft before creating a case."
)


if not df.empty:
    transaction_options = df["transaction_id"].tolist()

    selected_transaction_id = st.selectbox(
        "Select an Analyzed Transaction",
        transaction_options,
        key="automated_case_transaction",
    )

    selected_transaction = df[
        df["transaction_id"] == selected_transaction_id
    ].iloc[0].to_dict()


    case_draft = prepare_transaction_case(selected_transaction)

    st.subheader("Investigation Case Draft")
    st.write("**Transaction ID:**", case_draft["source_id"])
    st.write("**Customer ID:**", case_draft["customer_id"])
    st.write("**Suggested Priority:**", case_draft["priority"])
    st.write("**Summary:**", case_draft["case_summary"])

    confirm_case = st.checkbox(
        "I have reviewed this draft and want to create the case.",
        key="confirm_automated_case",
    )

    if st.button("Create Case from Transaction"):
        if not confirm_case:
            st.warning("Please review the draft and confirm first.")
        else:
            try:
                new_case = create_case(
                    case_draft["source_type"],
                    case_draft["source_id"],
                    case_draft["customer_id"],
                    case_draft["priority"],
                    case_draft["case_summary"],
                )
                st.success(
                    f"Investigation case {new_case['case_id']} created!"
                )
            except ValueError as error:
                st.warning(str(error))

else:
    st.info("No analyzed transactions are available.")


# ==================================================
# AGENT 8: FRAUD & CYBERSECURITY CORRELATION
# ==================================================

st.divider()
st.header("🔗 Fraud & Cybersecurity Correlation")

st.write(
    "Compare transaction risk with a simulated security event "
    "to identify signals that may warrant combined review."
)

if not df.empty:
    correlation_transaction_id = st.selectbox(
        "Select Transaction",
        df["transaction_id"].tolist(),
        key="correlation_transaction",
    )

    correlation_transaction = df[
        df["transaction_id"] == correlation_transaction_id
    ].iloc[0].to_dict()

    st.subheader("Simulated Security Event")

    security_event_id = st.text_input(
        "Security Event ID",
        value="SEC001",
        key="correlation_event_id",
    )

    security_failed_attempts = st.number_input(
        "Failed Login Attempts",
        min_value=0,
        max_value=100,
        value=7,
        key="correlation_failed_attempts",
    )

    security_event_hour = st.slider(
        "Security Event Hour",
        min_value=0,
        max_value=23,
        value=2,
        key="correlation_event_hour",
    )

    security_foreign = st.checkbox(
        "Foreign-source activity indicator",
        value=True,
        key="correlation_foreign",
    )

    if st.button("Analyze Combined Risk", key="run_correlation"):
        security_event = {
            "event_id": security_event_id.strip() or "UNKNOWN",
            "failed_attempts": security_failed_attempts,
            "hour": security_event_hour,
            "is_foreign": int(security_foreign),
        }

        correlation_result = correlate_risk_signals(
            correlation_transaction,
            security_event,
        )

        st.subheader("Combined Risk Assessment")

        st.write(
            "**Transaction:**",
            correlation_result["transaction_id"],
        )
        st.write(
            "**Security Event:**",
            correlation_result["security_event_id"],
        )
        st.write(
            "**Combined Risk:**",
            correlation_result["combined_risk"],
        )

        st.write("**Findings**")
        for finding in correlation_result["findings"]:
            st.write(f"- {finding}")

        st.write(
            "**Recommended Action:**",
            correlation_result["recommendation"],
        )

        st.warning(correlation_result["correlation_status"])

st.caption(
    "This prototype compares supplied records. "
    "A combined risk assessment does not establish that the "
    "transaction and security event share an identity or causal link."
)


# ==================================================
# AGENT 9: EXECUTIVE RISK DASHBOARD
# ==================================================

st.divider()
st.header("📊 Executive Risk Dashboard")

st.write(
    "Management overview of transaction risk, AML screening, "
    "and investigation case progress."
)

# Transaction metrics
if not df.empty:
    total_transactions = len(df)

    high_risk_count = int((df["risk_level"] == "High").sum())
    medium_risk_count = int((df["risk_level"] == "Medium").sum())
    low_risk_count = int((df["risk_level"] == "Low").sum())

    flagged_count = int(
        (
            (df["risk_level"] == "High")
            | (df["risk_level"] == "Medium")
        ).sum()
    )

    st.subheader("💳 Transaction Risk Overview")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Transactions Analyzed", total_transactions)
    metric2.metric("High-Risk Transactions", high_risk_count)
    metric3.metric("Flagged Transactions", flagged_count)

    metric4, metric5 = st.columns(2)

    metric4.metric("Medium-Risk Transactions", medium_risk_count)
    metric5.metric("Low-Risk Transactions", low_risk_count)

    risk_chart_data = pd.DataFrame(
        {
            "Risk Level": ["High", "Medium", "Low"],
            "Transactions": [
                high_risk_count,
                medium_risk_count,
                low_risk_count,
            ],
        }
    )

    st.bar_chart(
        risk_chart_data.set_index("Risk Level")
    )

# Case management metrics
cases = load_cases()

st.subheader("📁 Investigation Case Overview")

if not cases.empty:
    total_cases = len(cases)
    open_cases = int((cases["status"] == "Open").sum())
    review_cases = int((cases["status"] == "Under Review").sum())
    closed_cases = int((cases["status"] == "Closed").sum())

    case_metric1, case_metric2 = st.columns(2)

    case_metric1.metric("Total Cases", total_cases)
    case_metric2.metric("Open Cases", open_cases)

    case_metric3, case_metric4 = st.columns(2)

    case_metric3.metric("Under Review", review_cases)
    case_metric4.metric("Closed Cases", closed_cases)

    case_chart_data = pd.DataFrame(
        {
            "Case Status": ["Open", "Under Review", "Closed"],
            "Cases": [open_cases, review_cases, closed_cases],
        }
    )

    st.bar_chart(
        case_chart_data.set_index("Case Status")
    )

    st.subheader("🚨 High-Priority Cases")

    high_priority_cases = cases[
        cases["priority"] == "High"
    ]

    if not high_priority_cases.empty:
        st.dataframe(
            high_priority_cases[
                [
                    "case_id",
                    "source_type",
                    "source_id",
                    "priority",
                    "status",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.info("There are currently no high-priority cases.")

    st.download_button(
        label="📥 Download Executive Case Report",
        data=cases.to_csv(index=False).encode("utf-8"),
        file_name="fraudlens_executive_case_report.csv",
        mime="text/csv",
    )

else:
    st.info("No investigation cases have been created yet.")

st.caption(
    "Executive metrics reflect the current prototype dataset "
    "and saved local cases. Risk flags are preliminary and "
    "require human review."
)



# ==================================================
# AGENT 10: AUTOMATED AML CASE CREATION
# ==================================================

st.divider()
st.header("🏦 Automated AML Case Creation")

st.write(
    "Review AML screening alerts and create investigation "
    "cases directly in the existing case register."
)

if "aml_results" in locals() and not aml_results.empty:

    aml_customer_options = aml_results["customer_id"].tolist()

    selected_aml_customer_id = st.selectbox(
        "Select an AML Alert",
        aml_customer_options,
        key="automated_aml_customer"
    )

    aml_alert = aml_results[
        aml_results["customer_id"] == selected_aml_customer_id
    ].iloc[0]

    aml_priority = aml_alert["aml_review_priority"]

    aml_case_summary = (
        f"AML screening alert for customer "
        f"{selected_aml_customer_id}. "
        f"Repeated bank transfers detected: "
        f"{int(aml_alert['transfer_count'])}. "
        f"Combined transfer amount: "
        f"₹{float(aml_alert['total_amount']):,.2f}. "
        f"Transaction IDs: {aml_alert['transaction_ids']}. "
        f"Reason: {aml_alert['aml_reason']}. "
        f"Human review required; this alert does not establish wrongdoing."
    )

    st.subheader("AML Investigation Case Draft")

    st.write("**Customer ID:**", selected_aml_customer_id)
    st.write("**Transfer Count:**", int(aml_alert["transfer_count"]))
    st.write(
        "**Combined Transfer Amount:**",
        f"₹{float(aml_alert['total_amount']):,.2f}"
    )
    st.write("**Transaction IDs:**", aml_alert["transaction_ids"])
    st.write("**AML Reason:**", aml_alert["aml_reason"])
    st.write("**Suggested Priority:**", aml_priority)
    st.write("**Status:**", aml_alert["aml_review_status"])

    st.text_area(
        "Case Summary",
        value=aml_case_summary,
        height=150,
        disabled=True,
        key="automated_aml_case_summary"
    )


   
    existing_aml_case = find_case_by_source(
        "AML Alert",
        f"AML-{selected_aml_customer_id}"
    )

    if existing_aml_case:
        st.warning("An investigation case already exists for this AML alert.")

        st.subheader("Existing AML Investigation Case")

        st.write("**Case ID:**", existing_aml_case["case_id"])
        st.write("**Customer ID:**", existing_aml_case["customer_id"])
        st.write("**Status:**", existing_aml_case["status"])
        st.write("**Priority:**", existing_aml_case["priority"])
        st.write("**Created At:**", existing_aml_case["created_at"])

        st.write("**Case Summary:**")
        st.write(existing_aml_case["case_summary"])

        st.write("**Analyst Notes:**")
        analyst_notes = existing_aml_case.get("analyst_notes", "")
        if pd.isna(analyst_notes) or not str(analyst_notes).strip():
            st.write("No analyst notes recorded yet.")
        else:
            st.write(analyst_notes)

        st.info(
            "Use the Case Management Dashboard above to update "
            "this case's status, priority, or analyst notes."
        )
        
        st.subheader("Update Existing AML Case")

        status_options = ["Open", "Under Review", "Closed"]
        priority_options = ["Low", "Medium", "High"]

        current_status = str(existing_aml_case.get("status", "Open"))
        current_priority = str(existing_aml_case.get("priority", "Medium"))

        if current_status not in status_options:
            current_status = "Open"

        if current_priority not in priority_options:
            current_priority = "Medium"

        current_notes = existing_aml_case.get("analyst_notes", "")
        if pd.isna(current_notes):
            current_notes = ""
        else:
            current_notes = str(current_notes)

        with st.form(key=f"update_aml_case_{existing_aml_case['case_id']}"):
            updated_status = st.selectbox(
                "Case Status",
                options=status_options,
                index=status_options.index(current_status),
            )

            updated_priority = st.selectbox(
                "Case Priority",
                options=priority_options,
                index=priority_options.index(current_priority),
            )

            updated_notes = st.text_area(
                "Analyst Notes",
                value=current_notes,
                height=120,
            )

            save_aml_updates = st.form_submit_button(
                "Save AML Case Updates"
            )

        if save_aml_updates:
            try:
                update_case(
                    case_id=existing_aml_case["case_id"],
                    status=updated_status,
                    priority=updated_priority,
                    analyst_notes=updated_notes,
                )
                st.success("AML investigation case updated successfully!")
                st.rerun()
            except ValueError as error:
                st.error(str(error))


    else:
        confirm_aml_case = st.checkbox(
            "I reviewed this AML alert and approve creating an investigation case.",
            key="confirm_automated_aml_case"
        )

        if st.button("Create Case from AML Alert", key="create_aml_case"):

            if not confirm_aml_case:
                st.warning("Please review the alert and confirm first.")

            else:
                try:
                    new_aml_case = create_case(
                        source_type="AML Alert",
                        source_id=f"AML-{selected_aml_customer_id}",
                        customer_id=selected_aml_customer_id,
                        priority=aml_priority,
                        case_summary=aml_case_summary
                    )

                    st.success(
                        f"AML investigation case "
                        f"{new_aml_case['case_id']} created successfully!"
                    )

                    st.info(
                        "Open the Case Management Dashboard above "
                        "to view and manage this case."
                    )

                except ValueError as error:
                    st.warning(str(error))



        else:
            st.info("No AML alerts are currently available for case creation.")

st.caption(
    "AML case creation is a prototype workflow. Alerts are preliminary "
    "screening results and require human investigation; they do not "
    "establish money laundering or other wrongdoing."
)
