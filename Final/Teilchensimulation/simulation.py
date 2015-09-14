#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Finale Version für die Teilchensimulation mit zwei und drei Zuständen

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import random
from collections import Counter
from abc import ABCMeta, abstractmethod 

import numpy as np
import matplotlib.pyplot as plt


# Speichert alle interessanten Dinge einer Simulation ab
# Hat Methoden zur Simulation, sowie zur Berechnung von Peakdaten
class Simulation(metaclass = ABCMeta):
    """Simuliert und speichert Daten einer Simulation
    """
    def __init__(self, params, model, approach, length=1000, number=1000, maxtime=240, times=[]):
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

    def set_model(self):
        '''Aus der Anzahl der Parameter das dahinter liegende Modell extrahieren'''
        print ("modell setzen")
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
        #print (self.times)
        c = Counter(self.times)
        #print (c.most_common())
        #print (c.most_common(1), c.most_common(1)[0][0])
        #most_common(x) gibt Liste mit häufigsten x Werten als Liste von Tupeln aus (Wert, Anzahl) zurück
        if not self.valid:
            pd = (float("nan"), [float("nan"), float("nan"), float("nan")], float("nan"), float("nan"))
        else:
            try:
                loc = c.most_common(1)[0][0]
                #Quartile berechnen
                quartiles = (np.percentile(self.times, 25), np.percentile(self.times, 50), np.percentile(self.times, 75))
                #IQR berechnen
                iqr =  quartiles[2] - quartiles[0]
                #QK berechnen
                qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
                pd = (loc, quartiles, iqr, qk)
            # Der Fehler tritt bei leeren Ankunftszeitlisten auf, dann ist kein Teilchen angekommen, sollte nciht mehr vorkommen, da dann schon invalid
            except IndexError:
                pd = (float("nan"), [float("nan"), float("nan"), float("nan")], float("nan"), float("nan"))
                self.valid = False
        self.pd=pd
        return
    
    @abstractmethod   
    def simulate_step(self, locations, mobile_states, number):
        pass

    def simulate_step_by_step(self):
        """ Simuliere jeden Zeitschritt fuer jedes Teilchen"""
        # starttime für Laufzeitmessungen
        starttime = time.time()
        # Wird Liste aller Ankunftstimes
        arrival_counter = []
        # Simulationszeit in Sekunden
        time_needed = 0
        # Anzahl zu simulierender Teilchen
        number = self.number
        self.valid = True
        self.approach="S"
        
        # aktuelle Orte der Teilchen
        if self.model == "2s":
            locations = np.ones(number)
        else:
            locations = np.zeros(number)
        # akutelle Zustaende der Teilchen 
        mobile_states = np.array([True]*number)
    
        #Teil 1: Sim bis frueheste Teilchen ankommen koennen, hier muss noch keine Abbruchbed. getestet werden. 
        # Carrier ist nach length Schritten durch, das entspricht 0.1 sec
        while time_needed <= (self.length):
            locations, mobile_states = self.simulate_step(locations, mobile_states, number)
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
            if number < 0.001*self.number:
                logging.log(25, "fertig, simzeit: %s, realtime: %s", time_needed, (time.time()-starttime))
                break
            if time_needed > self.maxtime * 10000:
                logging.log(30, "Ueberschreitung der Maximalzeit von %s Sekunden, Simdauer: %s", self.maxtime, (time.time()-starttime))
                self.valid = False
                # alle noch nicht fertigen Teilchen bekommen Strafe, damit man sieht, dass Simulation nicht zu Ende durchgefuehrt wurde
                #for j in range(len(locations)):
                #    arrival_counter.append(time_needed+self.length*1000)
                break    
            
            # Damit es schneller geht, nach je x schritten nur testen
            for x in range (50):
                locations, mobile_states = self.simulate_step(locations, mobile_states, number)
                time_needed+=1
        # durch Schritte pro Sekunde teilen, zur normierung der zeiten
        self.times = [date/10000 for date in arrival_counter]
    
    def test_finished(self, particle_list):
        """Teste, ob die Teilchen schon durch sind. Aufruf durch simulate_by_event_2s"""        
        #extrahiere nicht fertige Teilchen als (zustands-ort)-Paare
        particles = [(state, location) for state, location in particle_list if location < self.length]
        #extrahiere zeiten fertiger Teilchen
        times = [(location-self.length) for state, location in particle_list if location >= self.length]      
        #Rueckgabe der nicht fertigen Teilchen und Ankunftszeiten fertiger Teilchen
        return particles, times
       
    @abstractmethod   
    def simulate_event(self, particle_list):
        pass
    
    def simulate_by_event(self, maxtime=240):
        """Simuliere mit Hilfe einer Liste von Events"""
        starttime = time.time()
        logging.log(20, "simuliere %s E", self.params)
        length = self.length
        number = self.number
        self.approach = "E"
        self.valid = True
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
        while len(events) >= 1 and act_time < self.maxtime * 10000:
            if act_time in events:
                #print (events)
                logging.log(15, "betrachte zeitpunkt %s", act_time)
                # teste, ob zum aktuellen Zeitpunkt schon Teilchen fertig, fuege deren Zeiten ein
                particle_list = np.array(events[act_time])
                particle_list, times = self.test_finished(particle_list)
                arrival_counter.extend([(act_time-(date)) for date in times])
                
                #logging.log(5, "noch da2, %s", arrival_counter)
                # Falls die Teilchen dieses Zeitpunktes alle durch sind, wird nicht mehr simuliert
                # sonst Simulation aller uebriger Teilchen
                if len(particle_list) > 0:
                    new_events = self.simulate_event(particle_list)
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
        #print (arrival_counter)
        if len(events) > 1:
            nr_failed = 0
            logging.log(20, "Das wird nix, uebrig: %s", (len(events)))
            # teste alle events, ob Teilchen nicht doch schon fertig
            for ev in events:
                particle_list = np.array(events[ev])
                #print("particles", ev, particle_list)
                particle_list, times = self.test_finished(particle_list)
                #times sind die zeiten der doch angekommenen teilchen
                arrival_counter.extend([(act_time-(date)) for date in times])
                #wenn teilchen uebrig, waren diese zu langsam
                nr_failed += len(particle_list)
            if nr_failed > 0.001*self.number:
                self.valid = False
                logging.log (25, "Kein vollständiger Peak, Anzahl verweilender Teilchen: %s", nr_failed)
        # Zeitpunkte normalisieren  
        # Dabei wegen Konstistenz mit step-by-step und Zusammenlegen von Messzeitpunkten runden
        self.times = [round(date/10000, 2) for date in arrival_counter]

        logging.log(25, "fertig, simschritte: %s, realtime: %s", act_time, (time.time()-starttime))
        
    def __repr__(self):
        if self.model == "2s":
            return (self.model + "_" + str(round(self.params[0],8))+ "_" + str(round(self.params[1],5)) )#+ "_" + self.approach)
        if self.model == "3s" or self.model == "3a":
            result = ''
            for param in self.params:
                result+=("[")
                for i in range(len(param)-1):
                    result+=(str(round(param[i], 6)) + "_")
                result+=(str(round(param[-1], 6)) + "]")
            #result+=("]")                      
            return result
        return (self.model + "_" + str(self.params))# + "_" + self.approach)
              
    def simulate(self, model=None, approach=None):
        '''Simuliert je nach Modell und Modus'''
        #TODO Abfragen, dass Anzahl der Params und Modell zusammen passen
        if self.model == "2s" or model == "2s" or self.model == "3s" or model == "3s" or self.model == "3a" or model == "3a" :
            if self.approach == "E" or approach == "E":
                self.simulate_by_event()
            elif self.approach == "S" or approach == "S":
                self.simulate_step_by_step()
            else:
                print ("Bitte gewuenschten Simulationsmodus angeben; ", self.approach, " nicht gueltig")
        else:
            print ("Modell auswählen (2s/3s/3a), ", self.model, " nicht gültig")
    
    
