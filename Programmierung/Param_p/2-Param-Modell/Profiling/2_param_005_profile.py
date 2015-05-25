#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen, Klappe die zweite...
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import pickle
import time
import logging
import argparse
import os

import numpy as np
import scipy.stats as stats
import scipy
import matplotlib.pyplot as plt

import plotkram
import simulation
import peak_width

def main():
    startzeit = time.clock()
    logging.log(35, time.strftime("%d%b%Y_%H:%M:%S"))
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke, in mikrometern
    global length, number
    length = 200000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    
    # Die Simulationen werden hier zwischengespeichert
    ergebnisse = []
    
    #liste aller zu simulierenden kombis erstellen
    pkombis = [(0.999, 0.1), (0.999, 0.1), (0.999, 0.1)] * 2
    #pkombis = [(0.999, 0.1), (0.999, 0.1), (0.999, 0.1), (0.999, 0.1)] * 2
    print (pkombis)
    
    # nr_todo: wie viele noch nicht bearbeitet, nr_ready: wie viele schon fertig
    nr_todo, nr_ready = len(pkombis), 0
    for ps, pm in pkombis:
            logging.log(24, "ps, pm, %(ps)f %(pm)f", locals())
            # gehe erst mal davon aus, dass Sim vorhanden ist, daher nicht speichern
            store = False
            try:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".pp" 
                logging.log(15,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(data)
                    logging.log(20, mySim)
                    # test, ob aktuelle version. Im Moment nicht nötig, aber schmeißt noch AttributeError, wenn nicht vorhanden, sodass Dinge nachberechnet werden können, spaeter kann hier weitere versionanpassung rein
                    if mySim.version < 4.1:
                        logging.log(31, "alte version")
                        mySim = update_sim(mySim)
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename schon laenge und anzahl drin sind
                    if (not mySim.length == length) or (not mySim.number == number):
                        logging.warn('neue Sim nötig, da l/n oder so falsch,')
                        store = True
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                        mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number)
                        mySim.simulate()
                        width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                        pd = (ls, width, heigth)
                        mySim.set_pd(pd)
                        
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = False
                logging.log(25, err)
                mySim = update_sim(mySim)
                
            # nicht vorhanden, daher neue Sim machen
            except IOError:
                store =  False
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
                
                mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number)
                mySim.simulate()
                width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                pd = (ls, width, heigth)
                mySim.set_pd(pd)
               # mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, 
                #                              simulate(round(ps,10), round(pm, 10), length, np.zeros(number), np.array([True]*number)))
            
            # komischer Fehler, im Zweifel wohl auch neu simulieren ? TODO
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(35, err)
                time.sleep(20)
                
            nr_todo -= 1
            nr_ready += 1 
            
            ergebnisse.append(mySim)
            logging.log(20, "peakdaten: ls, b, h: %s", mySim.pd)
            if store:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                with open(filename, 'wb') as data:
                    pickle.dump(mySim, data)
 
    # Ende :)
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=25)
    main()  
