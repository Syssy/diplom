#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Finale Version für die Teilchensimulation mit zwei Zuständen

from __future__ import division
import pickle
import logging
import argparse
import time
import math
from collections import Counter

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt


# Speichert alle interessanten Dinge einer Simulation ab
# Hat Methoden zur Simulation, sowie zur Berechnung von Peakdaten
class Simulation():
    """Simuliert und speichert Daten einer Simulation
    """
    
    def __init__(self, params, model, length = 1000, times = [], maxtime = 240, number = 1000, approach = "E"):
        """__init__
        params - Parameter ps,pm bzw pmm,pml,paa,pll
        model - 2s/3s 
        length - Laenge der Säule
        times - Ankunftszeiten
        maxtime - Maximale Zeit in Sekunden
        number - Anzahl simulierter Teilchen
        approach - Wie wird simuliert, each_timestep (T) oder by_event (E)
        """
        self.params = params
        if model:
            self.model = model
        else:
            self.set_model()
        self.length = length
        if times:
            self.times = times
            # peakdaten der form (loc, [quartile], iqr, qk) berechnen, valid-flag setzen
            self.calculate_pd()
        self.maxtime = maxtime
        self.number = number
        self.approach = approach
#TODO Valid Flag. Wo setzen?

    def set_model(self):
        '''Aus der Anzahl der Parameter das dahinter liegende Modell extrahieren'''
        if len(self.params) == 2:
            self.model = "2s"
        elif len(self.params) == 4 or len(self.params) == 6 or len(self.params) == 9:
            self.model = "3s"
        else:
            self.model = "unbekanntes Modell"
            logging.log(40, "Falsche Anzahl Parameter, Kein Modell erkennbar. %s", self.params)

    def calculate_pd(self):
        """Peakdaten, (Lage, [Quartile], IQK und QK), setze Valid-Flag"""
        #Lage bestimmen ( = am häufigsten vorkommende Ankunftszeit)
        c = Counter(self.times)
        #print (c.most_common(1), c.most_common(1)[0][0])
        #most_common(x) gibt Liste mit häufigsten x Werten als Liste von Tupeln aus (Wert, Anzahl) zurück
        loc = c.most_common(1)[0][0]
        #Quartile berechnen
        quartiles = (np.percentile(self.times, 25), np.percentile(self.times, 50), np.percentile(self.times, 75))
        #IQR berechnen
        iqr =  quartiles[2] - quartiles[0]
        #QK berechnen
        qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
        pd = (loc, quartiles, iqr, qk)
        self.pd=pd
        return

    def simulate_step_2s(self, locations, mobile_states, number):
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
        new_locations = locations + (new_mobile_states)
              
        return new_locations, new_mobile_states

    def simulate_step_by_step_2s(self, maxtime=240):
        """ Simuliere jeden Zeitschritt fuer jedes Teilchen"""
        # starttime für Laufzeitmessungen
        starttime = time.time()
        # Wird Liste aller Ankunftstimes
        arrival_counter = []
        # Simulationszeit in Sekunden
        time_needed = 0
        # Anzahl zu simulierender Teilchen
        number = self.number
        self.approach="T"
        
        # aktuelle Orte der Teilchen
        locations = np.ones(number)
        # akutelle Zustaende der Teilchen 
        mobile_states = np.array([True]*number)
    
        #Teil 1: Sim bis frueheste Teilchen ankommen koennen, hier muss noch keine Abbruchbed. getestet werden. 
        # Carrier ist nach length Schritten durch, das entspricht 0.1 sec
        while time_needed <= (self.length):
            locations, mobile_states = self.simulate_step_2s(locations, mobile_states, number)
            time_needed += 1
        logging.log(20, "Teil1 vorbei, zeit:%s, simdauer:%s", time_needed, time.time()-starttime)
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
                logging.log(25, "fertig, simzeit: %s, realtime: %s", time_needed, (time.time()-starttime))
                break
            if time_needed > self.maxtime * 10000:
                logging.log(30, "Ueberschreitung der Maximalzeit von %s Sekunden, %s", self.maxtime, (time.time()-starttime))
                self.valid = False
                # alle noch nicht fertigen Teilchen bekommen Strafe, damit man sieht, dass Simulation nicht zu Ende durchgefuehrt wurde
                for j in range(len(locations)):
                    arrival_counter.append(time_needed+self.length*1000)
                break    
            
            # Damit es schneller geht, nach je x schritten nur testen
            for x in range (50):
                locations, mobile_states = self.simulate_step_2s(locations, mobile_states, number)
                time_needed+=1
        # durch Schritte pro Sekunde teilen, zur normierung der zeiten
        self.times = [date/10000 for date in arrival_counter]
       
    def _test_finished(self, particle_list):
        """Teste, ob die Teilchen schon durch sind. Aufruf durch simulate_by_event_2s"""        
        #extrahiere nicht fertige Teilchen als (zustands-ort)-Paare
        particles = [(state, location) for state, location in particle_list if location < self.length]
        #extrahiere zeiten fertiger Teilchen
        times = [(location-self.length) for state, location in particle_list if location >= self.length]      
        #Rueckgabe der nicht fertigen Teilchen und Ankunftszeiten fertiger Teilchen
        return particles, times
        
    def _simulate_event_2s(self, particle_list):
        """Simuliere ein zeitliches Event, gebe neue Ereignisliste zurueck, Aufruf durch simulate_by_event_2s"""
        
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
        locations += (periods_pm)  
        logging.log(10, "locations %s", locations[0:10])
        
        new_events = list(zip(periods, states, locations))
        
        return new_events
        
    def simulate_by_event_2s(self):
        """Simuliere mit Hilfe einer Liste von Events"""
        starttime = time.time()
        logging.log(20, "simuliere %s E", self.params)
        length = self.length
        number = self.number
        self.approach = "E"
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
                    new_events = self._simulate_event_2s(particle_list)
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
        #self.times = [date/(50*self.step) for date in arrival_counter]
        #self.times = arrival_counter
        self.times = [date/10000 for date in arrival_counter]

        logging.log(25, "fertig, simschritte: %s, realtime: %s", act_time, (time.time()-starttime))
        
    def __repr__(self):
        if self.model == "2s":
            return (self.model + "_" + str(round(self.params[0],8))+ "_" + str(round(self.params[1],5)) )#+ "_" + self.approach)
        
        return (self.model + "_" + str(self.params))# + "_" + self.approach)
              
    def simulate(self, model = None, approach = None):
        '''Simuliert je nach Modell und Modus'''
        #TODO Abfragen, dass Anzahl der Params und Modell zusammen passen
        if self.model == "2s" or model == "2s":
            if self.approach == "E" or approach == "E":
                self.simulate_by_event_2s()
            elif self.approach == "T" or approach == "T":
                self.simulate_step_by_step_2s()
            else:
                print ("Bitte gewuenschten Simulationsmodus angeben; ", self.approach, " nicht gueltig")
        else:
            print ("Modell auswählen (2s/3s), ", self.model, " nicht gültig")
            
# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "beschreibung")  
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--number", "-n", type = int, default = "1000",
                   help = "Anzahl zu simulierender Teilchen")
    p.add_argument("--maxtime", "-mt", type = int, default = "240",
                   help = "Maximale Retentionszeit in Sekunden")
    p.add_argument("--approach", "-a", default = "E", 
                   help = "Art der Simulation; E = by-event, T = each_timestep")
    p.add_argument("--model", "-m",
                   help = "Modell: 2 oder 3 Zustände (2s/3s)")
    p.add_argument("--params", "-p", nargs = '+', type = float,
                   help = "Parameter fuer die Simulation")
    #TODO: Jeden Param eingeben?
    return p

# Nutzung für Testzwecke
def main():
    p = get_argument_parser()
    args = p.parse_args()
    logging.log(20, "Eingaben fuer Simulation, %s", args)
    print ("n", args.number, "l", args.length, "m", args.approach, time.strftime("%d%b%Y_%H:%M:%S"))
    
    testsim = Simulation((args.params), args.model, args.length, maxtime = args.maxtime, number = args.number, approach = args.approach)
    print (testsim)
    testsim.simulate()
    
    param_list = []
    pss = [0.997, 0.999, 0.9992, 0.9995, 0.9999]
    pms = [0.01, 0.3, 0.9, 0.999]
    for ps in pss:
        for pm in pms:
            param_list.append((ps, pm))
            
    for ps, pm in param_list:
        neueSim = Simulation((ps, pm), "2s", args.length, maxtime = args.maxtime, number = args.number, approach = args.approach)
        print ("ps ", ps, " pm ", pm)
        for i in range(1):
            neueSim.simulate()
    print ("neuesim")
    neueSim = Simulation((0.999, 0.999), "2s", length, None, approach = "T")
  
    #neueSim.simulate_by_event_2s()
    #neueSim.calculate()
    print("pd by t1", n5eueSim.pd, len(neueSim.times))
    n, bins, patches = plt.hist(neueSim.times, 50, alpha=0.5, normed =True)   
    plt.ylabel("")
    plt.xlabel("Zeit / s")
    plt.title("ps: "+ str(neueSim.params[0])+" pm: "+ str(neueSim.params[1]) + " by t1")
    plt.show()
    
    #length = 20000
    neueSim.length = length
    #neueSim.step = 100
    #print (neueSim.length)
    neueSim.simulate_step_by_step_2s()
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
