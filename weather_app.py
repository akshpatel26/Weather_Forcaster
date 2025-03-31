from datetime import datetime
import pyowm
import streamlit as st
from matplotlib import dates
from matplotlib import pyplot as plt

# Use streamlit secrets to fetch the secret ApiKey.
try:
    api_key = st.secrets["API_KEY"]
except:
    st.error("API Key not found in secrets. Please configure your secrets.toml file.")
    st.stop()

sign = u"\N{DEGREE SIGN}"
owm = pyowm.OWM(api_key)
mgr = owm.weather_manager()

st.title("Weather Forecaster :sun_behind_rain_cloud:")

st.write("### Enter the city name, choose a Temperature unit and a graph type from the bottom:")

# Improved location input with guidance
location = st.text_input(
    "Name of The City :", 
    placeholder="Format: City, Country Code (e.g., London, GB or New York, US)"
)

# Help section for location format
with st.expander("Need help with location format?"):
    st.markdown("""
    For best results, use the format: **City, CountryCode**
    
    Examples:
    - London, GB
    - New York, US
    - Paris, FR
    - Delhi, IN
    - Tokyo, JP
    - Sydney, AU
    
    Common country codes:
    - USA: US
    - United Kingdom: GB
    - India: IN
    - Canada: CA
    - Australia: AU
    - Germany: DE
    - France: FR
    - Japan: JP
    - China: CN
    
    Using the country code helps the weather service identify the correct city.
    """)

units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
graph = st.selectbox("Select Graph Type:", ('Bar Graph', 'Line Graph'))

if units == 'celsius':
    degree = 'C'
else:
    degree = 'F'

def get_temperature():
    """ Get the max and min temepature for the next 5 days using API call."""
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast

    days = []
    dates_list = []
    temp_min = []
    temp_max = []
    for weather in forecast:
        day = datetime.utcfromtimestamp(weather.reference_time())
        date = day.date()
        if date not in dates_list:
            dates_list.append(date)
            temp_min.append(None)
            temp_max.append(None)
            days.append(date)
        temp = weather.temperature(unit=units)['temp']
        if not temp_min[-1] or temp < temp_min[-1]:
            temp_min[-1] = temp
        if not temp_max[-1] or temp > temp_max[-1]:
            temp_max[-1] = temp
    return (days, temp_min, temp_max)

def plot_bar_graph_temp():
    """ Plot the bar graph of temperature data with the updated matplotlib approach """
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    
    # Get temperature data
    days, temp_min, temp_max = get_temperature()
    days_num = dates.date2num(days)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Style the plot
    plt.style.use('ggplot')
    ax.set_xlabel('Day')
    ax.set_ylabel(f'Temperature({sign}{degree})')
    ax.set_title("Weekly Forecast")
    
    # Plot data
    bar_x = ax.bar(days_num-0.25, temp_min, width=0.5, color='#42bff4', label='Min')
    bar_y = ax.bar(days_num+0.25, temp_max, width=0.5, color='#ff5349', label='Max')
    
    # Format x-axis
    ax.set_xticks(days_num)
    xaxis_format = dates.DateFormatter('%m/%d')
    ax.xaxis.set_major_formatter(xaxis_format)
    
    # Add legend
    ax.legend(fontsize='x-small')
    
    # Add text labels on bars
    y_axis_max = ax.get_ylim()[1]
    label_offset = y_axis_max * 0.1
    
    for bar_chart in [bar_x, bar_y]:
        for index, bar in enumerate(bar_chart):
            bar_height = bar.get_height()
            xpos = bar.get_x() + bar.get_width() / 2.0
            ypos = bar_height - label_offset
            label_text = f"{int(bar_height)}{sign}"
            ax.text(xpos, ypos, label_text, ha='center', va='bottom', color='white')
    
    # Display the plot in Streamlit
    st.pyplot(fig)

def plot_line_graph_temp():
    """ Plot the line graph of temperature data with the updated matplotlib approach """
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    
    # Get temperature data
    days, temp_min, temp_max = get_temperature()
    days_num = dates.date2num(days)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Style the plot
    plt.style.use('ggplot')
    ax.set_xlabel('Day')
    ax.set_ylabel(f'Temperature({sign}{degree})')
    ax.set_title("Weekly Forecast")
    
    # Plot data
    ax.plot(days_num, temp_min, label='Min', color='#42bff4', marker='o')
    ax.plot(days_num, temp_max, label='Max', color='#ff5349', marker='o')
    
    # Format x-axis
    ax.set_xticks(days_num)
    xaxis_format = dates.DateFormatter('%m/%d')
    ax.xaxis.set_major_formatter(xaxis_format)
    
    # Add legend
    ax.legend(fontsize='x-small')
    
    # Display the plot in Streamlit
    st.pyplot(fig)

def plot_humidity_graph():
    """ Plot the humidity graph with the updated matplotlib approach """
    st.write("_____________________________________")
    st.title("Humidity Index of 5 days")
    
    # Get humidity data
    days, humidity = get_humidity()
    days_num = dates.date2num(days)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Style the plot
    plt.style.use('ggplot')
    ax.set_xlabel('Day')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Humidity Forecast')
    
    # Format x-axis
    ax.set_xticks(days_num)
    xaxis_format = dates.DateFormatter('%m/%d')
    ax.xaxis.set_major_formatter(xaxis_format)
    
    # Plot data
    bars = ax.bar(days_num, humidity, color='#42bff4')
    
    # Add text labels on bars
    y_max = ax.get_ylim()[1]
    label_offset = y_max * 0.1
    
    for bar in bars:
        height = bar.get_height()
        xpos = bar.get_x() + bar.get_width() / 2.0
        ypos = height - label_offset
        label_text = f"{str(height)}%"
        ax.text(xpos, ypos, label_text, ha='center', va='bottom', color='white')
    
    # Display the plot in Streamlit
    st.pyplot(fig)

