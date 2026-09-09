from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import cv2
import numpy as np
from datetime import datetime


# ============================================================
# 1. CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AGRI-SHIELD AI",
    description="AI-powered Smart Farming Assistant Backend",
    version="1.0.0"
)


# ============================================================
# 2. CORS
# Allows frontend/mobile application to communicate with backend
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. BASIC CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# 4. HOME / HEALTH CHECK
# ============================================================

@app.get("/")
def home():

    return {
        "project": "AGRI-SHIELD AI",
        "message": "Smart Farming Assistant Backend is running",
        "status": "active",
        "time": datetime.now().isoformat()
    }


# ============================================================
# 5. IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_bytes):

    # Convert bytes into numpy array
    image_array = np.frombuffer(image_bytes, np.uint8)

    # Decode image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image")

    # Resize image for AI model
    image = cv2.resize(image, (224, 224))

    # Convert BGR → RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Normalize pixel values
    image = image.astype(np.float32) / 255.0

    # Add batch dimension
    image = np.expand_dims(image, axis=0)

    return image


# ============================================================
# 6. AI CROP DISEASE PREDICTION
# ============================================================

def predict_crop_health(image):

    """
    Replace this function with your trained TensorFlow model.

    Example:
        model.predict(image)

    For now, this returns a sample prediction so that
    the backend can be tested before the ML model is ready.
    """

    prediction = {
        "status": "Disease detected",
        "disease": "Leaf Disease",
        "confidence": 0.87,
        "severity": "Medium"
    }

    return prediction


# ============================================================
# 7. WEATHER DATA
# ============================================================

def get_weather(latitude, longitude):

    """
    Later connect this function to a real Weather API.

    Example weather parameters:
    - Temperature
    - Humidity
    - Rainfall
    - Wind speed
    """

    # Sample weather data for testing
    weather = {
        "temperature": 32,
        "humidity": 72,
        "rainfall": 5,
        "wind_speed": 12,
        "forecast": "Partly cloudy"
    }

    return weather


# ============================================================
# 8. RISK ANALYSIS
# ============================================================

def calculate_risk(disease_result, weather):

    risks = []

    # Disease risk
    if disease_result["confidence"] >= 0.80:
        risks.append("High crop disease risk")

    elif disease_result["confidence"] >= 0.60:
        risks.append("Medium crop disease risk")

    # Heat risk
    if weather["temperature"] >= 38:
        risks.append("Heat wave risk")

    # High humidity can increase disease risk
    if weather["humidity"] >= 80:
        risks.append("High humidity risk")

    # Rainfall risk
    if weather["rainfall"] >= 50:
        risks.append("Heavy rainfall / flood risk")

    # Irrigation / dry condition
    if weather["rainfall"] < 10 and weather["temperature"] >= 30:
        risks.append("Water stress risk")

    if len(risks) == 0:
        overall_risk = "Low"

    elif len(risks) <= 2:
        overall_risk = "Medium"

    else:
        overall_risk = "High"

    return {
        "overall_risk": overall_risk,
        "identified_risks": risks
    }


# ============================================================
# 9. IRRIGATION ANALYSIS
# ============================================================

def irrigation_recommendation(weather):

    temperature = weather["temperature"]
    rainfall = weather["rainfall"]

    if rainfall >= 20:
        return {
            "status": "No immediate irrigation required",
            "reason": "Sufficient rainfall expected"
        }

    elif temperature >= 35 and rainfall < 10:
        return {
            "status": "Irrigation recommended",
            "reason": "High temperature and low rainfall"
        }

    else:
        return {
            "status": "Monitor soil moisture",
            "reason": "Moderate weather conditions"
        }


# ============================================================
# 10. FARMER RECOMMENDATION
# ============================================================

def generate_recommendation(disease_result, risk_result, irrigation):

    recommendations = []

    # Disease recommendation
    if disease_result["status"] == "Disease detected":

        recommendations.append(
            "Inspect affected plants and separate severely affected leaves."
        )

        recommendations.append(
            "Monitor nearby plants for similar symptoms."
        )

    # Risk recommendation
    if risk_result["overall_risk"] == "High":

        recommendations.append(
            "Take immediate preventive action and monitor the field frequently."
        )

    elif risk_result["overall_risk"] == "Medium":

        recommendations.append(
            "Increase field monitoring and take preventive measures."
        )

    # Irrigation recommendation
    recommendations.append(
        irrigation["status"]
    )

    return recommendations


# ============================================================
# 11. MAIN ANALYSIS API
# ============================================================

@app.post("/analyze")
async def analyze_crop(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    crop_name: str = Form("Unknown")
):

    # --------------------------------------------------------
    # Step 1: Validate image
    # --------------------------------------------------------

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/jpg"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed."
        )


    # --------------------------------------------------------
    # Step 2: Read image
    # --------------------------------------------------------

    image_bytes = await file.read()

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty image received."
        )


    # --------------------------------------------------------
    # Step 3: Preprocess image
    # --------------------------------------------------------

    try:

        processed_image = preprocess_image(image_bytes)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Unable to process image."
        )


    # --------------------------------------------------------
    # Step 4: AI prediction
    # --------------------------------------------------------

    disease_result = predict_crop_health(processed_image)


    # --------------------------------------------------------
    # Step 5: Get weather
    # --------------------------------------------------------

    weather = get_weather(
        latitude,
        longitude
    )


    # --------------------------------------------------------
    # Step 6: Calculate agricultural risks
    # --------------------------------------------------------

    risk_result = calculate_risk(
        disease_result,
        weather
    )


    # --------------------------------------------------------
    # Step 7: Irrigation recommendation
    # --------------------------------------------------------

    irrigation = irrigation_recommendation(
        weather
    )


    # --------------------------------------------------------
    # Step 8: Generate farmer recommendation
    # --------------------------------------------------------

    recommendations = generate_recommendation(
        disease_result,
        risk_result,
        irrigation
    )


    # --------------------------------------------------------
    # Step 9: Return complete response
    # --------------------------------------------------------

    return {

        "success": True,

        "crop": {
            "name": crop_name
        },

        "location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "ai_analysis": disease_result,

        "weather": weather,

        "risk_analysis": risk_result,

        "irrigation": irrigation,

        "recommendations": recommendations,

        "analyzed_at": datetime.now().isoformat()
    }


# ============================================================
# 12. WEATHER API ENDPOINT
# ============================================================

@app.get("/weather")
def weather(
    latitude: float,
    longitude: float
):

    weather_data = get_weather(
        latitude,
        longitude
    )

    return {
        "success": True,
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "weather": weather_data
    }


# ============================================================
# 13. RISK API ENDPOINT
# ============================================================

@app.post("/risk")
def risk_analysis(
    temperature: float,
    humidity: float,
    rainfall: float,
    disease_confidence: float
):

    disease_result = {
        "confidence": disease_confidence
    }

    weather = {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall
    }

    result = calculate_risk(
        disease_result,
        weather
    )

    return {
        "success": True,
        "risk_analysis": result
    }
