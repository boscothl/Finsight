import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Setup credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expandvars(r"%APPDATA%\gcloud\application_default_credentials.json")
PROJECT_ID = "finsight-484914"
LOCATION = "asia-east1" 

def test_style_extraction(image_path="test_style_reference.png"):
    print("\n--- TESTING MULTIMODAL STYLE EXTRACTION ---")
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # We use gemini-1.5-pro or gemini-2.5-pro which support multimodal input
    model = GenerativeModel("gemini-2.5-pro")
    
    # Check if the image exists, if not, guide the user
    if not os.path.exists(image_path):
        print(f"\n[!] Error: Test image '{image_path}' not found.")
        print(f"Please create a sample image named '{image_path}' in this directory to extract styles from.")
        return

    print(f"1. Loading reference image: {image_path}")
    image_part = Part.from_image(open(image_path, "rb").read(), mime_type="image/jpeg")

    prompt = """
    You are an expert UI/UX and graphical designer. Look at the attached document/image.
    Please extract the styling information to be used as a design system reference for generating reports (Excel, PowerPoint, Word).
    
    Identify the following:
    1. Primary Color (hex code)
    2. Secondary Color (hex code)
    3. Background Color (hex code)
    4. Text Color (hex code)
    5. Primary Font (guess the closest standard font like Arial, Calibri, Times New Roman, etc.)
    6. Title Layout (e.g., Centered, Left-Aligned)
    
    Respond STRICTLY in pure JSON format:
    {
      "colors": {
        "primary": "",
        "secondary": "",
        "background": "",
        "text": ""
      },
      "fonts": {
        "primary": ""
      },
      "layout": {
        "title_alignment": ""
      },
      "description": "A short 1-sentence prompt-friendly description of the styling vibe."
    }
    """

    print("2. Sending image and prompt to Gemini...")
    response = model.generate_content([image_part, prompt])
    
    print("\n[AI Extracted Style Data]\n")
    # Clean markdown if present
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        style_json = json.loads(raw_text)
        print(json.dumps(style_json, indent=2))
        print("\n✅ SUCCESS! Style was successfully extracted and structured.")
    except Exception as e:
        print(f"\n❌ Error parsing JSON: {e}")
        print("Raw response:\n", raw_text)

if __name__ == "__main__":
    # Feel free to change the path to a real image on your desktop
    test_style_extraction("test_style_reference.png")
