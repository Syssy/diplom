#!/usr/bin/env python
# -*- coding: latin-1 -*-

''' Sucht in allen vorhandenen Simulationen Peaks mit bestimmten Eigenschaften wie Location (loc-Parameter, entspricht Retentionszeit) und Breite des Peaks auf halber Hoehe'''

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
import math
import matplotlib.pyplot as plt

import plotkram
import simulation
import peak_width 


def plot_all_width(sim_list, locmin=0, locmax=240):
    """Erstelle diverse Plots"""
    plotkram.plot_widthandskew(sim_list, True, False) 
    #p = get_argument_parser()
    #args = p.parse_args()
    #logging.log(25, "starte plotting")
    #peak_data = []
    #for sim in sim_list:
        #try:
            #pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], sim.skewness)
            ##willkürlich gewählt: loc <> xy, scale < z width < v...
            #if sim.pd[0][0] < locmax and sim.pd[0][1] < 60 and sim.pd[1] < 150 and sim.pd[0][0] > locmin:
                #peak_data.append(pd)
        #except AttributeError as err:
            #print (err)
    #logging.log(22, "plotte Groessenverhaeltnisse")
    ##print ("pd", peak_data)
    #filename = "l" + str(args.length) + "n" + str(args.number) + "_peakdaten.p"
    #with open(filename, "wb") as data:
        #pickle.dump(peak_data, data)
    #peak_width.plot_relation(filename)
    #logging.log (15, "plot1 fertig")
   
def get_approximate_sims(retention, width = 10, retepsilon=1, widepsilon=10):
    """Gebe Liste aller nahe liegenden Simulationen zurück"""
    p = get_argument_parser()
    args = p.parse_args()
    list_of_all_sims = []
    approximate_sims = []
     #Liste mit allen vorhandenen Sims laden
    files = os.listdir('v005/l' + str(args.length) + "/n" + str(args.number))
    for aFile in files:
        if aFile.endswith(".p"):    
            try:
                with open('v005/l' + str(args.length) + "/n" + str(args.number) +"/" + aFile, "rb") as aSimFile: 
                    aSim = pickle.load(aSimFile)
                    #print (aSim)
                    list_of_all_sims.append(aSim)
            except pickle.UnpicklingError as Err:
                print (Err)
    logging.log(20, "number of all sims: %s", len(list_of_all_sims))
    list_of_all_sims.sort(key = lambda Simulation : Simulation.params)
    logging.log(10, list_of_all_sims[110:120])
    
    for i, mySim in enumerate(list_of_all_sims):
        if (mySim.pd[0][0]<(retention + retepsilon) and mySim.pd[0][0]>(retention - retepsilon) 
               and mySim.pd[1] > (width - widepsilon) and mySim.pd[1] < (width + widepsilon)):
            approximate_sims.append(mySim)
            #print (i, mySim.pd, mySim)    
    return approximate_sims


def do_calculation(params):
    ps, pm, zahl = params
    print ("do calc", params, zahl, multiprocessing.current_process().name)
    mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number)
    mySim.simulate()
    width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
    pd = (ls, width, heigth)
    mySim.set_pd(pd)    
    filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
    logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
    with open(filename, 'wb') as data:
        pickle.dump(mySim, data)      
    return mySim

def start_process():
    print ('Starting', multiprocessing.current_process().name)
    
