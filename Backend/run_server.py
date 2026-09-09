import uvicorn
import os
if __name__ == "__main__":
    print("Starting BugBoosters Smart Farming Assistant Backend Server...")
    print("Swagger Documentation available at: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
