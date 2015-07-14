#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Plottet die mosdi-ausgabe

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import os
import csv

import scipy.stats   
#import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt

def plot(filename):
    with open(filename, "r") as data:
        #print ("data", data)
        wkeiten, wkeiten2 = [], []
        for i, x in enumerate(data):
            wkeiten.append(float(x))
            #if i > 708000 and i < 708200:
            #    print (i, x)
        print ("ausschnitt", wkeiten[9990:10010])
        plt.plot(wkeiten)
        plt.show()
        ##print ("sum, len wkeiten ", sum(wkeiten), len(wkeiten))  
        #laenge = len(wkeiten)
        #bins = 100
        ##print (laenge//bins)
        #for i in range(bins):
            #summe = 0
            #for j in range(laenge//bins):
                #summe += (wkeiten[(i*(laenge//bins))+j])
            #wkeiten2.append(summe)
        ##print ("wkeiten2", wkeiten2, sum(wkeiten2))    
        #plt.plot(wkeiten2)
        #plt.show()
    
 
def erzeuge_Tabelle(directory):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    normfactor = 10000
    starttime = time.clock()
    peakdata = []
    for filename in filenames:
        params = [float(p) for p in filename[4:].split("_")]
        print (filename)
        with open(directory+filename, "r") as data:
            #reader = csv.reader(data) # Mit csv ist das overkill, einfach nur einlesen geht schneller (cs 2/3 der Zeit)
            mytimes = []
            for line in data:
            #    print (line)
                mytimes.append(float(line))
            offset = (mytimes.pop(0)/normfactor)
            #print (offset, " ", mytimes[0:10])
            #daten zusammenfassen
            #newtimes = []
            ##print (mytimes)
            #for i in range (len(mytimes)//1000):
                #summe = 0.0
                #for j in range (1000):
                    #summe += (mytimes[i*1000 + j])
                #newtimes.append(summe)    
            mytimes = np.array(mytimes)
            #print ("argmax", np.argmax(mytimes))
            print ("summe", sum(mytimes))
            wsumme = sum(mytimes)
            if wsumme < 0.9:
                continue
            p25, i = 0, 0
            quartiles = [0, 0, 0]
            while p25 < 0.25*wsumme:
                p25+= mytimes[i]
                i += 1
           # print ("p25", i)
            quartiles[0] = i/normfactor
            p50 = p25
            while p50 < 0.5 * wsumme:
                p50 += mytimes[i]
                i += 1
            quartiles[1] = i/normfactor
           # print ("p50", i)
            p75 = p50
            while p75 < 0.75 * wsumme:
                p75 += mytimes[i]
                i += 1
            quartiles[2] = i/normfactor
           # print ("p75", i)   
            print (quartiles)
            # Lage des Maximums, quartile, iqr, qk
            iqr = (quartiles[2] - quartiles[0])
            #print (type(params))
            #print ("max, quartiles, iqr, qk")
            #print (pd)
            #plt.plot(mytimes)
            #plt.show()
            qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
            if qk > 0.2 and (np.argmax(mytimes) > 500000):
                print ("    ", qk)
                #plt.plot(mytimes)
                params.extend([offset + np.argmax(mytimes)/normfactor, quartiles, iqr, qk]) 
                peakdata.append(params)
                #plt.show()
    print ("zeit", time.clock() - starttime)       
    #TODO aus den Daten die PD, also Loc, IQR und QK 
    with open('mycsv.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        #mywriter.writerows (tabelle)
        print ("laengen", len(peakdata))
        for i in range(len(peakdata)):
            mywriter.writerow(peakdata[i])
    print ("fertig mit Tabelle")  
      
def plot_all(source_directory):
    dest_directory = "savefigs_python/l1000"
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    all_params = [[float(p) for p in filename[4:].split("_")] for filename in filenames]
    for pkombi, filename in zip(all_params, filenames):
        print (pkombi, filename)
        if not os.path.exists(dest_directory+filename+".png"):
           # with open(source_directory+filename, "r") as data:
            with open(source_directory+"Sim_0.9_0.1_0.0_0.001_0.999_0.0_5.0e-5_0.0_0.99995", "r") as data:
                wkeiten = [float(x) for x in data]
                #print (type(wkeiten))
                offset = wkeiten.pop(0)
                plt.plot(wkeiten)
                plt.ylabel("")
                plt.xlabel("Zeit / Schritten")
                plt.xlim(0, len(wkeiten)+offset)
                plt.suptitle("PAA; Params: "+ str(pkombi))
                #plt.savefig(dest_directory + "/" + filename[4:] + ".png")
                plt.show()
                plt.clf()
                time.sleep(5)


def compress_data(source_directory, comp_factor = 10000):
    dest_directory = "savefigs_python/l1000"
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    all_params = [[float(p) for p in filename[4:].split("_")] for filename in filenames]
    for pkombi, filename in zip(all_params, filenames):
        print ("pkombi, filename", pkombi, filename)
        if not os.path.exists(dest_directory+filename+".p"):
            with open (source_directory + filename , "r" ) as data:
                wkeiten = [float(x) for x in data]
                offset = wkeiten.pop(0)/comp_factor 
                pd = calculate(wkeiten, offset, comp_factor)
                print ("peakdata", pd)
                comp_probs = []
                for i in range(comp_factor):
                    secsum = 0
                    for j in range((len(wkeiten)//comp_factor)):
                        secsum += wkeiten[i*(len(wkeiten)//comp_factor) + j]
                    comp_probs.append(secsum)    
                pd2 = calculate(comp_probs, offset, 1)
                print("pd2 ", pd)
                

       
def main():
    mypath = "savedata_julia/l1000/"
    #plot(mypath + "Sim_0.99_0.0049999906_0.005_0.003000021_0.997_0.0_2.4974346e-5_0.0_0.999975")
    #plot_all(mypath)
    #erzeuge_Tabelle(mypath)
    #time.sleep(10)
    #plot(mypath + "Sim_0.3_0.69_0.01_0.000100016594_0.9999_0.0_5.0008297e-5_0.0_0.99995")
    compress_data(mypath)
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 
