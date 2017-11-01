from pyowm import OWM
import time

class ToulouseWeather:

    def __init__(self):
        self.owm = OWM('0bb35d44e01c168892fc66f9e70914f4')
        self.toulouse = "Toulouse,fr"


    def get_current_temp_and_pressure(self):
        observation = self.owm.weather_at_place(self.toulouse)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')["temp"]
        pressure = w.get_pressure()["press"]
        return temp, pressure

    def is_day(self):
        observation = self.owm.weather_at_place(self.toulouse)
        w = observation.get_weather()
        sunrise = w.get_sunrise_time()
        print(sunrise)
        sunset = w.get_sunset_time()
        print(sunset)
        current_time = time.time()
        print(current_time)
        return ((current_time > sunrise) & (current_time < sunset))

if __name__ == "__main__":
    tw = ToulouseWeather()
    print(tw.is_day())
