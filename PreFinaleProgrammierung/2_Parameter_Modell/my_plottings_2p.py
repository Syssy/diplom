# -*- coding: utf-8 -*-#!/usr/bin/env python
# -*- coding: latin-1 -*-
''
import argparse        
import logging
import pickle
import math
import time
import csv

import scipy.stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import pylab
import matplotlib.gridspec as gridspec
from matplotlib import colors, cm

import simulation_2p as simulation


# Eine einzelne Heatmap aus einer .pickleDatei machen
def plot_heatmap_from_file(datei, squareroot_num_sim, moment, recalc = False):
    startzeit = time.clock()
    print ("plot heatmap " + datei)
    with open(datei, 'rb') as daten:
        sim_array = pickle.load(daten)  
        squareroot_num_sim = sim_array.shape[0]
        sim_array = np.reshape(sim_array, squareroot_num_sim*squareroot_num_sim)
        if recalc:
            for sim in sim_array:
                sim.recalculate()
        mySortedSims = sorted(sim_array, key= Simulation.get_pm)
        #print mySortedSims1, '\n\n'
        sim_array = sorted(mySortedSims, key = Simulation.get_ps)
        plot_heatmap(sim_array, squareroot_num_sim, moment)

def plot_widthmap(sim_array, nr_ps=10, nr_pm=10):
    print ("plot heatmap of width")
    
    ps_list = sorted(list(set([sim.params[0] for sim in sim_array])))
    pm_list = sorted(list(set([sim.params[1] for sim in sim_array])))
    print ("ps", ps_list, "pm", pm_list)
    
    hilfsdings = [[sim.pd[1] for sim in sim_array if sim.params[0]==ps] for ps in ps_list]
    print ("breiten", hilfsdings)
    #for sim in sim_array:
    #    print (round(sim.params[0],5), round(sim.params[1], 5) , sim.pd[1])
    
    fig, ax = plt.subplots() 
    cax = ax.imshow(hilfsdings, origin = 'lower', interpolation="nearest", extent = [0,len(pm_list),0,len(ps_list)])  
    plt.yticks(np.arange(len(ps_list)), ps_list)
    plt.xticks(np.arange(len(pm_list)), pm_list)
    #plt.xlabels(ps_list)
    plt.ylabel("pm")
    plt.xlabel("ps")
    plt.suptitle("widthmap")
    
    cbar = fig.colorbar(cax)#, ticks=[np.amin(to_plot), 0, np.amax(to_plot)])*
            
   #
def plot_widthandskew(sim_list, plotwidth = True, plotskew = False):
    peak_data = []
    sims = []
    for sim in sim_list:
        try:
            pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], sim.skewness)
            #willkürlich gewählt: loc <> xy, scale < z width < v...
            if sim.pd[0][0] < 240 and sim.pd[0][1] < 60 and sim.pd[1] < 50 and sim.pd[0][0] > 0:
                peak_data.append(pd)
                sims.append(sim)
                #print ("pd", pd)
                #with open(filename, "r+") as data:
                #   x = data.read()
                  # print (data, x)
                    #data.write(str(pd) + '\n')    
        except AttributeError as err:
            print (sim.params, err)
            sim.recalculate_moments()
            with open('v005/l' + str(sim.length) + "/n" + str(sim.number) + '/Sim_' + str(round(sim.params[0], 10)) + 
                      '_' + str(round(sim.params[1], 10)) + ".p", "wb") as datei:
                pickle.dump(sim, datei)
            pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], sim.skewness)
            #willkürlich gewählt: loc <> xy, scale < z width < v...
            if sim.pd[0][0] < 240 and sim.pd[0][1] < 60 and sim.pd[1] < 50 and sim.pd[0][0] > 0:
                peak_data.append(pd)
                sims.append(sim)
    logging.log(22, "plotte Groessenverhaeltnisse")
    fig2 = plt.figure()
    if plotwidth:
        ax3 = fig2.add_subplot(1,1+plotskew,1)
        ax3.set_ylabel("Breite")
    if plotskew:
        ax4 = fig2.add_subplot(1,1+plotwidth,1+plotwidth)
        ax4.set_title("Skew")
    points = []
       # print (peakdaten)
    for pd in peak_data:
           # print (pd)
            (params, (loc, scale), breite, hoehe, skew) = pd
            #print (loc, breite)
            if plotwidth:
                point = ax3.plot([loc], [breite], "ro")
                #text = plt.text(s=params, x= loc,y= breite, fontsize = "xx-small")
                #ax3.annotate(params, (loc, breite))
                t = ax3.text(loc, breite, str(params[0])+'\n'+str(params[1]), size= "xx-small")
            if plotskew:
                anotherpoint = ax4.plot([loc], [skew], "bx")
           # print("Params:", params, ":", point[0].get_xydata(), "Scale:", scale, "hoehe", hoehe)
           # points.extend(point)        
    plt.show()
    #TODO: Eigentlich sollte hier kein return mehr sein, aber ist historisch so :/
    return sims
       
