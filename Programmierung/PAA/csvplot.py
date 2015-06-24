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
        #print ("ausschnitt", wkeiten[9990:10010])
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
    #params = [name[4:] for name in filenames]
    #params = [p.split("_") for p in params]
    ##params = [[p.strip(" ").split(" ") for p in pp] for pp in params]
    ##print (params[1])
    #newparams = []
    #for pkombi in params:
        #param = []
        #for p in pkombi:
            #param.append(float(p))
        #newparams.append(param)
    ##print (newparams)
    starttime = time.clock()
    peakdata = []
    for filename in filenames[0:5]:
        params = [float(p) for p in filename[4:].split("_")]
        print (filename)
        with open(directory+filename, "r") as data:
            #reader = csv.reader(data) # Mit csv ist das overkill, einfach nur einlesen geht schneller (cs 2/3 der Zeit)
            mytimes = []
            for line in data:
            #    print (line)
                mytimes.append(float(line))
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
            #print ("summe", sum(mytimes))
            wsumme = sum(mytimes)
            if wsumme < 0.9:
                continue
            p25, i = 0, 0
            quartiles = [0, 0, 0]
            while p25 < 0.25*wsumme:
                p25+= mytimes[i]
                i += 1
           # print ("p25", i)
            quartiles[0] = i/10000
            p50 = p25
            while p50 < 0.5 * wsumme:
                p50 += mytimes[i]
                i += 1
            quartiles[1] = i/10000
           # print ("p50", i)
            p75 = p50
            while p75 < 0.75 * wsumme:
                p75 += mytimes[i]
                i += 1
            quartiles[2] = i/10000
           # print ("p75", i)   
            print (quartiles)
            # Lage des Maximums, quartile, iqr, qk
            iqr = (quartiles[2] - quartiles[0])
            qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
            #print (type(params))
            #print ("max, quartiles, iqr, qk")
            #print (pd)
            #print (" ")
            #if qk < 0.001:
                #print ("  ", qk)
            #plt.plot(mytimes)
            #plt.show()
            if qk > 0.2 and (np.argmax(mytimes) > 500000):
                print ("    ", qk)
                #plt.plot(mytimes)
                params.extend([np.argmax(mytimes)/10000, quartiles, iqr, qk]) 
                peakdata.append(params)
                #plt.show()
    print ("zeit", time.clock() - starttime)       
    #TODO aus den Daten die PD, also Loc, IQR und QK 
    with open('schiefe_dinger.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        #mywriter.writerows (tabelle)
        print ("laengen", len(peakdata))
        for i in range(len(peakdata)):
            mywriter.writerow(peakdata[i])
    print ("fertig mit Tabelle")  
      
def plot_all(directory):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    all_params = [[float(p) for p in filename[4:].split("_")] for filename in filenames]
    for pkombi in all_params:
        
    
      
def main():
    mypath = "savedata_julia/l1000/"
    erzeuge_Tabelle(mypath)
    #time.sleep(10)
    #plot(mypath + "Sim_0.3_0.69_0.01_0.000100016594_0.9999_0.0_5.0008297e-5_0.0_0.99995")
    plot(mypath + "Sim_0.99_0.0049999906_0.005_0.003000021_0.997_0.0_2.4974346e-5_0.0_0.999975")

    #plot("output2")
    
    #with open("filename", "r") as data:
        ##print (data)
        #wkeiten = data.readline().strip().split(",")
        ##print (type(wkeiten[0]))
        ##print (wkeiten)
        #wkeiten2, wkeiten3 = [], []
        #for i in range(len(wkeiten)-1):
            ##print(wkeiten[i], type(wkeiten[i]))
            #wkeiten2.append(float(wkeiten[i]))
            #print(wkeiten2[i], i)
        #print (sum(wkeiten2))    
        #for i in range(100):
            #summe = 0
            #for j in range(1000):
                #summe += wkeiten2[i*j]
            #wkeiten3.append(summe)
        #print (wkeiten3)    
        #n, bin, patches = plt.hist(wkeiten3, 50)
        #plt.show()
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 
