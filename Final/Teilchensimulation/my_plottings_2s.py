# -*- coding: utf-8 -*-#!/usr/bin/env python
# -*- coding: latin-1 -*-
''
import argparse        
import logging
import pickle
import math
import time
import csv
import random

import scipy.stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statsmodels.api as sm
import numpy as np
import pylab
import matplotlib.gridspec as gridspec
from matplotlib import colors, cm

import simulation_2s as simulation

def plot_single_peak(data, histogram = False, peak=True, quartiles= True, num_bins = 50):
    '''Plotte fuer einen Peak Histogramm oder Peakkurve mit/ohne Quartile nach Wahl'''
    if peak:    
        fig, ax = plt.subplots()
        hist, bins = np.histogram(data.times, bins=num_bins, normed = True)
        offset = bins[1:]-bins[:-1]
        plt.plot(bins[:-1]+offset, hist)
        print (data.pd)
        print (hist, bins)
        hoehe = np.max(hist)
        # Quartile mitplotten
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
        plt.ylim((0, 0.3))
        plt.xlim((0, maxtime))
        plt.xlabel("Retentionszeit")
        plt.ylabel("Intensität")
        plt.suptitle("Spektrum mit Rauschen")
        plt.show()


def plot_widthmap(sim_array):
    '''Erstelle Heatmap ueber die Breiten der Peaks'''
    #print ("plot heatmap of width")
    #sortierte Liste der Params erstellen, noetig fuer die Ticks und die groesse des plots
    ps_list = sorted(list(set([sim.params[0] for sim in sim_array])))
    pm_list = sorted(list(set([sim.params[1] for sim in sim_array])))
    #print ("ps", ps_list, "pm", pm_list)   
    #Alle Breiten ins array, das sind die zu plottenden Daten
    array_of_width = [[sim.pd[3] for sim in sim_array if sim.params[0]==ps] for ps in ps_list]
    #print ("breiten", array_of_width)
    #Plot erstellen
    fig, ax = plt.subplots()
    cax = ax.imshow(array_of_width, origin = 'lower', interpolation="nearest", extent = [0,len(pm_list),0,len(ps_list)])  
    #Skala passend setzen
    plt.yticks(np.arange(len(ps_list)), ps_list)
    plt.xticks(np.arange(len(pm_list)), pm_list)
    # Beschriftungen
    plt.ylabel("ps")
    plt.xlabel("pm")
    plt.suptitle("widthmap")
    #Colorbar als Legende
    cbar = fig.colorbar(cax)
    plt.show()
            
def plot_widthandskew(sim_list, plot_width = True, plot_skew = False):
    '''Erstelle quasi Scatterplots, mit jeder Punkt ist eine Sim, beschriftet mit seinen Params, Koords aus Zeitpunkt und IQR/Schiefe'''
    #logging.log(22, "plotte Groessenverhaeltnisse")
    fig2 = plt.figure()
    #Gewuenschte Plots erstellen und Beschriften
    if plot_width:
        ax3 = fig2.add_subplot(1,1+plot_skew,1)
        ax3.set_ylabel("breite")
        ax3.set_xlabel("Zeit")
        ax3.set_title("ps \n pm")
        #ax3.legend
    if plot_skew:
        ax4 = fig2.add_subplot(1,1+plot_width,1+plot_width)
        ax4.set_ylabel("Skewness")
        ax4.set_xlabel("Zeit")
        ax4.set_title("Schiefe")
    #Alle Peakdaten plotten
    for sim in sim_list:
        if sim.pd[0][0] < 240:
            if plot_width:
                (loc, scale), breite, height, iqr = sim.pd
                point = ax3.plot([loc], [breite], "ro-")
                t = ax3.text(loc, breite, str(sim.params[0])+'\n'+str(sim.params[1]), size= "small")#oder xx-small
            if plot_skew:
                anotherpoint = ax4.plot([loc], [sim.skewness], "bx")  
    plt.show()
     
