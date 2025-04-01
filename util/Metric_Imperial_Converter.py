import re
class convert:
    precision = 2
    supported_systems = ["metric", "imperial"]
    float_part_of_string = r"-?\d*\.\d+|-?\d+"

    def __init__(self, system: str):
        if system not in self.supported_systems:
            raise ValueError('unit system not supported')
        else:
            self.system = system

    def temperature(self, temp_string: str):
        try:
            fahrenheit = float(re.findall(self.float_part_of_string, temp_string)[0]) if temp_string else 'NA'

            if self.system == "metric":
                return round((fahrenheit - 32) * 5 / 9, self.precision)
            else:
                return fahrenheit

        except Exception as e:
            print(f'{e}! Empty data row')
            return 'NA'

    def dew_point(self, dew_point_string: str):
        try:
            fahrenheit = float(
                re.findall(self.float_part_of_string, dew_point_string)[0]) if dew_point_string else 'NA'
            if self.system == "metric":
                return round((fahrenheit - 32) * 5 / 9, self.precision)
            else:
                return fahrenheit

        except Exception as e:
            print(f'{e}! Empty data row')
            return 'NA'

    def humidity(self, humidity_string: str):
        try:
            humidity = float(re.findall(self.float_part_of_string, humidity_string)[0]) if humidity_string else 'NA'
            return humidity

        except Exception as e:
            print('Empty data row')
            return 'NA'

    def speed(self, speed_string: str):
        try:
            mph = float(re.findall(self.float_part_of_string, speed_string)[0]) if speed_string else 'NA'
            if self.system == "metric":
                kmh = mph * 1.609
                return round(1.609*mph, self.precision)
            else:
                return mph

        except Exception as e:
            print('Empty data row')
            return 'NA'

    def pressure(self, pressure_string: str):
        try:
            inhg = float(re.findall(self.float_part_of_string, pressure_string)[0]) if pressure_string else 'NA'
            if self.system == "metric":
                return round(inhg*33.86389, self.precision)
            else:
                return inhg

        except Exception as e:
            print(f'{e}! Empty data row')
            return 'NA'

    def precipitation(self, precip_string: str):
        try:
            inches = float(re.findall(self.float_part_of_string, precip_string)[0]) if precip_string else 'NA'
            if self.system == "metric":
                return round(inches*25.4, self.precision)
            else:
                return inches

        except Exception as e:
            print(f'{e}! Empty data row')
            return 'NA'

    def clean_and_convert(self, dict_list: list):
        converted_list = []
        for dict in dict_list:
            converted = {}
            for key, value in dict.items():
                if key == 'Date':
                    converted['Date'] = value
                if key == 'Time':
                    converted['Time'] = value
                if key == 'Temperature':
                    converted['Temperature'] = self.temperature(value)
                if key == 'Dew_Point':
                    converted['Dew_Point'] = self.dew_point(value)
                if key == 'Humidity':
                    converted['Humidity'] = self.humidity(value)
                if key == 'Wind':
                    converted['Wind'] = value
                if key == 'Wind Speed':
                    converted['Wind Speed'] = self.speed(value)
                if key == 'Wind Gust':
                    converted['Gust'] = self.speed(value)
                if key == 'Pressure':
                    converted['Pressure'] = self.pressure(value)
                if key == 'Precip.':
                    converted['Precip_Rate'] = self.precipitation(value)
                if key == 'Condition':
                    converted['Condition'] = value


            converted_list.append(converted)

        return converted_list