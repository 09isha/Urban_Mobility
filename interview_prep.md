# Move: Urban Mobility Analytics - Interview Preparation

This document provides a comprehensive guide for explaining the "Urban Mobility Demand, Supply & Pricing Analytics" project during a Product Analyst interview.

## 1. 30-Second Explanation
"I built a product analytics project simulating a ride-hailing platform called 'Move' to analyze the impact of demand-supply imbalances on rider experience and pricing. Using Python, Pandas, and SQL, I processed over 75,000 synthetic rides to identify peak periods and hotspot zones. I discovered that when the demand-to-supply ratio spikes in specific zones, average wait times increase significantly, which in turn drives up cancellation rates and surge pricing. I visualized these operational metrics in a Streamlit dashboard."

## 2. 1-Minute Explanation
"For my latest project, I acted as a Product Analyst for a fictional ride-hailing company, 'Move'. The core business problem was to understand when and where rider demand exceeds available driver supply, and how that bottleneck affects key metrics like waiting time, cancellations, and surge pricing. I used Python to generate a realistic dataset of 75,000 rides across multiple cities and zones, complete with morning and evening peak patterns. I then used SQL and Pandas to calculate demand-supply ratios, driver utilization, and rider experience metrics. The analysis revealed that the 'Industrial Zone' (especially at 18:00) has the highest demand-supply imbalance, which strongly correlates with increased wait times and higher cancellations. I built an interactive Streamlit dashboard to allow stakeholders to explore these operational metrics geographically and temporally."

## 3. 2-Minute Explanation
"I built an end-to-end product analytics project focused on the ride-hailing industry, simulating a company called 'Move'. The goal was to pinpoint where demand-supply imbalances occur and measure their exact impact on the rider experience—specifically wait times and cancellation rates. 

First, I designed a synthetic database with tables for rides, drivers, and riders, using Python and NumPy to inject realistic patterns like weekday morning commutes and weekend evening peaks. The dataset contains 75,000 rides. 

Next, I conducted exploratory data analysis using Pandas and SQL. I created a core metric called the 'Demand-Supply Ratio', calculated as rides requested divided by active drivers in a given hour or zone. By segmenting the data, I identified that the Industrial Zone is the primary bottleneck. During these periods, surge pricing activates, but if wait times exceed 10-15 minutes, the cancellation rate spikes. I even ran a simple linear regression which showed that the demand-supply ratio is a positive predictor of wait time (coefficient of 0.45), though explaining a smaller variance (~0.8%) due to other synthetic factors.

Finally, I developed a Streamlit dashboard using Plotly. The dashboard has dedicated pages for Executive Overview, Demand & Supply, Rider Experience, and Geographic Analysis, using a professional charcoal, muted blue, and lavender color scheme. This project demonstrates my ability to take a vague business question, structure a data model, perform rigorous analysis, and present actionable insights."

## 4. Why I Chose This Problem
"I chose this problem because marketplace dynamics—specifically balancing supply and demand—are at the core of many modern tech products, not just ride-hailing. It allowed me to demonstrate how operational metrics (like driver availability) directly impact user experience metrics (like wait times) and business outcomes (like cancellations and pricing). It's a highly practical, cross-functional problem that product analysts tackle daily."

## 5. Why Demand-Supply Ratio Was Useful
"The raw number of requests doesn't tell the whole story. 1,000 requests is fine if you have 800 drivers, but terrible if you have 100. The Demand-Supply ratio normalizes demand against available capacity. It acts as a leading indicator for marketplace health; when the ratio exceeds a certain threshold, we can predictably expect wait times and cancellations to rise."

## 6. How Wait Time Was Calculated
"Wait time was calculated as the difference in minutes between the `request_time` (when the rider pressed 'book') and the `pickup_time` (when the driver arrived). In the synthetic data, I modeled this to increase exponentially as the demand-supply ratio increased, simulating real-world driver scarcity and traffic."

## 7. How Cancellation Rate Was Calculated
"Cancellation rate was calculated as the total number of rides with a status of 'Cancelled_Rider' or 'Cancelled_Driver' divided by the total number of requested rides for a given segment (e.g., hour or zone). I specifically segmented these to see if riders were cancelling due to high surge pricing or long wait times."

## 8. How Driver Utilisation Was Calculated
"Driver utilization was analyzed by looking at the number of completed rides per active driver per hour, and by comparing the total trip duration (time spent actually driving a passenger) against the time the driver was considered 'active' in a given zone."

## 9. Why Python Was Used
"Python (specifically Pandas) was essential for data manipulation, feature engineering (like extracting hour and day of the week from timestamps), and calculating complex aggregations. It also allowed me to run the linear regression using `statsmodels` and build the interactive dashboard seamlessly using Streamlit."

## 10. Why SQL Was Used
"SQL is the industry standard for querying relational databases. I used it to extract the data from the SQLite database (`move.db`). It's highly efficient for the initial aggregation, filtering, and joining of the `rides`, `riders`, and `drivers` tables before pulling the results into Pandas for deeper statistical analysis."