def plot_params_at_time(sim_list, t, epsilon = 0.1, show_params = False):
    """plotte Parameterkombinationen zu Zeit t, mit erlaubter Abweichung von t um epsilon"""
    # Plot erstellen und beschriften
    ax = plt.axes()
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    plt.xlabel("ps")
    plt.ylabel("pm")
    # Alle Sim durchgehen, wenn Bedingung erfuellt, plotten
    for sim in sim_list:
        if abs(sim.pd[0][0] - t) > epsilon:
            logging.log(24, "Abweichung zu gross, %s, bei sim %s", sim.pd[0], sim)
        else:
            #Groesse der Punkte zeigt Breite(IQR) des Peaks    
            ax.plot(sim.params[0], sim.params[1], "co", markersize = sim.pd[3]*2)
            if show_params:
                ax.text((sim.params[0]), sim.params[1], str(round(sim.pd[3], 2)))
        logging.log(21, sim.pd[3])
    plt.suptitle("Parameter fuer Zeit "+ str(t) + " mit Epsilon " + str(epsilon))
    plt.show()    
    
def plot_heatmap_of_moments(data, ff = False, moment = "skewness"):
    '''Heatmap ueber gewaehltes Moment plotten, geht davon aus, dass alle moeglichen ps/pm-Kombis da sind.'''
    logging.log(20, "plot heatmap")
    sim_array = data
    #evtl Daten laden
    if ff:
        with open (data, 'rb') as daten:
            sim_array = pickle.load(daten)          
    #sortierte Liste der Params erstellen, noetig fuer die Ticks und die groesse des plots
    ps_list = sorted(list(set([sim.params[0] for sim in sim_array])))
    num_ps = len(ps_list)
    pm_list = sorted(list(set([sim.params[1] for sim in sim_array]))) 
    num_pm = len(pm_list)
    sim_array = np.reshape(sim_array, (num_ps, num_pm))
    logging.log(20, "Moment %s", moment)
    
    #Zu plottende Daten zusammentragen
    to_plot = np.zeros((num_ps, num_pm))
    for i in range(num_ps):
    #print '\n'
        for j in range(num_pm): 
            #Falls Logscale gewuenscht ist
            if False:#moment == "mean" or moment == "variance":
                to_plot[i][j] = math.log(sim_array[i][j].get_moment(moment))
            else:
                to_plot[i][j] = sim_array[i][j].get_moment(moment) 
    #Plot erstellen
    fig, ax = plt.subplots() 
    cax = ax.imshow(to_plot, origin = 'lower', interpolation="nearest")
    #Beschriftungen
    plt.xticks(np.arange(num_pm), pm_list)    
    plt.yticks(np.arange(num_ps), ps_list)
    plt.xlabel("pm")
    plt.ylabel("ps")
    plt.suptitle("Laenge"+ str(sim_array[i][j].length)+ " Anzahl"+ str(sim_array[i][j].number) + " \nMoment: " + moment)
    
    cbar = fig.colorbar(cax)
    plt.show()
    
# Vier Heatmaps fuer die Ecken plotten, je mit einzelner Colorbar, da die Werte oft nicht vergleichbar sind, ruft plot_4_heatmaps auf       
def plot_4_heatmaps_ff(filename, moment="skewness"):
    logging.log(20, "oeffne: %s", filename)
    with open (filename, "rb") as datei:
        sim_array = pickle.load(datei)
    num = 0
    #print len(sim_array), sim_array
    for sl in sim_array:
        for sim in sl:
            num +=1
    logging.log(25, "anzahl sim: %s", str(num))
    # Nach Parametern sortieren, damit das plotten der Heatmap was sinnvolles ergibt
    # TODO eigentlich total bescheuert, da in dieser Variante eigentlich schon sortiert ist. Nur halt andere RF
    sim_array = np.reshape(sim_array, num)
    mySortedSims = sorted(sim_array, key= simulation.get_pm)
        #print mySortedSims1, '\n\n'
    sim_array = sorted(mySortedSims, key = simulation.get_ps)
        #print sim_array    
    plot_4_heatmaps(sim_array, num, moment)
       
