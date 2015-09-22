#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Weiterverarbeitung einer PAA-Simulation aus Julia/Java für Simulationen mit zwei Zuständen

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import os
import csv
 
import numpy as np
import matplotlib.pyplot as plt

from process_simulations import PAA
       
def erzeuge_Tabelle(directory, csv_name, time_range=[0,240], iqr_range=[0,150], qk_range=[0,1]):
    '''Tabelle anlegen mit allen Peaks (Sim-Parameter) die die gegebenen Vorgaben (range) erfuellen'''
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    starttime = time.clock()
    peaks_found = []
    print ("erzeuge_Tabelle")    
    # Ueberpruefe jeden Peak
    for filename in filenames:
        with open(directory+filename, "rb") as mydata:
            myPAA = pickle.load(mydata)
            params = myPAA.params
            #Ueberpruefung, ob Peak die Vorgaben erfuellt
            if myPAA.pd[0] > time_range[0] and myPAA.pd[0] < time_range[1] and myPAA.pd[2] > iqr_range[0] and myPAA.pd[2] < iqr_range[1] and myPAA.pd[3] > qk_range[0] and myPAA.pd[3] < qk_range[1]:
                # Die Peakdaten als Zeile die Tabelle anhaengen
                #print (myPAA)
                params.extend([myPAA.pd[0], myPAA.pd[2], myPAA.pd[3]]) 
                peaks_found.append(params)
    print ("zeit", time.clock() - starttime)       
    # Abspeichern der Tabelle als csv Datei
    #TODO Tabelle in irgendnen ordner packen
    with open(csv_name, 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        print ("Anzahl gefundener Peaks", len(peaks_found))
        for i in range(len(peaks_found)):
            mywriter.writerow(peaks_found[i])
    print ("fertig mit Tabelle") 
    return peaks_found

def plotte_Zeitpunkt(directory, time_range=[1,240], iqr_range=[0,100], iqk_range=[0,1], show_params=False):
    '''Alle zu geg Zeit/IQR/IQK gefundenen Peaks plotten'''
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    tabellenname = "xy_" + str(time_range[0]) + "_" + str(time_range[1]) + "_" + str(iqr_range[0]) + "_" + str(iqr_range[1]) + "_"+  str(iqk_range[0]) + "_" + str(iqk_range[1]) + ".csv"
    peaks_found = []
    #if os.path.exists(tabellenname):
        #print (tabellenname)
        #with open (tabellenname, "r", newline='') as csvfile:
            #myreader = csv.reader(csvfile)
            #for line in myreader:
               ## print (line)
                #peaks_found.append([float(x) for x in line])
    #else:
    peaks_found = erzeuge_Tabelle(directory, tabellenname, time_range, iqr_range, iqk_range)
    
    starttime = time.clock()
    plt.suptitle("Erreichbare Breiten und Schiefen \nfür Retentionszeiten von " + str(time_range[0]) + " bis: " + str(time_range[1]))
    plt.xlabel("Breite (IQR)")
    plt.ylabel("Schiefe (QK)")
    for peak in peaks_found:
        plt.plot([peak[10]], [peak[11]], "go")
    plt.ylim(0, 1)
    plt.show()    
    if show_params:
        fig = plt.figure()
        plt.suptitle("Zeit: " + str(time_range) + " IQR: " + str(iqr_range) + " IQK: " + str(iqk_range))
        # der Übersicht halber für alle vier relevanten Parameter ein Plot, jeden Plot anlegen
        ax0 = fig.add_subplot(221)
        ax0.set_title("pmm")
        plt.ylabel("Schiefe (IQK)")
        ax1 = fig.add_subplot(222)
        ax1.set_title("pml")
        ax2 = fig.add_subplot(223)
        ax2.set_title("paa")
        plt.xlabel("Breite (IQR)")
        plt.ylabel("Schiefe (IQK)")
        ax3 = fig.add_subplot(224)
        ax3.set_title("pll")
        plt.xlabel("Breite (IQR)")
        ax = [ax0, ax1, ax2, ax3]
        for peak in peaks_found:
            print (peak)
            #TODO: Die markersize sinnvoll nutzen
            # TODO: Sinnvolle Kennzeichung über formen und farben der punkte
            for i, j in enumerate([0, 2, 4, 8]):
                ax[i].plot([peak[10]], [peak[11]], "go")#, markersize = 2*abs(np.median([time_range[1], time_range[0]])-peak[9]))
                t = ax[i].text(peak[10], peak[11], str(peak[j]), size= "small")
        plt.show()

def plot_single_peak(filename, model, quartiles=False):
    '''Einzelnen Peak und seine Quartile plotten'''
    with open (filename, "rb") as data:
        aPeak = pickle.load(data)
        fig, ax = plt.subplots()
        #print (aPeak.distribution)
        #plt.tight_layout()
        plt.plot(aPeak.distribution, label = " ")
        hoehe = np.max(aPeak.distribution)
        logging.log(20, aPeak.pd)
        # Quartile mitplotten
        if quartiles:
            plt.plot([aPeak.pd[1][0] * 10, aPeak.pd[1][0] * 10], [0, hoehe], color = "lightblue")
            plt.plot([aPeak.pd[1][1] * 10, aPeak.pd[1][1] * 10], [0, hoehe], color = "lightblue")
            plt.plot([aPeak.pd[1][2] * 10, aPeak.pd[1][2] * 10], [0, hoehe], color = "lightblue")
        plt.axis([0.0,2400,0.0,0.03])
        if model == "2s":
            plt.title("ps: " + str(aPeak.params[0]) +" pm: " + str(aPeak.params[1])) 
        if model == "3a":
            plt.title("pmm: " + str(aPeak.params[0]) +" pml: " + str(aPeak.params[2]) + " paa: " + str(aPeak.params[4]) +" pll: " + str(aPeak.params[8])) 
        plt.xlabel("Retentionszeit / s")
        plt.ylabel("Signalintensität")    
        ax.set_xticklabels([0, 50, 100, 150, 200])
        plt.legend(title = "Lage " + str(round(aPeak.pd[0],4))+ " Breite "+str(round(aPeak.pd[2],2)) + " Schiefe " +str(round(aPeak.pd[3],2)))
        plt.show()
    return

def plot_festen_param(directory, ps, pm, fest):
    ''' Einen Parameter (fest) vorgeben, den anderen variieren'''
    if fest == "ps":
        vp = 1
        variabel = "pm"
        fester_param = ps
        variable_params = pm
    else:
        vp = 0
        variabel = "ps"
        fester_param = pm
        variable_params = ps
    myPAA_list = []
    
    for p0 in ps:
        for p1 in pm:
            filename = "Sim_" + str(p0) + "_"+ str(p1) + ".p"
            myPAA_list.append(filename)
    print (myPAA_list)
        
    for filename in myPAA_list:
        if os.path.exists(directory + filename):
            with open (directory + filename , "rb" ) as data:
                myPAA = pickle.load(data)
                logging.log(20, "pd %s, params %s", myPAA.pd, myPAA.params)
                if myPAA.pd[2] == myPAA.pd[2]:
                    #plt.plot([myPAA.pd[0]],[myPAA.pd[2]], "o", markersize = (myPAA.pd[3])*500, label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[3],3)) )
                    #plt.text(myPAA.pd[0], myPAA.pd[2], str(myPAA.params[vp]))
                    plt.plot([myPAA.pd[0]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[2])*1, label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[2],3)) )
                    plt.text(myPAA.pd[0], myPAA.pd[3], str(myPAA.params[vp]))
    plt.xlabel("Zeitpunkt")
    #plt.ylabel("Breite")   
    plt.ylabel("Schiefe")   
    plt.xlim([0, 200])
    plt.ylim([0, 1])
    plt.legend(title=  variabel + ",  Breite", numpoints = 1, loc = 1)
    
    plt.suptitle("Fester Parameter: " + fest + " = " + str(fester_param[0]))
    figname = variabel + "_fest_" + fest + "_"+ str(fester_param[0]) + ".png"
    #plt.savefig(figname, bbox_inches = 'tight')                
    plt.show()
    return

