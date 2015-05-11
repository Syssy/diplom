#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Erste Version für die 3 Zustände Simulation mit erst mal vier Parametern

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import random
import os

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt
import seaborn

import simulation_3s as sim

def save_figure(sim, save, show):
    if sim.mean > 0.1 and sim.mean < 180 and sim.pd[1] > 1 and sim.pd[1] < 25:
        logging.log(30, "params, %s", sim )
        logging.log(29, "mean, %s", sim.mean )
        logging.log(29, "ls, breite, h, %s", sim.pd )
        logging.log(29, "skew, %s", sim.skewness )
        n, bins, patches = plt.hist(sim.times, 150, normed=1, alpha=0.5)
        plt.ylabel("")
        plt.xlabel("Zeit / s")
        plt.title("params: " + str(sim))
        info = "loc " +  str(sim.pd[0][0]) + "\nbreite " + str(sim.pd[1]) + "\nskew " + str(sim.skewness)
        #plt.text(1.5*sim.mean, 2*sim.pd[2], info, size=12, ha="center", va="center", bbox = dict(boxstyle="round", fc=(1., 1., 1.),))
        plt.figtext(0.7, 0.8, info, size=12, ha="center", va="center", bbox = dict(boxstyle="round", fc=(1., 1., 1.),))
        #print (neueSim.params, neueSim.mean, neueSim.pd, neueSim.pd[0])
        if save:
            plt.savefig("savefig/p"+ str(sim.params[0])+"_"+ str(sim.params[1])+"_"+ str(sim.params[2]) + "_timestep_n" + str(sim.number) + ".png")
           # print ("save")
        if show:
            plt.show()
           # print ("show")
        plt.hold(False)
        plt.close()
    #time.sleep(1)

