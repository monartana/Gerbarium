from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .model import Plant
from .schema import PlantRead
from favorite.model import Favorite
from comment.model import Comment
from database import get_db


class PlantRecommendationService:
    # Weights for different types of interactions
    LIKE_WEIGHT = 2.0
    COMMENT_WEIGHT = 1.5
    COMMENT_COUNT_FACTOR = 0.5  # Additional weight per comment
    MAX_COMMENT_BONUS = 10.0  # Cap on additional comment weight
    
    # Time decay factors (in days)
    TIME_DECAY_FACTOR = 0.1
    MAX_TIME_PENALTY = 0.5  # Maximum penalty for old interactions

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_similar_plants(self, plant_id: int, limit: int = 5) -> List[PlantRead]:
        """Get similar plants based on name, species, and description similarity."""
        # Get the target plant
        target_plant = self.db.query(Plant).filter(Plant.id == plant_id).first()
        if not target_plant:
            return []

        # Get all other plants
        all_plants = self.db.query(Plant).filter(Plant.id != plant_id).all()
        if not all_plants:
            return []

        # Create text representations for similarity calculation
        plant_texts = [f"{p.name} {p.species} {p.description}" for p in all_plants]
        target_text = f"{target_plant.name} {target_plant.species} {target_plant.description}"

        # Calculate text similarity using TF-IDF and cosine similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([target_text] + plant_texts)
        
        # Calculate similarity scores
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Get top similar plants
        similar_indices = np.argsort(cosine_similarities)[::-1][:limit]
        return [all_plants[i] for i in similar_indices]

    def get_personalized_recommendations(self, user_id: int, limit: int = 5) -> List[PlantRead]:
        """Get personalized plant recommendations based on weighted user interactions."""
        # Get user's interactions
        interactions = self._get_user_interactions(user_id)
        if not interactions:
            return self._get_most_popular_plants(limit)

        # Get interaction weights for each plant
        plant_weights = self._calculate_interaction_weights(interactions)

        # Get all plants the user hasn't interacted with
        interacted_plant_ids = set(plant_weights.keys())
        recommendations = (
            self.db.query(Plant)
            .filter(Plant.id.notin_(interacted_plant_ids))
            .all()
        )

        if not recommendations:
            return []

        # Get plants user has interacted with for similarity comparison
        interacted_plants = self.db.query(Plant).filter(Plant.id.in_(interacted_plant_ids)).all()
        
        # Score recommendations
        scored_recommendations = []
        for rec in recommendations:
            # Calculate similarity scores and find the most similar interacted plant
            similarities = []
            for plant in interacted_plants:
                similarity = self._calculate_plant_similarity_score(rec, plant)
                weight = plant_weights[plant.id]
                similarities.append((similarity, weight))

            if similarities:
                # Find the most similar plant and its weight
                max_similarity, corresponding_weight = max(similarities, key=lambda x: x[0])
                
                # The final score is based on both similarity and interaction weight
                # We multiply similarity by weight to emphasize plants similar to highly-interacted ones
                # We also add a bonus based on the weight to further boost recommendations similar to
                # plants with many interactions
                final_score = (max_similarity * corresponding_weight) + (corresponding_weight * 0.5)
                
                scored_recommendations.append((rec, final_score))

        # Sort by score and return top recommendations
        scored_recommendations.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in scored_recommendations[:limit]]

    def _get_user_interactions(self, user_id: int) -> Dict[int, Dict[str, any]]:
        """Get user's interactions with plants with timestamps and interaction types."""
        interactions = defaultdict(lambda: {"latest_time": None, "comment_count": 0, "has_like": False})

        # Get current time as naive datetime for consistent comparison
        now = datetime.utcnow()

        # Get likes with timestamps
        likes = (
            self.db.query(Favorite.plant_id, Favorite.created_at)
            .filter(Favorite.user_id == user_id)
            .all()
        )
        for plant_id, created_at in likes:
            interactions[plant_id]["has_like"] = True
            # Ensure created_at is naive datetime for comparison
            if created_at and created_at.tzinfo:
                created_at = created_at.replace(tzinfo=None)
            if (interactions[plant_id]["latest_time"] is None or 
                (created_at and created_at > interactions[plant_id]["latest_time"])):
                interactions[plant_id]["latest_time"] = created_at

        # Get comments with timestamps and count
        comments = (
            self.db.query(Comment.plant_id, Comment.created_at)
            .filter(Comment.user_id == user_id)
            .all()
        )
        for plant_id, created_at in comments:
            interactions[plant_id]["comment_count"] += 1
            # Ensure created_at is naive datetime for comparison
            if created_at and created_at.tzinfo:
                created_at = created_at.replace(tzinfo=None)
            if (interactions[plant_id]["latest_time"] is None or 
                (created_at and created_at > interactions[plant_id]["latest_time"])):
                interactions[plant_id]["latest_time"] = created_at

        return interactions

    def _calculate_interaction_weights(self, interactions: Dict) -> Dict[int, float]:
        """Calculate weights for each plant based on interaction patterns."""
        now = datetime.utcnow()  # Use naive UTC datetime
        weights = {}

        for plant_id, data in interactions.items():
            weight = 0
            
            # Base weights for interaction types
            if data["has_like"]:
                weight += self.LIKE_WEIGHT

            # Comment weight with bonus for multiple comments
            comment_count = data["comment_count"]
            if comment_count > 0:
                comment_weight = self.COMMENT_WEIGHT + (
                    min(comment_count * self.COMMENT_COUNT_FACTOR, self.MAX_COMMENT_BONUS)
                )
                weight += comment_weight

            # Time decay
            if data["latest_time"]:
                # Calculate days between naive datetimes
                days_old = (now - data["latest_time"]).days
                time_penalty = min(
                    days_old * self.TIME_DECAY_FACTOR,
                    self.MAX_TIME_PENALTY
                )
                weight *= (1 - time_penalty)

            weights[plant_id] = max(weight, 0.1)  # Ensure minimum weight of 0.1

        return weights

    def _calculate_plant_similarity_score(self, plant1: Plant, plant2: Plant) -> float:
        """Calculate a comprehensive similarity score between two plants."""
        # Text similarity using TF-IDF
        text1 = f"{plant1.name} {plant1.species} {plant1.description}"
        text2 = f"{plant2.name} {plant2.species} {plant2.description}"

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        text_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()[0]

        # Name similarity for numerical names (like "123" and "1236")
        name_number_similarity = 0
        if (plant1.name and plant2.name and 
            plant1.name.isdigit() and plant2.name.isdigit()):
            # Calculate similarity based on common prefix
            min_len = min(len(plant1.name), len(plant2.name))
            common_prefix = 0
            for i in range(min_len):
                if plant1.name[i] == plant2.name[i]:
                    common_prefix += 1
                else:
                    break
            if common_prefix > 0:
                name_number_similarity = 0.3 * (common_prefix / min_len)

        # Species similarity (exact match bonus)
        species_bonus = 0.3 if plant1.species == plant2.species else 0
        
        # Name similarity for plants in the same family/genus
        name_similarity = 0
        if plant1.name and plant2.name and not (plant1.name.isdigit() or plant2.name.isdigit()):
            # Split names and check for common terms
            name1_parts = set(plant1.name.lower().split())
            name2_parts = set(plant2.name.lower().split())
            common_terms = name1_parts.intersection(name2_parts)
            if common_terms:
                name_similarity = 0.2 * (len(common_terms) / min(len(name1_parts), len(name2_parts)))

        return text_similarity + species_bonus + max(name_similarity, name_number_similarity)

    def _get_most_popular_plants(self, limit: int = 5) -> List[Plant]:
        """Get most popular plants based on weighted likes and comments."""
        return (
            self.db.query(Plant)
            .join(Favorite, Plant.id == Favorite.plant_id, isouter=True)
            .join(Comment, Plant.id == Comment.plant_id, isouter=True)
            .group_by(Plant.id)
            .order_by(
                (func.count(Favorite.id) * self.LIKE_WEIGHT +
                 func.count(Comment.id) * self.COMMENT_WEIGHT).desc()
            )
            .limit(limit)
            .all()
        )


def get_recommendation_service(db: Session = Depends(get_db)) -> PlantRecommendationService:
    return PlantRecommendationService(db) 
