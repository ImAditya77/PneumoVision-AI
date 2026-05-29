from pathlib import Path
from PIL import Image, ImageStat


def predict_image(image_path):
    """
    Deterministic placeholder inference.

    A trained DenseNet121 model can replace this function once model/pneumonia_model.h5
    is available. Until then, this examines brightness and local contrast so the complete
    app flow remains testable end to end.
    """
    image = Image.open(image_path).convert("L").resize((224, 224))
    stat = ImageStat.Stat(image)
    mean = stat.mean[0]
    stddev = stat.stddev[0]

    dark_region_signal = max(0, 120 - mean) / 120
    texture_signal = min(stddev / 72, 1)
    pneumonia_probability = (dark_region_signal * 0.55) + (texture_signal * 0.45)
    pneumonia_probability = min(max(pneumonia_probability, 0.04), 0.96)

    if pneumonia_probability >= 0.5:
        return {
            "prediction": "Pneumonia",
            "confidence": round(pneumonia_probability * 100, 2),
        }
    return {
        "prediction": "Normal",
        "confidence": round((1 - pneumonia_probability) * 100, 2),
    }

