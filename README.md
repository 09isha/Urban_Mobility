# Urban Mobility Demand, Supply & Pricing Analytics

This project simulates a fictional ride-hailing company called **Move** to analyze and understand when and where rider demand exceeds available driver supply, and how that bottleneck affects key metrics like waiting time, cancellations, and surge pricing.

It is designed as an end-to-end product analytics portfolio project showcasing exploratory data analysis, geographic segmentation, and operational metrics visualization.

## Project Structure

*   **`generate_data.py`**: A Python script using `pandas` and `numpy` to generate ~75,000 synthetic rides with realistic morning/evening peak patterns and demand/supply imbalances. It saves the resulting datasets to CSV files (`rides.csv`, `drivers.csv`, `riders.csv`) and an SQLite database (`move.db`).
*   **`app.py`**: A `streamlit` dashboard to explore the generated data interactively. It includes visualizations built with `plotly` and features multiple views such as Executive Overview, Demand & Supply, Rider Experience, Pricing, and Geographic Analysis.
*   **`get_insights.py`**: A quick analysis script that extracts key factual insights (e.g., peak demand hours, bottleneck zones) directly from the generated database using `pandas` and calculates a simple linear regression using `statsmodels`.
*   **`interview_prep.md`**: A comprehensive guide designed for interview preparation, containing summaries of the project, data insights, and potential interview Q&A for Product Analyst roles.
*   **`requirements.txt`**: List of Python dependencies required to run the project.

## Tech Stack

*   **Python**: Data manipulation and scripting.
*   **Pandas & NumPy**: Feature creation, aggregation, and data cleaning.
*   **SQLite**: Local relational database for storing generated records.
*   **Streamlit**: Interactive web dashboard framework.
*   **Plotly**: Data visualization.
*   **Statsmodels**: Simple linear regression for operational metrics.

## Setup & Installation

1.  **Install Dependencies**
    Ensure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate the Data**
    Run the data generation script to build the synthetic SQLite database and CSV files:
    ```bash
    python generate_data.py
    ```

3.  **Run the Dashboard**
    Start the Streamlit application to view the interactive dashboard:
    ```bash
    streamlit run app.py
    ```
    This will open the dashboard in your default web browser (typically at `http://localhost:8501`).

## Key Business Metrics Addressed

*   **Demand & Supply**: Rides requested, active drivers, demand-supply ratio.
*   **Rider Experience**: Average wait times, cancellation rates, completion rates.
*   **Pricing**: Average fare, surge multiplier distribution.
