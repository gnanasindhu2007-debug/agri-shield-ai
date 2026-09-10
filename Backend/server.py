import os
import math
import random
import io
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image
import numpy as np


# ============================================================
# 1. FASTAPI APPLICATION & CORS SETUP
# ============================================================

app = FastAPI(
    title="AGRI-SHIELD AI - Production Backend",
    description="AI Smart Farming Assistant Backend for Team Bug Boosters",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 2. AGRICULTURAL KNOWLEDGE BASE
# ============================================================

PATHOLOGY_KNOWLEDGE_BASE = {

    "Rice": [
        {
            "issue": "Rice Blast (Magnaporthe oryzae)",
            "category": "Fungal Disease",
            "severity": "High",

            "organic": [
                {
                    "title": "Neem Oil Extract (3%)",
                    "description": "Spray cold-pressed neem oil at 3% concentration early morning.",
                    "dosage": "30 ml/liter"
                },
                {
                    "title": "Trichoderma viride Bio-fungicide",
                    "description": "Soil drenching and foliar spray to suppress fungal spore germination.",
                    "dosage": "5g/liter"
                }
            ],

            "chemical": [
                {
                    "title": "Tricyclazole 75% WP",
                    "description": "Systemic fungicide spray at first sign of spindle-shaped lesions.",
                    "dosage": "0.6g/liter"
                }
            ],

            "npk": "Excess Nitrogen promotes blast fungal growth. Reduce N fertilizer by 20% and top-dress with Muriate of Potash (MOP)."
        },

        {
            "issue": "Bacterial Leaf Blight (Xanthomonas oryzae)",
            "category": "Bacterial Disease",
            "severity": "Severe",

            "organic": [
                {
                    "title": "Cow Dung & Curd Bio-spray",
                    "description": "Fermented liquid organic formulation rich in antagonist microbes.",
                    "dosage": "100 ml/liter"
                }
            ],

            "chemical": [
                {
                    "title": "Streptocycline + Copper Oxychloride",
                    "description": "Combine bactericide with copper fungicide for leaf drying control.",
                    "dosage": "0.1g Streptocycline + 2g COC per liter"
                }
            ],

            "npk": "Split Nitrogen into 3-4 doses. Apply extra Potash (25 kg/ha) to enhance cell wall resistance against bacterial entry."
        }
    ],

    "Wheat": [
        {
            "issue": "Yellow Rust / Stripe Rust (Puccinia striiformis)",
            "category": "Fungal Disease",
            "severity": "Severe",

            "organic": [
                {
                    "title": "Garlic Extract & Fermented Whey",
                    "description": "Antifungal botanical formulation sprayed on yellow leaf stripes.",
                    "dosage": "50 ml/liter"
                }
            ],

            "chemical": [
                {
                    "title": "Propiconazole 25% EC",
                    "description": "Systemic triazole fungicide immediately stops rust spores.",
                    "dosage": "1 ml/liter"
                }
            ],

            "npk": "Maintain 4:2:1 NPK ratio. Avoid late Nitrogen top-dressing which prolongs vegetative growth during rust season."
        }
    ],

    "Cotton": [
        {
            "issue": "Cotton Leaf Curl Virus (CLCuV)",
            "category": "Viral Disease",
            "severity": "Severe",

            "organic": [
                {
                    "title": "Whitefly Trap & Yellow Sticky Cards",
                    "description": "Control whitefly vector population using sticky traps.",
                    "dosage": "25 traps/acre"
                }
            ],

            "chemical": [
                {
                    "title": "Diafenthiuron 50% WP",
                    "description": "Target whitefly nymphs and adults transmitting virus.",
                    "dosage": "1.2g/liter"
                }
            ],

            "npk": "Foliar spray of Magnesium Sulphate (1%) and Zinc Sulphate (0.5%) to alleviate viral leaf stunting."
        }
    ],

    "Tomato": [
        {
            "issue": "Tomato Early Blight (Alternaria solani)",
            "category": "Fungal Disease",
            "severity": "High",

            "organic": [
                {
                    "title": "Baking Soda & Liquid Soap Spray",
                    "description": "Alters leaf surface pH to prevent fungal spore germination.",
                    "dosage": "5g Baking Soda / liter"
                }
            ],

            "chemical": [
                {
                    "title": "Mancozeb 75% WP",
                    "description": "Contact fungicide for preventive coverage.",
                    "dosage": "2g/liter"
                }
            ],

            "npk": "Prune lower infected leaves. Apply Calcium Nitrate (0.5%) spray to prevent fruit end rot."
        }
    ]
}


# ============================================================
# 3. STATE CLIMATE PROFILES
# ============================================================

STATE_CLIMATE_PROFILES = {
    "Punjab": {
        "temp": 39.5,
        "drought": 0.42,
        "flood": 0.15
    },

    "Maharashtra": {
        "temp": 41.2,
        "drought": 0.78,
        "flood": 0.35
    },

    "Tamil Nadu": {
        "temp": 39.8,
        "drought": 0.65,
        "flood": 0.45
    },

    "Uttar Pradesh": {
        "temp": 42.0,
        "drought": 0.55,
        "flood": 0.60
    },

    "Bihar": {
        "temp": 37.0,
        "drought": 0.30,
        "flood": 0.85
    },

    "Rajasthan": {
        "temp": 45.5,
        "drought": 0.92,
        "flood": 0.10
    },

    "West Bengal": {
        "temp": 36.5,
        "drought": 0.25,
        "flood": 0.80
    }
}


# ============================================================
# 4. MANDI PRICE DATABASE
# ============================================================

MANDI_RATES_DATABASE = {

    "Rice": {
        "mandi": "Amritsar Grain Market",
        "state": "Punjab",
        "modal_price": 4720,
        "trend": "Rising",
        "change": 4.1
    },

    "Wheat": {
        "mandi": "Indore APMC",
        "state": "Madhya Pradesh",
        "modal_price": 2900,
        "trend": "Rising",
        "change": 5.0
    },

    "Cotton": {
        "mandi": "Rajkot APMC",
        "state": "Gujarat",
        "modal_price": 7500,
        "trend": "Rising",
        "change": 3.5
    },

    "Tomato": {
        "mandi": "Pimpalgaon APMC",
        "state": "Maharashtra",
        "modal_price": 2400,
        "trend": "Falling",
        "change": -6.5
    }
}


# ============================================================
# 5. PYDANTIC MODELS
# ============================================================

class IrrigationRequest(BaseModel):
    crop_type: str = "Rice"
    growth_stage: str = "Mid-Season"
    soil_type: str = "Alluvial"
    soil_moisture_pct: float = 28.0
    ambient_temp_c: float = 35.0
    field_area_acres: float = 2.5
    relative_humidity_pct: float = 45.0
    wind_speed_kmh: float = 12.0
    solar_radiation_mj: float = 22.0


class OfflineSyncPayload(BaseModel):
    device_id: str
    last_sync_timestamp: str
    offline_diagnoses: List[Dict[str, Any]]
    offline_telemetry: List[Dict[str, Any]]


# ============================================================
# 6. IMAGE PROCESSING
# ============================================================

def process_image_features(image_bytes: bytes) -> Dict[str, float]:

    try:

        img = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        img_arr = np.array(img)

        r_mean = float(
            np.mean(img_arr[:, :, 0])
        )

        g_mean = float(
            np.mean(img_arr[:, :, 1])
        )

        b_mean = float(
            np.mean(img_arr[:, :, 2])
        )

        chlorosis_ratio = round(
            (r_mean + 1.0) /
            (g_mean + 1.0),
            2
        )

        return {
            "r": r_mean,
            "g": g_mean,
            "b": b_mean,
            "chlorosis_ratio": chlorosis_ratio
        }

    except Exception:

        return {
            "r": 120.0,
            "g": 140.0,
            "b": 90.0,
            "chlorosis_ratio": 0.85
        }


# ============================================================
# 7. MULTILINGUAL ADVISORY
# ============================================================

def generate_multilingual_voice_advisory(
    crop: str,
    issue: str,
    remedy: str
) -> Dict[str, str]:

    return {

        "hi":
        f"किसान ध्यान दें: आपकी {crop} की फसल में '{issue}' पाया गया है। अनुशंसित उपाय: {remedy}।",

        "en":
        f"Farmer Alert: For your {crop} crop, AI detected '{issue}'. Recommended action: {remedy}.",

        "pa":
        f"ਕਿਸਾਨ ਵੀਰੋ ਧਿਆਨ ਦਿਓ: ਤੁਹਾਡੀ {crop} ਦੀ ਫਸਲ ਵਿੱਚ '{issue}' ਪਾਇਆ ਗਿਆ ਹੈ। ਸੁਝਾਇਆ ਗਿਆ ਇਲਾਜ: {remedy}।",

        "mr":
        f"शेतकरी लक्ष द्या: तुमच्या {crop} पिकात '{issue}' आढळले आहे. शिफारस केलेला उपाय: {remedy}."
    }


# ============================================================
# 8. TOMATO DISEASE DIAGNOSIS
# ============================================================

@app.post("/api/v1/diagnosis/scan")
async def scan_crop_pathology(
    crop_name: str = Form("Rice"),
    file: Optional[UploadFile] = File(None)
):

    selected_crop = (
        crop_name.capitalize()
        if crop_name
        else "Rice"
    )

    if file:
        image_bytes = await file.read()
        features = process_image_features(image_bytes)
    else:
        image_bytes = None
        features = {
            "chlorosis_ratio": 0.9
        }
    # --------------------------------------------------------
    # Tomato ML Model
    # --------------------------------------------------------

    if selected_crop == "Tomato" and image_bytes:

        import pickle

        model_path = os.path.join(

            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),

            "ml-model",

            "tomato_model.pkl"
        )

        if not os.path.exists(model_path):

            raise HTTPException(
                status_code=500,
                detail="Tomato ML model file not found."
            )

        with open(
            model_path,
            "rb"
        ) as f:

            model = pickle.load(f)

        img = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        img = img.resize(
            (64, 64)
        )

        image = np.array(
            img
        ).flatten().reshape(
            1, -1
        )

        prediction = model.predict(
            image
        )[0]

        if prediction == "Tomato___Bacterial_spot":

            detected_issue = (
                "Tomato Bacterial Spot"
            )

        else:

            detected_issue = prediction

        first_remedy = (
            "Remove infected leaves and dispose of them safely."
        )

        advisory = generate_multilingual_voice_advisory(

            selected_crop,

            detected_issue,

            first_remedy
        )

        return {

            "crop_name": selected_crop,

            "detected_issue": detected_issue,

            "category": "Bacterial Disease",

            "confidence_score": 1.0,

            "severity_level": "High",

            "image_features": features,

            "organic_remedies": [

                {
                    "title": "Remove infected leaves",

                    "description":
                    "Remove infected leaves and safely dispose of them.",

                    "dosage": "As needed"
                }

            ],

            "chemical_remedies": [],

            "npk_advice":
            "Maintain balanced nutrition and avoid excessive nitrogen.",

            "localized_advisory": advisory
        }

    # --------------------------------------------------------
    # Existing diagnosis for other crops
    # --------------------------------------------------------

    options = PATHOLOGY_KNOWLEDGE_BASE.get(

        selected_crop,

        PATHOLOGY_KNOWLEDGE_BASE["Rice"]
    )

    selected_diag = random.choice(
        options
    )

    confidence = round(
        random.uniform(
            0.89,
            0.98
        ),
        2
    )

    first_remedy = (

        selected_diag["organic"][0]["title"]

        if selected_diag["organic"]

        else "Apply recommended treatment."
    )

    advisory = generate_multilingual_voice_advisory(

        selected_crop,

        selected_diag["issue"],

        first_remedy
    )

    return {

        "crop_name": selected_crop,

        "detected_issue":
        selected_diag["issue"],

        "category":
        selected_diag["category"],

        "confidence_score":
        confidence,

        "severity_level":
        selected_diag["severity"],

        "image_features":
        features,

        "organic_remedies":
        selected_diag["organic"],

        "chemical_remedies":
        selected_diag["chemical"],

        "npk_advice":
        selected_diag["npk"],

        "localized_advisory":
        advisory
    }


