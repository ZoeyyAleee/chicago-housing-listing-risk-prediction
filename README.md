# Chicago Housing Listing Risk Prediction

A machine-learning project that predicts monthly listing risk in the Chicago housing market using historical Redfin data.

## Project Goal

The project estimates when market conditions may be more difficult for sellers. Listing risk is represented by:

- Price drops
- Median days on market
- Months of supply

## Dataset

The source data is Redfin Metro Market Tracker data for the Chicago, IL metro area.

- Raw data: 561,266 records across U.S. locations
- Chicago monthly records: 168
- Final engineered dataset: 155 monthly records from February 2013 to December 2025

## Workflow

1. Data preparation and cleaning
2. Exploratory data analysis
3. Time-series feature engineering
4. Model training
5. Model evaluation
6. Historical prediction and visualization

## Models

- Linear Regression
- Random Forest Regressor
- Logistic Regression
- Random Forest Classifier

The final risk-score model is Linear Regression because it performed best on unseen test months.

## Results

On the unseen test period, Linear Regression achieved:

- R²: 0.2362
- RMSE: 0.2212
- MAE: 0.1826

The classification results are exploratory because the final test period contained only low-risk months.

## Limitations

- Small dataset: one metro area with 155 usable monthly observations
- No external economic features, such as mortgage rates or unemployment
- The classification model could not be fully evaluated on unseen high-risk months

## Future Improvements

- Add mortgage rates, unemployment, inflation, and other economic indicators
- Expand the project to multiple metro areas
- Use time-series cross-validation
- Build an interactive dashboard
