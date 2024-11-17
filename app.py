import streamlit as st
import plotly.graph_objects as go
from datetime import timedelta, date
import joblib
from machine_learning.predict import forecast_energy, predict_energy
from streamlit_autorefresh import st_autorefresh
from data_aquisition.db_operations import load_historical_data, load_real_time_data
from config import MODEL

# Set page configuration
st.set_page_config(page_title="Operational Energy Dashboard", layout="wide")


# Load the machine learning model
@st.cache_resource()
def load_model() -> joblib:
    """Load and return the machine learning model."""
    return joblib.load(MODEL)


model = load_model()

# Load historical and real-time data
historical_data = load_historical_data()
real_time_data = load_real_time_data()
station_list = historical_data["Station"].unique().tolist()


# Create a Plotly gauge chart
def create_gauge_chart(
    label: str, value: float, min_val: float, max_val: float, threshold: float
) -> go.Figure:
    """Create a gauge chart with specified parameters."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": label},
            gauge={
                "axis": {"range": [min_val, max_val]},
                "bar": {"color": "darkblue"},
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": threshold,
                },
            },
        )
    )
    fig.update_layout(height=250)
    return fig


# Update the dashboard with filtered data and predictions based on user settings
def update_dashboard(station: str, mode: str, start_date: date, end_date: date) -> None:
    """Update and display the dashboard based on user selections."""
    data = None

    # Filter data based on mode and station
    if mode == "Historical":
        data = historical_data[
            (historical_data["Timestamp"].dt.date >= start_date)
            & (historical_data["Timestamp"].dt.date <= end_date)
        ]
        if station != "Overall":
            data = data[data["Station"] == station]
        # Generate predictions for the historical data
        historical_predictions = forecast_energy(model, data)
    else:
        data = load_real_time_data()
        if station != "Overall":
            data = data[data["Process_ID"] == station].tail(120)

        # Add predicted energy for real-time data
        data["Predicted_Energy"] = predict_energy(model, data)

    # Display current energy metrics
    current_data = data.iloc[-1]
    current_energy = current_data["Energy"]
    if mode == "Historical":
        last_prediction = historical_predictions["Predicted_Energy"].iloc[-1]
    else:
        future_predictions = forecast_energy(model, data)
        last_prediction = future_predictions["Predicted_Energy"].iloc[-1]

    energy_change = (last_prediction - current_energy) / current_energy * 100
    st.header(f"{mode} Energy Usage for {station}")

    # Display metrics
    _, col2 = st.columns([5, 1])
    with col2:
        st.metric(
            label="Energy (Next Hour)",
            value=f"{last_prediction:.2f} kWh",
            delta=f"{energy_change:.2f}%",
        )

    # Plot actual vs predicted energy
    energy_figure = go.Figure()
    energy_figure.add_trace(
        go.Scatter(
            x=data["Timestamp"],
            y=data["Energy"],
            mode="lines",
            name="Actual Energy",
            line=dict(color="blue"),
        )
    )
    if mode == "Real-time":
        energy_figure.add_trace(
            go.Scatter(
                x=data["Timestamp"],
                y=data["Predicted_Energy"],
                mode="lines",
                name="Predicted Energy",
                line=dict(color="red", dash="dash"),
            )
        )
    elif mode == "Historical":
        energy_figure.add_trace(
            go.Scatter(
                x=historical_predictions["Timestamp"],
                y=historical_predictions["Predicted_Energy"],
                mode="lines",
                name="Predicted Energy",
                line=dict(color="red", dash="dash"),
            )
        )

    energy_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Energy (kWh)",
        title=f"{mode} Energy Usage for {station}",
        legend=dict(x=0, y=1),
    )
    st.plotly_chart(energy_figure, use_container_width=True)
    st.divider()

    # Display current values using gauges
    col1, col2, col3 = st.columns(3)
    with col1:
        voltage_gauge = create_gauge_chart(
            "Voltage (V)", current_data["Voltage"], 220, 240, 230
        )
        st.plotly_chart(voltage_gauge, use_container_width=True)
    with col2:
        current_gauge = create_gauge_chart(
            "Current (A)", current_data["Current"], 0, 5, 2.5
        )
        st.plotly_chart(current_gauge, use_container_width=True)
    with col3:
        power_gauge = create_gauge_chart(
            "Power (W)", current_data["Power"], 0, 500, 250
        )
        st.plotly_chart(power_gauge, use_container_width=True)

    # Additional gauges
    col4, col5, col6 = st.columns(3)
    with col4:
        energy_gauge = create_gauge_chart(
            "Energy (kWh)", current_data["Energy"], 0, 5, 2.5
        )
        st.plotly_chart(energy_gauge, use_container_width=True)
    with col5:
        frequency_gauge = create_gauge_chart(
            "Frequency (Hz)", current_data["Frequency"], 49, 51, 50
        )
        st.plotly_chart(frequency_gauge, use_container_width=True)
    with col6:
        pf_gauge = create_gauge_chart("Power Factor", current_data["PF"], 0, 1, 0.75)
        st.plotly_chart(pf_gauge, use_container_width=True)
    st.divider()

    if mode == "Real-time":
        # Plot future predictions
        future_df = forecast_energy(model, data)
        energy_figure.add_trace(
            go.Scatter(
                x=future_df["Timestamp"],
                y=future_df["Predicted_Energy"],
                mode="markers+lines",
                name="Future Predictions",
                line=dict(color="green", dash="dot"),
                marker=dict(size=8),
            )
        )

        energy_figure.update_layout(
            xaxis_title="Time",
            yaxis_title="Energy (kWh)",
            title="Predicted Energy Usage (Next Hour)",
            legend=dict(x=0, y=1),
        )
        st.plotly_chart(energy_figure, use_container_width=True)


def display_about() -> None:
    """Display the About section of the dashboard."""
    st.header("About this Dashboard")
    st.image("icons/K.JPG", use_container_width=True)
    st.write(
        """
        This Operational Energy Prediction Dashboard is designed to monitor and forecast energy usage 
        based on real-time data collected from sensors. The dashboard utilizes machine learning 
        models to predict energy consumption and provides insights into voltage, current, energy, 
        energy usage, and energy factor. 

        ### Features:
        - **Real-Time Monitoring:** Visualize energy consumption in real time.
        - **Energy Prediction:** Predict energy usage for the next hour using a trained model.
        - **Historical Data Analysis:** Analyze past data for different stations.
        - **Interactive Gauges:** Track key metrics like voltage, current, energy, and energy factor.

        The platform supports data collection from multiple sources including sensors and serial inputs, 
        and allows for auto-refresh to provide the latest data for informed decision-making.
    """
    )
    st.subheader("Technologies Used:")
    st.write(
        """
        - **Streamlit:** For creating interactive web apps.
        - **Plotly:** For interactive charts and visualizations.
        - **Joblib:** For loading machine learning models.
        - **Serial Communication:** To collect real-time data from sensors.
        - **Pandas:** For data manipulation and analysis.
    """
    )
    st.subheader("Contact Information:")
    st.write(
        """
        For inquiries or support, please contact us at [ndimuhululishivha@gmail.com](mailto:ndimuhululishivha@gmail.com).
    """
    )


def main() -> None:
    """Main function to run the Streamlit app."""
    logo_path = "icons/logo.png"
    st.sidebar.image(logo_path, use_container_width=True)
    st.title("Operational Energy Prediction Dashboard")

    # Sidebar for user inputs
    st.sidebar.header("Settings")
    option = st.sidebar.selectbox("Select Option", ["Dashboard", "About", "Settings"])

    if option == "Dashboard":
        selected_station = st.sidebar.selectbox(
            "Select Station", ["Overall"] + station_list
        )
        data_mode = st.sidebar.selectbox("Data Mode", ["Real-time", "Historical"])

        # Date range selector for historical data
        start_date, end_date = None, None
        if data_mode == "Historical":
            min_date = historical_data["Timestamp"].min().date()
            max_date = historical_data["Timestamp"].max().date()
            start_date = st.sidebar.date_input(
                "Start Date", min_date, min_value=min_date, max_value=max_date
            )
            end_date = st.sidebar.date_input(
                "End Date", max_date, min_value=min_date, max_value=max_date
            )
            if start_date > end_date:
                st.sidebar.error("Start date must be before end date.")

        # Auto-refresh mechanism for real-time data
        if data_mode == "Real-time":
            st_autorefresh(interval=10000, key="data_refresh")

        # Update and display the dashboard
        update_dashboard(selected_station, data_mode, start_date, end_date)

    elif option == "About":
        display_about()


if __name__ == "__main__":
    main()
