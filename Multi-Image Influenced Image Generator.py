import os
import sys
import base64
import requests
from typing import List

# --- CONFIGURATION ---
# Set your Google API key here or via environment variable
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyCx09ug0Q7b0eaeaOGILR3vy53MTKA9FF0")

# Gemini and Imagen endpoints
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
IMAGEN_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={API_KEY}"

# --- UTILITY FUNCTIONS ---
def file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def print_usage():
    print("Usage: python react_image_to_image_demo.py <image1> [<image2>] [<image3>]")
    print("Example: python react_image_to_image_demo.py avatar.png shirt.jpg pants.jpg")

# --- MAIN WORKFLOW ---
def main(image_paths: List[str]):
    if not API_KEY or API_KEY == "aSyCx09ug0Q7b0eaeaOGILR3vy53MTKA9FF0":
        print("ERROR: Please set your Google API key in the script or as the GOOGLE_API_KEY environment variable.")
        return

    if not (1 <= len(image_paths) <= 3):
        print_usage()
        return

    # Step 1: Prepare Gemini request
    chat_history = [
        {
            "role": "user",
            "parts": [
                {"text": "Describe these three images in detail, focusing on their main subjects, styles, and any common themes or elements. Provide a unified, creative, and descriptive prompt (max 150 words) that could be used to generate a new image combining aspects of all three."}
            ]
        }
    ]
    for idx, path in enumerate(image_paths):
        mime_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
        chat_history[0]["parts"].append({
            "inlineData": {"mimeType": mime_type, "data": file_to_base64(path)}
        })

    print("[1/3] Sending images to Gemini 2.0 Flash for prompt generation...")
    gemini_payload = {"contents": chat_history}
    gemini_response = requests.post(GEMINI_ENDPOINT, json=gemini_payload)
    if not gemini_response.ok:
        print(f"Gemini API error: {gemini_response.text}")
        return
    gemini_result = gemini_response.json()
    text_prompt = gemini_result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    if not text_prompt:
        print("Failed to generate a text prompt from the images.")
        return
    print("[2/3] Generated prompt:")
    print(text_prompt)

    # Step 2: Use Imagen 3.0 to generate image from prompt
    print("[3/3] Sending prompt to Imagen 3.0 for image generation...")
    imagen_payload = {
        "instances": {"prompt": text_prompt},
        "parameters": {"sampleCount": 1}
    }
    imagen_response = requests.post(IMAGEN_ENDPOINT, json=imagen_payload)
    if not imagen_response.ok:
        print(f"Imagen API error: {imagen_response.text}")
        return
    imagen_result = imagen_response.json()
    predictions = imagen_result.get("predictions", [])
    if predictions and predictions[0].get("bytesBase64Encoded"):
        image_b64 = predictions[0]["bytesBase64Encoded"]
        output_path = "generated_result.png"
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_b64))
        print(f"Image generated and saved to {output_path}")
    else:
        print("No image data found in the Imagen response.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
    else:
        main(sys.argv[1:]) 

        