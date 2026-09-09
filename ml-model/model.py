import pickle
import numpy as np
from PIL import Image

model = pickle.load(open("tomato_model.pkl", "rb"))

def predict_disease(image_path):
    img = Image.open(image_path)
    img = img.resize((64, 64))

    image = np.array(img).flatten().reshape(1, -1)

    prediction = model.predict(image)

    return prediction[0]
