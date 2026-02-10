# WeatherPeg

## Broadcast friendly weather software

![screenshot of full mode of WeatherPeg](images/image0.png)

### Prerequisites

- Python 3.10 or higher
- `pip` package manager
- coordinates of the location you want to get weather data for (latitude and longitude)

### Running the application

1. Clone the repository or download the source code.

2. Install the required dependencies using pip:

   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   ```

3. Update the txt/source.txt file with the link to the RSS feed for weather. Example: Navigating to ```https://weather.gc.ca/en/location/index.html?coords=49.895,-97.135``` and scrolling down to the RSS feed icon, click that and copy the URL and paste it into the txt/source.txt file. Example (and default): ```https://weather.gc.ca/rss/weather/49.895_-97.135_e.xml```

4. Run the application:

   ```bash
   #!/bin/bash
   python main.py
   ```

### Features

- Displays current weather conditions, forecasts, and warnings.
- Configurable GUI with options for full-screen mode, windowed mode, and customizable colors.

### Common problems

- **Issue**: The application does not display weather data or shows an error message.
  - **Solution**: Ensure that the RSS feed URL in `txt/source.txt` is correct and accessible. Check your internet connection and try again.
- **Issue**: The application gets stuck opening a small white box
- **Solution**: This is likely due to failing to fetch weather information. Check the RSS feed URL and your internet connection.
- **Issue**: The radar image does not open or shows an error.
  - **Solution**: Ensure that the radar image URL is correct and accessible. Check your internet connection and try again.
