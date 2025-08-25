import sys
import os
import subprocess

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Uruchamia aplikację webową EVE Echoes Planetary Optimizer"""
    print("Uruchamiam EVE Echoes Planetary Optimizer...")
    
    # Uruchom aplikację Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "web_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Błąd uruchamiania aplikacji: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nAplikacja została zatrzymana przez użytkownika.")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 