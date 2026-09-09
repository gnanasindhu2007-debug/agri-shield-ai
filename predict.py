import pickle
import numpy as np
from PIL import Image

model = pickle.load(open("tomato_model.pkl", "rb"))

image_path = "dataset/Tomato___Bacterial_spot/fe9f6122-ab3f-46bb-b9db-fee295881270___GCREC_Bact.Sp 6341.JPG"

img = Image.open(image_path)
img = img.resize((64, 64))

image = np.array(img).flatten().reshape(1, -1)

prediction = model.predict(image)

print("Prediction:", prediction[0])