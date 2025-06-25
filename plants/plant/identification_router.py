import base64
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from http import HTTPStatus
import logging
from typing import List
import re

from plant.identification import PlantIdentificationService, get_plant_identification_service
from plant.service import PlantService, get_plant_service
from common.schema import ApiResponse
from util.decorators import with_api_exception_handling

logger = logging.getLogger(__name__)
router = APIRouter()

def normalize_text(text: str) -> str:
    """Normalize text for better matching."""
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def find_best_match(plant_name: str, plants: List) -> tuple:
    """Find the best matching plant from the database."""
    if not plants or not plants:
        return None, 0.0

    normalized_search = normalize_text(plant_name)
    search_words = set(normalized_search.split())
    
    best_match = None
    best_score = 0.0

    for plant in plants:
        # Normalize plant name and description
        plant_name_norm = normalize_text(plant.name)
        plant_desc_norm = normalize_text(plant.description) if plant.description else ""
        
        # Calculate word match score
        plant_words = set(plant_name_norm.split())
        desc_words = set(plant_desc_norm.split())
        
        # Calculate matches in name
        name_matches = len(search_words.intersection(plant_words))
        name_score = name_matches / len(search_words) if search_words else 0
        
        # Calculate matches in description
        desc_matches = len(search_words.intersection(desc_words))
        desc_score = desc_matches / len(search_words) if search_words else 0
        
        # Weight name matches more heavily than description matches
        total_score = (name_score * 0.7) + (desc_score * 0.3)
        
        if total_score > best_score:
            best_score = total_score
            best_match = plant

    return best_match, best_score

@router.post("/identify", response_model=ApiResponse)
@with_api_exception_handling
def identify_plant(
    file: UploadFile = File(...),
    identification_service: PlantIdentificationService = Depends(get_plant_identification_service),
    plant_service: PlantService = Depends(get_plant_service)
):
    # Read and encode the image
    contents = file.file.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    
    # Get identification from Plant.ID API
    result = identification_service.identify_plant(base64_image.encode('utf-8'))
    
    result = result.get('result', {})
    result = result.get('classification', {})
    result = result.get('suggestions', [])
    
    if not result:
        return ApiResponse(
            status=HTTPStatus.NOT_FOUND,
            data={"message": "No plant matches found", "identified": False}
        )
    
    # Get the best match
    best_match = result[0]
    plant_name = best_match.get('name', '')
    confidence = best_match.get('probability', '')
    image_url = best_match.get('similar_images', [])[0].get('url', '')
    
    plants = []

    for word in plant_name.split():
        plants.extend(plant_service.fetch(page_size=10, page=1, search_query=word).items)

    matched_plant, match_confidence = find_best_match(plant_name, plants)
    
    response_data = {
        "identified": True,
        "plant_name": plant_name,
        "confidence": confidence,
        "image_url": image_url,
        "found_in_database": False
    }
    
    if matched_plant and match_confidence > 0.3:  # Only consider it a match if confidence is above 30%
        response_data["found_in_database"] = True
        response_data["plant_id"] = matched_plant.id
        response_data["match_confidence"] = match_confidence
        
    return ApiResponse(status=HTTPStatus.OK, data=response_data) 