def plot_3feste_Params(directory, pmm=[], pml=[], paa=[], pll=[], variabel="pmm"):
    '''drei Parameter bleiben fest, einer wird verändert (im sinnvollen bereich), alle Params werden als Liste übergeben, die festen halt mit nur einem Element, der veränderliche mit mehreren
    evtl: erzeuge Liste mit noch nicht für diesen Plot vorhandenen Simulationen'''
        #TODO TODO
    mydict = {"pmm": pmm, "pml": pml, "paa": paa, "pll": pll}
    dict2 =  {"pmm": 0, "pml": 2, "paa": 4, "pll": 8}
    print ("mydict", mydict)
    myPAA_list, todolist = [], []
    #Zugriffsnummer des variablen Parameters
    vp = dict2[variabel]
    #print ("nummer", vp)
    
    #print (mydict[variabel])
    
    for p1 in pmm:
        for p2 in pml:
            for p3 in paa:
                for p4 in pll:
                    filename = "Sim_" + str(p1) + "_"+ str(p2) + "_" + str(p3) + "_" + str(p4) + ".p"
                    myPAA_list.append(filename)
    #print (myPAA_list)
        
    for filename in myPAA_list:
        if os.path.exists(directory + filename):
            #print (filename)
            with open (directory + filename , "rb" ) as data:
                myPAA = pickle.load(data)
                print("pd, params", myPAA.pd, myPAA.params)
                if myPAA.pd[2] == myPAA.pd[2]:
                #plt.set_label(str(myPAA.params[0]) + str(myPAA.pd[0]))
                    # Achsen x:Breite, y:Schiefe
                    #plt.plot([myPAA.pd[2]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[0]/10), label=str(myPAA.params[vp]) +" "+ str(myPAA.pd[0]) )
                    #plt.text(myPAA.pd[2], myPAA.pd[3], str(myPAA.params[vp]))
                    # Achsen x:Zeitpunkt, y:Schiefe
                    plt.plot([myPAA.pd[0]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[2]), label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[2],2)) )
                    plt.text(myPAA.pd[0], myPAA.pd[3], str(myPAA.params[vp]))
                    # Achsen: x:Zeitpunkt, y:Breite
                    #plt.plot([myPAA.pd[0]],[myPAA.pd[2]], "o", markersize = (myPAA.pd[3]*10), label=str(myPAA.params[vp]) +" "+ str(myPAA.pd[3]) )
                    #plt.text(myPAA.pd[0], myPAA.pd[2], str(myPAA.params[vp]))
        else:
            todolist.append(filename)
    #plt.xlabel("Breite (IQR)")
    plt.xlabel("Zeitpunkt")
    #plt.ylabel("Breite (IQR)")
    plt.ylabel("Schiefe")
    plt.xlim([0, 200])
    plt.ylim([0, 0.9])
    print ("todolist", todolist)
    del mydict[variabel]
    title = ""
    for key in ["pmm", "pml", "paa", "pll"]:
        if key in mydict:
            title += (" " + key + "="+ str(mydict[key][0]))
    plt.suptitle("fest:" + title)#+ "\n variabel: " + variabel)
    plt.legend(title= variabel+ ",  Breite", numpoints = 1, loc = 1)
    #print ("3fest_" +  str(mydict["pmm"][0])+"_" +  str(mydict["pml"][0])+"_" +  str(mydict["paa"][0])+"_" +  str(mydict["pll"][0]))# + mydict[pml] + mydict[paa] + mydic[pll])
    #plt.savefig(figname)
    plt.show()    
    return

