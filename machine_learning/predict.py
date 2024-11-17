import pandas as pd
from datetime import timedelta


def forecast_energy(model, df):
    """Forecast energy for the next hour using the model and dataframe."""
    X = df[["Voltage", "Current", "Power", "Frequency", "PF"]]
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

    return forecast_df


def predict_energy(model, df):
    """Predict energy for all data points in the dataframe using the model."""
    X = df[["Voltage", "Current", "Power", "Frequency", "PF"]]
    predictions = model.predict(X)
    return pd.DataFrame({"Predicted_Energy": predictions})


# if __name__ == "__main__":
#     # Load the model
#     import joblib

#     st.cache_resource()
#     model = joblib.load("../model/random_forest_energy_model_20241113_191917.pkl")
#     df = pd.read_csv("sample_data.csv")
#     df["Timestamp"] = pd.to_datetime(df["Timestamp"])
#     forecast_df = forecast_energy(model, df)
#     predictions_df = predict_energy(model, df)
#     print("\nForecasted Energy for the Next Hour:")
#     print(forecast_df)
#     print("\nPredicted Energy for All Data Points:")
#     print(predictions_df)