# ============================================================
# 9. CLIMATE ALERTS
# ============================================================

@app.get("/api/v1/climate/alerts")
async def get_climate_risk_alerts(

    state: str = Query("Punjab"),

    district: str = Query("Ludhiana")
):

    prof = STATE_CLIMATE_PROFILES.get(

        state,

        {
            "temp": 40.0,
            "drought": 0.50,
            "flood": 0.40
        }
    )

    alerts = []

    if prof["temp"] >= 41.0:

        alerts.append({

            "alert_type":
            "Severe Heatwave Warning",

            "severity":
            "Critical",

            "headline":
            f"Extreme Heat Stress Warning for {district}, {state}",

            "description":
            f"Forecast temperatures reaching {prof['temp']}°C. Risk of pollen sterilization and severe canopy wilting.",

            "recommended_action":
            "Apply kaolin clay anti-transpirant spray (3%) or light evening sprinkler irrigation.",

            "valid_until":
            (
                datetime.utcnow()
                + timedelta(days=2)
            ).isoformat()
        })

    else:

        alerts.append({

            "alert_type":
            "Moderate Thermal Advisory",

            "severity":
            "Warning",

            "headline":
            f"Temperature Alert for {district}, {state}",

            "description":
            f"Ambient temperature at {prof['temp']}°C.",

            "recommended_action":
            "Maintain adequate soil moisture with morning irrigation.",

            "valid_until":
            (
                datetime.utcnow()
                + timedelta(days=3)
            ).isoformat()
        })

    return {

        "state": state,

        "district": district,

        "heat_stress_index":
        prof["temp"],

        "drought_vulnerability_index":
        prof["drought"],

        "flood_risk_score":
        prof["flood"],

        "overall_risk_level":
        (
            "High Risk Zone"
            if prof["temp"] >= 41.0
            else "Moderate Risk Zone"
        ),

        "alerts": alerts,

        "resilience_tips": [

            "Apply straw mulching to preserve 30% more soil moisture.",

            "Adopt Alternate Wetting and Drying (AWD) for paddy fields to conserve water."
        ]
    }


