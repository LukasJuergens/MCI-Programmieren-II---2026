class BatteryPack:
    """
    Class for simulationg a BatteryPack
    """
    def __init__(
        self,
        capacity_nom_Ah: float,
        voltage_profile: dict[float, float],
        internal_resistance_mOhm: float = 80.0,
        initial_soc: float = 1.0,
        Vmin: float = 3.0,
        Vmax: float = 4.2,
    ):
        """
        args:
            capacity_nom_Ah: capacity of the BatteryPack in Ah (must be over 0.0)
            voltage_profile: a dict in the form of [soc between 0.0 and 1.0, Voltage in V] (minimum 2 entrys)
            internal_resistance_mOhm: The internal resistance of the BatteryPack (must be at least 0.0)
            initial_soc: The initial State of Charge between 0.0 an 1.0
            Vmin: minimal Voltage of the BatteryPack
            Vmax: maximum Voltage of the BatteryPack
        """

        if capacity_nom_Ah <= 0:
            raise ValueError("Kapazität muss über 0 sein")
        self.capacity_nom_Ah = capacity_nom_Ah

        if len(voltage_profile) < 2:
            raise ValueError("Spannungsprofil muss mindestens 2 Einträge haben")
        for soc, voltage in voltage_profile.items():
            if not 0 <= soc <= 1:
                raise ValueError("Alle SoC-Werte müssen zwischen 0 und 1 sein")
            if not Vmin <= voltage <= Vmax:
                raise ValueError("Alle Spannungen müssen zwischen Vmin und Vmax sein")
        self.voltage_profile = voltage_profile

        if internal_resistance_mOhm < 0:
            raise ValueError("Innenwiderstand muss mindestens 0 sein")
        self.internal_resistance_mOhm = internal_resistance_mOhm

        if not 0 <= initial_soc <= 1:
            raise ValueError("State of charge muss zwischen 0 und 1 sein")
        self.soc = initial_soc

        self.Vmin = Vmin

        self.Vmax = Vmax



    def apply_current(self, current: float, duration: float) -> None:
        """
        calculates the state of charge after a current is applied

        args:
            current: current in Amps
            time: timeduration in hours (must be positive)
        A positiv current means the Battery charges, while a negative means it discharges
        """

        if duration < 0:
            raise ValueError("Zeitdauer muss positiv sein")
        self.soc += current*duration/self.capacity_nom_Ah
        if self.is_full():
            self.soc=1
        elif self.is_empty():
            self.soc=0
            raise ValueError("Akkustand darf nicht unter 0% fallen.")



    def is_empty(self) -> bool:
        return self.soc <= 0



    def is_full(self) -> bool:
        return self.soc >= 1



    def voltage(self, current: float = 0.0) -> float:
        """
        calculates the voltage of the BatteryPack based on the current applied to it

        args:
            current: current in Amps
        A positive current means the Battery charges, a negative current means it discharges
        """

        soc_values = list(sorted(self.voltage_profile))
        for idx in range(1, len(soc_values)):
            if soc_values[idx] >= self.soc:
                voltage = (self.voltage_profile[soc_values[idx]]-self.voltage_profile[soc_values[idx-1]])*(self.soc-soc_values[idx-1])/(soc_values[idx]-soc_values[idx-1])+self.voltage_profile[soc_values[idx-1]]+current*self.internal_resistance_mOhm/1000
                return voltage
        raise ValueError(f"Das Spannungsprofil deckt den aktuellen State of Charge {self.soc} nicht ab")



    def __str__(self):
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.voltage():.2f} V)"
    


    @staticmethod
    def calculate_min_capacity_Ah(currents, cell_capacity=5):
        time_defferences = currents.index.to_series().diff().dt.total_seconds().fillna(1)
        currents = currents.fillna(0)
        charges = time_defferences*currents.values
        capacities = charges.cumsum()/3600
        capacities = capacities - capacities.min()
        return (int(capacities.max()/cell_capacity)+1)*cell_capacity, capacities.iloc[-1]






if __name__ == "__main__":
    batteryPack = BatteryPack(3, {0.00: 32.00, 
                                  0.04: 35.87,
                                  0.09: 36.85,
                                  0.13:	37.56,
                                  0.17:	37.87,
                                  0.21:	38.28,
                                  0.26:	38.81,
                                  0.30:	39.05,
                                  0.40:	39.55,
                                  0.52:	40.27,
                                  0.64:	40.70,
                                  0.76:	41.16,
                                  0.88:	41.65,
                                  1.00:	42.00}, 8, 1, 32, 42)
    print(batteryPack.is_empty())
    print(batteryPack.is_full())
    print(batteryPack.voltage(1))
    batteryPack.apply_current(-1, 1)
    print(batteryPack.voltage(1))
