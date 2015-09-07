# -*- coding: utf-8 -*-#!/usr/bin/env python
# -*- coding: latin-1 -*-
'''Enthaelt einige Funktionen zum Plotten von Simulationen/Simulationslisten der 2s-Teilchensimulation'''

import argparse        
import logging
import pickle
import math
import time
import random
import os

import matplotlib.pyplot as plt
import numpy as np
#from matplotlib import colors, cm

import simulation

def plot_single_peak(data, histogram = False, peak=True, quartiles= True, num_bins = 50):
    '''Plotte fuer einen Peak Histogramm oder Peakkurve mit/ohne Quartile nach Wahl'''
    if peak:    
        fig, ax = plt.subplots()
        hist, bins = np.histogram(data.times, bins=num_bins, normed = True)
        offset = bins[1:]-bins[:-1]
        plt.plot(bins[:-1]+offset, hist)
        #print (data.pd)
        #print (hist, bins)
        hoehe = np.max(hist)
        # Quartile mitplotten (Linien von 0 bis hoehe)
        if quartiles:
            plt.plot([data.pd[1][0], data.pd[1][0]], [0, hoehe], color="lightblue")
            plt.plot([data.pd[1][1], data.pd[1][1]], [0, hoehe], color="lightblue")
            plt.plot([data.pd[1][2], data.pd[1][2]], [0, hoehe], color="lightblue")
        plt.xlabel("Retentionszeit")
        plt.ylabel("Anteil Teilchen")
        plt.title("Parameter:" + str(data.params))
        plt.suptitle("loc " + str(round(data.pd[0],2))+ " iqr "+str(round(data.pd[2],2)) + " skew " +str(round(data.pd[3],2)))
        plt.annotate(str(data.pd[0])+str(data.pd[2])+str(data.pd[3]),(data.pd[1][2] * 10, data.pd[1][2] * 10))
        plt.show()
    #Normales Histogramm plotten
    if histogram:
        n, bins, patches = plt.hist(data.times, num_bins, alpha=0.5 )
        plt.title("ps: " + str(data.params[0]) +" pm: " + str(data.params[1]))
        plt.xlabel("Retentionszeit")
        plt.ylabel("Anzahl Teilchen")
        plt.show()

def plot_spectrum(sims, noise = False, maxtime=240): 
    """Plottet ein Spektrum aus maximal 30 Peaks bis zu Retentionszeit maxtime, wahlweise mit oder ohne Rauschen"""
    logging.log(15, "starte plotting")
    #ein Spektrum mit max 30 Chroms, gemeinsame Zeitenliste erstellen
    if len(sims) < 30:
        spectrum = [0,maxtime]
        #evtl Rauschen hinzufuegen
        if noise:
            for i in range(int(sims[0].number*len(sims)/10)):
                spectrum.append(random.uniform(0, maxtime))
        for sim in sims:
            for t in sim.times:
                if sim.pd[0] < 250:
                    spectrum.append(t)
        hist, bins = np.histogram(spectrum, bins= maxtime, normed = True)
        offset = bins[1:]-bins[:-1]
        plt.plot(bins[:-1]+offset, hist)
        #plt.ylim((0, 0.3))
        plt.xlim((0, maxtime))
        plt.xlabel("Retentionszeit")
        plt.ylabel("Intensität")
        title = "Spektrum"
        if noise:
            title += " mit Rauschen"
        plt.suptitle(title)
        plt.show()