def simulate_new (pkombis):
    """Simuliere für alle pkombis"""
    new_list = []
    todolist = []
    todo, ready = len(pkombis), 0
    for ps, pm in pkombis:
            try:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                logging.log(15,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet, %s, %s", ps, pm)
                    mySim = pickle.load(data)
            except IOError:
                todolist.append((ps, pm, ready))
                ready += 1
    
    logging.log(29, "todo %s, laenge: %s", todolist, len(todolist))
    pool_size = 2
    mychunksize = min(15, int(len(todolist)/3))
    if mychunksize < 1 : mychunksize = 1
    pool = multiprocessing.Pool(processes=pool_size, initializer=start_process,)
    pool_outputs = pool.imap(do_calculation, todolist, chunksize = mychunksize)
    pool.close() # no more tasks
    pool.join()  # wrap up current tasks
    print ("output", pool_outputs)
    #new_list.append(mySim) 
                        
    return pool_outputs             
                 
def find_good_params(retention_time, zahl = 1):
    """Plotte mögliche Parameterkombinationen für gegebene Zeit inklusive deren Breite"""
    # zahl ist von 0 bis -x!
    epsilon = pow(10, zahl)
    logging.log(25, "find_good_params for time: %s, runde %s", retention_time, zahl)
    approximate_sims = get_approximate_sims(retention_time, 15, epsilon, 15)
    
    pkombis = []
    number_of_good = 0
    for sim in approximate_sims:
        if (sim.pd[0][0] - retention_time) > 0.1*epsilon: #TODO war auf 0.1*epsilon
            logging.log(20, "nahe %s, %s, %s", sim.params[0], sim.params[1], sim.pd)
            #print ("neuer test bei", sim.params[0]+0.1*(1-sim.params[0]), "und", sim.params[1]+0.1*sim.params[1])
            pkombis.append((sim.params[0], sim.params[1]+0.1*sim.params[1]))
            pkombis.append((sim.params[0] - 0.1*(1-sim.params[0]), sim.params[1]))
        elif (retention_time - sim.pd[0][0]) > 0.1*epsilon:
            logging.log(20, "nahe %s, %s, %s", sim.params[0], sim.params[1], sim.pd)
            #print ("neuer test bei", sim.params[1]-0.1*sim.params[1])
            pkombis.append((sim.params[0], sim.params[1]-0.1*sim.params[1]))
            pkombis.append((sim.params[0] + 0.1*(1-sim.params[0]), sim.params[1]))
        elif (abs(retention_time-sim.pd[0][0])) < 0.1*epsilon :
            logging.log(25, "sim: %s, %s", retention_time, sim.pd[0])
            number_of_good += 1      
    
    plot_all_width(get_approximate_sims(retention_time, 15, epsilon, 15), retention_time+epsilon, retention_time-epsilon)
    #pkombis.reverse()
    logging.log(27, "number of good: %s", number_of_good)
    if number_of_good < 23 - int(retention_time/10)+zahl:
        logging.log(25, "pkombis: %s", pkombis)
        #simulate_new(pkombis)
    else:
        logging.log(24, "alte anzahl good %s, neu: %s, ", len(approximate_sims), len(get_approximate_sims(retention_time, 15, epsilon, 15)))
    #for sim in get_approximate_sims(retention_time):
    #    print (sim.params, sim.pd)
    plotkram.plot_params_at_time(get_approximate_sims(retention_time, 15, epsilon, 15), retention_time, epsilon)
    
    
def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "beschreibung") 
    p.add_argument("--retention", "-r", type = float, help ="gewuenschte Retentionszeit")
    p.add_argument("--retepsilon", "-re", type = float, help ="moegliche Abweichung der Retentionszeit")
    p.add_argument("--width", "-w", type = float, help = "gewuenschte Breite")
    p.add_argument("--widepsilon", "-we", type = float, help = "moegliche Abweichung der Breite")
    p.add_argument("--destdir", "-d", help = "Ordner, in dem die Simulationen sind")
    p.add_argument("--length", "-l", type = int, help = "Laenge der Saeule")
    p.add_argument("--number", "-n", type = int, help = "Anzahl der Teilchen")
    p.add_argument("--test", "-atgfjzfjzf", action = "store_true", help = "plot a heatmap from single file with multiple simulations")
    return p

def main():
    startzeit = time.clock()
    logging.log(35, time.strftime("%d%b%Y_%H:%M:%S"))
    
    p = get_argument_parser()
    args = p.parse_args()
    
    global length, number
    length = args.length
    number = args.number
    
    for j in range(1):
        i=j-1
        logging.log(25, "Runde %s, epsilonj: %s, epsiloni: %s", j,  pow(10, 0-j), pow(10, 0-i))
        #find_good_params(25, 0-i)
        find_good_params(50, 0-i)
        find_good_params(50, 0-j)
        #find_good_params(75, 0-i)
        #find_good_params(100, 0-i)
        #find_good_params(125, 0-i)
        #zfind_good_params(150, pow(10, 0-i))
        #find_good_params(175, pow(10, 0-i))
        #find_good_params(200, pow(10, 0-i))
    
    plot_all_width(list_of_all_sims)
    
    approximate_sims = get_approximate_sims(args.retention, args.width, args.retepsilon, args.widepsilon)
    plot_all_width(approximate_sims)
    
    while True:            
        for i, aSim in enumerate(approximate_sims):
            print (i, aSim, aSim.pd)
        j = int(input("nr auswaehlen "))
        psvari = float(input("variiere ps um: "))
        pmvari = float(input("variiere pm um: "))
        print (j)
        selected_sim = approximate_sims[j]
        if selected_sim not in approximate_sims:
            print ("Ende")
            break
        else:
            print (type(selected_sim.params[0]))
            ps, pm = selected_sim.params
            pkombis = [(ps+psvari, pm), (ps-psvari, pm), (ps, pm+pmvari), (ps, pm-pmvari), (ps+psvari, pm+pmvari), (ps-psvari, pm-pmvari),
                    (ps+psvari,pm-pmvari), (ps-psvari, pm+pmvari)]
            pkombis = [(ps+psvari, pm+pmvari)]
            
            print (pkombis)
            
            if (input("testen?, dann ok tippen ") != "ok"):
                pass
            else:
                newsims = simulate_new(pkombis)
                print (newsims)  
            
            print ("apx", approximate_sims)
            time.sleep(10)
            for i, mySim in enumerate(newsims):
                if (mySim.pd[0][0]<(args.retention+args.retepsilon) and mySim.pd[0][0]>(args.retention-args.retepsilon) 
                    and mySim.pd[1] > (args.width-args.widepsilon) and mySim.pd[1] < (args.width+args.widepsilon)):
                    approximate_sims.append(mySim)
                    #print (i, mySim, mySim.pd)
            
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=22)
    main() 