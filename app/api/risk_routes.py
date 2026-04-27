from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ML.risk_predictor import load_current_shipments, predict_shipment_risk

from app.ML.risk_explainer import explain_risk_with_llm


router = APIRouter(prefix="/risk", tags=["risk"])


class RiskPredictionRequest(BaseModel):
    shipment_id: str


@router.get("/shipments")
def get_current_shipments():
    df = load_current_shipments()

    display_columns = [
        "shipment_id",
        "order_id",
        "customer_name",
        "origin_city",
        "destination_city",
        "carrier",
        "shipment_status",
        "priority",
        "shipment_mode",
    ]

    available_columns = [col for col in display_columns if col in df.columns]

    return {
        "shipments": df[available_columns].to_dict(orient="records")
    }


@router.post("/predict")
def predict_risk(payload: RiskPredictionRequest):
    try:
        prediction = predict_shipment_risk(payload.shipment_id)

        llm_explanation = explain_risk_with_llm(prediction)

        return {
            **prediction,
            **llm_explanation,
        }

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))