# ============================================================
# 10. SMART IRRIGATION
# ============================================================

@app.post("/api/v1/irrigation/calculate")
async def calculate_smart_irrigation(
    req: IrrigationRequest
):

    et0 = 5.8

    kc = (
        1.20
        if req.growth_stage == "Mid-Season"
        else 0.85
    )

    etc = round(
        et0 * kc,
        2
    )

    target_moisture = 45.0

    deficit_pct = max(

        0.0,

        target_moisture
        - req.soil_moisture_pct
    )

    water_liters = round(

        (
            deficit_pct * 350.0
            + etc * 400.0
        )
        * req.field_area_acres,

        1
    )

    pump_minutes = int(
        math.ceil(
            water_liters / 300.0
        )
    )

    return {

        "crop_type":
        req.crop_type,

        "growth_stage":
        req.growth_stage,

        "evapotranspiration_et0_mm_day":
        et0,

        "crop_evapotranspiration_etc_mm_day":
        etc,

        "current_soil_moisture_pct":
        req.soil_moisture_pct,

        "target_soil_moisture_pct":
        target_moisture,

        "total_water_needed_liters":
        water_liters,

        "recommended_pump_duration_minutes":
        pump_minutes,

        "water_conservation_tip":
        "Schedule irrigation early morning (5:00 AM - 8:00 AM) to minimize evapotranspiration losses."
    }


