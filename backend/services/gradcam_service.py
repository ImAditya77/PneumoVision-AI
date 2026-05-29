from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "uploads"


def create_gradcam_overlay(image_path, prediction):
    source = Image.open(image_path).convert("RGB")
    display = source.copy()
    display.thumbnail((700, 700))

    grayscale = display.convert("L")
    edges = grayscale.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(10))
    heat_alpha = edges.point(lambda p: min(190, int(p * 1.8)))

    color = (224, 56, 56) if prediction == "Pneumonia" else (45, 139, 111)
    heat = Image.new("RGBA", display.size, color + (0,))
    heat.putalpha(heat_alpha)

    overlay = Image.alpha_composite(display.convert("RGBA"), heat)
    output = UPLOAD_DIR / f"gradcam-{uuid4().hex}.png"
    overlay.convert("RGB").save(output, "PNG")
    return output

