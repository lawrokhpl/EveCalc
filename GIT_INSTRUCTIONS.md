# 📦 Instrukcja przesłania na GitHub

## ✅ Problem z dużymi plikami został rozwiązany!

Usunięte zostały:
- `eve_planets.json` (52 MB) - aplikacja używa `eve_planets.parquet` (1.3 MB)
- `system_planet.json` - niepotrzebny plik
- Folder `.git` - jeśli istniał z poprzedniej próby

## Kroki do wykonania w PowerShell:

### 1. Przejdź do folderu projektu
```powershell
cd E:\Programy\AI\Eve Echoes Logistic\EVE_Working_Backup
```

### 2. Zainicjalizuj nowe repozytorium Git
```powershell
git init
```

### 3. Dodaj wszystkie pliki
```powershell
git add .
```

### 4. Zrób pierwszy commit
```powershell
git commit -m "Initial commit - EVE Echoes Planetary Mining Optimizer"
```

### 5. Połącz z repozytorium GitHub
Zastąp `yourusername` swoją nazwą użytkownika GitHub i `your-repo-name` nazwą repozytorium:
```powershell
git remote add origin https://github.com/yourusername/your-repo-name.git
```

### 6. Wyślij na GitHub
```powershell
git branch -M main
git push -u origin main
```

## Jeśli wystąpi błąd z autentykacją:

### Opcja A: Personal Access Token (zalecane)
1. Wejdź na GitHub → Settings → Developer settings → Personal access tokens
2. Kliknij "Generate new token (classic)"
3. Nadaj nazwę, zaznacz `repo` scope
4. Skopiuj token
5. Przy push użyj tokena jako hasła

### Opcja B: GitHub Desktop
1. Pobierz [GitHub Desktop](https://desktop.github.com/)
2. Zaloguj się
3. Dodaj folder jako repozytorium
4. Commit i push przez GUI

## Sprawdzenie przed wysłaniem:

```powershell
# Sprawdź rozmiar największych plików (powinny być < 25 MB)
Get-ChildItem -Recurse -File | Sort-Object Length -Descending | Select-Object -First 5 Name, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB, 2)}}
```

## Po wysłaniu na GitHub:

1. Przejdź na [share.streamlit.io](https://share.streamlit.io)
2. Zaloguj się przez GitHub
3. Kliknij "New app"
4. Wybierz swoje repozytorium
5. Main file: `web_app.py`
6. Deploy!

---

**Wszystkie pliki są teraz poniżej limitu 25 MB i gotowe do przesłania!** 🎉
