import random

CROPS = ["Wheat", "Rice", "Maize", "Cotton", "Potato"]
DISEASES = {
    "Wheat": ["Healthy", "Rust", "Blight"],
    "Rice": ["Healthy", "Leaf Blast", "Brown Spot"],
    "Maize": ["Healthy", "Northern Leaf Blight", "Gray Leaf Spot"],
    "Cotton": ["Healthy", "Aphids", "Whitefly"],
    "Potato": ["Healthy", "Late Blight", "Common Scab"]
}

FERTS = {
    "Wheat": "NPK 20:20:0",
    "Rice": "Urea + Potash",
    "Maize": "Balanced NPK",
    "Cotton": "NPK 12:32:16",
    "Potato": "Potash-rich fertilizer"
}

PESTS = {
    "Wheat": "Fungicide: Propiconazole",
    "Rice": "Fungicide: Copper oxychloride",
    "Maize": "Fungicide/Insecticide: Azoxystrobin",
    "Cotton": "Insecticide: Imidacloprid or Neem oil",
    "Potato": "Fungicide: Mancozeb"
}

def generate_advice(crop, disease):
    if disease == "Healthy":
        return f"{crop} looks healthy. Continue regular care and monitor weekly."
    else:
        return f"For {disease} on {crop}: follow recommended spray schedule, avoid overwatering, and apply recommended fertilizer."

def predict_from_image(filename):
    """Demo heuristic: if filename contains crop name, bias toward that;
       otherwise random pick."""
    lower = filename.lower()
    for crop in CROPS:
        if crop.lower() in lower:
            disease = random.choice(DISEASES[crop])
            return {
                "crop": crop,
                "disease": disease,
                "fertilizer": FERTS[crop],
                "pesticide": PESTS[crop],
                "advice": generate_advice(crop, disease)
            }
    crop = random.choice(CROPS)
    disease = random.choice(DISEASES[crop])
    return {
        "crop": crop,
        "disease": disease,
        "fertilizer": FERTS[crop],
        "pesticide": PESTS[crop],
        "advice": generate_advice(crop, disease)
    }
