import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import pickle

DATASET_PATH = "dataset/Tomato___Bacterial_spot"

X = []
y = []

for file in os.listdir(DATASET_PATH):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        img = Image.open(os.path.join(DATASET_PATH, file))
        img = img.resize((64, 64))
        X.append(np.array(img).flatten())
        y.append("Tomato___Bacterial_spot")

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print("Accuracy:", accuracy)

with open("tomato_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as tomato_model.pkl")