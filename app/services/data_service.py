import pandas as pd
import json
import os
from typing import Dict, List, Optional
from app.models.data_model import Planet, PlanetaryResource, PlanetType, Richness

class DataService:
    def __init__(self, data_path: str, mining_units_path: str = "data/mining_units.json"):
        self.data_path = data_path
        self.mining_units_path = mining_units_path
        self.df = None
        self.planets = {}
        self.resources_set = set()
        
    def load_data(self) -> None:
        """Load data from Parquet or Excel file and merge with mining units"""
        parquet_path = self.data_path.replace('.xlsx', '.parquet')
        
        if os.path.exists(parquet_path):
            self.df = pd.read_parquet(parquet_path, engine='pyarrow')
        elif os.path.exists(self.data_path):
            self.df = pd.read_excel(self.data_path, engine='openpyxl')
        else:
            raise FileNotFoundError(f"Data file not found at {self.data_path} or {parquet_path}")

        mining_units = self._load_mining_units()
        self._process_data(mining_units)
        
    def _load_mining_units(self) -> Dict[str, int]:
        """Load mining units. Uses SQL backend if enabled, otherwise JSON file."""
        from app.config import settings
        if settings.DATA_BACKEND == "sql":
            from app.services.mining_units_service_sql import SQLMiningUnitsService
            return SQLMiningUnitsService().load_units_map()
        if os.path.exists(self.mining_units_path):
            try:
                with open(self.mining_units_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_mining_units(self) -> None:
        """Save mining units. Uses SQL backend if enabled, otherwise JSON file."""
        mining_units = {}
        for planet in self.planets.values():
            for resource in planet.resources:
                if resource.mining_units > 0:
                    key = f"{resource.planet_id}_{resource.resource}"
                    mining_units[key] = resource.mining_units

        from app.config import settings
        if settings.DATA_BACKEND == "sql":
            from app.services.mining_units_service_sql import SQLMiningUnitsService
            SQLMiningUnitsService().save_units_map(mining_units)
            return
        os.makedirs(os.path.dirname(self.mining_units_path), exist_ok=True)
        with open(self.mining_units_path, 'w') as f:
            json.dump(mining_units, f, indent=4)

    def _process_data(self, mining_units: Dict[str, int]) -> None:
        """Process the dataframe into Planet and PlanetaryResource objects"""
        for _, row in self.df.iterrows():
            planet_id = int(row['Planet ID'])
            resource = row['Resource']
            
            # Add to resource set
            self.resources_set.add(resource)
            
            key = f"{planet_id}_{resource}"
            num_units = mining_units.get(key, 0)

            # Create planetary resource
            planetary_resource = PlanetaryResource(
                planet_id=planet_id,
                region=row['Region'],
                constellation=row['Constellation'],
                system=row['System'],
                planet_name=row['Planet Name'],
                planet_type=PlanetType(row['Planet Type']),
                resource=resource,
                richness=Richness(row['Richness']),
                output=float(row['Output']),
                mining_units=num_units
            )
            
            # Add to planet or create new planet
            if planet_id not in self.planets:
                self.planets[planet_id] = Planet(
                    planet_id=planet_id,
                    region=row['Region'],
                    constellation=row['Constellation'],
                    system=row['System'],
                    name=row['Planet Name'],
                    planet_type=PlanetType(row['Planet Type'])
                )
            
            self.planets[planet_id].add_resource(planetary_resource)
    
    def get_all_planets(self) -> List[Planet]:
        """Return list of all planets"""
        return list(self.planets.values())
    
    def get_all_resources(self) -> List[str]:
        """Returns a list of all unique resource names."""
        if self.df is not None:
            return self.df['Resource'].unique().tolist()
        return []

    def get_active_mining_systems(self):
        """Returns a list of systems with active mining units."""
        if self.df is None or 'Mining Units' not in self.df.columns:
            return []
        
        active_systems_df = self.df[self.df['Mining Units'] > 0]
        return active_systems_df['System'].unique().tolist()

    def update_dataframe_mining_units(self):
        """
        Refreshes the 'Mining Units' column in the internal DataFrame
        based on the current values in the planet objects. This is crucial
        for other parts of the app to see changes without a full cache clear.
        """
        if self.df is None or not hasattr(self, '_all_planets') or not self._all_planets:
            return
        
        mining_units_map = {
            f"{resource.planet_id}_{resource.resource}": resource.mining_units
            for planet in self.get_all_planets() for resource in planet.resources
        }
        
        self.df['Mining Units'] = self.df['id'].map(mining_units_map).fillna(0)

    def update_mining_units(self, resource_id, new_units):
        """Updates the mining units for a specific resource."""
        if self.df is not None:
            pass # Placeholder for the new method
    
    def get_regions(self) -> List[str]:
        """Get list of all regions"""
        return sorted(self.df['Region'].unique().tolist())
    
    def get_constellations(self, regions: Optional[List[str]] = None) -> List[str]:
        """Get list of constellations, optionally filtered by a list of regions"""
        if regions:
            return sorted(self.df[self.df['Region'].isin(regions)]['Constellation'].unique().tolist())
        return sorted(self.df['Constellation'].unique().tolist())
    
    def get_systems(self, constellations: Optional[List[str]] = None) -> List[str]:
        """Get list of systems, optionally filtered by a list of constellations"""
        if constellations:
            return sorted(self.df[self.df['Constellation'].isin(constellations)]['System'].unique().tolist())
        return sorted(self.df['System'].unique().tolist()) 