def plot_erreichbare_regionen(directory, show_params):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    for filename in filenames:
        with open(directory+filename, "rb") as mydata:
            myPAA = pickle.load(mydata)
            # Wenn nicht zu spät und kein Nan
            if myPAA.pd[0] < 240 and myPAA.pd[0] > 0.1 and myPAA.pd[2] == myPAA.pd[2]:
                point = plt.plot([myPAA.pd[0]], myPAA.pd[2], "ro-")
                if show_params:
                    t = plt.text(myPAA.pd[0], myPAA.pd[2], str(round(myPAA.params[0],6))+'\n'+str(round(myPAA.params[1],4)), size= "small")
    plt.suptitle("Erreichbare Zeit-Breiten-Kombinationen")
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Breite")
    plt.show()
    return

def plot_params_at_time(folder, t, epsilon=0.1, show_params=False):
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
            #if sim.valid:
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
    
def get_argument_parser():
    '''Kommandozeilenparameter'''
    p = argparse.ArgumentParser(
        description = "Ruft Plotfunktionen auf")
    p.add_argument("model", choices = ["2s", "3a"],
                   help = "Modell: 2 oder 3 Zustände (2s/3a)")  
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--source", "-s", default = "julia",
                   help = "Quelle der PAA-Daten")
    p.add_argument("--plot_peak", "--pp", nargs = '+', type = float,
                   help = "Einzelne Parameterkombi eingeben, deren Peak dann geplottet wird" )
    p.add_argument("--quartiles", "-q", action = "store_true",
                   help = "wenn gewaehlt, werden beim plot_peak die Quartile mitgeplottet")
    p.add_argument("--plot_params_at_time", "--ppt", action = "store_true",
                  help = "Auswahl ob Parameter für Retentionszeit -r und Abweichung -e geplottet werden soll")
    p.add_argument("--retention", "-r", default = [float(50), float(60)], nargs = '+', type = float,
                  help = "zu plottende Retentionszeit fuer plot_params_at_time, Intervall fuer plot_pd")
    p.add_argument("--epsilon", "-e", default = "5", type = float,
                  help = "erlaubte Abweichung von -r fuer plot_params_at_time")
    p.add_argument("--plot_reachable", "--pr", action = "store_true",
                   help = "Auswahl ob Plot erreichbarer Zeiten/Breiten erstellt werden soll")
    p.add_argument("--show_params", "--sp", action = "store_true",
                   help = "Wenn gewählt, werden im Plot Parameter angezeigt, Option verfuegbar fuer --ppt, --pr")
    p.add_argument("--plot_festen_param", "--pfp", nargs = "+",
                   help = "Plottet Peakdaten für einen festen und einen variablen Parameter, als Argumente erst den festen Parameter, dann dessen Wert angeben, z.B. --pfp ps 0.999")
    p.add_argument("--plot_pd", "--pd", action = "store_true",
                   help = "Plottet nach den vorgegebenen Peakdatenintervallen -r, --iqr, --qk")
    p.add_argument("--iqr", default = [float(1), float(20)], nargs = '+', type = float,
                  help = "IQR-Intervall fuer plot_pd")
    p.add_argument("--qk", default = [float(0), float(1)], nargs = '+', type = float,
                  help = "QK-Intervall fuer plot_pd")
    p.add_argument("--plot_3fest", "--p3", action = "store_true",
                   help = "Plottet Peakdaten für drei feste und einen variablen Parameter, Wert der drei festen Parameter mit --pmm/--pml/--paa/--pll angeben")
    p.add_argument("--pmm", type=float, nargs='+',default = [float(0.1), float(0.2), float(0.3), float(0.4), float(0.5), float(0.6), float(0.7), float(0.8), float(0.9)],
                   help = "Wert als festen Parameter im 3_fest-Plot")
    p.add_argument("--pml", type=float, nargs='+', default = [float(0.0001), float(0.0003), float(0.0005), float(0.0007), float(0.001), float(0.003), float(0.005)],
                   help = "Wert als festen Parameter im 3_fest-Plot")
    p.add_argument("--paa", type=float, nargs='+', default = [float(0.997), float(0.998), (0.9985), float(0.999), float(0.9992), float(0.9994), float(0.9995), float(0.9996)],
                   help = "Wert als festen Parameter im 3_fest-Plot")
    p.add_argument("--pll",type=float, nargs='+',default = [float(0.9999),float(0.99995),float(0.999975), float(0.99999), float(0.999995)],
                   help = "Wert als festen Parameter im 3_fest-Plot")
    #p.add_argument("--plot_spectrum", "-ps", action = "store_true",
    #               help = "Auswahl ob Spektrum geplottet werden soll fuer Rauschen zusaetzlich -an")
    #p.add_argument("--addnoise", "-an", action= "store_true",
    #               help = "Rauschen hinzufuegen")
    #p.add_argument("--plot_trait", "-pt", 
    #               help = "Auswahl ob Heatmap ueber Eigenschaft (loc, iqr, qk) geplottet werden soll")
    #p.add_argument("--trait", "-t", 
    #               help = "Zu plottende Eigenschaft für plot_trait")
    return p

