import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from datetime import timedelta
import os
from datetime import datetime

# Load data
df = pd.read_csv("/Users/nlishivha_sandtech/Desktop/energy/data/high.csv")

# Convert Timestamp to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Set up features and target
X = df[["Voltage", "Current", "Power", "Frequency", "PF"]]
y = df["Energy"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Calculate and display Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Save the model to a file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_filename = f"../model/random_forest_energy_model_{timestamp}.pkl"
os.makedirs("model", exist_ok=True)  # Create the directory if it doesn't exist
joblib.dump(model, model_filename)

print(f"Model saved to {model_filename}")
print(X.columns.tolist())
print(X_test.columns.tolist())
# Forecast energy for the next hour
last_row = df.iloc[-1][
    ["Voltage", "Current", "Power", "Frequency", "PF"]
]  # Ensure this matches the training features
future_predictions = []
for i in range(12):
    pred = model.predict([last_row])[0]
    future_predictions.append(pred)
    # import pdb

    # pdb.set_trace()
    last_row["Energy"] = pred
    last_row = last_row.drop(
        "Energy"
    )  # Drop the 'Energy' column to maintain the correct number of features

# Display forecasted energy for the next hour
future_times = [
    df["Timestamp"].iloc[-1] + timedelta(minutes=5 * i) for i in range(1, 13)
]
forecast_df = pd.DataFrame(
    {"Timestamp": future_times, "Predicted_Energy": future_predictions}
)

print("\nForecasted Energy for the Next Hour:")
print(forecast_df)
