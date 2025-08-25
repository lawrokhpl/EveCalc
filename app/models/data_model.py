from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

class PlanetType(Enum):
    TEMPERATE = "Temperate"
    BARREN = "Barren"
    OCEANIC = "Oceanic"
    GAS = "Gas"
    ICE = "Ice"
    LAVA = "Lava"
    STORM = "Storm"
    PLASMA = "Plasma"

class Richness(Enum):
    POOR = "Poor"
    MEDIUM = "Medium"
    RICH = "Rich"
    PERFECT = "Perfect"

@dataclass
class Resource:
    name: str
    current_price: float = 0.0
    
@dataclass
class PlanetaryResource:
    planet_id: int
    region: str
    constellation: str
    system: str
    planet_name: str
    planet_type: PlanetType
    resource: str
    richness: Richness
    output: float
    mining_units: int = 0
    
    def calculate_value_per_unit(self, price_dict: Dict[str, float]) -> float:
        """Calculate the hourly value of a single unit of this resource."""
        if self.resource not in price_dict:
            return 0.0
        return self.output * price_dict[self.resource]

    def calculate_total_value(self, price_dict: Dict[str, float]) -> float:
        """Calculate the total hourly value based on assigned mining units."""
        return self.calculate_value_per_unit(price_dict) * self.mining_units

@dataclass
class Planet:
    planet_id: int
    region: str
    constellation: str
    system: str
    name: str
    planet_type: PlanetType
    resources: List[PlanetaryResource] = None
    
    def __post_init__(self):
        if self.resources is None:
            self.resources = []
            
    def add_resource(self, resource: PlanetaryResource):
        self.resources.append(resource)
        
    def total_value(self, price_dict: Dict[str, float]) -> float:
        """Calculate total hourly value of all resources on this planet"""
        return sum(r.calculate_total_value(price_dict) for r in self.resources) 