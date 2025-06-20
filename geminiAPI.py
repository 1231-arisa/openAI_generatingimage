# To run this code you need to install the following dependencies:
# pip install google-generativeai Pillow
import os
import google.generativeai as genai
from PIL import Image
import mimetypes
import google.ai.generativelanguage as glm

# --- IMPORTANT: PLEASE READ THE INSTRUCTIONS ---

# 1. Add your Gemini API Key here
# You can get one from Google AI Studio: https://aistudio.google.com/
os.environ["GEMINI_API_KEY"] = "AIzaSyCx09ug0Q7b0eaeaOGILR3vy53MTKA9FF0"

# 2. Define the paths to your images.
#    - Make sure these filenames EXACTLY match your files.
#    - Common errors: spaces, typos, or wrong extension (.jpg vs .jpeg).
IMAGE_DIRECTORY = r"C:\AIstylist\input"
AVATAR_PATH = os.path.join(IMAGE_DIRECTORY, "avatar.png")
NAVY_SHIRT_PATH = os.path.join(IMAGE_DIRECTORY, "Navyshirt.jpg")
# I am correcting the filename to have a space, as you mentioned earlier.
# If this is wrong, please fix it.
NEW_CLOTHING_PATH = os.path.join(IMAGE_DIRECTORY, "new_clothing.jpg") 

# --- END OF SETUP ---

def save_binary_file(file_name, data):
    """Saves binary data (like an image) to a file."""
    try:
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"File saved successfully to: {file_name}")
    except IOError as e:
        print(f"Error saving file: {e}")

def generate_image_from_images():
    """Generates an image by combining input images and a text prompt."""
    try:
        # The correct way to configure the API key
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except Exception as e:
        print(f"API Key Error: {e}. Please make sure your GEMINI_API_KEY is set correctly.")
        return

    # This is the model that supports multi-image input for generation
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    print("Preparing images and prompt...")
    # Verify that all image files exist before proceeding
    for path in [AVATAR_PATH, NAVY_SHIRT_PATH, NEW_CLOTHING_PATH]:
        if not os.path.exists(path):
            print(f"FATAL ERROR: The file was not found: {path}")
            print("Please check the filename and the IMAGE_DIRECTORY path in the script.")
            return

    # Load images
    avatar_img = Image.open(AVATAR_PATH)
    shirt_img = Image.open(NAVY_SHIRT_PATH)
    pants_img = Image.open(NEW_CLOTHING_PATH)

    # The prompt describing what to do with the images
    prompt = """Based on the three images provided:
1. The illustrated avatar.
2. The navy blue shirt.
3. The grey pants.

Generate a new, single image showing the avatar wearing the navy shirt and the grey pants.
The final generated image should exactly match the illustration style and character design of the avatar. 
The colors of the clothing must be preserved. The final image should be a clean, full-body shot."""

    # Create the multimodal request
    contents = [
        # The API expects the image data to be wrapped in a specific format.
        glm.Part(inline_data=glm.Blob(mime_type='image/png', data=avatar_img.tobytes())),
        glm.Part(inline_data=glm.Blob(mime_type='image/jpeg', data=shirt_img.tobytes())),
        glm.Part(inline_data=glm.Blob(mime_type='image/jpeg', data=pants_img.tobytes())),
        glm.Part(text=prompt)
    ]

    print("Sending request to Gemini API. This may take a moment...")
    try:
        response = model.generate_content(contents)
        
        # The new SDK handles the response parts directly
        output_part = response.parts[0]
        
        # Check if the part contains image data
        if output_part.inline_data:
            output_image_data = output_part.inline_data.data
            output_mime_type = output_part.inline_data.mime_type
            
            file_extension = mimetypes.guess_extension(output_mime_type) or ".png"
            output_filename = f"generated_style{file_extension}"
            
            save_binary_file(output_filename, output_image_data)
        elif output_part.text:
            print("\nAPI returned text instead of an image:")
            print(output_part.text)

    except Exception as e:
        print(f"\nAn error occurred while calling the Gemini API: {e}")
        print("This could be due to several reasons:")
        print("- The API key may be invalid or lack permissions.")
        print("- The model may not support this specific combination of inputs (API capabilities can differ from the web UI).")
        print("- There might be a temporary issue with the Google API service.")

if __name__ == "__main__":
    generate_image_from_images()
