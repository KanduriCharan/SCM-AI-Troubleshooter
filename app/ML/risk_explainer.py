from typing import Any
import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def explain_risk_with_llm(prediction_result: dict[str, Any]) -> dict[str, Any]:
    predicted_risk = prediction_result.get("predicted_risk", "Unknown")
    probabilities = prediction_result.get("risk_probabilities", {})
    snapshot = prediction_result.get("shipment_snapshot", {})

    prompt = f"""
You are a senior logistics operations controller working in a real-time control tower.

A shipment has been flagged by an ML model.

Predicted Risk:
{predicted_risk}

Shipment Snapshot:
{snapshot}

Your job is NOT to give general advice.

You must generate REAL operational actions that a logistics team would EXECUTE immediately.

Rules:

1. Each action must:
   - Be specific (mention values like traffic, weather, etc.)
   - Be actionable (what exact system/process change)
   - Include impact (what delay/risk is reduced)

2. Avoid generic words:
   - DO NOT use: monitor, consider, review, assess
   - Use: trigger, reroute, escalate, reschedule, notify, reassign

3. Think in terms of systems:
   - TMS (Transportation Management System)
   - WMS (Warehouse)
   - Carrier communication
   - Customer notification

4. Make actions DIFFERENT depending on conditions

Return format:

Risk Explanation:
<short explanation>

Top Risk Drivers:
1. ...
2. ...
3. ...

Recommended Actions:
1. ...
2. ...
3. ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You explain supply chain risk using only the provided model output and shipment data.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    explanation_text = response.choices[0].message.content

    return {
        "llm_risk_explanation": explanation_text
    }