def start_simulations(length, number, mode, p_combinations):
    '''Teste, ob Simulationen in geeigneter Version vorhanden sind und simuliere ggf. neu'''
    # nr_todo: wie viele noch nicht bearbeitet, nr_ready: wie viele schon fertig
    nr_todo, nr_ready = len(p_combinations), 0    
    # Die Simulationen werden hier zwischengespeichert
    results = []
    # fuer alle vorhandenen Kombinationen von Parametern
    for params in p_combinations:
        #if sim.check_params(params):
            #logging.log(24, "ps, pm, %(ps)f %(pm)f", locals())
            # gehe erst mal davon aus, dass Sim vorhanden ist, daher nicht speichern, sondern auf Aktualitaet ueberpruefen
            sim_exists = True
            store = False
            try:
                filename = 'simulated_data/l' + str(length) + "/n" + str(number) + '/Sim_' + str(params[0])+"_"+ str(params[1])+"_"+ str(params[2]) + ".p" 
                logging.log(25,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(data)
                    logging.log(20, mySim)
                    # test, ob aktuelle version. Im Moment nicht nötig, aber schmeißt noch AttributeError, wenn nicht vorhanden, sodass Dinge nachberechnet werden können, spaeter kann hier weitere versionanpassung rein
                    if mySim.version < 1.0:
                        logging.log(31, "alte version, update")
                        mySim = update_sim(mySim)
                        store = True
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename/path schon laenge und anzahl drin sind
                    if (not mySim.length == length) or (not mySim.number == number):
                        logging.warn('neue Sim nötig, da Laenge oder Anzahl falsch,')
                        sim_exists = False
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim = update_sim(mySim)
            # Kombination nicht vorhanden, daher neue Sim machen
            except IOError:
                sim_exists =  False
                logging.log(25,"%s, simuliere, da nicht vorhanden, todo %s, ready %s", params, nr_todo, nr_ready)
            
            # diverse Fehler, im Zweifel wohl auch neu simulieren ? TODO
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(40, err)
                sim_exists = False
                
            #Nur der Uebersicht halber    
            nr_todo -= 1
            nr_ready += 1 
            
            #Neue Simulation notwendig
            if not sim_exists:
                store = True
                mySim = sim.Simulation(params, length, number, mode)
                mySim.simulate()
                mySim.calculate()
               # Jetzt noch abspeichern, entweder nach Update oder nach Neusimulation
            if store:    
                try:
                    filename = 'simulated_data/l' + str(length) + "/n" + str(number) + '/Sim_' + str(params[0])+"_"+ str(params[1])+"_"+ str(params[2]) + ".p" 
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
            #logging.log(20, "peakdaten: ls, b, h: %s", mySim.pd)
            save_figure(mySim, True, False)
    return results

def combine_params(args):  
    param_list = []
    if args=="3a":
        pmms = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
        pmls = [0.01, 0.001, 0.0005, 0.0001] 
        pms = []
        for pmm in pmms:
            for pml in pmls:
                pma = 1 - pmm - pml
                pms.append([pmm, pma, pml])
                
        paas = [0.999, 0.9993, 0.9996, 0.9999, 0.99992]   
        pas = []
        for paa in paas:
            pam = 1 - paa
            pas.append([pam, paa, 0.0])
        #print (pas)
        
        plls = [0.99999, 0.999993, 0.999996, 0.999999]
        pls = []
        for pll in plls:
            plm = 1 - pll
            pls.append([plm, 0.0, pll])
        
        for pm in pms:
            for pa in pas:
                for pl in pls:
                    param_list.append([pm, pa, pl]) 
     
    if args == "3b":
        pmms = [0.3, 0.5, 0.9, 0.99]
        pms = []
        for pmm in pmms:
            pms.append([pmm, 1-pmm, 0.0])
        
        paas = [0.99, 0.999, 0.9993, 0.9996, 0.9999]
        pals = [0.01, 0.001, 0.0005, 0.0001, 0.00001] 
        pas = []
        for paa in paas:
            for pal in pals:
                pam = 1 - paa-pal
                if pam > 0:
                    pas.append([pam, paa, pal])
        
        plls = [0.99999, 0.999993, 0.999996, 0.999999]
        pls = []
        for pll in plls:
            pla = 1 - pll
            pls.append([0.0, pla, pll])
        
        for pm in pms:
            for pa in pas:
                for pl in pls:
                    if sim.check_params([pm, pa, pl]):
                        param_list.append([pm, pa, pl]) 
    
    if args == "6p":
        pmms = [0.3, 0.5, 0.9, 0.99]
        pmas = [0.001, 0.1, 0.4]
        pms = []
        for pmm in pmms:
            for pma in pmas:
               pml = 1- pmm - pma
               if pml>0:
                    pms.append([pmm, pma, pml])
                    
        paas = [0.99, 0.999, 0.9993, 0.9996, 0.9999, 0.99995, 0.99999]   
        pals = [0.005, 0.001, 0.0005, 0.0001, 0.00005]
        pas = []
        for paa in paas:
            for pal in pals:
                pam = 1- paa -pal
                if pam>0:
                    pas.append([pam, paa, pal])
        
        for pm in pms:
            for pa in pas:
                for pl in pas: #Ja, absicht, dass pas und kein pls
                    if sim.check_params([pm, pa, pl]):
                        param_list.append([pm, pa, pl]) 
    
    #print (param_list)
    return param_list


def main(): #TODO: 3s
    number = 2000
    length = 200000
    print ("n", number, "l", length, time.strftime("%d%b%Y_%H:%M:%S"))
    #p = get_argument_parser()
    #args = p.parse_args()
    
    #params = [[0.5, 0.499, 0.001],[0.0005, 0.9995, 0.0],[0.000001, 0.0, 0.99999]]
    #params = [[0.7,0.0,0.3],[0.0,0.0,0.0],[0.0006, 0.0, 0.9994]]
    #params = [[0.7,0.3,0.0],[0.00006, .99994, 0.0],[0.0,0.0,0.0]]
    #params = [[0.0,0.5,0.5],[0.0,0.5,0.5],[0.0, 0.5, 0.5]]
    
    param_list = combine_params("3a")
    
    start_simulations(length, number, "E", param_list)
    #pms = [[0.8, 0.199, 0.001],[0.5, 0.499, 0.001],[0.5, 0.4999, 0.0001]]
    #pas = [[0.0008, 0.9992, 0.0],[0.0005, 0.9995, 0.0],[0.0001, 0.9999, 0.0]]
    #pls = [[0.00005, 0.0, 0.99995],[0.00001, 0.0, 0.99999],[0.000005, 0.0, 0.999995]]
    
    #for params in param_list:
    ##for pm in pms:
        ##for pa in pas:
            ##for pl in pls:
                ##params = [pm, pa, pl]                
                #print ("params", params)
                #neueSim = sim.Simulation(params, length, number, "E", [])
    
                #if neueSim.check_params(params):
                    ##neueSim.simulate_by_event()
                    ##neueSim.calculate()
                    ##print("pd by EVENT", neueSim.pd, len(neueSim.times))
                    ##n, bins, patches = plt.hist(neueSim.times, 50, normed=1, alpha=0.5)   
                    ##plt.ylabel("")
                    ##plt.xlabel("Zeit / s")
                    ##plt.title("params: "+ str(neueSim.params[0])+" "+ str(neueSim.params[1])+" "+ str(neueSim.params[2]) + " by event")
                    ##plt.savefig("p"+ str(neueSim.params[0])+"_"+ str(neueSim.params[1])+"_"+ str(neueSim.params[2]) + "_event_n" + str(number) + ".png")
                    ##plt.hold(False)
        ##plt.show()

                    #neueSim.simulate_each_timestep()
                    #neueSim.calculate()
                    ##print ("times by step", neueSim, neueSim.times)
                    #print ("pd by TIMESTEP", neueSim.pd, neueSim.get_moment("skewness"), len(neueSim.times))
                    #n, bins, patches = plt.hist(neueSim.times, 50, normed=1, alpha=0.5)
                    #plt.ylabel("")
                    #plt.xlabel("Zeit / s")
                    #plt.title("params: "+ str(neueSim.params[0])+" "+ str(neueSim.params[1])+" "+ str(neueSim.params[2]) + " timestep")
                    ##print (neueSim.params, neueSim.mean, neueSim.pd, neueSim.pd[0])
                    #plt.savefig("p"+ str(neueSim.params[0])+"_"+ str(neueSim.params[1])+"_"+ str(neueSim.params[2]) + "_timestep_n" + str(number) + ".png")
                    #plt.hold(False)
                    ##plt.show()
       
       
       
if __name__ == "__main__":
    logging.basicConfig(level=26)
    main()
