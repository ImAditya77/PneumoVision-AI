# PneumoVision AI

PneumoVision AI is a local web application for preliminary pneumonia screening from chest X-ray images.
It supports image upload, prediction, confidence scoring, Grad-CAM-style visualization, prediction history,
dashboard analytics, and downloadable PDF medical reports.

> This project is an educational clinical decision-support prototype. It is not a medical device and should
> not be used as the sole basis for diagnosis or treatment.

## Features

- Chest X-ray image upload
- Normal / Pneumonia prediction response
- Confidence score
- Heatmap overlay visualization
- SQLite-backed patient and prediction history
- Dashboard analytics
- PDF report generation
- Clean modular backend services
- Responsive browser UI

## Project Structure

```text
backend/
  app.py
  database/
    db.py
  routes/
    history.py
    predict.py
    reports.py
  services/
    gradcam_service.py
    model_service.py
    report_service.py
frontend/
  index.html
  src/
    app.js
    styles.css
model/
uploads/
reports/
data/
```

## Run Locally

The bundled Codex Python runtime already includes Pillow and ReportLab. From the project root:

```powershell
& "C:\Users\Aditya Dixit\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" backend\app.py
```

Then open:

```text
http://localhost:5000
```

If you want to use your own Python environment, install:

```powershell
pip install pillow reportlab
```

## Real Model Integration

The current `backend/services/model_service.py` contains a deterministic image-analysis placeholder so the
full application can run before model training is complete. Replace `predict_image` with TensorFlow/Keras
loading logic once `model/pneumonia_model.h5` is available.

Expected future model input:

- RGB image
- `224 x 224`
- normalized pixel values

## API

```text
POST   /api/predict
GET    /api/history
GET    /api/report/{id}
DELETE /api/history/{id}
```

