# 🚀 Google Cloud Deployment Guide

## Przygotowanie

### 1. Załóż konto Google Cloud
1. Wejdź na [console.cloud.google.com](https://console.cloud.google.com)
2. Załóż konto (dostaniesz $300 darmowych kredytów na 90 dni)
3. Utwórz nowy projekt (np. `eve-echoes-calculator`)

### 2. Zainstaluj Google Cloud SDK
1. Pobierz z [cloud.google.com/sdk](https://cloud.google.com/sdk)
2. Zainstaluj i uruchom:
```powershell
gcloud init
```
3. Zaloguj się i wybierz projekt

## Opcja A: Google Cloud Run (Zalecane - Łatwiejsze)

### Krok 1: Włącz Cloud Run API
```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Krok 2: Zbuduj i wyślij obraz Docker
```powershell
# Przejdź do folderu projektu
cd E:\Programy\AI\Eve Echoes Logistic\EVE_Working_Backup

# Ustaw region (np. europe-central2 dla Warszawy)
$REGION = "europe-central2"
$PROJECT_ID = "your-project-id"  # Zastąp swoim ID projektu
$SERVICE_NAME = "eve-echoes-calculator"

# Zbuduj obraz
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
```

### Krok 3: Deploy na Cloud Run
```powershell
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --port 8080 `
  --max-instances 10
```

### Krok 4: Otrzymasz URL aplikacji
Aplikacja będzie dostępna pod adresem typu:
```
https://eve-echoes-calculator-xxxxx-lm.a.run.app
```

## Opcja B: Google App Engine

### Krok 1: Włącz App Engine
```powershell
gcloud app create --region=europe-central2
gcloud services enable appengine.googleapis.com
```

### Krok 2: Deploy aplikacji
```powershell
# Przejdź do folderu projektu
cd E:\Programy\AI\Eve Echoes Logistic\EVE_Working_Backup

# Deploy
gcloud app deploy app.yaml --version v1
```

### Krok 3: Otwórz aplikację
```powershell
gcloud app browse
```

## Opcja C: Google Compute Engine (VM)

### Krok 1: Utwórz VM
```powershell
gcloud compute instances create eve-calculator `
  --zone=europe-central2-a `
  --machine-type=e2-medium `
  --image-family=debian-11 `
  --image-project=debian-cloud `
  --tags=http-server,https-server
```

### Krok 2: SSH do VM
```powershell
gcloud compute ssh eve-calculator --zone=europe-central2-a
```

### Krok 3: Zainstaluj aplikację na VM
```bash
# Na VM (Linux)
sudo apt update
sudo apt install -y python3-pip git

# Klonuj repo
git clone https://github.com/lawrokhpl/Eve-Echoes---PI-Mining-Calculator.git
cd Eve-Echoes---PI-Mining-Calculator

# Zainstaluj zależności
pip3 install -r requirements.txt

# Uruchom aplikację
streamlit run web_app.py --server.port 8080 --server.address 0.0.0.0
```

### Krok 4: Skonfiguruj firewall
```powershell
gcloud compute firewall-rules create allow-streamlit `
  --allow tcp:8080 `
  --source-ranges 0.0.0.0/0 `
  --target-tags http-server
```

## 💰 Koszty

### Cloud Run (Najtańsze)
- **Free Tier**: 2 miliony żądań/miesiąc darmowe
- **Po Free Tier**: ~$0.00002400 za żądanie
- **Szacowany koszt**: $0-10/miesiąc dla małego ruchu

### App Engine
- **Free Tier**: 28 godzin instancji F1 dziennie
- **Po Free Tier**: ~$0.05/godzinę
- **Szacowany koszt**: $0-40/miesiąc

### Compute Engine
- **e2-micro**: Darmowa w ramach Free Tier (1 instancja)
- **e2-medium**: ~$25/miesiąc
- **Szacowany koszt**: $0-25/miesiąc

## 🔧 Zarządzanie i monitorowanie

### Sprawdź logi
```powershell
# Cloud Run
gcloud run services logs read $SERVICE_NAME --region $REGION

# App Engine
gcloud app logs tail

# Compute Engine
gcloud compute ssh eve-calculator --zone=europe-central2-a --command "journalctl -f"
```

### Aktualizacja aplikacji
```powershell
# Cloud Run - przebuduj i wdróż ponownie
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME

# App Engine
gcloud app deploy

# Compute Engine - SSH i git pull
```

### Skalowanie
```powershell
# Cloud Run
gcloud run services update $SERVICE_NAME --max-instances=20

# App Engine (edytuj app.yaml)
automatic_scaling:
  max_instances: 20
```

## 📊 Monitorowanie

1. Wejdź na [console.cloud.google.com](https://console.cloud.google.com)
2. Przejdź do sekcji odpowiedniej dla Twojej usługi:
   - Cloud Run → Services
   - App Engine → Dashboard
   - Compute Engine → VM instances
3. Sprawdzaj:
   - Metryki użycia (CPU, RAM)
   - Logi aplikacji
   - Koszty w Billing

## ⚠️ Ważne uwagi

1. **Bezpieczeństwo**: 
   - Nie commituj pliku `app/secure/users.json` z prawdziwymi hasłami
   - Użyj Google Secret Manager dla wrażliwych danych

2. **Persystencja danych**:
   - Cloud Run i App Engine nie zachowują danych między restartami
   - Rozważ użycie Google Cloud Storage lub Firestore

3. **Domena własna**:
   - Możesz podpiąć własną domenę w Cloud Console
   - Certyfikaty SSL są automatyczne i darmowe

## 🆘 Rozwiązywanie problemów

### Błąd: "Permission denied"
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Błąd: "Quota exceeded"
- Zwiększ limity w Cloud Console → IAM & Admin → Quotas

### Aplikacja nie działa
- Sprawdź logi
- Upewnij się, że port 8080 jest używany
- Sprawdź requirements.txt

## 📝 Checklist przed deploymentem

- [ ] Usuń pliki .bak, .last, __pycache__
- [ ] Sprawdź requirements.txt
- [ ] Przetestuj lokalnie
- [ ] Ustaw odpowiednie limity pamięci (min. 2GB)
- [ ] Skonfiguruj monitoring
- [ ] Ustaw budżet w Billing

---

## 🎉 Gratulacje!

Twoja aplikacja EVE Echoes Calculator jest teraz dostępna w chmurze Google!

**Pamiętaj o donacji!** 💰  
Jeśli aplikacja Ci pomaga, wesprzyj rozwój wysyłając ISK do **lawrokhPL** w EVE Echoes!
