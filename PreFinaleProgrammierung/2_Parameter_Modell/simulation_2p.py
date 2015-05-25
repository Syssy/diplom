#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Hoffentlich finale Version für die 2-Param Simulation

from __future__ import division
import pickle
import logging
import argparse
import time
import math

import scipy.stats   
#import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt

#import peak_width_2p

# Speichert alle interessanten Dinge einer Simulation ab
# Hat Methoden zur Simulation, sowie zur Berechnung von Peakdaten
class Simulation():
    """Simuliert und speichert Daten einer Simulation
    """
    version_number = 7.0
    
    def __init__(self, ps, pm, length, number, mode, step = 200, times = [], pd = (), version = version_number):
        """__init__
        
        ps, pm - Parameter; Wahrscheinlichkeit, stationaer/mobil zu bleiben, wenn ein Teilchen schon in diesem Zustand ist
        length - Laenge der Saule
        number - Anzahl simulierter Teilchen
        mode - Wie wird simuliert, each_timestep (T) oder by_event (E)
        times - Ankunftszeiten
        pd - aus den times errechnete Peakdaten: ((loc, scale), width, height)
        v - Versionsnummer eben ;)
        """
        self.params = (ps, pm)
        self.length = length
        self.number = number
        self.mode = mode
        self.step = step
        if times:
            self.times = times
            self.mean = np.mean(self.times)
            self.variance = np.var(self.times)
            self.skewness = scipy.stats.skew(self.times)
            self.kurtosis = scipy.stats.kurtosis(self.times)
        # peakdaten der form: ((loc,scale),width,height)
        if pd:
            self.pd = pd
        self.version = version

    #Fuer das Sortieren einer Liste von Simulationen, als key = ...
    def get_ps(self):
        return self.params[0]
    
    def get_pm(self):
        return self.params[1]

    def _simulate_step(self, locations, mobile_states, number):
        """Simuliere einen Schritt für alle Teilchen innerhalb der each_timestep-Simulation
        
        Wahrscheinlichkeit stationaer/mobil zu bleiben, Zugriff über self.params
        (new_)locations -- np-array aller Orte vor bzw. nach diesem Aufruf
        (new_)mobile_states -- np-array aller Teilchenstates vor bzw. nach diesem Aufruf
        number -- Anzahl der zu simulierenden Teilchen, nicht immer gleich self.number, da es am Ende weniger werden
        """
        zzv = np.random.random(number)
        zzv2 = zzv < self.params[0]
        zzv3 = zzv < self.params[1]
        #berechne neuen Zustand für die Teilchen    
        # entweder: vorher mobil und bleibe es (zzv3, pm)
        # oder: war nicht mobil und bleibe nicht (invertiert zu oder)
        new_mobile_states =  np.bitwise_or(np.bitwise_and(mobile_states, zzv3), (np.invert(np.bitwise_or(mobile_states, zzv2))))
        # wenn mobil, addiere 200 zum Ort; Festlegung auf 0.2mm mitte November 2014
        new_locations = locations + (self.step * new_mobile_states)
               
        return new_locations, new_mobile_states

    def simulate_each_timestep(self):
        """ Simuliere jeden Zeitschritt fuer jedes Teilchen"""
        # starttime für Laufzeitmessungen
        starttime = time.clock()
        # Wird Liste aller Ankunftstimes
        arrival_counter = []
        # Simulationszeit in Sekunden
        time_needed = 0
        # Anzahl zu simulierender Teilchen
        number = self.number
        self.mode="T"
        time_step = 1
        
        # aktuelle Orte der Teilchen
        locations = np.zeros(number)
        # akutelle Zustaende der Teilchen 
        mobile_states = np.array([True]*number)
    
        #Teil 1: Sim bis frueheste Teilchen ankommen koennen, hier muss noch keine Abbruchbed. getestet werden. 
        # Carrier ist nach length Schritten durch bei einzelschritten, sonst bei length/step
        while time_needed < self.length/self.step:
            locations, mobile_states = self._simulate_step(locations, mobile_states, number)
            time_needed += time_step
        logging.log(20, "Teil1 vorbei, zeit:%s, simdauer:%s", time_needed, time.clock()-starttime)
        #Teil 2: Ab jetzt koennen Teilchen fertig sein, teste erst, dann x neue Runden
        while True:
            # d ist bitmaske aller aktuell angekommenen Teilchen
            d = locations <= self.length
            logging.log(15, "in der trueschleife, zeit: %s, d:%s", time_needed, len(d))
            # die beiden Arrays aktualisieren (rauswerfen aller fertigen Teilchen)
            locations = locations[d]
            mobile_states = mobile_states[d]   
            #zähle (suminvert...) wie viele schon durch, haenge deren Zeiten ans Ergebnis an
            for j in range(np.sum(np.invert(d))):
                arrival_counter.append(time_needed)

            # Abbruchbedingung: alle teilchen angekommen :) oder Simulation dauert schon zu lange :(
            number = len(locations)
            if number < 1:
                logging.log(25, "fertig, simzeit: %s, realtime: %s", time_needed, (time.clock()-starttime))
                break
            if time_needed > 2400*(self.length/self.step):#24000000:
                logging.log(30, "Überschreitung der Maximalzeit von 240s, %s", (time.clock()-starttime))
                # alle noch nicht fertigen Teilchen bekommen 100 Sek Strafe, damit man sieht, dass Simulation nicht zu Ende durchgefuehrt wurde
                for j in range(len(locations)):
                    arrival_counter.append(time_needed+(self.length/self.step)*1000)
                break    
            
            # Damit es schneller geht, nach je x schritten nur testen
            for x in range (1):
                locations, mobile_states = self._simulate_step(locations, mobile_states, number)
                time_needed+=time_step
        
        self.times = [date/10000 for date in arrival_counter]
       
    def _test_finished(self, particle_list):
        """Teste, ob die Teilchen schon durch sind. Aufruf durch simulate_by_event"""
        
        #extrahiere nicht fertige Teilchen als (zustands-ort)-Paare
        particles = [(state, location) for state, location in particle_list if location < self.length]
        
        #extrahiere zeiten fertiger Teilchen
        times = [(location-self.length)/self.step for state, location in particle_list if location >= self.length]
        
        #Rueckgabe der nicht fertigen Teilchen und Ankunftszeiten fertiger Teilchen
        return particles, times
        
    def _simulate_event(self, particle_list):
        """Simuliere ein zeitliches Event, gebe neue Ereignisliste zurueck, Aufruf durch simulate_by_event"""
        
        # extrahiere je eine liste von Zustaenden und Orten
        states, locations = zip(*particle_list)
        
        # Geometrisch verteilt: Zeitspannen bis zum naechsten Erfolg, jeweils fuer alle Teilchen und fuer ps und pm
        periods_ps = scipy.stats.geom.rvs(1-self.params[0], size = len(particle_list))
        periods_pm = scipy.stats.geom.rvs(1-self.params[1], size = len(particle_list))
        
        #fuer pm nur die mobilen Zustaende relevant
        periods_pm *= states
        # Zustaende aendern
        states = [not x for x in states]
        # fuer ps nur die neuen mobilen Zustaende relevant
        periods_ps *= states        
        #neue events nach den jeweilig relevanten Zeitspannen erstellen
        periods = periods_pm + periods_ps
        
        # gehe nur bei den mobilen Zustaenden weiter
        locations += (periods_pm * self.step)  
        logging.log(10, "locations %s", locations[0:10])
        
        new_events = list(zip(periods, states, locations))
        
        return new_events
        
    def simulate_by_event(self):
        """Simuliere mit Hilfe einer Liste von Events"""
        starttime = time.clock()
        logging.log(25, "simuliere %s", self.params)
        length = self.length
        number = self.number
        self.mode = "E"
        act_time = 0
    
        # Ereignisse als dict. Jeweils als key einen Zeitpunkt (enthaelt nur diejenigen, wo auch was passiert, Vergangenheit wird geloescht) und eine Liste aller Teilchen, mit denen dann was passieren soll
        events = {}
        hl = list()
        # Init: Zu Zeitpunkt 0 passiert mit allen Teilchen was
        # Teilchen repraesentiert als Tupel von Zustand (0=stat, 1=mob) und Ort
        for i in range(number):
            hl.append((True, 0))
        events[act_time]=hl
        #act_time = 1
        
        # Hier kommen die Ankunftszeiten rein
        arrival_counter = []
        
        # solange noch Ereignisse ausstehen, wird simuliert
        while len(events) >= 1:
            if act_time in events:
                #print (events)
                logging.log(15, "betrachte zeitpunkt %s", act_time)
                # teste, ob zum aktuellen Zeitpunkt schon Teilchen fertig, fuege deren Zeiten ein
                particle_list = np.array(events[act_time])
                particle_list, times = self._test_finished(particle_list)
                arrival_counter.extend([(act_time-(date)) for date in times])
                
                #logging.log(5, "noch da2, %s", arrival_counter)
                # Falls die Teilchen dieses Zeitpunktes alle durch sind, wird nicht mehr simuliert
                # sonst Simulation aller uebriger Teilchen
                if len(particle_list) > 0:
                    new_events = self._simulate_event(particle_list)
                    for timediff, state, location in new_events:
                        try:
                            # Zeitpunkt schon vorhanden -> einfuegen
                            events[act_time + timediff].append((state, location))
                        except KeyError as err:
                            # Zeitpunkt nicht vorhanden -> erstellen
                            events.update({act_time + timediff:[(state, location)]})
                ##Zeitpunkt abgearbeitet, Vergangenheit loeschen                         
                del events[act_time]
            #naechste Zeit betrachen    
            act_time += 1  
        # Zeitpunkte normalisieren    
        self.times = [date/10000 for date in arrival_counter]
        logging.log(25, "fertig, simschritte: %s, realtime: %s", act_time, (time.clock()-starttime))
        
    def set_pd(self, pd, v = version_number):
        """setzt Peakdaten und Versionsnummer neu, falls veraltet, nicht vorhanden, nicht zu gebrauchen"""
        self.pd = pd
        self.version = v

    def __repr__(self):
            return (str(self.params) + self.mode)
        
    def get_moment(self, moment):
        """Gebe den Wert des moment zurück."""
        if moment == "mean":
            return self.mean
        if moment == "variance":
            return self.variance
        if moment == "skewness":
            return self.skewness
        if moment == "kurtosis":
            return self.kurtosis
        return None
        
    def simulate(self, mode = None):
        '''Simuliert je nach Modus, TODO: Achtung, Direktaufruf der Simulationsmethoden fuehrt zu potenziell falsch eingetragenem Mode'''
        if self.mode == "E" or mode == "E":
            self.simulate_by_event()
        elif self.mode == "T" or mode == "T":
            self.simulate_each_timestep()
        else:
            print ("Bitte gewuenschten Simulationsmodus mit angeben ", self.mode, "nicht gueltig")
    
    def _find_intersection(self, fun1, fun2, x0):
        '''finde Schnittpunkt zweier Funktionen (fun1, fun2) ausgehend von geschätzten Wert(en) x0'''
        return scipy.optimize.fsolve(lambda x : fun1(x) - fun2(x), x0)      
    
    def calculate(self):
        """Berechne Momente, Breite und Hoehe bei halber Peakhoehe, sowie Loc und Scale, ausgehend von Gaussverteilung"""
        # Momente berechnen
        self.mean = np.mean(self.times) 
        self.variance = np.var(self.times)
        self.skewness = scipy.stats.skew(self.times)
        self.kurtosis = scipy.stats.kurtosis(self.times)
        
        # Peakdaten berechnen
        # Finde Parameter fuer passende Gausskurve zum Schneiden
        loc_n, scale_n = scipy.stats.norm.fit(self.times)
        # halben Maximalwert berechnen
        halfmax = 1/(math.sqrt(2*math.pi)*scale_n *2)
        #print ("halfmax", halfmax)
            
        # Funktionen erstellen, die dann für die find intersections genutzt werden. TODO: Hier noch andere verteilungen ermöglichen
        # Funktion der Normalverteilung.
        norm = lambda x: np.exp(-(x-loc_n)**2 / (2*scale_n**2)) / math.sqrt(2*math.pi * scale_n**2)
        # Funktion einer Linie
        linie = lambda x: halfmax + 0*x
        # print ("max bei", norm(loc), "starte test bei:", loc-scale, loc+scale)
        # finde Schnittpunkte zwischen Linie auf halber Hoehe und Gausskurve, Startwerte sind median +- standardabweichung
        intersections = self._find_intersection(linie, norm, [loc_n+scale_n, loc_n-scale_n])
        logging.log(15, "Intersections %s", intersections)
        
        #width ist Abstand zwischen den Schnittpunkten
        width = abs(max(intersections) - min(intersections))
        ls =  (loc_n, scale_n)
        pd = (ls, width, halfmax)
        self.set_pd(pd)

# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "beschreibung")  
    p.add_argument("--inputfile", "-i", type = str,  help = "input file (pickled)")
    p.add_argument("--moment", "-m" , help = "which moment is of interest")
    p.add_argument("--recalc", "-rc", type=str, help = "recalculate moments")
    p.add_argument("--number", "-n", help = "how many files to recalculate")
    
    return p

# Nutzung für Testzwecke
def main():
    number = 1000
    length = 200000
    print ("n", number, "l", length, time.strftime("%d%b%Y_%H:%M:%S"))
    p = get_argument_parser()
    args = p.parse_args()
    neueSim = Simulation(0.000999, 0.999999, length, number, None, 20)
  
    neueSim.simulate_by_event()
    neueSim.calculate()
    print("pd by event", neueSim.pd, len(neueSim.times))
    n, bins, patches = plt.hist(neueSim.times, 50, alpha=0.5)   
    plt.ylabel("")
    plt.xlabel("Zeit / s")
    plt.title("ps: "+ str(neueSim.params[0])+" pm: "+ str(neueSim.params[1]) + " by event")
    plt.show()
    
    neueSim.simulate_each_timestep()
    neueSim.calculate()
    #print ("times by step", neueSim, neueSim.times)
    print ("pd by timestep", neueSim.pd, len(neueSim.times))
    n, bins, patches = plt.hist(neueSim.times, 50, alpha=0.5)
    plt.xlabel("Zeit / s")
    plt.title("ps: "+ str(neueSim.params[0])+" pm: "+ str(neueSim.params[1]) + " by timestep")
    #neueSim.calculate()
    #print (neueSim.params, neueSim.mean, neueSim.pd, neueSim.pd[0])
    plt.show()
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()
