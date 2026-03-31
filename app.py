from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

# The exact name you provided
DATASET_FILE = "devices_dataset.csv.xlsx"


@app.get("/get-devices")
def get_devices():
    df = pd.read_excel("devices_dataset.csv.xlsx")

    # ADD THESE LINES TO FIX THE ERROR:
    df = df.astype(str)  # Converts everything to text to avoid Arrow errors

    return df.to_dict(orient="records")