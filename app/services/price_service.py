import pandas as pd
import json
import os
import re
from datetime import datetime
from typing import Dict, List
from app.models.price_model import ResourcePrice

class PriceService:
    def __init__(self, price_file_path: str = "data/prices.json"):
        self.price_file_path = price_file_path
        self.prices = {}
        self.load_prices()
        
    def load_prices(self) -> None:
        """Load prices from JSON file if it exists"""
        if os.path.exists(self.price_file_path):
            try:
                with open(self.price_file_path, 'r') as f:
                    self.prices = json.load(f)
            except json.JSONDecodeError:
                self.prices = {}
        
    def save_prices(self) -> None:
        """Save current prices to JSON file"""
        os.makedirs(os.path.dirname(self.price_file_path), exist_ok=True)
        with open(self.price_file_path, 'w') as f:
            json.dump(self.prices, f, indent=4)
            
    def get_price(self, resource_name: str) -> float:
        """Get price for a specific resource"""
        return self.prices.get(resource_name, 0.0)
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get all resource prices"""
        return self.prices
    
    def update_price(self, resource_name: str, price: float) -> None:
        """Update price for a specific resource"""
        self.prices[resource_name] = price
    
    def update_multiple_prices(self, price_dict: Dict[str, float]) -> None:
        """Update prices for multiple resources at once"""
        self.prices.update(price_dict)
    
    def import_prices_from_csv(self, file_path: str) -> None:
        """Import prices from a CSV file"""
        import pandas as pd
        try:
            df = pd.read_csv(file_path)
            if 'resource' in df.columns and 'price' in df.columns:
                for _, row in df.iterrows():
                    self.prices[row['resource']] = float(row['price'])
                self.save_prices()
        except Exception as e:
            print(f"Error importing prices: {e}") 

    def get_price_history(self, username):
        """
        Scans the user's price_imports directory, loads all CSVs,
        and returns a consolidated DataFrame with historical price data.
        
        It assumes filenames contain dates in YYYY-MM-DD format.
        It assumes CSVs have columns: 'resource', 'buy', 'sell', 'average'.
        """
        imports_dir = os.path.join("data", "user_data", username, "price_imports")
        if not os.path.exists(imports_dir):
            return pd.DataFrame()

        all_price_data = []
        date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")

        for filename in os.listdir(imports_dir):
            if filename.endswith(".csv"):
                match = date_pattern.search(filename)
                if not match:
                    continue # Skip files without a valid date in the name

                price_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                file_path = os.path.join(imports_dir, filename)
                
                try:
                    df = pd.read_csv(file_path)
                    # Check for required columns
                    if all(col in df.columns for col in ['resource', 'buy', 'sell', 'average']):
                        df['date'] = price_date
                        all_price_data.append(df)
                except Exception:
                    # Silently ignore files that can't be parsed
                    continue
        
        if not all_price_data:
            return pd.DataFrame()

        history_df = pd.concat(all_price_data, ignore_index=True)
        history_df['date'] = pd.to_datetime(history_df['date'])
        return history_df.sort_values(by="date") 