def main():
    '''Aufruf der Plottings, gesteuert durch Kommandozeilenparameter'''
    p = get_argument_parser()
    args = p.parse_args()
    print (args)  
    
    directory = "savedata_python/"+ args.model+"/l" + str(args.length) + "/from_" + args.source + "/"
    
    if args.plot_peak:
        if args.model == "2s":
            filename = directory + "Sim_" + str(args.plot_peak[0]) + "_" + str(args.plot_peak[1]) + ".p"
        if args.model == "3a":
            filename = directory + "Sim_"+ str(args.plot_peak[0]) + "_" + str(args.plot_peak[1]) + "_"+ str(args.plot_peak[2]) + "_" + str(args.plot_peak[3]) + ".p"
        plot_single_peak(filename, args.model, args.quartiles)
    
    if args.model == "2s":
        if args.plot_reachable:
            plot_erreichbare_regionen(directory, args.show_params)
        if args.plot_params_at_time:
            plot_params_at_time(directory, t=args.retention[0], epsilon=args.epsilon, show_params=args.show_params)
        if args.plot_festen_param:
            if args.plot_festen_param[0] == "ps":
                pss = [args.plot_festen_param[1]]
                pms = [0.1, 0.3, 0.5, 0.7, 0.9]
            else :
                pss = [0.998, 0.999, 0.9992, 0.9994, 0.9996, 0.9999]
                pms = [args.plot_festen_param[1]]
            #TODO: Liste der variablen flexibel einlesbar machen
            plot_festen_param(directory, pss, pms, args.plot_festen_param[0])
    
    if args.model == "3a":
        if args.plot_pd:
            plotte_Zeitpunkt(directory, args.retention, args.iqr, args.qk, args.show_params)
        if args.plot_3fest:
            #TODO Das ist nicht schön, aber funktioniert bei korrekter Eingabes
            print (args.pmm, args.pml)
            if len(args.pmm) > 1:
                variabel = "pmm"
            if len(args.pml) > 1:
                variabel = "pml"
            if len(args.paa) > 1:
                variabel = "paa"
            if len(args.pll) > 1:
                variabel = "pll"
            plot_3feste_Params(directory, args.pmm, args.pml, args.paa, args.pll, variabel)

if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()   
    