# 🌱 AGRI-SHIELD AI

## AI-Powered Smart Farming Assistant

AGRI-SHIELD AI is a field-deployable AI-powered smart farming assistant designed to help farmers detect crop diseases, pests, nutrient deficiencies, and irrigation needs at an early stage.

It combines crop image analysis with weather intelligence to provide early risk detection, smart recommendations, and alerts for agricultural risks.

---

## 🚜 Problem Statement

Farmers often face crop diseases, pest attacks, nutrient deficiencies, water shortages, and climate-related risks such as droughts, floods, heat waves, and other agricultural threats.

AGRI-SHIELD AI aims to help farmers make faster and better farming decisions using artificial intelligence, computer vision, and weather data.

---

## 💡 Proposed Solution

The system takes crop/leaf images and weather information and processes them using AI to identify crop problems, assess risks, and provide useful recommendations.

### Core Flow

Crop Image + Weather Data
        ↓
Image Processing
        ↓
AI Analysis
        ↓
Disease / Pest Detection
        ↓
Risk Assessment
        ↓
Smart Recommendation
        ↓
Alert to Farmer

---

## ✨ Key Features

- Early crop disease detection
- Pest detection
- Nutrient deficiency detection
- Irrigation recommendations
- Weather-based risk monitoring
- Drought risk alerts
- Flood risk alerts
- Heat-wave risk alerts
- AI-based crop analysis
- Farmer-friendly interface
- Early and actionable recommendations
- Low-cost deployment approach
- Offline support for low-connectivity areas

---

## 🛠️ Technologies Used

### AI / Machine Learning
- Python
- TensorFlow
- Transfer Learning
- PlantVillage Dataset

### Image Processing
- OpenCV
- NumPy

### Backend
- Flask / FastAPI

### Weather
- Weather API
- Real-time weather data

### Frontend
- HTML
- CSS
- JavaScript

---

# 👥 TEAM ROLES

| Person | Role | Main Responsibility | Folder |
|---|---|---|---|
| Person 1 | Team Lead & Integration | Project coordination, GitHub management, module integration, testing and final demo | Entire Project |
| Person 2 | AI/ML Developer | Dataset preparation, model training, disease detection and model testing | `ml-model/` |
| Person 3 | Image Processing Developer | Image preprocessing, resizing, RGB conversion, normalization and image quality checks | `image-processing/` |
| Person 4 | Backend Developer | API development and connecting frontend, image processing, AI model and weather modules | `Backend/` |
| Person 5 | Weather & Risk Developer | Weather API, weather analysis, irrigation recommendations and risk alerts | `weather/` |
| Person 6 | Frontend Developer | User interface, image upload, prediction display, alerts and recommendations | `Frontend/` |

---

# 📁 PROJECT STRUCTURE

```text
agri-shield-ai/
│
├── Backend/
│   └── main.py
│
├── Frontend/
│   └── index.html
│   └── upload.html
│   └── result.html
│
├── image-processing/
│   └── process_image.py
│
├── ml-model/
│   └── model.py
│
├── weather/
│   └── weather.py
│
└── README.md
