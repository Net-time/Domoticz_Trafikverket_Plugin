# Domoticz_Trafikverket_Plugin
Fetches weather data from Swedish road weather station

Why buy your own when there is a open API :)

## Compability
Tested on Rasbian Buster.
Domoticz:
Version: 2020.2
Python Version: 3.7.3 

## Futures
Reads weather station data from Trafikverket.
The road stations does not have a barometer.

## Support
Not likley.

# Usage
Create a folder "Trafikverket" in Domotics/Plugins and copy plugin.py there.

Restart Domoticz.

Add "Trafikverket API" in the Hardware tab.

Leave Trafikverket API and Data Format as is.
Change Road Station to the one closest to you.
https://www.trafikverket.se/trafikinformation/vag/?TrafficType=personalTraffic&map=4.4250257533028705%2F638264.05%2F6710984.49%2F&Layers=RoadWeather%2b

Insert your personal API-Key that you got from:
https://api.trafikinfo.trafikverket.se/Account/Register


### Build Status
Thrown together with no respect at all for Python3 or standards.

Todo\:
- [ ] Cleanup code
- [x] Finish basic README
- [x] Initial upload
