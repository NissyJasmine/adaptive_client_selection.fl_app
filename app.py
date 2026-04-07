from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI()

# Path logic to ensure it finds the file in the Vercel environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "devices_dataset.csv.xlsx")

@app.get("/")
def home():
    """
    Root route to prevent 'Not Found' errors when visiting the base URL.
    """
    return {
        "status": "online",
        "message": "Adaptive Client Selection API is running",
        "endpoints": {
            "get_devices": "/get-devices",
            "docs": "/docs"
        }
    }

@app.get("/get-devices")
def get_devices():
    # Check if the file exists before trying to read it
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset file not found at {DATASET_PATH}"
        )

    try:
        # Reading the Excel file
        df = pd.read_excel(DATASET_PATH)

        # Fix for Arrow/JSON serialization errors
        # This converts numbers/NaNs to strings to ensure the JSON is valid
        df = df.astype(str)

        return df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
