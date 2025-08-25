# 🚀 Instrukcja publikacji na Streamlit Community Cloud

## Wymagania wstępne

1. **Konto GitHub** - Załóż darmowe konto na [github.com](https://github.com)
2. **Konto Streamlit** - Załóż konto na [share.streamlit.io](https://share.streamlit.io)

## Krok 1: Przygotowanie repozytorium GitHub

### 1.1 Utwórz nowe repozytorium na GitHub

1. Zaloguj się na GitHub
2. Kliknij **"New repository"** (zielony przycisk)
3. Nazwij repozytorium np. `eve-echoes-optimizer`
4. Ustaw jako **Public** (wymagane dla darmowego hostingu)
5. NIE inicjalizuj z README (mamy już własny)
6. Kliknij **"Create repository"**

### 1.2 Wyślij kod na GitHub

W PowerShell, w folderze `EVE_Working_Backup`:

```powershell
# Inicjalizacja git
git init

# Dodaj wszystkie pliki
git add .

# Pierwszy commit
git commit -m "Initial commit - EVE Echoes Planetary Mining Optimizer"

# Dodaj remote (zastąp 'yourusername' swoją nazwą użytkownika GitHub)
git remote add origin https://github.com/yourusername/eve-echoes-optimizer.git

# Wyślij na GitHub
git branch -M main
git push -u origin main
```

## Krok 2: Deployment na Streamlit Community Cloud

### 2.1 Połącz konta

1. Wejdź na [share.streamlit.io](https://share.streamlit.io)
2. Zaloguj się używając konta GitHub (przycisk "Continue with GitHub")
3. Autoryzuj Streamlit do dostępu do Twoich repozytoriów

### 2.2 Utwórz nową aplikację

1. Kliknij **"New app"**
2. Wypełnij formularz:
   - **Repository**: Wybierz `yourusername/eve-echoes-optimizer`
   - **Branch**: `main`
   - **Main file path**: `web_app.py`
3. Kliknij **"Deploy"**

### 2.3 Poczekaj na deployment

- Proces zajmuje zazwyczaj 2-5 minut
- Możesz śledzić logi w czasie rzeczywistym
- Po zakończeniu otrzymasz link do aplikacji: `https://[nazwa-aplikacji].streamlit.app`

## Krok 3: Konfiguracja aplikacji (opcjonalne)

### 3.1 Ustawienia zaawansowane

W panelu Streamlit Cloud możesz:
- Zmienić URL aplikacji
- Ustawić zmienne środowiskowe
- Skonfigurować secrets (dla wrażliwych danych)

### 3.2 Secrets Management

Jeśli masz wrażliwe dane (np. klucze API):

1. W panelu aplikacji kliknij **"Settings"**
2. Wybierz **"Secrets"**
3. Dodaj secrets w formacie TOML:

```toml
[passwords]
admin = "your_secure_password"

[api_keys]
some_api = "your_api_key"
```

## Krok 4: Aktualizacje aplikacji

### Automatyczne aktualizacje

Każdy push do brancha `main` automatycznie zaktualizuje aplikację:

```powershell
# Po wprowadzeniu zmian
git add .
git commit -m "Opis zmian"
git push
```

### Ręczny restart

W panelu Streamlit Cloud możesz:
- Kliknąć **"Reboot app"** aby zrestartować
- Sprawdzić logi w zakładce **"Logs"**

## 📝 Ważne uwagi

### Limity darmowego planu

- **Zasoby**: 1 GB RAM
- **Storage**: Ograniczone
- **Uptime**: Aplikacja może być uśpiona po okresie nieaktywności
- **Prywatne repo**: Niedostępne w darmowym planie

### Optymalizacja

1. **Dane**: Przechowuj duże pliki danych w repo (do 100MB) lub używaj zewnętrznego storage
2. **Cache**: Używaj `@st.cache_data` dla ciężkich obliczeń
3. **Requirements**: Minimalizuj zależności w `requirements.txt`

### Rozwiązywanie problemów

**Aplikacja nie startuje:**
- Sprawdź logi w panelu Streamlit Cloud
- Upewnij się, że `requirements.txt` jest poprawny
- Sprawdź czy wszystkie pliki są w repo

**Błędy importu:**
- Upewnij się, że struktura folderów jest zachowana
- Sprawdź ścieżki w importach

**Aplikacja jest wolna:**
- Użyj cache'owania (`@st.cache_data`)
- Zoptymalizuj ładowanie danych
- Rozważ upgrade do płatnego planu

## 🎉 Gotowe!

Twoja aplikacja jest teraz dostępna publicznie pod adresem:
`https://[nazwa-aplikacji].streamlit.app`

Podziel się linkiem z społecznością EVE Echoes!

## Wsparcie

W razie problemów:
1. Sprawdź [dokumentację Streamlit](https://docs.streamlit.io)
2. Odwiedź [forum Streamlit](https://discuss.streamlit.io)
3. Zgłoś issue na GitHub

---

**Pamiętaj o donacji!** 💰  
Jeśli aplikacja Ci pomaga, wesprzyj rozwój wysyłając ISK do **lawrokhPL** w EVE Echoes!