def plot_params_at_time(sim_list, t, epsilon = 0.1):
    """plotte Parameterkombinationen zu Zeit t"""
    ax = plt.axes()
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    plt.xlabel("ps")
    plt.ylabel("pm")
    for sim in sim_list:
        if abs(sim.pd[0][0] - t) > epsilon:
            logging.log(35, "Fehler, Abweichung zu groß, %s, bei sim %s", sim.pd[0], sim)
        ax.plot(sim.params[0], sim.params[1], "go", markersize = sim.pd[1]*2)
        #text = ax.text((sim.params[0]-0.000005), sim.params[1]+0.02, str(round(sim.pd[1], 2)), rotation = -45)
        logging.log(21, sim.pd[1])
    plt.suptitle("Parameter für Zeit "+ str(t))
    plt.show()    
        
# Eine einzelne Heatmap aus einem array plotten, (Aufruf von der Simulation)      
def plot_heatmap(sim_array, squareroot_num_sim, moment):
    print ("plot heatmap")
    #print sim_array,len(sim_array)
   # squareroot_num_sim = int(len(sim_array)/2)
   # print squareroot_num_sim
    
    if not squareroot_num_sim:
        print ("kein squareroot_num_sim")
        return None
    
    sim_array = np.reshape(sim_array, (squareroot_num_sim,squareroot_num_sim))
    print ("Moment", moment)
    to_plot = np.zeros((squareroot_num_sim, squareroot_num_sim))
    
    for i in range(squareroot_num_sim):
    #print '\n'
        for j in range(squareroot_num_sim):
            if sim_array[i][j]: 
                #print sim_array[i][j].get_moment(moment), 
                #print type(sim_array[i][j])
            #   if sim_array[i][j].get_moment(moment) == 0 or sim_array[i][j].get_moment(moment) <0:
            #         print "params +moment ", sim_array[i][j].params, ' ', (sim_array[i][j].get_moment(moment)), (sim_array[i][j].times)
            
                if False:#moment == "mean" or moment == "variance":
                    to_plot[i][j] = math.log(sim_array[i][j].get_moment(moment))
                else:
                    to_plot[i][j] = sim_array[i][j].get_moment(moment)
        
            else:
                to_plot[i][j] = None
                print ("none")
     
    #print "toplot ", to_plot
    

    fig, ax = plt.subplots() 
    # extent scheint die achsenbeschriftung zu sein
    cax = ax.imshow(to_plot, origin = 'lower', interpolation="nearest", extent = [0,1,0,1])  
    plt.xticks(np.arange(2))
    #plt.yticks([0, 0.5, 1])
    plt.yticks(np.arange(2))
    plt.xlabel("pm")
    plt.ylabel("ps")
    #print sim_array[i][j].length
    plt.suptitle("Laenge"+ str(sim_array[i][j].length)+ " Anzahl"+ str(sim_array[i][j].number))
    
    cbar = fig.colorbar(cax)#, ticks=[np.amin(to_plot), 0, np.amax(to_plot)])*
    #plt.show()
    