def weather_forcast():
    """ Show the current weather forecast."""
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    icon = weather.weather_icon_url(size='4x')

    temp = weather.temperature(unit=units)['temp']
    temp_felt = weather.temperature(unit=units)['feels_like']
    st.image(icon, caption= (weather.detailed_status).title())
    st.markdown(f"## 🌡️ Temperature: **{round(temp)}{sign}{degree}**")
    st.write(f"### Feels Like: {round(temp_felt)}{sign}{degree}")

    cloud = weather.clouds
    st.write(f"### ☁️ Clouds Coverage: {cloud}%")

    wind = weather.wind()['speed']
    st.write(f"### 💨 Wind Speed: {wind}m/s")

    humidity = weather.humidity
    st.write(f"### 💧 Humidity: {humidity}%")

    pressure = weather.pressure['press']
    st.write(f"### ⏲️ Pressure: {pressure}mBar")

    visibility = weather.visibility(unit='kilometers')
    st.write(f"### 🛣️ Visibility: {visibility}km")

def upcoming_weather_alert():
    """ Shows the upcoming weather alerts."""
    forecaster = mgr.forecast_at_place(location, '3h')
    flag = 0
    st.write("_____________________________________")
    st.title("Upcoming Weather Alerts")
    if forecaster.will_have_clouds():
        st.write("### - Cloud Alert ⛅")
        flag += 1
        if forecaster.will_have_rain():
            st.write("### - Rain Alert 🌧️")
            flag += 1
    if forecaster.will_have_snow():
        st.write("### - Snow Alert ❄️")
        flag += 1
    if forecaster.will_have_hurricane():
        st.write("### - Hurricane Alert 🌀")
        flag += 1
    if forecaster.will_have_tornado():
        st.write("### - Tornado Alert 🌪️")
        flag += 1
    if forecaster.will_have_fog():
        st.write("### - Fog Alert 🌫️")
        flag += 1
    if forecaster.will_have_storm():
        st.write("### - Storm Alert 🌩️")
        flag += 1
    if flag == 0:
        st.write("### No Upcoming Alerts!")

def sunrise_sunset():
    """ Show the sunrise and sunset time."""
    st.write("_____________________________________")
    st.title("Sunrise and Sunset")
    obs = mgr.weather_at_place(location)
    weather = obs.weather

    sunrise_unix = datetime.utcfromtimestamp(int(weather.sunrise_time()))
    sunrise_date = sunrise_unix.date()
    sunrise_time = sunrise_unix.time()

    sunset_unix = datetime.utcfromtimestamp(int(weather.sunset_time()))
    sunset_date = sunset_unix.date()
    sunset_time = sunset_unix.time()

    st.write(f"#### Sunrise Date: {sunrise_date}")
    st.write(f"### --Sunrise Time: {sunrise_time}")
    st.write(f"#### Sunset Date: {sunset_date}")
    st.write(f"### --Sunset Time: {sunset_time}")

def get_humidity():
    """ Get the humidity data of 5 days using API call."""
    days = []
    dates_list = []
    humidity_max = []
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast

    for weather in forecast:
        day = datetime.utcfromtimestamp(weather.reference_time())
        date = day.date()
        if date not in dates_list:
            dates_list.append(date)
            humidity_max.append(None)
            days.append(date)

        humidity = weather.humidity
        if not humidity_max[-1] or humidity > humidity_max[-1]:
            humidity_max[-1] = humidity

    return(days, humidity_max)

def validate_location(location_input):
    """Check if location is properly formatted"""
    if ',' in location_input:
        city, country = location_input.split(',', 1)
        country = country.strip()
        # Check if country code is likely valid (2 letters)
        if len(country) == 2:
            return True
    return False

if __name__ == '__main__':
    if st.button('Submit'):
        if location == '':
            st.warning('Provide a city name!!')
        else:
            try:
                # Check if the location is properly formatted
                if not validate_location(location) and ',' not in location:
                    st.warning(f"""
                    **For more accurate results, please use format: City, CountryCode**
                    
                    Examples:
                    - London, GB (not just London)
                    - New York, US (not just New York)
                    - Delhi, IN (not just Delhi)
                    
                    Attempting to search for "{location}" without country code...
                    """)
                
                weather_forcast()
                if graph == 'Bar Graph':
                    plot_bar_graph_temp()
                elif graph == 'Line Graph':
                    plot_line_graph_temp()

                upcoming_weather_alert()
                sunrise_sunset()
                plot_humidity_graph()
            except Exception as e:
                st.error("""
                ### Location Not Found!!
                
                To make search more precise put the city's name, comma, 2-letter country code.
                
                Examples:
                - London, GB
                - New York, US
                - Paris, FR
                - Delhi, IN
                - Tokyo, JP
                
                This helps avoid confusion between cities with the same name in different countries.
                """)
                
                # Suggestions for common cities
                st.info("""
                ### Common city formats:
                
                **United States:**
                - New York, US
                - Los Angeles, US
                - Chicago, US
                
                **India:**
                - Delhi, IN
                - Mumbai, IN
                - Bangalore, IN
                
                **United Kingdom:**
                - London, GB
                - Manchester, GB
                - Birmingham, GB
                """)