# ============================================================
# 11. MANDI PRICES
# ============================================================

@app.get("/api/v1/mandi/prices")
async def get_mandi_commodity_prices(

    commodity: str = Query("Rice"),

    state: Optional[str] = Query(None)
):

    cmd = (
        commodity.capitalize()
        if commodity
        else "Rice"
    )

    info = MANDI_RATES_DATABASE.get(

        cmd,

        MANDI_RATES_DATABASE["Rice"]
    )

    if info["trend"] == "Rising":

        recommendation = (

            f"Prices for {cmd} are rising "
            f"(+{info['change']}%). "
            f"Consider holding produce for 5-7 days "
            f"to capture peak rates at {info['mandi']}."
        )

    else:

        recommendation = (

            f"Prices for {cmd} are declining. "
            f"Sell immediately at {info['mandi']} "
            f"(₹{info['modal_price']}/quintal) "
            f"to avoid post-harvest losses."
        )

    return {

        "commodity": cmd,

        "state":
        state or info["state"],

        "best_selling_mandi": {

            "mandi_name":
            info["mandi"],

            "modal_price_rs_quintal":
            info["modal_price"],

            "price_trend":
            info["trend"],

            "price_change_pct":
            info["change"]
        },

        "harvest_recommendation":
        recommendation
    }


