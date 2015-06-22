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
#import seaborn

import simulation_2p as simulation

def plot_single_peak(peak, ff = False, num_bins = 50, qq = scipy.stats.norm):
    '''Plotte fuer einen Peak das Histogramm sowie qq-Plot zur Verteilung qq
    Besser plot_simlist verwenden, wenn nicht nur gezielt ein Peak angeschaut werden soll, oder Histogrammdarstellung erwuenscht'''
    data = peak
    # Falls from_file gewaehlt, oeffne file
    if ff:
        with open (peak, 'rb') as daten:
            data = pickle.load(daten)
    #Normales Hist plotten
    n, bins, patches = plt.hist(data.times, num_bins, normed=1, alpha=0.5 )
    plt.suptitle("params:" + str(data.params))
    # Jetzt noch ein qq-Plot
    x = np.arange(1, 250, 0.5)
    if qq == scipy.stats.invgauss:
        mu, loc, scale =  scipy.stats.invgauss.fit(data.times)
        logging.log(20, "ig-paramss, %s, %s, %s", str(mu), str(loc), str(scale))
        plt.plot(x,scipy.stats.invgauss.pdf(x,mu, loc, scale))
        logging.log(20,'skew, %s', str(scipy.stats.skew(data.times)))
        sm.qqplot(np.array(data.times), qq, distargs=(mu,),  line = 'r')
        plt.suptitle("params:" + str(data.params) + " qq-Plot mit Normalverteilung" )
    elif qq == scipy.stats.norm:
        sm.qqplot(np.array(data.times), qq, line='r')
        plt.suptitle("params:" + str(data.params) + " qq-Plot mit Inverser Gauss Verteilung: ")
    else: 
        print("not yet implemented, distribution:", qq)
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
        if sim.valid:
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
    
# erwartet datei, in der die sim als liste abgespeichert sind           
def plot_simlist_ff(datei, histogram_spec, histogram_noise, peak, qq_Plot_norm, fit_qq_Plot, num_bins = 50, compare_Dist= scipy.stats.invgauss):
    '''Erstelle simliste aus Datei, rufe plot_simlist auf'''
    logging.log(20, "plot_file: %s" + datei)
    with open(datei, 'rb') as daten:
        sim_list = pickle.load(daten)
       # print sim_list
        #print sim_list[0].times, sim_list[0].params
    plot_simlist(sim_list, histogram_spec, histogram_noise, peak,  qq_Plot_norm, fit_qq_Plot, num_bins, compare_Dist)

def plot_simlist(sim_list, histogram_spec, histogram_noise, peak, qq_Plot_norm, fit_qq_Plot, num_bins = 50, compare_Dist= scipy.stats.invgauss):
    '''Plotte eine Menge Simulationen, als Spektrum und je Peak als Einzelplot sowie qq-Plots zu gewaehlter Verteilung'''
    #TODO: Leider noch unflexibel was die Verteilung angeht. Momentan geloest mit fit = True
    # Spektrum aller enthaltenen Simulationen
    if histogram_spec:
        plot_spectrum(sim_list)
    #Spektrum mit zusaetzlichem Rauschen
    if histogram_noise and len(sim_list) < 20:
        noise = []
        for i in range(int(sim_list[0].number*len(sim_list)/10)):
            #noise.append(random.uniform(0, round(time_max)))
            noise.append(random.uniform(0, 240))
        for sim in sim_list:
            for t in sim.times:
                if sim.pd[0][0] < 250:
                    noise.append(t)
        plt.hist(noise, 500, normed = 1, alpha = 0.6)
        plt.suptitle("Spektrum mit Rauschen")
        plt.show()       
    # Je Peak ein Ausgabefenster mit separatem Histogramm/qq-Plot mit gewaehlten Params/qq mit automatischem Fit 
    number_stats = sum([peak, qq_Plot_norm, fit_qq_Plot])
    #print (number_stats)
    if peak or qq_Plot_norm or fit_qq_Plot:
        logging.log(25, "Erstelle separate Plots")
    for sim in sim_list:
        startzeit = time.clock() 
        # korrekte Anzahl Unterfenster erstellen
        fig = plt.figure(figsize=(4*number_stats, 4))
        gs1 = gridspec.GridSpec(1, number_stats)
        ax_list = [fig.add_subplot(ss) for ss in gs1]
        #zaehler fuer die gewuentschte Anzahl Fenster
        akt = 0
        fig.suptitle("ps, pm"+str(sim.params), size = 15)
        # Einzelnen Peak als Kurve (nicht Histogram) darstellen
        if peak:
            ax_list[akt].set_title("Peak")
            hist, bins = np.histogram(sim.times, bins=num_bins)
            offset = bins[1:]-bins[:-1]
            ax_list[akt].plot(bins[:-1]+offset, hist)
            akt+=1      
        # qq-Plot mit Normalverteilung
        if qq_Plot_norm:
            sm.qqplot (np.array(sim.times), scipy.stats.norm,  line = 'r', ax=ax_list[akt])
            ax_list[akt].set_title("qq-Plot; Normalverteilung")
            akt+=1  
        #qq Plot mit anderer Verteilung (z.B. Inverse Gauss)
        if fit_qq_Plot:
            sm.qqplot (np.array(sim.times), compare_Dist, fit=True,  line = 'r', ax=ax_list[akt])
            ax_list[akt].set_title("qq-Plot; gewaehlte Verteilung")
            akt+=1
            gs1.tight_layout(fig, rect=[0, 0.03, 1, 0.95]) 
        logging.log(20, "Zeit fuer Plot: %s", str(time.clock()-startzeit))
        plt.show()    

def plot_spectrum(sim_list, maxtime=250): 
    """Plottet ein Spektrum mehrerer Peaks, wird auch von plot_simlist aufgerufen, mit fester maxtime von 250s"""
    #plotkram.plot_widthmap(sim_list)
    logging.log(25, "starte plotting")
    sims = sim_list
    #ein Spektrum mit max 30 Chroms
    if len(sims) < 30:
        figg = plt.figure()
        legende = list()
        pp = list()
        plt.ylim((0, 1))
        plt.xlim((0, maxtime))
        for i, si in enumerate(sims):
            logging.log(24, "simparams: %s, peakdaten %s, max %f", si, si.pd, max(si.times))
            # teste hier auf bestimmte eigenschaften
            if (si.pd[0][0]<maxtime and si.pd[0][0]>0.01):
                n, bins, patches = plt.hist(si.times, 50, normed=1, alpha=0.5)
                pp.append(patches[0])
                legende.append(str(round(si.params[0], 10)) + ' ' + str(round(si.params[1], 10)))        
        plt.suptitle("l:" + str(sims[0].length) + " n:" + str(sims[0].number))
        figg.legend(pp, legende)
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
        
