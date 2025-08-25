import json
import os
import hashlib
import shutil

class UserService:
    def __init__(self, user_file_path="app/secure/users.json"):
        self.user_file_path = user_file_path
        self.users = self._load_users()

    def _load_users(self):
        if os.path.exists(self.user_file_path):
            try:
                with open(self.user_file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_users(self):
        os.makedirs(os.path.dirname(self.user_file_path), exist_ok=True)
        with open(self.user_file_path, 'w') as f:
            json.dump(self.users, f, indent=4)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register_user(self, username, password):
        if username in self.users:
            return False, "Username already exists."
        
        if not username or not password:
            return False, "Username and password cannot be empty."

        self.users[username] = self._hash_password(password)
        self._save_users()
        
        # Create user-specific directories and default files
        user_dir = os.path.join("data", "user_data", username)
        os.makedirs(user_dir, exist_ok=True)

        user_data_dir = os.path.join("data", "user_data", username, "price_imports")
        os.makedirs(user_data_dir, exist_ok=True)

        # Create default prices.json and mining_units.json if they don't exist
        default_prices_path = os.path.join("data", "prices.json")
        user_prices_path = os.path.join(user_dir, "prices.json")
        if not os.path.exists(user_prices_path) and os.path.exists(default_prices_path):
            shutil.copy(default_prices_path, user_prices_path)
        
        return True, "User registered successfully."

    def verify_user(self, username, password):
        """Verifies a user's credentials, handling both old and new password storage formats."""
        if username not in self.users:
            return False
        
        user_data = self.users[username]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check for new format (dictionary)
        if isinstance(user_data, dict):
            return user_data.get("password") == hashed_password
        # Check for old format (string)
        elif isinstance(user_data, str):
            # This is the old format. If password matches, migrate to the new format.
            if user_data == hashed_password:
                self.users[username] = {"password": hashed_password}
                self._save_users()
                return True
            return False
            
        return False

    def _get_preferences_path(self, username):
        """Returns the path to the user's preferences file."""
        return os.path.join("data", "user_data", username, "preferences.json")

    def load_user_preferences(self, username):
        """Loads user preferences from a JSON file."""
        prefs_path = self._get_preferences_path(username)
        if os.path.exists(prefs_path):
            with open(prefs_path, 'r') as f:
                return json.load(f)
        return {} # Return empty dict if no preferences saved yet

    def save_user_preferences(self, username, preferences):
        """Saves user preferences to a JSON file."""
        prefs_path = self._get_preferences_path(username)
        with open(prefs_path, 'w') as f:
            json.dump(preferences, f, indent=4) 