# Vier Heatmaps für die Ecken plotten, je mit einzelner Colorbar, da die Werte oft nicht vergleichbar sind       
def plot_4_heats_from_file(filename, moment, recalc = False):
    print ("öffne", filename)
    with open (filename, "rb") as datei:
        sim_array = pickle.load(datei)
    num = 0
    #print len(sim_array), sim_array
    for sl in sim_array:
        for sim in sl:
            if recalc:
                sim.recalculate()
            num +=1
    print ("anzahl sim: ", num   )
    # Nach Parametern sortieren, damit das plotten der Heatmap was sinnvolles ergibt
    # TODO eigentlich total bescheuert, da in dieser Variante eigentlich schon sortiert ist. Nur halt andere RF
    sim_array = np.reshape(sim_array, num)
    mySortedSims = sorted(sim_array, key= Simulation.get_pm)
        #print mySortedSims1, '\n\n'
    sim_array = sorted(mySortedSims, key = Simulation.get_ps)
        #print sim_array    
    plot_4_heatmaps(sim_array, num, moment)
       
# Wie from file, nur der input sim_array sollte sortiert eine nxn-M der Sim sein     
def plot_4_heatmaps(sim_array, num_sim, moment):    
    print ("4heats", num_sim, math.sqrt(num_sim)/2)
    
    #Die darzustellende Achsenweite/Parameterraum, 
    scale = int(math.sqrt(num_sim)/2)
    print (scale, "scale")
    
    #veraltet erstelle plotlisten (data für imshow), TODO kann noch hübscher werden, 
    #print sim_array
    #print np.shape(sim_array)
    sim_array = np.reshape(sim_array, (math.sqrt(num_sim), math.sqrt(num_sim)))
    
    #plotlist = []
    #hilfsliste1 = [] 
    
    fig = plt.figure()
    
    # Jetzt folgen die vier plots, Unterscheidung nur durch Zugriff auf sim_array[i(+scale)][j(+scale)]
    #ul, ps&pm klein
    print ("Plot1, ul223")
    hilfsliste2 = []
    labelset1, labelset2 =  set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i][j].get_moment(moment))
            # print sim_array[i][j], math.log(sim_array[i][j].get_moment(moment)),
            labelset1.add(sim_array[i][j].params[1])
            labelset2.add(sim_array[i][j].params[0])
        hilfsliste2.append(hilfsliste1)
    #print '\n'
    #plotlist.append(hilfsliste2)
    ax = fig.add_subplot(223) 
    #print min(labelset1), max(labelset1), min(labelset2), max(labelset2)
    cax = plt.imshow(hilfsliste2, origin = "lower", extent=[min(labelset1), max(labelset1), min(labelset2), max(labelset2)])
   # print "max", max([max(hl) for hl in hilfsliste2]), " min", min([min(hl) for hl in hilfsliste2]), 
   # print "achse", np.linspace(min([min(hl) for hl in hilfsliste2]), max([max(hl) for hl in hilfsliste2]), 5)
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in hilfsliste2]), max([max(hl) for hl in hilfsliste2]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps")
    
    #ur, pspm!!
    print ("plot2, ol221")
    hilfsliste2 = []
    labelset1, labelset2 = set(), set()
#    print labelset 
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i+scale][j].get_moment(moment))
    #       print sim_array[i+scale][j], (sim_array[i+scale][j].get_moment(moment)),
            labelset1.add(sim_array[i+scale][j].params[1])
            labelset2.add(sim_array[i+scale][j].params[0])
        hilfsliste2.append(hilfsliste1)
    #   print '\n'
    ax = fig.add_subplot(221) 
#    print len(hilfsliste2), len(hilfsliste1)
#    print '\n', labelset, '\n\n', labelset1, labelset2
    #print min(labelset1), max(labelset1), min(labelset2), max(labelset2)
    cax = plt.imshow(hilfsliste2, origin = "lower", extent=[min(labelset1), max(labelset1), min(labelset2), max(labelset2)])