# Hier soll der input ein sim_array ein, sortiert eine nxn-M der Sim    
def plot_4_heatmaps(data, ff = False, moment = "skewness"):
    '''Plottet jeweils die "Ecken" der heatmap der Momente, gedacht, um Detailunterschiede besser sichtbar zu machen und wenn jeweils alle Werte nah bei 0/1 geplottet werden sollen, ohne den ganzen Raum dazwischen. Funktioniert nur bei gerader, quadratischer Anzahl von Simulationen'''
    sim_array = data
    #evtl Daten laden
    if ff:
        with open (data, 'rb') as daten:
            sim_array = pickle.load(daten) 
    #Anzahl der Sim bestimmen        
    num_sim = 0
    for sl in sim_array:
    #    for sim in sl:
            num_sim +=1
    print (num_sim)       
    #Die darzustellende Achsenweite/Parameterraum, 
    scale = int(math.sqrt(num_sim)/2)
    print (scale)
    #Sim sortieren und in numpy format umwandeln
    sim_array = sorted(sim_array, key = simulation.Simulation.get_pm)
    sim_array = sorted(sim_array, key = simulation.Simulation.get_ps)
    sim_array = np.reshape(sim_array, (math.sqrt(num_sim), math.sqrt(num_sim)))
    #Plot erstellen
    fig = plt.figure()
    plt.suptitle(moment)
    
    # Jetzt folgen die vier plots, Unterscheidung nur durch Zugriff auf sim_array[i(+scale)][j(+scale)]
    #ul, ps&pm klein
    logging.log(20, "Plot1, ul223")
    data_to_plot = []
    labelset0, labelset1 =  set(), set()
    #Gesuchte Momente in die Datenliste packen, Listen fuer Beschriftung erstellen
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i][j].get_moment(moment))
            labelset0.add(sim_array[i][j].params[0])
            labelset1.add(sim_array[i][j].params[1])
        data_to_plot.append(hilfsliste1)
    #Plotten
    ax = fig.add_subplot(223) 
    cax = plt.imshow(data_to_plot, origin = "lower")
    #Beschriften
    pslabels = sorted(list(labelset0)) 
    plt.yticks(np.arange(len(pslabels)), pslabels)
    pmlabels = sorted(list(labelset1)) 
    plt.xticks(np.arange(len(pmlabels)), pmlabels)
    plt.xlabel("pm")
    plt.ylabel("ps")
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in data_to_plot]), max([max(hl) for hl in data_to_plot]), 5))
    
    #ur, pspm gross, klein, gleiches wie oben
    logging.log(20, "plot2, ol221")
    data_to_plot = []
    labelset1, labelset0 = set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i+scale][j].get_moment(moment))
            labelset1.add(sim_array[i+scale][j].params[1])
            labelset0.add(sim_array[i+scale][j].params[0])
        data_to_plot.append(hilfsliste1)
    ax = fig.add_subplot(221) 
    cax = plt.imshow(data_to_plot, origin = "lower")
    pslabels = sorted(list(labelset0)) 
    plt.yticks(np.arange(len(pslabels)), pslabels)
    pmlabels = sorted(list(labelset1)) 
    plt.xticks(np.arange(len(pmlabels)), pmlabels)
    plt.xlabel("pm")
    plt.ylabel("ps")
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in data_to_plot]), max([max(hl) for hl in data_to_plot]), 5))
   
    #ol ps klein & pm gross, gleiches wie oben
    logging.log(20,"plot3, ur224")
    data_to_plot = []
    labelset1, labelset0 = set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i][j+scale].get_moment(moment))
            labelset1.add(sim_array[i][j+scale].params[1])
            labelset0.add(sim_array[i][j+scale].params[0])  
            #    print sim_array[i][j],
        data_to_plot.append(hilfsliste1)
    ax = fig.add_subplot(224) 
   # print min(labelset1), max(labelset1), min(labelset0), max(labelset0)
    cax = plt.imshow(data_to_plot, origin = "lower")#, extent=[min(labelset1), max(labelset1), min(labelset0), max(labelset0)])
    pslabels = sorted(list(labelset0)) 
    plt.yticks(np.arange(len(pslabels)), pslabels)
    pmlabels = sorted(list(labelset1)) 
    plt.xticks(np.arange(len(pmlabels)), pmlabels)
    #print "max", max([max(hl) for hl in data_to_plot]), " min", min([min(hl) for hl in data_to_plot])
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in data_to_plot]), max([max(hl) for hl in data_to_plot]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps")
    #plotlist.append(data_to_plot)
   
    #or ps&pm gross
    logging.log("plot4, or222")
    data_to_plot = []
    labelset1, labelset0 = set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i+scale][j+scale].get_moment(moment))
            #print sim_array[i+scale][j+scale],math.log(sim_array[i+scale][j+scale].get_moment(moment)),
            labelset1.add(sim_array[i+scale][j+scale].params[1])
            labelset0.add(sim_array[i+scale][j+scale].params[0])
        data_to_plot.append(hilfsliste1)
        #print '\n'    
    ax = fig.add_subplot(222) 
   # print min(labelset1), max(labelset1), min(labelset0), max(labelset0)
    cax = plt.imshow(data_to_plot, origin = "lower")#, extent=[min(labelset1), max(labelset1), min(labelset0), max(labelset0)])
    pslabels = sorted(list(labelset0)) 
    plt.yticks(np.arange(len(pslabels)), pslabels)
    pmlabels = sorted(list(labelset1)) 
    plt.xticks(np.arange(len(pmlabels)), pmlabels)
    #print "max", max([max(hl) for hl in data_to_plot]), " min", min([min(hl) for hl in data_to_plot])
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in data_to_plot]), max([max(hl) for hl in data_to_plot]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps") 
    plt.show()
       
              
def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "beschreibung")
    #p.add_argument("--langerbefehl", "-l", help='hilfe', action='store_true', dest = 'destination')   
    p.add_argument("--inputfile", "-i", help = "input file")
    p.add_argument("--moment", "-m" , help = "which moment to plot as heatmap")
    p.add_argument("--singlefile", "-sf", action = "store_true", help = "plot a heatmap from single file with multiple simulations")
    p.add_argument("--singlesimulation", '-ss', action = "store_true", help = "plot a single simulation (histogram and qq)")
    p.add_argument("--multiple_files", '-mf', action="store_true", help = "read multiple files, each a single spectrum")
    p.add_argument("--number", "-n", type=int, help= "how many files to read")
    p.add_argument("--recalculate", "-rc", action = "store_true", help = "Whether moments should be recalculated before plotting")
    return p

