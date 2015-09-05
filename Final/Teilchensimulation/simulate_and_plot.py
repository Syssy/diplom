#!/usr/bin/env python
# -*- coding: latin-1 -*-
# Startet eine gewisse Menge von Simulationen und plottet die daraus resultierenden Peaks

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

import my_plottings_2s as plottings
import simulation_2s as simulation

def combine_params(args, nr_of_choice = 5):
    """Kombiniere Wahrscheinlichkeiten als ps- und pm-Parameter fuer die Simulation"""
    p_combinations = []
    if not args:
        args = "random"
    logging.log(20, "args" + args + "nr_of_choice" + str(nr_of_choice))
    p_combinations = []
    #Kleine Auswahl
    
    if args == "ellytest":
        p_combinations.append((0.9993, 0.5))
    
    if args == "small_set":
        ps_catalogue = [0.998, 0.999, 0.9993, 0.9996, 0.9999]
        pm_catalogue = [0.1, 0.3, 0.5, 0.7, 0.9]
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                p_combinations.append((ps, pm))
    #Mittlere Auswahl            
    if args == "medium_set":
        ps_catalogue = [0.997, 0.998, 0.999, 0.9991, 0.9992, 0.9993, 0.9995, 0.9996, 0.9999]
        pm_catalogue = np.arange(0.05, 1.0, 0.05)
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                p_combinations.append((ps, pm))   
    #Grosse Auswahl            
    if args == "large_set":
        ps_catalogue = list(np.arange(0.999, 1.0, 0.0001))
        ps_catalogue.extend([0.99, 0.995, 0.997, 0.998, 0.99995])
        pm_catalogue = list(np.arange(0.05, 1.0, 0.05))
        pm_catalogue.extend([0.001, 0.01, 0.99, 0.999])
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                p_combinations.append((ps, pm))   
    # zufaellige Kombis, bei denen ps > 0.99 ist
    if args == "random":
        while len(p_combinations) < nr_of_choice:
            ps = random.uniform(0.99, 0.99999)
            pm = np.random.random()
            p_combinations.append((round(ps, 10), round(pm, 10)))
    logging.log(20, "p_combinations %s, anzahl: %s", p_combinations, len(p_combinations))    
    return (sorted(list(set(p_combinations))))

def start_simulations(length, number, approach, p_combinations):
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
            mySim = simulation.Simulation((round(ps, 10), round(pm,10)), "2s", length, number=number, approach=approach)
            filename = 'simulated_data/2_states/l' +str(length) + "/n" + str(number) + '/Sim_' + str(mySim) + ".p" 
            try:
                logging.log(24,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(data)
                    logging.log(22, mySim)
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename/path schon laenge und anzahl drin sind
                    if (not mySim.length == length) or (not mySim.number == number):
                        logging.warn('neue Sim nötig, da Laenge oder Anzahl falsch,')
                        sim_exists = False
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                    #TODO Re-Sim Optionen überlegen
                    #if approach != mySim.approach:
                    #    logging.log(35, "andere Simulationsart gewuenscht, simuliere neu")
                    #    sim_exists = False
            # Fehler beim Laden daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim.calculate_pd()
            # Kombination nicht vorhanden, daher neue Sim machen
            except IOError:
                sim_exists =  False
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
            
            # diverse Fehler, im Zweifel auch neu simulieren
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(40, err)
                sim_exists = False
                
            #Nur der Uebersicht halber    
            nr_todo -= 1
            nr_ready += 1 
            
            #Neue Simulation notwendig
            if not sim_exists:
                logging.log(20,"simuliere")
                store = True
                #mySim = simulation.Simulation(round(ps, 10), round(pm,10), "2s", length, number=number, approach=approach)
                mySim.simulate()
                mySim.calculate_pd()
               # Jetzt noch abspeichern, entweder nach Update oder nach Neusimulation
            if store:    
                try:
                    #filename ='simulated_data/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                    logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                    with open(filename, 'wb') as data:
                        pickle.dump(mySim, data)
                # Ornder existieren nicht, daher neu anlegen        
                except FileNotFoundError as err:
                    logging.log(40, "%s, lege Ordner an", err)
                    if not os.path.exists('simulated_data/2_states/l' + str(length)):
                        os.makedirs('simulated_data/2_states/l' + str(length))
                    os.makedirs('simulated_data/2_states/l' + str(length)  + "/n" + str(number)) 
                    logging.log(35, "Speichern weiter Versuch, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                    with open(filename, 'wb') as data:
                        pickle.dump(mySim, data)  
            results.append(mySim)
            logging.log(20, "peakdaten: ls, b, h: %s", mySim.pd)
    return results

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "Beschreibung") 
    p.add_argument("--choicenumber", "-cn", type = int, default = "5",
                   help = "bei zufaelliger Parameterwahl: Wie viele Kombinationen sollen gewaehlt werden")
    p.add_argument("--pcombioption", "-p",  
                   help = "Wie sollen die ps/pm-Kombinationen gewaehlt werden: small_set, medium_set, large_set, random")
    p.add_argument("--reverse", "-r", action = "store_true",
                   help = "Reihenfolge der p_combinations invertieren")
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--number", "-n", type = int, default = "1000",
                   help = "Anzahl zu simulierender Teilchen")
    p.add_argument("--approach", "-a", default = "E", 
                   help = "Art der Simulation; E = by-event, T = each_timestep")
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
    
    simlist = start_simulations(args.length, args.number, args.approach, p_combinations)
   # plottings.plot_single_peak(simlist[0]) 
    plottings.plot_spectrum(simlist, noise=True)
    
    
    #for i in range(len(new_sims)):
        #plotkram.plot_single_peak(new_sims[i], qq= scipy.stats.norm)
        #time.sleep(2)
    #plotkram.plot_widthmap(new_sims)
    #plotkram.plot_widthandskew(new_sims)
    #plotkram.plot_params_at_time(new_sims, 100, 5, True)
    #plotkram.plot_heatmap_of_moments(filename, ff = True, moment= "mean")
    #plotkram.plot_heatmap_of_moments(new_sims, moment="mean") 
    #plotkram.plot_4_heatmaps(filename, ff=True, moment="mean")   
    #plotkram.plot_4_heatmaps(new_sims, moment="mean") 
    #plotkram.plot_simlist_ff(filename, True, True, True, True, True, compare_Dist = scipy.stats.gamma)
    #plotkram.plot_simlist(new_sims, False, False, True, False, False)
    
    
    
    # Ende :)
    print ("Zeit " + str(time.clock()-starttime))
    
if __name__ == "__main__":
    if sys.version_info.major < 3:
        print ("Bitte python3 verwenden")
        exit()
    logging.basicConfig(level=20)
    main()
