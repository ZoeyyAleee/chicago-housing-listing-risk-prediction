# Chicago Housing Listing Risk Prediction

An end-to-end machine-learning project for estimating **monthly listing risk** in the Chicago, Illinois housing market. It turns historical Redfin market data into a composite risk score, evaluates forecasting models with a time-aware split, and serves the latest prediction through a FastAPI application.

> This project is an educational market-analysis tool, not financial, investment, or real-estate advice.

## Contents

- [Overview](#overview)
- [Data](#data)
- [Risk definition](#risk-definition)
- [Methodology](#methodology)
- [Results](#results)
- [Repository layout](#repository-layout)
- [Getting started](#getting-started)
- [Run the API](#run-the-api)
- [Run tests](#run-tests)
- [Limitations and next steps](#limitations-and-next-steps)

## Overview

Listing risk describes market conditions that can make selling a home more difficult. The project models a continuous `RISK_SCORE` from three indicators:

- `PRICE_DROPS`: the share of listings with price reductions
- `MEDIAN_DOM`: median days a listing remains on the market
- `MONTHS_OF_SUPPLY`: available inventory relative to the sales pace

Higher scores indicate more challenging-than-usual selling conditions. The deployed model uses only calendar, lagged, and rolling-history features, so it does not rely on current-month market values that would be unavailable at prediction time.

## Data

The source is Redfin Metro Market Tracker data for the Chicago, IL metro area.

| Dataset | Description |
| --- | --- |
| `data/processed/chicago_housing_data.csv` | Cleaned monthly Chicago housing-market data |
| `data/processed/chicago_housing_engineered.csv` | Model-ready dataset with targets and engineered features |

The final engineered dataset contains **155 monthly observations**, covering **February 2013 through December 2025**. The source extract contained 561,266 records across U.S. locations; filtering to Chicago produced 168 monthly rows before feature engineering removed the early rows that lack historical context.

## Risk definition

`RISK_SCORE` is a composite regression target:

1. The three risk indicators are standardized with z-scores using the first 80% of the time series as the reference period.
2. Their standardized values are averaged.

```text
RISK_SCORE = mean(z(PRICE_DROPS), z(MEDIAN_DOM), z(MONTHS_OF_SUPPLY))
```

A score above `0` means above-average listing risk relative to that training-period baseline; a negative score means below-average risk. The API labels scores above `0` as `High` and all others as `Low`.

The project also includes a classification target, `RISK_LABEL`:

- `1` — high risk: `PRICE_DROPS` is above the training-period median
- `0` — low risk: otherwise

## Methodology

The notebooks document the full workflow in order:

| Notebook | Purpose |
| --- | --- |
| `01_data_preparation.ipynb` | Cleans and prepares the Chicago monthly dataset |
| `02_exploratory_analysis.ipynb` | Explores price, inventory, supply, days-on-market, and price-drop trends |
| `03_feature_engineering.ipynb` | Creates time-series features and the risk targets |
| `04_model_training.ipynb` | Trains and saves models, scaler, and feature list |
| `05_model_evaluation.ipynb` | Evaluates saved models on unseen future months |
| `06_predictions.ipynb` | Produces historical predictions and visualizations |

### Features

The final model receives 31 features:

- Calendar: month and year
- One- and three-month lags for sale price, homes sold, new listings, inventory, months of supply, median days on market, and price drops
- Three- and six-month rolling averages for those same market indicators
- Year-over-year change in price drops

Current-month raw market columns are deliberately excluded from the inputs to prevent target leakage.

### Train/test strategy

Because this is time-series data, observations are not shuffled. The earliest 80% of months are used for training and the latest 20% are held out as the test period. The `StandardScaler` is fit only on training data, then applied to both training and test features.

### Models

Two regression models predict the continuous risk score, while two classifiers predict the binary risk label:

- Linear Regression
- Random Forest Regressor
- Logistic Regression
- Random Forest Classifier

The saved API model is **Linear Regression** (`models/linear_regression.pkl`), selected because it performed best on the unseen test period.

## Results

Regression performance on the held-out future months:

| Model | R² | RMSE | MAE |
| --- | ---: | ---: | ---: |
| Linear Regression | 0.2362 | 0.2212 | 0.1826 |
| Random Forest Regressor | -0.6444 | 0.3245 | 0.2550 |

Classification results are exploratory only: the final test period contains low-risk months, so the classifiers cannot be fairly assessed on their ability to recognize unseen high-risk months.

## Repository layout

```text
.
├── app/
│   ├── main.py                     # FastAPI routes
│   ├── schemas.py                  # Response schema
│   └── services/prediction_service.py
├── data/processed/                 # Cleaned and engineered CSV datasets
├── models/                         # Serialized models, scaler, and feature list
├── notebooks/                      # Analysis, feature engineering, training, evaluation
├── sql_scripts/                    # Supporting SQL queries
├── tests/                          # API tests
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

- Python 3.12 (the project dependencies are pinned for this environment)
- `pip`

### Installation

Clone the repository, then create and activate a virtual environment:

```bash
git clone <your-repository-url>
cd listing-risk-prediction
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Explore or reproduce the analysis

Run Jupyter from the `notebooks/` directory and execute the notebooks in numeric order:

```bash
python -m pip install jupyter
cd notebooks
jupyter notebook
```

Notebooks use relative paths and are designed to be run from the `notebooks/` directory. Training saves these artifacts to `models/`:

- `linear_regression.pkl` — deployed regression model
- `rf_regressor.pkl` — comparison regression model
- `logistic_regression.pkl` — classification model
- `rf_classifier.pkl` — comparison classification model
- `scaler.pkl` — fitted feature scaler
- `feature_cols.pkl` — ordered list of the 31 required features

## Run the API

From the repository root, with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000`. The interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

### Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Confirms that the API is running |
| `GET` | `/predict/latest` | Predicts risk using the latest row in the engineered dataset |

### Examples

Check service health:

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status":"ok"}
```

Request the latest prediction:

```bash
curl http://127.0.0.1:8000/predict/latest
```

Example response shape:

```json
{
  "period": "YYYY-MM-DD",
  "predicted_risk_score": -0.891,
  "risk_level": "Low"
}
```

`period` identifies the newest engineered data month, `predicted_risk_score` is the regression prediction rounded to three decimals, and `risk_level` applies the zero-score threshold described above.

## Run tests

With dependencies installed and the virtual environment active:

```bash
python -m pip install pytest
pytest
```

The API tests verify the health endpoint and the response contract for the latest-prediction endpoint.

## Limitations and next steps

- The data covers one metro area and only 155 usable monthly observations.
- The model does not include external drivers such as mortgage rates, unemployment, inflation, or local economic conditions.
- The risk score is a relative composite measure, not a probability that a particular listing will fail to sell.
- Classification evaluation is limited by the lack of high-risk months in the held-out period.

Useful next steps include adding economic indicators, expanding to multiple metros, using rolling-origin time-series cross-validation, monitoring model drift, and deploying an interactive dashboard.

## License

This project is available under the [MIT License](LICENSE).
