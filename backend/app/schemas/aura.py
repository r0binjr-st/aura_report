from pydantic import BaseModel, Field


STAT_NAMES = [
    "арка злодея",
    "темный друн",
    "секс маньяк",
    "М М",
    "потапыч R.I.P",
    "артем коршунов (джокер)",
    "саша епифановский",
    "сигма синдром",
]

MENTAL_STATES = [
    "возвращаюсь к бывшей 3 раз",
    "дофаминовое голодание",
    "воздержание от женщин",
    "урод",
    "марк годин",
]

LOCATIONS = [
    "путилково (роковой поворот)",
    "путилково (упавший шкаф)",
    "пойма (воспоминания о прошлом)",
    "химки (потерял телефон)",
]

TRAIT_NAMES = [
    "night_energy",
    "chaos",
    "nostalgia",
    "brainrot",
    "self_irony",
    "toxicity",
    "sigma",
    "romantic_damage",
    "terminally_online",
    "local_legend",
    "grass_touching_probability",
    "pakhom_energy",
    "joker_energy",
    "judy_hopps_energy",
    "absurdity",
    "confidence",
    "self_deprecation",
    "cursed_energy",
    "party_energy",
    "impulsiveness",
    "emotional_suppression",
    "gym_energy",
    "self_improvement",
    "sadness",
]


class Observations(BaseModel):
    image: str
    nickname: str
    music: str
    text: str


class AuraReport(BaseModel):
    stats: dict[str, int]
    mental_state: str
    location: str
    archetype: str
    diagnosis: str
    explanation: str
    observations: Observations
    analysis_source: str = "llm"
    hidden_traits: dict[str, float] = Field(default_factory=dict)