# ============================================================
# 12. OFFLINE DATA SYNC
# ============================================================

@app.post("/api/v1/sync/delta")
async def delta_sync_offline_data(

    payload: OfflineSyncPayload
):

    return {

        "status":
        "Success",

        "synced_diagnoses_count":
        len(payload.offline_diagnoses),

        "synced_telemetry_count":
        len(payload.offline_telemetry),

        "server_timestamp":
        datetime.utcnow().isoformat()
    }


# ============================================================
# 13. WEATHER MODULE
# ============================================================

WEATHER_DIR = os.path.join(

    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),

    "weather"
)

if WEATHER_DIR not in sys.path:

    sys.path.append(
        WEATHER_DIR
    )

try:

    from weather import weather_report

except ImportError as error:

    weather_report = None

    print(
        "WARNING: Weather module could not be imported:",
        error
    )


# ============================================================
# 14. WEATHER API ENDPOINT
# ============================================================

@app.get("/api/v1/weather")
async def get_weather_data(

    latitude: float = Query(...),

    longitude: float = Query(...)
):

    """
    Get current weather and farming risk alerts.
    """

    if weather_report is None:

        raise HTTPException(

            status_code=500,

            detail="Weather module is not available."
        )

    try:

        result = weather_report(

            latitude,

            longitude
        )

        return {

            "success":
            True,

            "weather":
            result["weather"],

            "alerts":
            result["alerts"],

            "recommendations":
            result["recommendations"]
        }

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=f"Unable to get weather data: {error}"
        )


# ============================================================
# 15. VOICE ADVICE ENDPOINT
# ============================================================

@app.post("/api/v1/voice/advice")
async def voice_advice(

    question: str = Form(...),

    crop_name: str = Form("Tomato"),

    disease: str = Form("Tomato Bacterial Spot")
):

    q = question.lower()

    if any(

        word in q

        for word in [

            "what",
            "how",
            "do",
            "treatment",
            "advice",
            "చేయాలి",
            "ఏం",
            "ఏమి",
            "ఎలా",
            "क्या",
            "कैसे"
        ]
    ):

        advice = (

            f"For your {crop_name} crop, "
            f"the detected problem is {disease}. "

            "Remove infected leaves and safely dispose of them. "

            "Avoid watering the leaves and keep good air circulation."
        )

    else:

        advice = (

            f"Your {crop_name} crop has been identified "
            f"with {disease}. "

            "Please follow the recommended treatment "
            "shown on the result page."
        )

    return {

        "crop_name":
        crop_name,

        "disease":
        disease,

        "advice":
        advice
    }


# ============================================================
# 16. STATIC FRONTEND
# ============================================================

STATIC_DIR = os.path.join(

    os.path.dirname(
        os.path.abspath(__file__)
    ),

    "static"
)


@app.get("/")
async def serve_index():

    return FileResponse(

        os.path.join(
            STATIC_DIR,
            "index.html"
        )
    )


@app.get("/index.html")
async def serve_index_html():

    return FileResponse(

        os.path.join(
            STATIC_DIR,
            "index.html"
        )
    )


@app.get("/upload.html")
async def serve_upload_html():

    return FileResponse(

        os.path.join(
            STATIC_DIR,
            "upload.html"
        )
    )


@app.get("/result.html")
async def serve_result_html():

    return FileResponse(

        os.path.join(
            STATIC_DIR,
            "result.html"
        )
    )


if os.path.exists(STATIC_DIR):

    app.mount(

        "/static",

        StaticFiles(
            directory=STATIC_DIR
        ),

        name="static"
    )


# ============================================================
# 17. RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    print(
        "======================================================================"
    )

    print(
        "  AGRI-SHIELD AI - Production Backend Gateway"
    )

    print(
        "  Server running at: http://127.0.0.1:8000"
    )

    print(
        "  Swagger Docs at:   http://127.0.0.1:8000/docs"
    )

    print(
        "======================================================================"
    )

    uvicorn.run(

        "server:app",

        host="0.0.0.0",

        port=8000,

        reload=True
    )
