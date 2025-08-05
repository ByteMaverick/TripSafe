# Library holidays allows us flag as holiday or not.
import holidays
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

class DataExtractor:
    def __init__(self):
        self.us_holidays = holidays.US()

        # Temp solution, not great for CI/CD
        self.expected_columns = [
            'Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)',
            'Wind_Speed(mph)', 'Wind_Chill(F)', 'Precipitation(in)', 'Hour',
            'day_of_week', 'Month', 'Is_Holiday', 'Is_Rush_Hour',
            # Cities
            'City_Anaheim', 'City_Bakersfield', 'City_Fresno', 'City_Long Beach',
            'City_Los Angeles', 'City_Oakland', 'City_Ontario', 'City_Other',
            'City_Riverside', 'City_Sacramento', 'City_San Bernardino',
            'City_San Diego', 'City_San Francisco', 'City_San Jose',
            # Counties
            'County_Alameda', 'County_Contra Costa', 'County_Fresno', 'County_Kern',
            'County_Los Angeles', 'County_Monterey', 'County_Orange', 'County_Other',
            'County_Riverside', 'County_Sacramento', 'County_San Bernardino',
            'County_San Diego', 'County_San Francisco', 'County_San Joaquin',
            'County_San Mateo', 'County_Santa Clara', 'County_Solano',
            'County_Sonoma', 'County_Stanislaus', 'County_Tulare', 'County_Ventura',
            # Zip Groups
            'Zipcode_Group_900', 'Zipcode_Group_902', 'Zipcode_Group_906', 'Zipcode_Group_907',
            'Zipcode_Group_913', 'Zipcode_Group_917', 'Zipcode_Group_920', 'Zipcode_Group_921',
            'Zipcode_Group_923', 'Zipcode_Group_924', 'Zipcode_Group_925', 'Zipcode_Group_926',
            'Zipcode_Group_928', 'Zipcode_Group_930', 'Zipcode_Group_932', 'Zipcode_Group_933',
            'Zipcode_Group_935', 'Zipcode_Group_936', 'Zipcode_Group_937', 'Zipcode_Group_940',
            'Zipcode_Group_945', 'Zipcode_Group_946', 'Zipcode_Group_950', 'Zipcode_Group_951',
            'Zipcode_Group_952', 'Zipcode_Group_953', 'Zipcode_Group_954', 'Zipcode_Group_956',
            'Zipcode_Group_958', 'Zipcode_Group_959', 'Zipcode_Group_Other'
        ]


    def get_date_data(self, data):


        # Step 1: Convert the string to datetime
        dt = pd.to_datetime(data.strip(), format="%m/%d/%Y, %H:%M")

        # Step 2: Extract components
        hour = dt.hour
        day_of_week = dt.dayofweek
        month = dt.month

        # Step 3: Check if it's a holiday (US by default, or specify country)
        us_holidays = holidays.US()
        is_holiday = dt.date() in us_holidays

        # Step 4: Define rush hour (e.g., 6–9 AM and 4–7 PM)
        is_rush_hour = (7 <= hour <= 9)or (16 <= hour <= 19)



        date_data = {"day_of_week":day_of_week,"Hour":hour,"Month":month,"Is_Holiday":int(is_holiday),"Is_Rush_Hour":int(is_rush_hour)}

        return date_data

    def get_weather_data_le(self,location):
        import requests

        api_key = "e8596ef49660d3eebea854a77bca7faa"


        url = f"http://api.weatherstack.com/current?access_key={api_key}&query={location}&units=f"

        response = requests.get(url)
        data = response.json()
        print(data)

        current = data["current"]

        # Weather features
        temperature_f = current["temperature"]
        humidity_percent = current["humidity"]
        pressure_in = round(current["pressure"] * 0.02953, 2)  # hPa to inHg
        visibility_mi = current["visibility"]
        wind_speed_mph = current["wind_speed"]
        wind_chill_f = current["feelslike"]
        precipitation_in = round(current["precip"] * 0.03937, 2)  # mm to inches

        weather_data = {
            "Temperature(F)": temperature_f,
            "Humidity(%)": humidity_percent,
            "Pressure(in)": pressure_in,
            "Visibility(mi)": visibility_mi,
            "Wind_Speed(mph)": wind_speed_mph,
            "Wind_Chill(F)": wind_chill_f,
            "Precipitation(in)": precipitation_in
        }
        return weather_data

    def get_weather_data(self, location="San Jose"):
        import requests
        import datetime
        import os
        from dotenv import load_dotenv
        load_dotenv()


        api_key = os.getenv("WEAHTER_API")

        # Get today's date
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # Visual Crossing endpoint (daily or hourly)
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{today}?unitGroup=us&key={api_key}&include=current"

        try:
            response = requests.get(url)
            data = response.json()


            # Extract the current conditions
            current = data.get("currentConditions")
            if not current:
                raise ValueError("Missing 'currentConditions' in response")

            weather_data = {
                "Temperature(F)": current.get("temp", 65),
                "Humidity(%)": current.get("humidity", 50),
                "Pressure(in)": round(current.get("pressure", 1013) * 0.02953, 2),
                "Visibility(mi)": current.get("visibility", 10),
                "Wind_Speed(mph)": current.get("windspeed", 5),
                "Wind_Chill(F)": current.get("windchill", current.get("temp", 65)),
                "Precipitation(in)": round(current.get("precip", 0) * 0.03937, 2)
            }

            return weather_data

        except Exception as e:
            print(f"[Weather Fallback] Error: {e} — using default weather for {location}")
            return {
                "Temperature(F)": 65,
                "Humidity(%)": 50,
                "Pressure(in)": 29.92,
                "Visibility(mi)": 10,
                "Wind_Speed(mph)": 5,
                "Wind_Chill(F)": 65,
                "Precipitation(in)": 0.0
            }

    def get_weather_data_dev(self):
        # Dummy values; replace with real API/data
        return {
            "Temperature(F)": 72.0,
            "Humidity(%)": 50,
            "Pressure(in)": 29.92,
            "Visibility(mi)": 10,
            "Wind_Speed(mph)": 5,
            "Wind_Chill(F)": 70.0,
            "Precipitation(in)": 0.0
        }

    def get_transformed_data_v1(self, date_and_time, city, county, zipcode):
        # Step 1: Extract datetime and weather features
        base_data = {
            **self.get_date_data(date_and_time),
            **self.get_weather_data(city)
        }

        # Step 2: Extract zipcode group prefix
        valid_zip_groups = {
            col.split('_')[-1]
            for col in self.expected_columns
            if col.startswith("Zipcode_Group_")
        }
        zip_group = zipcode[:3] if zipcode[:3] in valid_zip_groups else "Other"

        # Step 3: Build raw data dict
        raw_data = {
            **base_data,
            "City": city,
            "County": county,
            "Zipcode_Group": zip_group,
        }

        # Step 4: Convert to single-row DataFrame
        df = pd.DataFrame([raw_data])

        # Step 5: One-hot encode location features
        df = pd.get_dummies(df, columns=["City", "County", "Zipcode_Group"])

        # Step 6: Add missing expected columns
        missing_cols = set(self.expected_columns) - set(df.columns)
        for col in missing_cols:
            df[col] = 0

        # Step 7: Reorder columns
        df = df[self.expected_columns]

        bool_cols = df.select_dtypes(include='bool').columns
        df[bool_cols] = df[bool_cols].astype("int64")

        # Only Standardization numerical columns
        cols_to_standardize = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)',
                               'Visibility(mi)', 'Wind_Speed(mph)', 'Wind_Chill(F)', 'Precipitation(in)', 'Hour']

        # Standardize numerical columns
        scaler = joblib.load("../models/scaler.pkl")
        scaled_data = scaler.transform(df[cols_to_standardize])

        # Make it back to a df
        scaled_df = pd.DataFrame(scaled_data, columns=cols_to_standardize)

        # Combine Standardize numerical df with Categorical df
        standardize_df = pd.concat([scaled_df, df.drop(columns=cols_to_standardize).reset_index(drop=True)],
                                   axis=1)

        pca = joblib.load("../models/pca_transformer.pkl")
        X_user_input_pca = pca.transform(standardize_df)

        # print(X_user_input_pca.shape)

        return X_user_input_pca



    def prediction(self, date_and_time, city, county, zipcode):

        data = self.get_transformed_data_v1(date_and_time,city,county, zipcode)
        model =  joblib.load("../models/model_version_4.pk1")
        result = model.predict(data)
        return result




d =DataExtractor()

#df = d.get_weather_data("Los Angele")


print("high")
print(d.prediction("08/03/2025, 23:45", "Los Angeles", "Los Angeles", "90003"))     # Late night in dense LA