def main():
    '''Fuer Testzwecke'''
    p = get_argument_parser()
    args = p.parse_args()
       
    if args.recalculate:
        filename = args.inputfile
        sims = None
        with open(filename,'rb') as datei:
            sims = pickle.load(datei)
           # print np.shape(sims)
        for ls in sims:
           # print '-',
            for sim in ls:
                sim.recalculate_params()
                sim.recalculate_moments()
        with open(filename, 'wb') as datei:
            pickle.dump(sims, datei)
        
    if args.singlefile:
        filename = args.inputfile
        plot_heatmap_from_file(filename,0, args.moment, args.recalculate)
        plot_4_heats_from_file(filename, args.moment, args.recalculate)
        
    if args.multiple_files: 
        number = args.number
        print( "multiple_files: ", number)
        filename = args.inputfile
        
        mySims = np.array([None]*number)
        num = 0
        fehlercounter = 0
        for i in range(number):
            #print "oeffne jetzt", ps, pm,
            try:
                with open(filename+str(i+1)+".p", 'rb') as daten:
                #print daten
                    aSim = pickle.load(daten)
                    mySims[num] = aSim
            except IOError:
                mySims[num] = Simulation(1, 1)
                fehlercounter +=1
                #print "fehler",
            num += 1    
            print ("alle offen mit ", fehlercounter, ' fehlend')
        
        # Nach Parametern sortieren, damit das plotten der Heatmap was sinnvolles ergibt
        mySortedSims1 = sorted(mySims, key= Simulation.get_pm)
        #print mySortedSims1, '\n\n'
        mySortedSims = sorted(mySortedSims1, key = Simulation.get_ps)
            #print mySortedSims
        plot_4_heatmaps(mySortedSims, number, args.moment)   
        print( "fertig")
            
    if args.singlesimulation:
        plot_single_histqq_ff(args.inputfile)
        plot_single_peak(args.inputfile, ff=True)


    
    plt.show()  

if __name__ == "__main__":
    main()
        
