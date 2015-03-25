 
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
import multiprocessing

import numpy as np
import scipy.stats as stats
import scipy
import matplotlib.pyplot as plt

import plotkram
import simulation
import peak_width
 
def combine_params(args, kwargs = 5):
    pkombis = []
    if not args:
        args = "choice"
    print ("args", args)

    if args == "viele005":
        schrittweite = 0.00001
        ps_catalogue = np.arange(0.9997, 0.99998, schrittweite)
        
        schrittweite = 0.02
        pm_catalogue = np.arange(0.1, 0.9, schrittweite)
        
        pkombis = []
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                pkombis.append((ps, pm))
       
    
    # groessere auswahl
    if args == "einige": 
        ps_catalogue = [0.999, 0.9995, 0.9999, 0.99991, 0.99992, 0.99993, 0.99994, 0.99995]
        pm_catalogue = [0.99, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.01, 0.001, 0.0001]
        
       # pkombis.append((1, 1))
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                pkombis.append((ps, pm))
        #pkombis = sorted(pkombis)
        
    if args == "auswahl":
        pkombis = [(0.999, 0.1), (0.999, 0.1), (0.999, 0.1)] * 4
        pkombis = [(0.99995, 0.873), (0.99995, 0.874), (0.99995, 0.875),(0.99995, 0.876),(0.99995, 0.877),
                   (0.99994, 0.85), (0.99994, 0.6), (0.99993, 0.5)
                   (0.99993, 0.825),(0.99993, 0.826),(0.99993, 0.827),
                   (0.99992, 0.8),
                   (0.99997, 0.85), (0.99995, 0.65), (0.9999, 0.45), (0.99992, 0.53),
                   (0.99997, 0.75), (0.99993, 0.2), (0.99996, 0.62), (0.99996, 0.58),
                   (0.99995, 0.357), (0.99995, 0.358), (0.99997, 0.62), (0.99997, 0.64), (0.999935, 0.18),
                   (0.99997, 0.5), (0.99997, 0.6)]
    if args == "auswahl25":  
        pkombis = [(0.99996, 0.9), (0.99996, 0.905),
                   (0.99995, 0.875),(0.99995, 0.876),
                   (0.99994, 0.85), (0.99994, 0.855),
                   (0.99993, 0.825),(0.99993, 0.826),
                   (0.99992, 0.8), (0.99992, 0.802),
                   (0.99991, 0.774), (0.99991, 0.775), (0.99991, 0.776),
                   (0.9999, 0.75),
                   (0.99985, 0.625), (0.99985, 0.626), (0.99985, 0.627), 
                   (0.9998, 0.5), 
                   (0.99975, 0.372), (0.99975, 0.373), (0.99975, 0.374), 
                   (0.9997, 0.25),(0.9997, 0.251),(0.9997, 0.252),
                   (0.9996, 0.001)]   
        
    if args == "auswahl50":
        pkombis = [(0.99998, 0.9), (0.99998, 0.899),
                   (0.999975, 0.86),(0.999975, 0.87),(0.999975, 0.88),(0.999975, 0.89),
                   (0.99997, 0.85), (0.99997, 0.847),(0.99997, 0.848),(0.99997, 0.849),
                   (0.99996, 0.8), (0.99996, 0.85),
                   (0.99995, 0.72),(0.99995, 0.74),(0.99995, 0.76),(0.99995, 0.78),
                   (0.99994, 0.7), (0.99994, 0.71),
                   (0.99993, 0.642), (0.99993, 0.644), (0.99994, 0.646), (0.99994,0.648),
                   (0.99992, 0.6), (0.99992, 0.63),
                   (0.99991, 0.54),(0.99991, 0.55),(0.99991, 0.56),
                   (0.9999, 0.5), (0.9999, 0.51),
                   (0.99989, 0.45),
                   (0.99985, 0.23),(0.99985, 0.24),(0.99985, 0.25)
            ]
    
    logging.log(20, "pkombis %s, anzahl: %s", pkombis, len(pkombis))    
    return pkombis
    #return (sorted(list(set(pkombis))))

    # Updatet von alter Version
def update_sim(aSim):
    width, heigth, ls = peak_width.fpwahph(aSim.times, 50, False, aSim.params)
    pd = (ls, width, heigth)
    aSim.set_pd(pd)
    return aSim

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "beschreibung") 
    p.add_argument("--pkombioption", "-p",  
                   help = "Wie sollen die ps/pm-Kombinationen gewaehlt werden")
    p.add_argument("--reverse", "-r", action = "store_true",
                   help = "pkombis von hinten durchtesten")
    
    p.add_argument("--test", "-atgfjzfjzf", action = "store_true", help = "plot a heatmap from single file with multiple simulations")
    return p

def do_calculation(params):
    print ("do calc", params, multiprocessing.current_process().name)
    print(params)
    ps, pm = params
    mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, "E")
    mySim.simulate_by_event()
    width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
    pd = (ls, width, heigth)
    mySim.set_pd(pd)   
    mySim.recalculate_moments()
    filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
    logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
    with open(filename, 'wb') as data:
        pickle.dump(mySim, data)      
    return mySim

def start_process():
    print ('Starting', multiprocessing.current_process().name)
    
def main():
    startzeit = time.clock()
    logging.log(35, time.strftime("%d%b%Y_%H:%M:%S"))
    
    p = get_argument_parser()
    args = p.parse_args()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke, in mikrometern
    global length, number
    length = 200000
    # Anzahl der zu simulierenden Teilchen
    number = 5000
    
    # Die Simulationen werden hier zwischengespeichert
    ergebnisse = []
    todolist =  []
    
    #liste aller zu simulierenden kombis erstellen
    pkombis = combine_params(args.pkombioption, number)
    if args.reverse:
        pkombis.reverse()
    
    # nr_todo: wie viele noch nicht bearbeitet, nr_ready: wie viele schon fertig
    nr_todo, nr_ready = len(pkombis), 0
    for ps, pm in pkombis:
            logging.log(24, "ps, pm, %(ps)f %(pm)f", locals())
            try:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
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
                        todolist.append((ps, pm))
                         
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim = update_sim(mySim)
                
            # nicht vorhanden, daher neue Sim machen
            except IOError:
                store =  True
                logging.log(25,"%s, %s, auf die liste, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
                todolist.append((ps, pm))
                
            # komischer Fehler, im Zweifel wohl auch neu simulieren ? TODO
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(35, err)
                time.sleep(20)
            
    #jetzt der multiprocessing-teil:
    logging.log(31, "laenge der todoliste %s", len(todolist))
    pool_size = multiprocessing.cpu_count() * 2
    print ("ppolsize:", pool_size)
    pool_size = 3
    pool = multiprocessing.Pool(processes=pool_size, initializer=start_process,)
    pool_outputs = pool.imap(do_calculation, todolist, chunksize = 3)
    pool.close() # no more tasks
    pool.join()  # wrap up current tasks

    print ('Pool    :', pool_outputs)
            
    #ergebnisse.append(mySim)            
 
    # Ende :)
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=29)
    main() 
