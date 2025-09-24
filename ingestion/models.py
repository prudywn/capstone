from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class AirQualityRecord(BaseModel):
    city: str
    timestamp: datetime
    pm2_5: Optional[float] = Field(None, ge=0)
    pm10: Optional[float] = Field(None, ge=0)
    ozone: Optional[float] = Field(None, ge=0)
    carbon_monoxide: Optional[float] = Field(None, ge=0)
    nitrogen_dioxide: Optional[float] = Field(None, ge=0)
    sulphur_dioxide: Optional[float] = Field(None, ge=0)
    uv_index: Optional[float] = Field(None, ge=0)
    source: str = "open-meteo"
    ingest_time: datetime

    # Optionally add custom validators if needed
    @validator("uv_index")
    def uv_index_max(cls, v):
        if v is not None and v > 20:
            raise ValueError("UV index out of expected range (0-20)")
        return v
