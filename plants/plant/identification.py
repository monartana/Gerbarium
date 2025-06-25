import os
import requests
from fastapi import HTTPException
from http import HTTPStatus
from typing import Optional, Dict, Any
from config import PLANT_ID_API_KEY

class PlantIdentificationService:
    def __init__(self):
        self.api_key = PLANT_ID_API_KEY
        if not self.api_key:
            raise ValueError("PLANT_ID_API_KEY environment variable is not set")
        self.api_url = "https://plant.id/api/v3/identification"

    def identify_plant(self, image_data: bytes) -> Dict[str, Any]:
        if not image_data:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="No image data provided"
            )

        data = {
            "images": [image_data.decode('utf-8')],
            "similar_images": True,
        }

        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(self.api_url, json=data, headers=headers)

        if not str(response.status_code).startswith('2'):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Failed to identify plant"
            )
            
        return response.json()

def get_plant_identification_service() -> PlantIdentificationService:
    return PlantIdentificationService() 