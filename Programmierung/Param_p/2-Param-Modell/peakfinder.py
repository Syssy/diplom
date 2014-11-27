#!/usr/bin/env python
# -*- coding: latin-1 -*-

''' Sucht in allen vorhandenen Simulationen Peaks mit bestimmten Eigenschaften wie Location (loc-Parameter, entspricht Retentionszeit) und Breite des Peaks auf halber Hoehe'''

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
    length = args.length
    number = args.number
        
    list_of_all_sims = []
    
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
    logging.log(20, len(list_of_all_sims))
    list_of_all_sims.sort(key = lambda Simulation : Simulation.params)
    
    logging.log(10, list_of_all_sims[110:120])
    
    approximate_sims = []
    for i, mySim in enumerate(list_of_all_sims):
        if (mySim.pd[0][0]<(args.retention+args.retepsilon) and mySim.pd[0][0]>(args.retention-args.retepsilon) 
               and mySim.pd[1] > (args.width-args.widepsilon) and mySim.pd[1] < (args.width+args.widepsilon)):
            approximate_sims.append(mySim)
            print (i, mySim.pd, mySim)
                #time.sleep(10)
    while True:            
        j = int(input("nr auswaehlen "))
        psvari = float(input("variiere ps um:"))
        pmvari = float(input("variiere pm um:"))
        print (j)
        selected_sim = list_of_all_sims[j]
        if selected_sim not in approximate_sims:
            print ("Ende")
            break
        else:
            print (type(selected_sim.params[0]))
            ps, pm = selected_sim.params
            pkombis = [(ps+psvari, pm), (ps-psvari, pm), (ps, pm+pmvari), (ps, pm-pmvari), (ps+psvari, pm+pmvari), (ps-psvari, pm-pmvari),
                    (ps+psvari,pm-pmvari), (ps-psvari, pm+pmvari)]
            
            print (pkombis)
            newsims =  []
            for ps, pm in pkombis:
                try:
                    filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                    logging.log(15,"filename: %s", filename)
                    with open(filename, 'rb') as data:
                        logging.log(20,"geoeffnet, %s, %s", ps, pm)
                        mySim = pickle.load(data)
                except IOError:
                    logging.log(25, "simuliere, %s %s", ps, pm)
                    filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                    mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number)
                    mySim.simulate()
                    width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                    pd = (ls, width, heigth)
                    mySim.set_pd(pd)
                    logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                    with open(filename, 'wb') as data:
                        pickle.dump(mySim, data)
                list_of_all_sims.append(mySim)
            print (newsims)  
        for i, mySim in enumerate(list_of_all_sims):
            if (mySim.pd[0][0]<(args.retention+args.retepsilon) and mySim.pd[0][0]>(args.retention-args.retepsilon) 
                and mySim.pd[1] > (args.width-args.widepsilon) and mySim.pd[1] < (args.width+args.widepsilon)):
                approximate_sims.append(mySim)
                print (i, mySim.pd, mySim)
        
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 