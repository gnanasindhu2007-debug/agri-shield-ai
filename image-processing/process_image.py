import cv2
import numpy as np


IMAGE_SIZE = (224, 224)


def process_image(image_path):
    # Read image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not read the image.")

    # Original dimensions
    height, width = image.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur detection
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Brightness detection
    brightness = float(gray.mean())

    warnings = []

    if blur_score < 100:
        warnings.append("Image may be blurry.")

    if brightness < 50:
        warnings.append("Image may be too dark.")

    if brightness > 230:
        warnings.append("Image may be too bright.")

    # Resize image
    resized = cv2.resize(image, IMAGE_SIZE)

    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    # Normalize pixels from 0-255 to 0-1
    normalized = rgb_image.astype(np.float32) / 255.0

    # Add batch dimension for AI model
    model_input = np.expand_dims(normalized, axis=0)

    return model_input, warnings, width, height


if __name__ == "__main__":

    image_path = "leaf.jpg"

    try:
        processed_image, warnings, width, height = process_image(image_path)

        print("✅ Image processed successfully")
        print(f"Original size: {width} x {height}")
        print(f"Processed size: {IMAGE_SIZE[0]} x {IMAGE_SIZE[1]}")
        print(f"Blur score: {blur_score if False else 'checked'}")
        print(f"Brightness: {brightness if False else 'checked'}")

        if warnings:
            print("⚠️ Warnings:")
            for warning in warnings:
                print("-", warning)
        else:
            print("✅ Image quality looks good")

        print("✅ BGR → RGB")
        print("✅ Normalized")
        print("✅ Ready for AI model")

    except Exception as e:
        print("❌ Error:", e)