def plot_trait(sim_array, trait = "loc"):
    '''Erstelle Heatmap ueber die Eigenschaft der Peaks, nur sinnvoll für systematische Simulationenliste'''
    # traitdict enhält die Positionen der gewählten Eigenschaft in den pd
    if sim_array[0].model != "2s":
        logging.log(40, "Plot nicht verfuegbar fuer 3-Zustaende Modell")
        return
    traitdict =  {"loc": (0, "Lage"), "iqr": (2, "Breite"), "qk": (3, "Schiefe")}
    try:
        c = traitdict[trait][0]
    except KeyError:
        logging.log(40, "Bitte Eigenschaft waehlen")
        return
    #sortierte Liste der Params erstellen, noetig fuer die Ticks und die groesse des plots
    ps_list = sorted(list(set([sim.params[0] for sim in sim_array])))
    pm_list = sorted(list(set([sim.params[1] for sim in sim_array])))
    #print ("ps", ps_list, "pm", pm_list)   
    #Alle Breiten ins array, das sind die zu plottenden Daten
    array_of_width = [[sim.pd[c] for sim in sim_array if sim.params[0]==ps] for ps in ps_list]
    print ("breiten", array_of_width)
    #Plot erstellen
    fig, ax = plt.subplots()
    cax = ax.imshow(array_of_width, origin = 'lower', interpolation="nearest", extent = [0,len(pm_list),0,len(ps_list)])  
    #Skala passend setzen
    plt.yticks(np.arange(len(ps_list)), ps_list)
    plt.xticks(np.arange(len(pm_list)), pm_list)
    # Beschriftungen
    plt.ylabel("ps")
    plt.xlabel("pm")
    plt.suptitle("Eigenschaft der Peaks: " + traitdict[trait][1])
    #Colorbar als Legende
    cbar = fig.colorbar(cax)
    plt.show()
            
def plot_reachable(folder, show_params = False):
    '''Erstelle Scatterplots, mit jeder Punkt ist eine Sim, beschriftet evtl mit seinen Params, Koords aus Zeitpunkt und IQR'''
    #logging.log(22, "plotte Groessenverhaeltnisse")
    if "2s" not in folder:
        logging.log(40, "Plot nicht verfuegbar fuer 3-Zustaende Modell")
        return
    filenames = [name for name in os.listdir(folder) if name.startswith("Sim_")]
    #print (len(filenames))
    fig2 = plt.figure()
    plt.ylabel("breite")
    plt.xlabel("Zeit")
    plt.title("ps \n pm")
    for filename in filenames:  
        with open (folder+filename, "r+b") as data:
            sim = pickle.load(data)
            #Alle Peakdaten plotten
            if sim.pd[0] < 240 and sim.valid:
                point = plt.plot(sim.pd[0], sim.pd[2], "ro-")
                if show_params:
                    t = plt.text(sim.pd[0], sim.pd[2], str(sim.params[0])+'\n'+str(sim.params[1]), size= "small")#oder xx-small
    plt.show()
     
def plot_params_at_time(folder, t, epsilon = 0.1, show_params = False):
    """plotte Parameterkombinationen zu Zeit t, mit erlaubter Abweichung von t um epsilon"""
    # Plot erstellen und beschriften
    if "2s" not in folder:
        logging.log(40, "Plot nicht verfuegbar fuer 3-Zustaende Modell")
        return    
    ax = plt.axes()
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    plt.xlabel("ps")
    plt.ylabel("pm")
    filenames = [name for name in os.listdir(folder) if name.startswith("Sim_")]
    # Alle Sim durchgehen, wenn Bedingung erfuellt, plotten
    for filename in filenames:  
        with open (folder+filename, "r+b") as data:
            sim = pickle.load(data)
            if sim.valid:
                if abs(sim.pd[0] - t) > epsilon:
                    logging.log(24, "Abweichung zu gross, %s, bei sim %s", sim.pd[0], sim)
                else:
                    #Groesse der Punkte zeigt Breite(IQR) des Peaks    
                    logging.log(20, "Gefunden: %s", sim.pd)
                    ax.plot(sim.params[0], sim.params[1], "o", markersize = 2+(sim.pd[2]), label = (str(round(sim.pd[2],2)) + "  " +  str(round(sim.pd[0], 2))))
                    if show_params:
                        ax.text(sim.params[0], sim.params[1], str(round(sim.params[0],8)) +"_" + str(round(sim.params[1],5)))
        logging.log(21, sim.pd[3])
    plt.suptitle("Parameter fuer Zeit "+ str(t) + " mit Abweichung " + str(epsilon))
    plt.legend(title = "Breite,   Retentionszeit", numpoints = 1, loc = 2)
    plt.show()    
    
def main():
    '''Fuer Testzwecke'''
    print ("Aufruf der Funktionen ueber simulate_and_plot")    

if __name__ == "__main__":
    main()
        
