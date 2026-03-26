from pydantic import BaseModel, Field
from typing import List


class PatientData(BaseModel):
    age: float = Field(..., description="Age")
    sex: float = Field(..., description="Sex")
    bmi: float = Field(..., description="Body mass index")
    bp: float = Field(..., description="Average blood pressure")
    s1: float = Field(..., description="Total serum cholesterol")
    s2: float = Field(..., description="Low-density lipoproteins")
    s3: float = Field(..., description="High-density lipoproteins")
    s4: float = Field(..., description="Total cholesterol / HDL")
    s5: float = Field(..., description="Log of serum triglycerides level")
    s6: float = Field(..., description="Blood sugar level")


class PredictionResponse(BaseModel):
    predict: float
