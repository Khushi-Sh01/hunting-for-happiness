"""Contracts and deterministic game rules. No model has database authority."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

CATALOG = {
    "leaf_shapes": {"title": "Three shapes, one small adventure", "task": "From a familiar outdoor path or seated outdoor spot, notice three leaf shapes. Observe without picking leaves. Describe one difference when you return."},
    "sound_map": {"title": "Listen beyond the feed", "task": "At a familiar outdoor spot, pause and notice three sounds. Keep your eyes open and stay aware of your surroundings. Remember one sound to describe later."},
    "color_hunt": {"title": "Find a color you almost missed", "task": "On a familiar outdoor path or from a seated outdoor spot, notice three colors in plants or the sky. Describe one detail you would usually miss."},
    "mindful_walk": {"title": "A walk with no destination", "task": "Walk or move at your own comfortable pace on a familiar outdoor route. Pause somewhere safe and notice one texture, one sound, and one color. Describe what you noticed later."},
}

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class QuestRequest(StrictModel):
    mood: Literal["restless", "low_energy", "overwhelmed", "curious"]
    minutes: Literal[5, 10, 15] = 5
    mobility: Literal["seated", "walking"] = "walking"

class MissionChoice(StrictModel):
    mission_key: Literal["leaf_shapes", "sound_map", "color_hunt", "mindful_walk"]

class Evaluation(StrictModel):
    completed: bool
    relevance: int = Field(ge=0, le=2)
    observation: int = Field(ge=0, le=2)
    reflection: int = Field(ge=0, le=2)
    feedback: str = Field(min_length=1, max_length=320)

class ReflectionRequest(StrictModel):
    reflection: str = Field(min_length=1, max_length=2000)
    @field_validator("reflection")
    @classmethod
    def nonempty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Please describe one thing you noticed.")
        return value

def xp_for(evaluation: Evaluation) -> int:
    # Progress reflects engagement, not a diagnosis or verified physical proof.
    return 20 + 5 * (evaluation.relevance + evaluation.observation + evaluation.reflection) if evaluation.completed else 0

def level_for(xp: int) -> int:
    return 1 + xp // 100

def public_player(doc):
    return {key: doc[key] for key in ("xp", "level", "active", "completed")}