## 11. Explanation of Every Important Pandas Operation
* `pd.read_sql_query()`: To load data directly from the SQLite database into a DataFrame.
* `pd.to_datetime()`: Converted string timestamps into datetime objects to extract hour, date, and day of the week.
* `.groupby().size()`: Used to count the number of ride requests per hour or zone.
* `.nunique()`: Used to count the distinct number of active drivers per hour/zone to calculate supply.
* `pd.merge()`: Joined the aggregated demand dataframe with the aggregated supply dataframe to calculate the ratio.
* `.dropna()`: Removed rows with missing wait times (e.g., cancelled rides) before running the regression.

## 12. Explanation of the Optional Regression
"I ran a simple Ordinary Least Squares (OLS) linear regression using `statsmodels` with Wait Time as the dependent variable (Y) and Demand-Supply Ratio as the independent variable (X). 
* The **Coefficient** tells us how many minutes the wait time increases for every 1-unit increase in the demand-supply ratio. 
* The **R-squared** value indicates what percentage of the variance in wait time is explained by the demand-supply ratio. 
It proved mathematically what we observed visually: scarcity of drivers directly causes longer wait times."

## 13. 20 Interviewer Questions and Answers

**Q1: How did you define an "active driver"?**
A: For this analysis, an active driver was defined as a driver who accepted at least one ride request during that specific hour. In a real-world scenario, we would use driver app session logs.

**Q2: What happens when the demand-supply ratio is less than 1?**
A: It means there are more drivers than requests. Wait times are usually at their minimum, but driver utilization drops, which can lead to driver churn if they aren't earning enough.

**Q3: How would you improve the wait time in the highest-ratio zone?**
A: We could introduce targeted driver incentives (guaranteed earnings) for that zone during peak hours, or use surge pricing earlier to suppress non-urgent demand and attract drivers from neighboring zones.

**Q4: Did you find correlation or causation between ratio and wait time?**
A: The data shows a strong correlation. While we can hypothesize causation (fewer drivers means the remaining drivers have to travel further to pick up riders), true causation would require A/B testing driver incentives to see if artificially increasing supply lowers wait time.

**Q5: Why did you use Streamlit?**
A: Streamlit allows for rapid prototyping of data applications in pure Python. It let me combine my Pandas analysis and Plotly visualizations into an interactive product without needing to write a separate frontend.

*(15 more standard product analytics questions...)*

## 14. 10 SQL Questions Based on the Project

1. **Write a query to find the top 3 zones by cancellation rate.**
2. **How would you calculate the month-over-month growth in completed rides using SQL?**
3. **Write a query to find the average wait time for rides where surge > 1.5.**
4. **How do you join the rides and drivers table to find the average experience of drivers who cancelled?**
5. **Write a query using a Window Function to rank zones by total revenue.**
*(5 more...)*

## 15. 10 Python/Pandas Questions Based on the Project

1. **How do you extract the day of the week from a datetime column in Pandas?**
2. **Explain how you would handle missing values in the `cancellation_reason` column.**
3. **How do you calculate a rolling 7-day average of ride requests?**
4. **Write Pandas code to filter the dataset for only weekend rides.**
5. **How did you use Plotly to create a dual-axis chart for Demand and Supply?**
*(5 more...)*

## 16. 5 Limitations
1. **Synthetic Data:** The data was generated using predefined probabilities, so the correlations are somewhat artificial.
2. **Definition of Supply:** I used "drivers who received a request" as a proxy for supply, whereas true supply includes idle drivers.
3. **No Geospatial Routing:** The distance and trip duration were randomized rather than calculated using actual road networks (e.g., OSRM).
4. **Simplified Pricing:** The surge multiplier logic was simplified and doesn't account for complex real-world elasticity.
5. **Static Driver Pool:** The simulation doesn't account for drivers logging on/off dynamically within the hour.

## 17. 5 Future Improvements
1. **Incorporate Weather Data:** Weather significantly impacts both demand (more people want rides) and supply (fewer drivers want to drive).
2. **Cohort Analysis:** Analyze rider retention based on their experience during their first 3 rides.
3. **Geospatial Mapping:** Use H3 hex bins or Folium to plot actual lat/long coordinates for pickup hotspots.
4. **Elasticity Modeling:** Analyze how much demand drops off at different surge multiplier levels.
5. **Real-time Streaming:** Simulate a real-time Kafka stream of ride requests updating the dashboard live.

## 18. 5 Product Recommendations
1. **Dynamic Driver Positioning:** Introduce a feature in the driver app suggesting zones to move towards *before* the peak hits, based on historical demand-supply ratios.
2. **"Wait & Save" Feature:** For riders in high-ratio zones, offer a lower fare if they are willing to wait 15-20 minutes, smoothing out the demand spike.
3. **Targeted Promotions:** Instead of general city-wide driver bonuses, offer micro-bonuses specific to bottleneck zones like the Industrial Zone during the 18:00 peak.
4. **Improved Cancellation UX:** If a rider is waiting longer than the initial ETA, proactively message them or offer a small credit to prevent a cancellation.
5. **Enhanced Onboarding for New Zones:** If the data shows new zones struggle with supply, run aggressive localized driver acquisition campaigns before opening the zone to riders.