#    print "max", max([max(hl) for hl in hilfsliste2]), " min", min([min(hl) for hl in hilfsliste2])
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in hilfsliste2]), max([max(hl) for hl in hilfsliste2]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps")
    #plotlist.append(hilfsliste2)
    #print hilfsliste2
   
   
    #ol ps klein & pm groß
   # print "plot2, ur224"
    hilfsliste2 = []
    labelset1, labelset2 = set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i][j+scale].get_moment(moment))
    #       print sim_array[i][j+scale], math.log(sim_array[i][j+scale].get_moment(moment)),
            labelset1.add(sim_array[i][j+scale].params[1])
            labelset2.add(sim_array[i][j+scale].params[0])  
            #    print sim_array[i][j],
        hilfsliste2.append(hilfsliste1)
    #print '\n'
    ax = fig.add_subplot(224) 
   # print min(labelset1), max(labelset1), min(labelset2), max(labelset2)
    cax = plt.imshow(hilfsliste2, origin = "lower", extent=[min(labelset1), max(labelset1), min(labelset2), max(labelset2)])
    #print "max", max([max(hl) for hl in hilfsliste2]), " min", min([min(hl) for hl in hilfsliste2])
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in hilfsliste2]), max([max(hl) for hl in hilfsliste2]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps")
    #plotlist.append(hilfsliste2)
   
    #or ps&pm groß
  #  print "plot2, or222"
    hilfsliste2 = []
    labelset1, labelset2 = set(), set()
    for i in range (scale):
        hilfsliste1 = []
        for j in range (scale):
            hilfsliste1.append(sim_array[i+scale][j+scale].get_moment(moment))
            #print sim_array[i+scale][j+scale],math.log(sim_array[i+scale][j+scale].get_moment(moment)),
            labelset1.add(sim_array[i+scale][j+scale].params[1])
            labelset2.add(sim_array[i+scale][j+scale].params[0])
        hilfsliste2.append(hilfsliste1)
        #print '\n'    
    ax = fig.add_subplot(222) 
   # print min(labelset1), max(labelset1), min(labelset2), max(labelset2)
    cax = plt.imshow(hilfsliste2, origin = "lower", extent=[min(labelset1), max(labelset1), min(labelset2), max(labelset2)])
    #print "max", max([max(hl) for hl in hilfsliste2]), " min", min([min(hl) for hl in hilfsliste2])
    cbar = fig.colorbar(cax, ticks = np.linspace(min([min(hl) for hl in hilfsliste2]), max([max(hl) for hl in hilfsliste2]), 5))
    plt.xlabel("pm")
    plt.ylabel("ps") 
    
# erwartet datei, in der die sim als liste abgespeichert sind           
def plot_file (datei, histogram_separate, histogram_spec, qq_Plot, fit_qq_Plot, num_bins = 50, compare_Dist= scipy.stats.invgauss):
    print ("plot_file " + datei)
    with open(datei, 'rb') as daten:
        sim_liste = pickle.load(daten)
       # print sim_liste
        #print sim_liste[0].times, sim_liste[0].params
    plot(sim_liste, histogram_separate, histogram_spec, qq_Plot, fit_qq_Plot, num_bins, compare_Dist)

def plot (sim_liste, histogram_separate, histogram_spec, qq_Plot, fit_qq_Plot, num_bins = 50, compare_Dist= scipy.stats.invgauss):
    startzeit = time.clock()   
    if histogram_spec:
        print ("Erstelle Spektrum")
        fig, ax = plt.subplots()
        fig.suptitle("Laenge: "+str(sim_liste[0].length)+" Anz Teilchen: " +str(sim_liste[1].number)) #TODO, gehe hier davon aus, dass gleiche sim-bedingungen vorliegen
        for sim in sim_liste:
            ax.hist(sim.times, num_bins, alpha=0.5, normed = 1, label = str(sim.params) )
       # plt.show()  
        legend = ax.legend(loc='upper right', shadow=True)

    # Je Simulation ein Ausgabefenster mit separatem Histogramm/qq-Plot mit gewählten Params/qq mit automatischem Fit 
    number_stats = sum([histogram_separate, qq_Plot, fit_qq_Plot])
    print (number_stats)
    if histogram_separate or qq_Plot or fit_qq_Plot:
        print ("Erstelle separate Dinge")
    for sim in sim_liste:
        fig = plt.figure(figsize=(4*number_stats, 4))
        gs1 = gridspec.GridSpec(1, number_stats)
        ax_list = [fig.add_subplot(ss) for ss in gs1]
           
        akt = 0
        fig.suptitle("ps, pm"+str(sim.params)+str(round(sim.params[0]-sim.params[1],5)), size = 15)
        if histogram_separate:
            ax_list[akt].hist(sim.times, num_bins)
            ax_list[akt].set_title("Histogramm")
            akt+=1
                    
            #print "hist sep", time.clock()-startzeit
        if qq_Plot:
            sm.qqplot (np.array(sim.times), scipy.stats.norm,  line = 'r', ax=ax_list[akt])
            ax_list[akt].set_title("qq-Plot; norm!! Params: 0.05")
            akt+=1
            #print 'qq 0.05', time.clock()-startzeit
        if fit_qq_Plot:
                        
                #mu, loc, scale = scipy.stats.invgauss.fit(sim.times)
                #mean, var = scipy.stats.invgauss.stats(mu, loc, scale, moments='mv')
                #print  "params", sim.params, '(mu, loc, scale), mean, var', round(mu, 5), round(loc, 2), round(scale, 2), '\n',  mean, '\n', var
                
                #sm.qqplot (np.array(sim.times), compare_Dist, fit = True,  line = 'r', ax=ax_list[akt])
        #ax_list[akt].set_title("qq-Plot mit auto Fit")
                #akt+=1 
            sm.qqplot (np.array(sim.times), compare_Dist, distargs= (sim.mu, ),  line = 'r', ax=ax_list[akt])
            ax_list[akt].set_title("qq-Plot mit mu:" + str(sim.mu))
            akt+=1
            #print "qq plus rechnen", time.clock()-startzeit                

                #fig.subplots_adjust(top=5.85)
            gs1.tight_layout(fig, rect=[0, 0.03, 1, 0.95]) 
            print( time.clock()-startzeit)
            #plt.tight_layout()
    plt.show()    

def plot_histogram(datei, histogram_separate, histogram_spec, num_bins=1000):
    with open(datei, 'rb') as csvfile:
        myreader = csv.reader(csvfile, delimiter = ";",quoting=csv.QUOTE_NONE)
        #number,length, params = myreader.next()
        liste = []
        # Erstelle Liste, mit der plt.hist umgehen kann
        for row in myreader:
            unterliste = []
            for r in row:
                r2 = float(r)
                unterliste.append(r2)
            liste.append(unterliste)
        # Erstelle Histogramme     
        if histogram_separate:
            print ("erstelle separate histogramme")
            #meine_range= (length, length+ length*(1/min(params)))
            #meine_range = (length, 4*length)
            meine_range = None
            #print meine_range
            figg = plt.figure()
            ax = figg.add_subplot(221)
            n, bins, patches = plt.hist(liste[0], num_bins, range = meine_range, normed=1, alpha=0.5 )
            ax = figg.add_subplot(222)
            n, bins, patches = plt.hist(liste[1], num_bins, range = meine_range, normed=1, alpha=0.5 )
            ax = figg.add_subplot(223)
            n, bins, patches = plt.hist(liste[2], num_bins, range = meine_range, normed=1, alpha=0.5 )
            ax = figg.add_subplot(224)
            n, bins, patches = plt.hist(liste[3], num_bins, range = meine_range, normed=1, alpha=0.5 )
        

        # ein gemeinsames Histogramm aller Datensätze erstellen; entspricht Spektrum
        if histogram_spec:
            meine_range = None
            print ("Erstelle Spektrum")
            figg = plt.figure()
            for row in liste:
                n, bins, patches = plt.hist(liste, num_bins, normed=1, alpha=0.5 )
                print ("Hist erstellt",)#, n, bins, patches#,(time.clock()-startzeit)
        plt.show()    

# Aus einer Sim (*.p) ein Histogramm mit IG-Plot und qq Plot erstellen
def plot_single_histqq_ff(datei, num_bins=50):
    with open(datei, 'rb') as daten:
        sim = pickle.load(daten)
        n, bins, patches = plt.hist(sim.times, num_bins, normed=1, alpha=0.5 )
        x = np.arange(50000, 250000, 100)
        print ("ig-params", scipy.stats.invgauss.fit(sim.times))
        mu, loc, scale =  scipy.stats.invgauss.fit(sim.times)
        plt.plot(x,scipy.stats.invgauss.pdf(x,mu, loc, scale))
        print ('skew', scipy.stats.skew(sim.times))
        
        sm.qqplot(np.array(sim.times), scipy.stats.invgauss, distargs=(mu,),  line = 'r')
               
def plot_qq(datei, qq_Plot, fit_qq_Plot, compare_Dist = scipy.stats.invgauss):
    with open(datei, 'rb') as csvfile:
        myreader = csv.reader(csvfile, delimiter = ";",quoting=csv.QUOTE_NONE)
        liste = []
        # Erstelle Liste wie oben
        for row in myreader:
            unterliste = []
            for r in row:
                r2 = float(r)
                unterliste.append(r2)
            liste.append(unterliste)

    # Und einen qq-Plot erstellen, evtl Parameter zur vergleichsfunktion müssen
    # per Hand eingestellt werden
    if qq_Plot:
        print ("erstelle qq-Plot",)
        fig = plt.figure()
        ax = fig.add_subplot(221)
        sm.qqplot (np.array(liste[0]), compare_Dist, distargs= (0.005,),  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[0]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
       # print "nr2",
        ax = fig.add_subplot(222)
        sm.qqplot (np.array(liste[1]), compare_Dist, distargs= (0.005,),  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[1]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "nr3",
        ax = fig.add_subplot(223)
        sm.qqplot (np.array(liste[2]), compare_Dist, distargs= (0.005,),  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[2]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "nr4",
        ax = fig.add_subplot(224)
        sm.qqplot (np.array(liste[3]), compare_Dist, distargs= (0.005,),  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[3]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "qqplot erstellt"

    # qq-Plot mit automatischem fit zur Vergleichsfunktion
    if fit_qq_Plot:
        print ("erstelle fit-qq-plot", )
        fig = plt.figure()
        ax = fig.add_subplot(221)
        sm.qqplot (np.array(liste[0]), compare_Dist, fit = True,  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[0]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
       # print "nr2",
        ax = fig.add_subplot(222)
        sm.qqplot (np.array(liste[1]), compare_Dist, fit = True,  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[1]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "nr3",
        ax = fig.add_subplot(223)
        sm.qqplot (np.array(liste[2]), compare_Dist, fit = True,  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[2]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "nr4",
        ax = fig.add_subplot(224)
        sm.qqplot (np.array(liste[3]), compare_Dist, fit = True,  line = 'r', ax =ax)
        #txt = ax.text(-1.8, 3500, str(params[3]) ,verticalalignment='top')
        #txt.set_bbox(dict(facecolor='k', alpha=0.1))
        #print "qqplot erstellt"

    plt.show()

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "beschreibung")
    #p.add_argument("--langerbefehl", "-l", help='hilfe', action='store_true', dest = 'destination')   
    p.add_argument("--inputfile", "-i", help = "input file (pickled) to plot a heatmap, n x n Matrix")
    p.add_argument("--moment", "-m" , help = "which moment to plot as heatmap")
    p.add_argument("--singlefile", "-sf", action = "store_true", help = "plot a heatmap from single file with multiple simulations")
    p.add_argument("--singlesimulation", '-ss', action = "store_true", help = "plot a single simulation (histogram and qq)")
    p.add_argument("--multiple_files", '-mf', action="store_true", help = "read multiple files, each a single spectrum")
    p.add_argument("--number", "-n", type=int, help= "how many files to read")
    p.add_argument("--recalculate", "-rc", action = "store_true", help = "Whether moments should be recalculated before plotting")
    return p

def main():
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
        
    if args.multiple_files: #TODO
        number = args.number
        print( "multiple_files: ", number)
        filename = args.inputfile
        
        mySims = np.array([None]*number)
        num = 0
        fehlercounter = 0
        for i in range(number):
            #print "öffne jetzt", ps, pm,
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


    
    plt.show()  

if __name__ == "__main__":
    main()
        
