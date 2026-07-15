import pandas as pd
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units
from scipy.signal import savgol_filter
from typing import Literal
import osmnx as ox

class inputDataProcessor:
    def __init__ (self) -> None:
        # CSV einlesen und präventiv nach der Zeit sortieren
        data = pd.read_csv("final_project_input_data.csv", sep=';')
        data['time'] = pd.to_datetime(data['time']) 
        data = data.sort_values('time') # neu sortieren

        data.set_index('time', inplace=True) # zeit als neuen Index setzen
        
        # daten resamplen und in 1s raster zwingen (zu kleine Messabstände werden gemittelt zu große werden NaN gesetzt)
        data = data.resample('1s').mean() 
        data = data.interpolate(method='linear') # füllt NaN Lücken
        
        # FILTERN
        windowLength = 31 # muss ungerade sein
        order = 2
        
        data['lat'] = savgol_filter(data['lat'], window_length=windowLength, polyorder=order)
        data['lon'] = savgol_filter(data['lon'], window_length=windowLength, polyorder=order)
        data['ele'] = savgol_filter(data['ele'], window_length=windowLength, polyorder=order)

        # Daten auftrennen
        self.time = data.index
        self.timeSinceStart = 0
        self.lat = data['lat']
        self.lon = data['lon']
        self.ele = data['ele']
        self.temp = data['temperature']

        self.timeTotal = (self.time[len(self.time)-1] - self.time[0])

        # Platzhalter
        self.distances = None
        self.distanceTotal = None
        self.inclines = None
        self.speeds = None
        self.speedMean = None
        self.accelerations = None
        self.forces = None
        self.torques = None
        self.powers = None
        self.powerMax = None
        self.currents = None

    def process(self, m:float=80, cwA:float=0.5625, d:float=27*0.0254, Km:float=1.5, PrekMax:float=200, cr:float = 0.005) -> None:
        """
        Berechnet folgende Werte zwischen den Messpunkten
        - Distanz
        - Himmelsrichtung
        - Steigung und Höhenunterschied
        - Geschwindigkeit
        - Beschleunigung
        - Kraft
        - Drehmoment
        - Motorstrom
        - Leisung

        Sowie folgende Gesamtwerte:
        - Durchschnittsgeschwindigkeit
        - Zurückgelgte Strecke
        - Benötigte Zeit
        - Maximalleistung

        Es werden folgende Inputs benötigt:
        - m: Masse von Fahrer und Fahrrad in kg
        - cwA: das Produkt aus Windangriffsfläche A und dem Strömungskoeffizienten c_w in m^2
        - d: Raddurchmesser in m
        - Km: Motorkonstante in Nm/A
        - PrekMax: Maximale Rekuperationsleistung
        - cr: Reibungskoeffizient
        """
        
        self._calcDistance()
        self._calcCardinalDirection()
        self._calcIncline()
        self._calcSpeed()
        self._calcAcceleration()
        self._calcForce(m, cwA, PrekMax, cr)
        self._calcTorque(d/2)
        self._calcCurrent(Km)
        self._calcPower()

    def _calcDistance(self) -> None:
        """
        Berechnet die zurückgelegte Distanz zwischen zwei aufeinanderfolgenden Messpunkten sowie die gesamte zurückgelegte Strecke
        """
        R = 6371000 # Erdradius in m
        lat1 = np.radians(self.lat)
        lon1 = np.radians(self.lon)
        lat2 = lat1.shift(-1)
        lon2 = lon1.shift(-1)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine
        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        self.distances = (2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
        self.distanceTotal = self.distances.sum()

    def _calcCardinalDirection(self) -> None:
        """
        Berechnet die Fahrtrichtung in Haupt und Nebenhimmelsrichtungen
        """
        lat1 = np.radians(self.lat)
        lon1 = np.radians(self.lon)
        lat2 = lat1.shift(-1)
        lon2 = lon1.shift(-1)

        bearings = ox.bearing.calculate_bearing(lat1, lon1, lat2, lon2)
        self.cardinalDirections = (np.round(bearings/45)*45) % 360
        directionMap = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
        self.cardinalDirections = self.cardinalDirections.map(directionMap)

    def _calcIncline(self) -> None:
        """
        Berechnet die Steigung in rad zwischen den Messpunkten
        """
        if self.distances is None:
            raise ValueError("Execute calcDistance() first!")
        
        self.eleDiff = self.ele.diff().shift(-1)
        self.eleDiff = self.eleDiff.clip(lower=-0.3)        
        self.inclines = np.arctan(self.eleDiff/self.distances)
        

    def _calcSpeed(self) -> None:
        """
        Berechnet die Momentangschwindigkeiten zwischen den Messpunkten
        """
        if self.distances is None:
            raise ValueError("Execute calcDistance() first!")
        
        # v = s/t
        self.speeds = (self.distances) / 1 # m/s
        self.speedMean = self.speeds.mean()

    def _calcAcceleration(self) -> None:
        """
        Berechnet die Momentanbeschleunigung zwischen den Messpunkten
        """
        if self.speeds is None:
            raise ValueError("Execute calcSpeed() first!")
        
        dv = self.speeds.diff().shift(-1)
        # a = dv/dt
        self.accelerations = (dv/1)

    @staticmethod
    def EnvironmentToFrictionCoefficient(
        bikeType:Literal["mountainbike", "racebike", "gravelbike"], 
        roadSurface:Literal["asphalt", "gravel"]) -> float:

        match (bikeType.lower(), roadSurface.lower()):
            case ("racebike", "asphalt"): cr = 0.0035
            case ("racebike", "gravel"):  cr = 0.01
            
            case ("gravelbike", "asphalt"): cr = 0.005
            case ("gravelbike", "gravel"):  cr = 0.0075
            
            case ("mountainbike", "asphalt"): cr = 0.014
            case ("mountainbike", "gravel"):  cr = 0.018
            
            case _: cr = 0.005

        return cr
 
    def _calcForce(self, m:float, cwA: float, PrekMax: float, cr: float) -> None:
        """
        Berechnet die benötigte Kraft um das Ebike anzutreiben
        """
        if self.inclines is None or self.speeds is None or self.accelerations is None:
            raise ValueError("Execute calcIncline(), calcSpeed() and calcAcceleration() first!")
        
        g = 9.81
        Fg = m * g
        Fha = Fg * np.sin(self.inclines)
        Fn = Fg * np.cos(self.inclines)
        Fr = Fn * cr

        # Luftdichte berechnen
        ele = self.ele.to_numpy() * units["m"]
        temp = self.temp.to_numpy() * units["degC"]
        pressure = mpcalc.height_to_pressure_std(ele)
        rho = mpcalc.density(pressure, temp, mixing_ratio=0)

        Fd = 0.5 * rho * cwA * self.speeds**2
        Facc = m * self.accelerations
        self.forces = Facc + Fd + Fha + Fr
        # Maximale Rekuperation einstellen:
        # P = F * v    --> F = P/v
        # speeds wird geclipt, damit keine division durch 0 entstehen kann
        self.forces = self.forces.clip(lower=-abs(PrekMax)/self.speeds.clip(lower=0.1))
        
    def _calcTorque(self, r: float) -> None:
        """
        Berechnet das Drehmoment, welches der Nabenmotor aufbringen muss

        r ist der Raddurchmesser
        """
        if self.forces is None:
            raise ValueError("Execute calcForce() first!")
        
        self.torques = r * self.forces

    def _calcCurrent(self, Km: float) -> None:
        """
        Berechnet den Motorstrom
        """
        if self.torques is None:
            raise ValueError("Execute calcTorque() first!")
        if Km == 0:
            raise ValueError("Km cant be 0")
        
        self.currents = self.torques / Km

    def _calcPower(self) -> None:
        """
        Berechnet die Leistung, welche der Motor aufbringen muss
        """
        if self.speeds is None or self.forces is None:
            raise ValueError("Execute calcSpeed() and calcForce() first!")
        
        self.powers = self.forces * self.speeds
        self.powerMax = self.powers.max()

if __name__ == "__main__":
    # Fahrrad daten
    m = 70 + 10 #kg
    cwA = 0.5625 #m^2 cw*A
    r = 27*0.0254 # Raddurchmesser in m
    Km = 1.5 # Nm/A

    dataProcessor = inputDataProcessor()
    dataProcessor.process(m, cwA, r, Km, 200)

    def printData(title, dataframe, unit):
        print()
        print(title)
        print(f"Max: {dataframe.max()} {unit}")
        print(f"Min: {dataframe.min()} {unit}")
        print(f"total: {dataframe.sum()} {unit}")
        print(f"mean: {dataframe.mean()} {unit}")
        #print(dataframe)

    printData("Distances", dataProcessor.distances, "m")    
    printData("Inclines", dataProcessor.inclines, "rad")       
    printData("EleDiff", dataProcessor.eleDiff, "m")    
    printData("Speeds", dataProcessor.speeds, "m/s")
    printData("Accelerations", dataProcessor.accelerations, "m/s^2")    
    printData("Forces", dataProcessor.forces, "N")
    printData("Torques", dataProcessor.torques, "Nm")
    printData("Currents", dataProcessor.currents, "A")
    printData("Powers", dataProcessor.powers, "W")

