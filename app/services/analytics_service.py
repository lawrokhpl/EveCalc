from typing import Dict, List, Tuple
from app.models.data_model import Planet, PlanetaryResource

class AnalyticsService:
    def __init__(self, data_service, price_service):
        self.data_service = data_service
        self.price_service = price_service
        
    def get_most_profitable_planets(self, top_n: int = 10) -> List[Tuple[Planet, float]]:
        """Get the most profitable planets based on current prices"""
        planets = self.data_service.get_all_planets()
        prices = self.price_service.get_all_prices()
        
        # Calculate value for each planet
        planet_values = [(planet, planet.total_value(prices)) for planet in planets]
        
        # Sort by value descending
        planet_values.sort(key=lambda x: x[1], reverse=True)
        
        return planet_values[:top_n]
    
    def get_most_profitable_systems(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get the most profitable systems based on current prices"""
        planets = self.data_service.get_all_planets()
        prices = self.price_service.get_all_prices()
        
        # Group planets by system
        systems = {}
        for planet in planets:
            if planet.system not in systems:
                systems[planet.system] = 0
            systems[planet.system] += planet.total_value(prices)
        
        # Convert to list and sort
        system_values = [(system, value) for system, value in systems.items()]
        system_values.sort(key=lambda x: x[1], reverse=True)
        
        return system_values[:top_n]
    
    def get_resource_distribution(self, resource_name: str) -> Dict[str, int]:
        """Get distribution of a specific resource across regions"""
        planets = self.data_service.get_all_planets()
        distribution = {}
        
        for planet in planets:
            for resource in planet.resources:
                if resource.resource == resource_name:
                    if planet.region not in distribution:
                        distribution[planet.region] = 0
                    distribution[planet.region] += 1
        
        return distribution
    
    def get_optimal_mining_route(self, starting_system: str, max_jumps: int = 5) -> List[Tuple[Planet, float]]:
        """Get optimal mining route from a starting system"""
        # This would require jump distance data which isn't in the dataset
        # For now, return nearby profitable planets
        planets = self.data_service.get_all_planets()
        prices = self.price_service.get_all_prices()
        
        # Filter planets in the same constellation as starting system
        starting_constellation = None
        for planet in planets:
            if planet.system == starting_system:
                starting_constellation = planet.constellation
                break
        
        if not starting_constellation:
            return []
        
        # Get planets in the same constellation
        nearby_planets = [p for p in planets if p.constellation == starting_constellation]
        
        # Calculate value and sort
        planet_values = [(planet, planet.total_value(prices)) for planet in nearby_planets]
        planet_values.sort(key=lambda x: x[1], reverse=True)
        
        return planet_values 