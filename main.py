from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

# ---------------------------------------------------
# 1. Load the trained pipeline (preprocessing + model)
# ---------------------------------------------------
MODEL_PATH = "best_model.pkl"   # make sure this file is in the same folder

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"WARNING: {MODEL_PATH} not found. Place your trained pipeline in this folder.")

app = FastAPI( 
    title="Loan Default Prediction API",
    description="Predicts whether a borrower will default on a loan",
    version="1.0"
)


# ---------------------------------------------------
# 2. Define the input schema (must match training columns)
#    Adjust field names/types to match YOUR dataset exactly.
# ---------------------------------------------------
class LoanApplication(BaseModel):
    Age: int
    Income: float
    LoanAmount: float
    CreditScore: int
    MonthsEmployed: int
    NumCreditLines: int
    InterestRate: float
    LoanTerm: int
    DTIRatio: float
    Education: str
    EmploymentType: str
    MaritalStatus: str
    HasMortgage: str
    HasDependents: str
    LoanPurpose: str
    HasCoSigner: str

    class Config:
        json_schema_extra = {
            "example": {
                "Age": 35,
                "Income": 55000,
                "LoanAmount": 15000,
                "CreditScore": 650,
                "MonthsEmployed": 36,
                "NumCreditLines": 4,
                "InterestRate": 12.5,
                "LoanTerm": 36,
                "DTIRatio": 0.35,
                "Education": "Bachelor's",
                "EmploymentType": "Full-time",
                "MaritalStatus": "Married",
                "HasMortgage": "Yes",
                "HasDependents": "No",
                "LoanPurpose": "Auto",
                "HasCoSigner": "No"
            }
        }


# ---------------------------------------------------
# 3. Routes
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "Loan Default Prediction API is running. Go to /docs to test it."}


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(application: LoanApplication):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded on server.")

    # Convert incoming JSON into a single-row DataFrame
    # (the pipeline expects the same raw column format used during training)
    input_df = pd.DataFrame([application.model_dump()])

    try:
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]  # probability of class 1 (default)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

    return {
        "prediction": int(prediction),
        "result": "Default" if prediction == 1 else "No Default",
        "default_probability": round(float(probability), 4)
    }