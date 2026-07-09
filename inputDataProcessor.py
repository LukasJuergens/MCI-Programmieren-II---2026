import pandas as pd
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units

class inputDataProcessor:
    def __init__ (self) -> None:
        # CSV einlesen
        self.data = pd.read_csv("final_project_input_data.csv", sep=';')
        
        # Daten auftrennen
        self.latDeg = self.data['lat']
        self.lat = np.radians(self.latDeg)
        self.lonDeg = self.data['lon']
        self.lon = np.radians(self.lonDeg)
        self.ele = self.data['ele']
        self.time = pd.to_datetime(self.data['time'])
        self.temp = self.data['temperature']

        # Platzhalter
        self.distances = None
        self.totalDistance = None
        self.seconds = None
        self.speeds = None
        self.accelerations = None

    def process(self) -> None:
        pass

    def calcDistance(self) -> None:
        """
        Berechnet die zurückgelegte Distanz zwischen zwei aufeinanderfolgenden Messpunkten
        """
        R = 6371 # Erdradius in km
        lat1 = self.lat
        lat2 = self.lat.shift(-1)
        lon1 = self.lon
        lon2 = self.lon.shift(-1)

        dlat = self.lat.diff().shift(-1)
        dlon = self.lon.diff().shift(-1)

        # Haversine
        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        self.distances = (2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))#.dropna()
        self.totalDistance = np.sum(self.distances)

    def calcIncline(self) -> None:
        """
        Berechnet die Steigung in rad zwischen den Messpunkten
        """

        dele = self.ele.diff().shift(-1)
        self.inclines = np.arctan(dele/self.distances)#.dropna()

    def calcTimeDiff(self) -> None:
        """
        Berechnet die Zeitdifferenz zwischen den Messpunkten und setzt self.seconds
        """
        timestampDiff = self.time.diff().shift(-1)
        self.seconds = timestampDiff.dt.total_seconds()#.dropna()
        

    def calcSpeed(self) -> None:
        """
        Berechnet die Momentangschwindigkeiten zwischen den Messpunkten
        """
        if self.distances is None or self.seconds is None:
            raise ValueError("Execute calcDistance() and calcTimeDiff() first!")
        self.speeds = (self.distances*1000) / self.seconds # m/s

    def calcAcceleration(self) -> None:
        """
        Berechnet die Momentanbeschleunigung zwischen den Messpunkten
        """
        if self.speeds is None or self.seconds is None:
            raise ValueError("Execute calcTimeDiff() and calcSpeed() first!")
        
        dv = self.speeds.diff().shift(-1)
        self.accelerations = (dv/self.seconds)#.dropna()

    def calcForce(self, m: float, cwA: float, ) -> None:
        """
        Berechnet die benötigte Kraft um das Ebike anzutreiben
        """
        g = 9.81
        Fg = m * g
        Fha = Fg / np.sin(self.inclines)

        # Luftdichte berechnen
        ele = self.ele * units("m")
        temp = self.temp*units("degC")
        pressure = mpcalc.height_to_pressure_std(ele)
        rho = mpcalc.density(pressure, temperature, mixing_ratio=0*units.unitless)

        Fd = 0.5 * rho * cwA * self.speeds**2
        Facc = m * self.accelerations
        self.Forces = Fd - Facc
        


if __name__ == "__main__":
    # Fahrrad daten
    m = 70 + 10 #kg
    cwA = 0.5625 #m^2 cw*A
    r = 27*0.0254 # Raddurchmesser in m
    Km = 1.5 # Nm/A

    data_input = inputDataProcessor()

    def printData(title, dataframe, unit):
        print()
        print(title)
        print(f"Max: {dataframe.max()} {unit}")
        print(f"Min: {dataframe.min()} {unit}")
        print(f"total: {dataframe.sum()} {unit}")
        print(f"mean: {dataframe.mean()} {unit}")
        print(dataframe)


    data_input.calcDistance()
    printData("Distances", data_input.distances, "km")    

    data_input.calcIncline()
    printData("Inclines", data_input.inclines, "rad")    

    data_input.calcTimeDiff()
    printData("Time", data_input.seconds, "s")    
    
    data_input.calcSpeed()
    printData("Speeds", data_input.speeds, "m/s")
    
    data_input.calcAcceleration()
    printData("Accelerations", data_input.accelerations, "m/s^2")    

    data_input.calcForce(m, cwA)
    printData("Forces", data_input.Forces, "N")