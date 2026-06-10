# 🔐 Network Security — Phishing Website Detection

An end-to-end machine learning system that detects phishing websites using 30 URL and page-level features. The project covers the full MLOps lifecycle: data ingestion from MongoDB, automated validation, KNN-based preprocessing, multi-model training with experiment tracking via MLflow + DagsHub, REST API serving with FastAPI, and artifact sync to AWS S3.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Architecture](#project-architecture)
- [Dataset](#dataset)
- [ML Pipeline](#ml-pipeline)
- [Model Performance & Metrics](#model-performance--metrics)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Usage](#api-usage)
- [Experiment Tracking](#experiment-tracking)
- [Cloud Deployment](#cloud-deployment)
- [Author](#author)

---

## Overview

This project builds a binary classifier to distinguish **phishing** websites from **legitimate** ones. URLs are described by 30 engineered features (encoding IP address presence, URL length, SSL state, redirects, domain age, etc.) with labels encoded as `1` (legitimate) and `-1`/`0` (phishing).

The pipeline is modular and production-ready:
- Data is stored and pulled from **MongoDB Atlas**
- Training is fully automated via a `TrainingPipeline` class
- The best model is selected via **GridSearchCV** across five classifiers
- Metrics and models are logged to **DagsHub / MLflow**
- Artifacts are synced to **AWS S3**
- Predictions are served via a **FastAPI** application

---

## Project Architecture

```
MongoDB Atlas
     │
     ▼
Data Ingestion
(export → feature store → train/test split)
     │
     ▼
Data Validation
(column count check + KS-test drift detection)
     │
     ▼
Data Transformation
(KNN Imputer pipeline → .npy arrays)
     │
     ▼
Model Training
(GridSearchCV over 5 classifiers → best model selection)
     │
     ├── MLflow / DagsHub  (metric & model logging)
     ├── AWS S3             (artifact + model sync)
     └── final_model/       (model.pkl + preprocessor.pkl)
                │
                ▼
          FastAPI App
      /train  →  trigger pipeline
      /predict →  upload CSV → get predictions
```

---

## Dataset

| Property | Value |
|---|---|
| Source file | `Network_data/phisingData.csv` |
| Total samples | **11,055** |
| Features | **30** (all numeric / binary-encoded) |
| Target column | `Result` (`1` = Legitimate, `-1`/`0` = Phishing) |
| Class distribution | Legitimate: 6,157 (55.7%) · Phishing: 4,898 (44.3%) |
| Missing value strategy | KNN Imputer (k=3, uniform weights) |

### Features

All 30 features are numeric encodings of URL and page properties:

`having_IP_Address`, `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix`, `having_Sub_Domain`, `SSLfinal_State`, `Domain_registeration_length`, `Favicon`, `port`, `HTTPS_token`, `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email`, `Abnormal_URL`, `Redirect`, `on_mouseover`, `RightClick`, `popUpWidnow`, `Iframe`, `age_of_domain`, `DNSRecord`, `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report`

---

## ML Pipeline

### 1. Data Ingestion (`data_ingestion.py`)
- Connects to MongoDB Atlas (database: `SAYANML`, collection: `NetworkData`)
- Exports collection to a pandas DataFrame → saves as CSV to the feature store
- Splits data into train (80%) / test (20%) sets

### 2. Data Validation (`data_validation.py`)
- Validates column count against `data_schema/schema.yaml`
- Runs **Kolmogorov-Smirnov (KS) test** on each feature to detect distribution drift between train and test sets
- Generates a YAML drift report saved under `Artifacts/.../drift_report/report.yaml`

### 3. Data Transformation (`data_transformation.py`)
- Drops the target column `Result` and converts `-1` labels to `0`
- Fits a `KNNImputer` (k=3) on training features and transforms both splits
- Saves transformed arrays as `.npy` files and the fitted preprocessor as `preprocessing.pkl`

### 4. Model Training (`model_trainer.py`)
Models evaluated via `GridSearchCV` (3-fold CV):

| Model | Hyperparameters Searched |
|---|---|
| Random Forest | `n_estimators`: [8, 16, 32, 128, 256] |
| Decision Tree | `criterion`: [gini, entropy, log_loss] |
| Gradient Boosting | `learning_rate`, `subsample`, `n_estimators` |
| Logistic Regression | — (default) |
| AdaBoost | `learning_rate`, `n_estimators` |

- Best model selected by highest **R² score** on the test set
- Final model + preprocessor saved to `final_model/`
- Train and test classification metrics logged to MLflow

---

## Model Performance & Metrics

Metrics are tracked across training runs via MLflow. Results from the two most recent completed runs:

### Latest Run (Test Set)
| Metric | Score |
|---|---|
| **F1 Score** | **0.9876** |
| **Precision** | **0.9838** |
| **Recall** | **0.9914** |

### Latest Run (Train Set)
| Metric | Score |
|---|---|
| **F1 Score** | **0.9914** |
| **Precision** | **0.9899** |
| **Recall** | **0.9930** |

### Previous Run (Test Set)
| Metric | Score |
|---|---|
| F1 Score | 0.9903 |
| Precision | 0.9914 |
| Recall | 0.9892 |

> Experiments tracked at: [DagsHub — sayantanman508/networksecurity](https://dagshub.com/sayantanman508/networksecurity)

The minimal gap between train and test metrics (~0.004 F1) indicates no significant overfitting.

---

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| ML / Preprocessing | scikit-learn, NumPy, pandas |
| Data Storage | MongoDB Atlas (pymongo) |
| Experiment Tracking | MLflow, DagsHub |
| API Server | FastAPI, Uvicorn |
| Cloud Storage | AWS S3 (boto3 / AWS CLI) |
| Serialization | pickle, dill |
| Config / Schema | PyYAML |
| Environment | python-dotenv |
| Containerization | Docker |
| Package Build | setuptools |

---

## Project Structure

```
NetworkSecurityProject/
│
├── app.py                         # FastAPI application entry point
├── main.py                        # Script-based training pipeline runner
├── push_data.py                   # Utility to push CSV data to MongoDB
├── setup.py                       # Package setup
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker container definition
├── .env                           # Environment variables (not committed)
├── .github/workflows/main.yml     # CI/CD workflow
│
├── data_schema/
│   └── schema.yaml                # Column names and types for validation
│
├── Network_data/
│   └── phisingData.csv            # Raw dataset (~11k samples)
│
├── valid_data/
│   └── test.csv                   # Sample CSV for inference testing
│
├── final_model/
│   ├── model.pkl                  # Trained best model
│   └── preprocessor.pkl           # Fitted KNN imputer pipeline
│
├── prediction_output/
│   └── output.csv                 # Last batch prediction results
│
├── templates/
│   └── table.html                 # Jinja2 template for prediction display
│
└── networksecurity/               # Main Python package
    ├── components/
    │   ├── data_ingestion.py
    │   ├── data_validation.py
    │   ├── data_transformation.py
    │   └── model_trainer.py
    │
    ├── pipeline/
    │   ├── training_pipeline.py   # Orchestrates all components + S3 sync
    │   └── batch_prediction.py
    │
    ├── entity/
    │   ├── config_entity.py       # Dataclasses for pipeline configs
    │   └── artifact_entity.py     # Dataclasses for pipeline artifacts
    │
    ├── constant/
    │   └── training_pipeline/
    │       └── __init__.py        # All pipeline constants
    │
    ├── utils/
    │   ├── main_utils/utils.py    # YAML, pickle, numpy utilities
    │   └── ml_utils/
    │       ├── model/estimator.py             # NetworkModel wrapper class
    │       └── metric/classification_metric.py # F1, precision, recall
    │
    ├── cloud/
    │   └── s3_syncer.py           # AWS S3 sync helpers
    │
    ├── exception/exception.py     # Custom exception with traceback info
    └── logging/logger.py          # Timestamped file logger
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (with a cluster and `SAYANML.NetworkData` collection)
- AWS account with an S3 bucket named `networksecurity`
- DagsHub account (for MLflow tracking)

### Installation

```bash
# Clone the repository
git clone https://github.com/sayantanman508/networksecurity.git
cd networksecurity

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

### Push Data to MongoDB (first time only)

```bash
python push_data.py
```

This reads `Network_data/phisingData.csv` and inserts all records into your MongoDB collection.

### Run Training Pipeline (standalone script)

```bash
python main.py
```

This runs all four stages sequentially and saves the final model to `final_model/`.

### Start the FastAPI Server

```bash
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

```env
# MongoDB connection string
MONGO_DB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/

# MongoDB key used in app.py
MONGODB_URL_KEY=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/

# AWS credentials (required for S3 artifact sync)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

---

## API Usage

### `GET /train`
Triggers the full training pipeline (data ingestion → validation → transformation → model training → S3 sync).

```bash
curl -X GET http://localhost:8000/train
```

**Response:** `"Training is successful"`

---

### `POST /predict`
Upload a CSV file of feature vectors (same 30 columns as the training data, without the `Result` column). Returns an HTML table with predictions appended as a `predicted_column`.

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@valid_data/test.csv"
```

**Output:** Rendered HTML table (also saved to `prediction_output/output.csv`)

**Prediction values:** `1.0` = Legitimate, `0.0` = Phishing

---

## Experiment Tracking

Experiments are logged to DagsHub-hosted MLflow. Each training call creates two runs (train metrics + test metrics) logging:

- `f1_score`
- `precision`
- `recall_score`
- Serialised sklearn model artifact

To view experiments locally:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then open `http://localhost:5000`.

---

## Cloud Deployment

### AWS S3 Sync

After each training run, artifacts and the final model are synced to S3:

```
s3://networksecurity/artifact/<timestamp>/
s3://networksecurity/final_model/<timestamp>/
```

The `S3Sync` class uses the AWS CLI `sync` command, so ensure the AWS CLI is installed and credentials are configured.

### Docker

A `Dockerfile` is included for containerised deployment. Build and run:

```bash
docker build -t networksecurity:latest .
docker run -p 8000:8000 --env-file .env networksecurity:latest
```

### CI/CD

GitHub Actions workflow is defined in `.github/workflows/main.yml`. Extend it with your preferred steps (lint, test, build Docker image, push to ECR, deploy to EC2/ECS).

---

## Author

**Sayantan Mandal**
- GitHub: [@sayantanman508](https://github.com/sayantanman508)
- Email: sayantanman508@gmail.com
- MLflow / DagsHub: [dagshub.com/sayantanman508/networksecurity](https://dagshub.com/sayantanman508/networksecurity)

---

## License

This project is open-source and available under the [MIT License](LICENSE).
