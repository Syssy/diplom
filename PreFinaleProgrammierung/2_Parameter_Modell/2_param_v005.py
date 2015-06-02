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
import sys

import numpy as np
import scipy.stats as stats
import scipy
import matplotlib.pyplot as plt

import my_plottings_2p as plotkram
import simulation_2p as simulation
import peak_width_2p as peak_width


def combine_params(args, nr_of_choice = 5): #TODO Auf die sinnvollen beschraenken
    """Kombiniere Wahrscheinlichkeiten als ps- und pm-Parameter fuer die Simulation"""
    p_combinations = []
    if not args:
        args = "choice"
    logging.log(20, "args" + args + "nr_of_choice" + str(nr_of_choice))
    if args == "choice":                    
        schrittweite = 0.000002
        ps_catalogue = np.arange(0.9998, 0.99997, schrittweite)
        pm_catalogue = np.arange(0.1, 0.9999, schrittweite*10)
        #print (pm_catalogue)
        
        for zahl in range(nr_of_choice):
                ps = random.choice(ps_catalogue)
                pm = random.choice(pm_catalogue) 
                p_combinations.append((ps, pm))
        logging.log(25, p_combinations)        
       # logging.log(25, ps_catalogue, pm_catalogue)        
  
    # unglaublich viele ;)        
    if args == "viele":
        schrittweite = 0.0004
        px = np.arange(0.993, 0.997, schrittweite)
        for ps in px:
            for pm in px:
                p_combinations.append((ps, pm))
        
        schrittweite = 0.0001
        px = np.arange(0.999, 0.9999, schrittweite)
        for ps in px:
            for pm in px:
                p_combinations.append((ps, pm))
        
        '''px = np.arange(0.998, 0.9992, schrittweite)
        for ps in px:
            for pm in px:
                p_combinations.append((ps, pm))'''
        
        schrittweite = 0.00001
        px = np.arange(0.9999, 0.99992, schrittweite)   
        for ps in px:
            for pm in px:
                p_combinations.append((ps, pm))
                
        '''px = np.arange(0.9998, 0.99991, schrittweite)
        for ps in px:
            for pm in px:
                p_combinations.append((ps, pm))'''
        p_combinations.reverse()
        print (len(p_combinations))
    
    if args == "viele005":
        schrittweite = 0.00005
        ps_catalogue = np.arange(0.999, 0.9998, schrittweite)
        #ps_catalogue = [0.999, 0.9992, 0.9998, 0.99992]
        
        schrittweite = 0.05
        pm_catalogue = np.arange(0.1, 0.9, schrittweite)
        #pm_catalogue = [0.99, 0.9, 0.3, 0.1]
        
        p_combinations = []
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                p_combinations.append((ps, pm))
       
    
    #festgelegte auswahl
    if args == "auswahl":
        p_combinations = [(0.99999, 0.99995),(0.995, 0.99),(0.9995, 0.999),(0.999, 0.995)]
        # p_combinations = [(0.995, 0.995),(0.9997, 0.9995),(0.9995, 0.9999),(0.9999, 0.9995)]
        # p_combinations = [(0.995, 0.999),(0.999, 0.9995),(0.995, 0.995),(0.9999, 0.9995)]
            
        p_combinations = [(0.9996, 0.99992),  (0.998, 0.992),(0.997, 0.99),(0.996, 0.99),  (0.998, 0.991)]
        
        p_combinations = [(0.99985, 0.62),(0.99985, 0.63), (0.99985, 0.64), (0.99985, 0.65)]
        p_combinations = [(0.99988, 0.45)]
        #p_combinations = [(0.99994, 0.85), (0.9999, 0.75),(0.999945, 0.01), (0.9998, 0.4),(0.999825, 0.001), (0.99992, 0.9)]
        #p_combinations = [(0.99991, 0.75),(0.99991, 0.76),(0.99991, 0.77),(0.99991, 0.78),(0.99991, 0.79)]

    if args == "auswahl25":  
        p_combinations = [(0.99996, 0.9), (0.99996, 0.905),
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
        p_combinations = [(0.99998, 0.9), (0.99998, 0.899),
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
    if args == "auswahl75":
        p_combinations = [(0.99997, 0.72),(0.99997, 0.74),(0.99997, 0.76),(0.99997, 0.78),
                   (0.99996, 0.7),
                   (0.99995, 0.61),(0.99995, 0.62),(0.99995, 0.63),(0.99995, 0.64),
                   (0.99994, 0.54),(0.99994, 0.55),(0.99994, 0.56),
                   (0.99993, 0.41),(0.99993, 0.42),(0.99993, 0.43),(0.99993, 0.44),
            ]
    if args == "auswahl100":
        p_combinations = [(0.99998, 0.8), (0.99998, 0.801),
                   (0.99997, 0.7), (0.99997, 0.705),
                   (0.99996, 0.6), (0.99996, 0.603),
                   (0.99995, 0.5), (0.99995, 0.501),
                   (0.99994, 0.395), (0.99994, 0.4),
                   (0.99993, 0.295), (0.99993, 0.3),
                   (0.99991, 0.1), (0.99991, 0.105)                   
            ]        
    if args == "auswahl125":
        p_combinations = [(0.99997, 0.626), (0.99997, 0.628), (0.99997, 0.630), (0.99997, 0.632),(0.99997, 0.634),
                   (0.99996, 0.5),
                   (0.99995, 0.353), (0.99995, 0.354), (0.99995, 0.355), (0.99995, 0.356), (0.99995, 0.357), (0.99995, 0.358), 
                   (0.99994, 0.25), (0.99994, 0.2501),
                   (0.99993, 0.12), (0.99993, 0.13), (0.99993, 0.14), 
                   (0.99992, 0.001)
            ]
    
    # groessere  
    if args == "einige": 
        ps_catalogue = [0.9989, 0.9995, 0.9997]
        #ps_catalogue = [0.999, 0.9995, 0.9999, 0.99991, 0.99992, 0.99993, 0.99994, 0.99995]
        pm_catalogue = [0.99, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.01, 0.0001]
        
       # p_combinations.append((1, 1))
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                p_combinations.append((ps, pm))
        #p_combinations = sorted(p_combinations)    
    #ps oder pm fest, das andere variabel
    if args == "d1":
        ps_catalogue = [0.99, 0.991, 0.992, 0.993, 0.994, 0.995, 0.996, 0.997, 0.998, 0.999]# 0.9992, 0.9993, 0.9994,0.9995, 0.9996]#,0.9997, 0.9998, 0.9999,0.99991, 0.99992, 0.99993, 0.99994]
        #ps_catalogue = [0.1*ps + 0.9 for ps in pm_catalogue]
        #ps_catalogue = np.array(ps_catalogue)*0.1
        #ps_catalogue += 0.9
        pm = 0.993
        for ps in ps_catalogue:
           p_combinations.append((ps,pm))
      
    # ps und pm abhängig  
    if args == "d2":
        ps_catalogue = [ 0.991, 0.993, 0.995, 0.997, 0.999, 0.9992, 0.9994, 0.9996]#,0.9997, 0.9998, 0.9999]
        pm_catalogue = [ 0.1*((1/ps)-1) + ps for ps in ps_catalogue]
#        for ps in ps_catalogue:
#            for pm in pm_catalogue:
#                p_combinations.append((ps, pm))
        for i in range(len(ps_catalogue)):
            print (ps_catalogue[i]-pm_catalogue[i], 1/ps_catalogue[i])
            p_combinations.append((ps_catalogue[i], pm_catalogue[i]))
        logging.log(25, p_combinations)     
    
    # auf festes ps und pm wird was drauf addiert
    if args == "d3":
        sdditor = np.array([0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09])*0.001
        mdittor = np.array([0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09])*0.001
        ps = 0.99
        pm = 0.993
        for s, m in zip(sdditor, mdittor):
            p_combinations.append((ps+s, pm+m))
       
    #  fuenf irgendwie zufaellige  ps und pm > 0.99
    if args == "5random":
        while len(p_combinations) < 5:
            ps = np.random.random()
            pm = random.random()
            if ps > 0.999:# and pm > 0.99:
                p_combinations.append((round(ps, 10), round(pm, 10)))
     
    if args == "wdh":#???
        p_combinations = [(0.999, 0.999), (0.05, 0.99)]
    
    logging.log(20, "p_combinations %s, anzahl: %s", p_combinations, len(p_combinations))    
    return (sorted(list(set(p_combinations))))

def start_simulations(length, number, mode, p_combinations):
    '''Teste, ob Simulationen in geeigneter Version vorhanden sind und simuliere ggf. neu'''
    # nr_todo: wie viele noch nicht bearbeitet, nr_ready: wie viele schon fertig
    nr_todo, nr_ready = len(p_combinations), 0    
    # Die Simulationen werden hier zwischengespeichert
    results = []
    # fuer alle vorhandenen Kombinationen von Parametern
    for ps, pm in p_combinations:
            logging.log(24, "ps, pm, %(ps)f %(pm)f", locals())
            # gehe erst mal davon aus, dass Sim vorhanden ist, daher nicht speichern, sondern auf Aktualitaet ueberpruefen
            sim_exists = True
            store = False
            try:
                filename = 'simulated_data/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                logging.log(25,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(data)
                    logging.log(22, mySim)
                    # test, ob aktuelle version. Im Moment nicht nötig, aber schmeißt noch AttributeError, wenn nicht vorhanden, sodass Dinge nachberechnet werden können, spaeter kann hier weitere versionanpassung rein
                    if mySim.version < 4.1:
                        logging.log(31, "alte version, update")
                        mySim = update_sim(mySim)
                        store = True
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename/path schon laenge und anzahl drin sind
                    if (not mySim.length == length) or (not mySim.number == number):
                        logging.warn('neue Sim nötig, da Laenge oder Anzahl falsch,')
                        sim_exists = False
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                    #if mode != mySim.mode:
                    #    logging.log(35, "andere Simulationsart gewuenscht, simuliere neu")
                    #    sim_exists = False
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim = update_sim(mySim)
            # Kombination nicht vorhanden, daher neue Sim machen
            except IOError:
                sim_exists =  False
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
            
            # diverse Fehler, im Zweifel wohl auch neu simulieren
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(40, err)
                sim_exists = False
                
            #Nur der Uebersicht halber    
            nr_todo -= 1
            nr_ready += 1 
            
            #Neue Simulation notwendig
            if not sim_exists:
                store = True
                mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, mode)
                mySim.simulate()
                mySim.calculate()
               # Jetzt noch abspeichern, entweder nach Update oder nach Neusimulation
            if store:    
                try:
                    filename = 'simulated_data/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                    logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                    with open(filename, 'wb') as data:
                        pickle.dump(mySim, data)
                # Ornder existieren nicht, daher neu anlegen        
                except FileNotFoundError as err:
                    logging.log(40, "%s, lege Ordner an", err)
                    if not os.path.exists('simulated_data/l' + str(length)):
                        os.makedirs('simulated_data/l' + str(length))
                    os.makedirs('simulated_data/l' + str(length)  + "/n" + str(number)) 
                    logging.log(35, "Speichern weiter Versuch, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                    with open(filename, 'wb') as data:
                        pickle.dump(mySim, data)  
            results.append(mySim)
            logging.log(20, "peakdaten: ls, b, h: %s", mySim.pd)
    return results
        
    # Updatet von alter Version
def update_sim(aSim):
    width, heigth, ls = peak_width.calculate_width(aSim.times, 50, False, aSim.params)
    pd = (ls, width, heigth)
    aSim.set_pd(pd)
    return aSim

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "Beschreibung") 
    p.add_argument("--choicenumber", "-cn", type = int, default = "5",
                   help = "bei zufaelliger Parameterwahl: Wie viele Kombinationen sollen gewaehlt werden")
    p.add_argument("--pcombioption", "-p",  
                   help = "Wie sollen die ps/pm-Kombinationen gewaehlt werden: choice, viele, viele005, auswahl, auswahlx, d1-3, einige, random, wdh")
    p.add_argument("--reverse", "-r", action = "store_true",
                   help = "Reihenfolge der p_combinations invertieren")
    p.add_argument("--length", "-l", type = int, default = "200000",
                   help = "Laenge der Saeule")
    p.add_argument("--number", "-n", type = int, default = "1000",
                   help = "Anzahl zu simulierender Teilchen")
    p.add_argument("--mode", "-m", default = "E", 
                   help = "Art der Simulation; E = by-event, T = each_timestep")
    
    p.add_argument("--test", "-t", action = "store_true", help = "nutzlos; Test")
    return p

def main():
    starttime = time.clock()
    logging.log(35, time.strftime("%d%b%Y_%H:%M:%S"))
   
    p = get_argument_parser()
    args = p.parse_args()
       
    #liste aller zu simulierenden kombis erstellen
    p_combinations = combine_params(args.pcombioption, args.choicenumber)
    if args.reverse:
        p_combinations.reverse()
    
    new_sims = start_simulations(args.length, args.number, args.mode, p_combinations)
    #filename = "testspeicherung"
    #with open (filename, "wb") as data:
    #    pickle.dump(new_sims, data)
    #Tests fuer Plotkram
    #plotkram.plot_spectrum(new_sims, 1000)
    #for i in range(len(new_sims)):
    #    plotkram.plot_single_peak(new_sims[i], qq= scipy.stats.norm)
    #    time.sleep(2)
    plotkram.plot_widthmap(new_sims)
    plotkram.plot_widthandskew(new_sims)
    #plotkram.plot_params_at_time(new_sims, 50, 10, True)
    #plotkram.plot_heatmap_of_moments(filename, ff = True, moment= "mean")
    #plotkram.plot_heatmap_of_moments(new_sims, moment="mean") 
    #plotkram.plot_4_heatmaps(filename, ff=True, moment="mean")   
    #plotkram.plot_4_heatmaps(new_sims, moment="mean") 
    #plotkram.plot_simlist_ff(filename, True, True, True, True, True, compare_Dist = scipy.stats.gamma)
    #plotkram.plot_simlist(new_sims, True, False, True, True, True)
    
    # Ende :)
    print ("Zeit " + str(time.clock()-starttime))
    
if __name__ == "__main__":
    if sys.version_info.major < 3:
        print ("Bitte python3 verwenden")
        exit()
    logging.basicConfig(level=20)
    main()
