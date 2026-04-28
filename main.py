import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os
from fastapi import HTTPException
from typing import Dict
from config import FUSION_BASE_URL, FUSION_USERNAME, FUSION_PASSWORD
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, Depends


app = FastAPI()

# Oracle Config

# ---------------- AUTH ----------------
security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    if (
        credentials.username == os.getenv("PLAN_USERNAME")
        and credentials.password == os.getenv("PLAN_PASSWORD")
    ):
        return credentials.username
    raise HTTPException(status_code=401, detail="Unauthorized")



PLAN_ID = "300000326061212"
TABLE_ID = "9002"

from pydantic import BaseModel

class UpdateRequest(BaseModel):
    item: str
    organization: str
    month: str
    measure: str
    value: float

HEADERS = {
    "Content-Type": "application/vnd.oracle.adf.resourceitem+json",
    "REST-Framework-Version": "2"
}

# Column mapping (IMPORTANT)
COLUMN_INDEX: Dict[str, int] = {
    "Shipments History 1 Year Ago": 3,
    "Shipments History": 4,
    "Adjusted Shipments History": 5,
    "Final Shipments History": 6,
    "Sales Orders": 7,
    "Shipments Forecast": 8,
    "Adjusted Shipments Forecast": 9,
    "Final Shipments Forecast": 10,
    "Shipments Forecast MAPE": 11,
    "Shipments Forecast Bias": 12,
    "Shipments Forecast MAD": 13,
}

TOTAL_COLUMNS = 14

@app.post("/update-table")
def update_table(data: UpdateRequest, username: str = Depends(authenticate_user)):

    item = data.item
    org = data.organization
    month = data.month
    measure = data.measure
    value = data.value

    # ✅ Validation
    if not all([item, org, month, measure, value]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    if measure not in COLUMN_INDEX:
        raise HTTPException(status_code=400, detail="Invalid measure")

    # ✅ Build row
    row = [""] * TOTAL_COLUMNS
    row[0] = item
    row[1] = org
    row[2] = month

    col_index = COLUMN_INDEX[measure]
    row[col_index] = str(value)

    table_data = ",".join(row)

    payload = {
        "TableHierarchies": "PRT Planning Cat Set,Enterprise,Gregorian Calendar",
        "TableDataHeader": "Item,Organization,Month,Shipments History 1 Year Ago,Shipments History,Adjusted Shipments History,Final Shipments History,Sales Orders,Shipments Forecast,Adjusted Shipments Forecast,Final Shipments Forecast,Shipments Forecast MAPE,Shipments Forecast Bias,Shipments Forecast MAD",
        "TableData": table_data
    }

    url = f"{FUSION_BASE_URL}/fscmRestApi/resources/11.13.18.05/supplyChainPlans/{PLAN_ID}/child/PlanningTables/{TABLE_ID}/child/Data"

    response = requests.post(
        url,
        json=payload,
        headers=HEADERS,
        auth=(FUSION_USERNAME, FUSION_PASSWORD)
    )

    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail=response.text)

    return {
        "status": "success",
        "row": table_data,
        "oracle_response": response.json()
    }