class Simulation_2s(Simulation):    
    '''Unterklasse für 2-Zustände Modell'''
    def simulate_step(self, locations, mobile_states, number):
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
        # wenn mobil, addiere einen Schritt
        new_locations = locations + (new_mobile_states)
              
        return new_locations, new_mobile_states

    def simulate_event(self, particle_list):
        """Simuliere ein zeitliches Event, gebe neue Ereignisliste zurueck, Aufruf durch simulate_by_event_2s"""
        
        # extrahiere je eine liste von Zustaenden und Orten
        states, locations = zip(*particle_list)
        
        # Geometrisch verteilt: Zeitspannen bis zum naechsten Erfolg, jeweils fuer alle Teilchen und fuer ps und pm
        periods_ps = np.random.geometric(1-self.params[0], size = len(particle_list))
        periods_pm = np.random.geometric(1-self.params[1], size = len(particle_list))
        
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
        

class Simulation_3s(Simulation):
    '''Unterklasse für 3-Zustände Modell'''
    def __init__(self, params, model, approach="E", length=1000, number=1000, maxtime=240, times=[]):
        '''Muss beim initialisieren zusätzliche Informationen berechnen'''
        super().__init__(params, model, approach, length, number, maxtime, times)
        # das allgemeine 3s nimmt nur [[pmm,pma,pml],[pam,paa,pal],[plm,pla,pll]]
        # 3a kann [pmm,pml,paa,pll] annehmen, das muss entsprechend umgeformt werden
        if self.model == "3a":
            self.params = self.init_params_3a(params)
        self.kum_params = self.kumulate_params()
        self.num_states = len(params)
        self.zielmatrix = self.erstelle_zielmatrix(self.num_states)
    
    def init_params_3a(self, params):
        pm = [params[0], (1-params[0]-params[1]), params[1]]
        pa = [1-params[2], params[2], 0]
        pl = [1-params[3], 0, params[3]]
        new_params = [pm, pa, pl]
        return new_params
    
    def erstelle_zielmatrix(self, num_states):
        '''Matrix mit Wahrscheinlichkeiten für Event basierte Sim'''
        zielmatrix = [0,0,0]
        for i in range(3):
            nenner = 1 - self.params[i][i]
            #print ("i ", i, " folge ", (i+1)%3)
            zaehler = self.params[i][(i+1)%3]
            #print("z ", zaehler, " n ", nenner)
            if nenner == 0:
                zielmatrix[i] = 1
            else:
                zielmatrix[i] = zaehler/nenner
        #print ("zielmatrix", zielmatrix)
        return zielmatrix

    def kumulate_params(self):
        '''Vorberechnung für Übergangswahrscheinlichkeiten für by-step Simulation'''
        result = []
        for p in self.params:
            r = []
            r.append(p[0])
            for pp in range(len(p)-1):
                r.append(r[pp]+p[pp+1])
            result.append(r)    
        return result
    
    def simulate_step(self, locations, mobile_states, number):
        """Simuliere einen Schritt für alle Teilchen innerhalb der each_timestep-Simulation    
        Wahrscheinlichkeit stationaer/mobil zu bleiben, Zugriff über self.params
        (new_)locations -- np-array aller Orte vor bzw. nach diesem Aufruf
        (new_)mobile_states -- np-array aller Teilchenstates vor bzw. nach diesem Aufruf
        number -- Anzahl der zu simulierenden Teilchen, nicht immer gleich self.number, da es am Ende weniger werden
        """
        zzv = np.random.random(number)
        #print ("zzv", zzv)
        #print ("sl", mobile_states, locations)
        
        mobile_states = np.array(mobile_states)
        
        maske_0 = mobile_states == 0
        maske_1 = mobile_states == 1
        maske_2 = mobile_states == 2
        
        #aktualisiere orte
        new_locations = locations + (maske_0)
        
        # uebergang_x2 kann jeweils wegfallen, da immer 0. kum_params[x][2] ist nämlich immer 1       
        uebergang_00 = zzv > self.kum_params[0][0]
        uebergang_01 = zzv > self.kum_params[0][1]
        #uebergang_02 = zzv > self.kum_params[0][2]
        #print ("uebergang_0", ((0) + uebergang_00 + uebergang_01 + uebergang_02))
        uebergang_0 = ((0) + uebergang_00 + uebergang_01 ) * maske_0
        
        uebergang_10 = zzv > self.kum_params[1][0]
        uebergang_11 = zzv > self.kum_params[1][1]
        #uebergang_12 = zzv > self.kum_params[1][2]
        uebergang_1 = ((0) + uebergang_10 + uebergang_11) * maske_1
        
        
        uebergang_20 = zzv > self.kum_params[2][0]
        uebergang_21 = zzv > self.kum_params[2][1]
        #uebergang_22 = zzv > self.kum_params[2][2]
        uebergang_2 = ((0) + uebergang_20 + uebergang_21 ) * maske_2
                
        new_mobile_states= (uebergang_0 + uebergang_1 + uebergang_2)
 
        return new_locations, new_mobile_states

    def simulate_event(self, particle_list):
        """Simuliere ein zeitliches Event, gebe neue Ereignisliste zurueck, Aufruf durch simulate_by_event"""
        periods, n_states, n_locations = [], [], []      
        # extrahiere je eine liste von Zustaenden und Orten
        states, locations = zip(*particle_list)
        for s, l in particle_list:
            #Zufallszahlen ziehen: Geom fuer Zeitpunkt des naechsten Events, entspricht Zeitpunkt des Misserfolgs (also nicht-Verweilen)
            period = np.random.geometric(1-self.params[s][s])
            # zz fuer Bestimmung des naechsten Zustands
            zz = random.random()
            #print("period ", period, " zz ", zz)
            # Berechne neuen Zustand (gehe 1 weiter und evtl noch einen, falls Zufall das sagt, mod 3)
            n_zustand = (s + 1 + ( zz > self.zielmatrix[s])) % 3
            #print ("rechnung ", (s+1+(zz > self.zielmatrix[s]))%3, "bool ",zz > self.zielmatrix[s]  )
            #print("zustand, alt ", s, " neu ", n_zustand)
            #n_locations.append(!n_zustand*period +l)
            #loc = l + period*100 if s== 0 else l
            #Wenn alter Zustand mobil war, gehe vor, sonst nicht
            if s == 0:
                n_locations.append(l+period)
            else:
                n_locations.append(l)
            #n_locations.append(loc)
            #Entsprechende neue Zustaende und Zeitpunkte anhaengen
            n_states.append(n_zustand)
            periods.append(period)
            
        return list(zip(periods, n_states, n_locations)) #new_events 
    
    
# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "Simuliert nach den vorgegebenen Parametern")  
    p.add_argument("model", choices=["2s", "3s", "3a"],
                   help = "Modell: 2 oder 3 Zustände (2s/3s/3a)")
    p.add_argument("params", nargs = '+', type = float,
                   help = "Parameter fuer die Simulation")
    p.add_argument("--quiet", "-q", action= "store_true",
                   help = "Wenn gewählt, wird keine Ausgabe der Zeiten in der Kommandozeilen angezeigt")
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--number", "-n", type = int, default = "1000",
                   help = "Anzahl zu simulierender Teilchen")
    p.add_argument("--maxtime", "-m", type = int, default = "240",
                   help = "Maximale Retentionszeit in Sekunden")
    p.add_argument("--approach", "-a", default = "E", choices=["E", "S"],
                   help = "Art der Simulation; E = by-event, S = step-by-step")
    p.add_argument("--plot", "-p", action = "store_true",
                   help = "Wenn ausgewählt, wird zusätzlich zur Kommandozeilenausgabe ein Plot erzeugt")
    #TODO: Jeden Param eingeben?
    return p

# Nutzung für Testzwecke
def main():
    p = get_argument_parser()
    args = p.parse_args()
    print (args)
    logging.log(20, "Eingaben fuer Simulation, %s", args)
    #print ("n", args.number, "l", args.length, "a", args.approach, time.strftime("%d%b%Y_%H:%M:%S"))
    
    #Parameterübergabe für 3s an die Simulationsklasse: Komplett als 3x3 matrix. daher Umformung der Eingabe 
    if args.model == "3s":
        args.params = [[args.params[0],args.params[1],args.params[2]],[args.params[3],args.params[4],args.params[5]],[args.params[6],args.params[7],args.params[8]]]
 
    if args.model.startswith("3"):
        #print ("Starte Simulation")
        testsim3s = Simulation_3s(args.params, args.model, args.approach, args.length, number=args.number, maxtime=args.maxtime )
        testsim3s.simulate()
        if  not args.quiet:
            print ("Ankunftszeiten der Teilchen: ", testsim3s.times)
        testsim3s.calculate_pd()
        print ("Peakdaten: ", testsim3s.pd)
        if args.plot:
            n, bins, patches = plt.hist(testsim3s.times, 50)
            plt.title(str(args.params) + " " + args.approach)
            plt.show()
    
    if args.model == "2s":
        #print ("Starte Simulation")
        testsim = Simulation_2s((args.params), args.model, args.approach, args.length, number = args.number, maxtime = args.maxtime)
        #print (testsim.params)
        testsim.simulate()
        if not args.quiet:
            print ("Ankunftszeiten der Teilchen: ", testsim.times)
        testsim.calculate_pd()
        print ("Peakdaten: (Lage, (Quartile), Breite, Schiefe)", testsim.pd)
        if args.plot:
            n, bins, patches = plt.hist(testsim.times, 50)
            plt.title(str(args.params) + " " + args.approach)
            plt.show()
       
if __name__ == "__main__":
    logging.basicConfig(level=25)
    main()
