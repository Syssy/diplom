#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Hier versuche ich, die Verteilung der Teilchen statistisch zu berechnen. 
# Ausgangspunkt ist das einfache Modell mit den zwei Zustaenden und Uebergangsw'keiten
# berechne also: p(t, q, s) mit t:Zeitpunkt, q:Zustand, s:Ort
# im zweiten Schritt muss dann auch hier bei s=saeulenlaenge irgendwie gezaehlt werden
# p(0,mobil,0) = 1 ; p(0,stat,0) = 0 ; alle sind erst mal mobil und bei Ort null
# p(t+1, mobil, s) = p(t, mobil, s-1) * pm + p(t, stat, s) * 1-ps
# p(t+1, stat, s) = p(t, stat, s) * ps  + p(t, mobil, s-1) * 1-pm

import random
import numpy as np
import time
import scipy.stats as stats
import scipy
import plotkram
import simulation
import pickle
import matplotlib.pyplot as plt
import logging


def p_alt(t, q, s):
    pm = 0.9
    ps = 0.9
    
    
  #  if t == 0 and q and s[0] == 1:
#	return 1
    if t == 0 and not q:
	return np.zeros(len(s))   
    if t == 0 and q:
	result = np.zeros(len(s))
	result[0] = 1
	return result
    
    if q:
	teila = p(t-1, q, s-1) * pm 
	teilb = p(t-1, False, s) * (1-ps)
	print t, q, teila, teilb
	result = teila + teilb
	
    else:
	teila = p(t-1, q, s) * ps
	teilb =  p(t-1, True, s-1) * (1-pm)
	print t, q, teila, teilb
	result = teila + teilb
	
    print t, q, result
    return result
 
 
def p(t, q, s):
    pm = 0.9
    ps = 0.9
   # print t, q, s
    
    if t == 0:
	tneu = np.zeros(s)
	if q:
	    tneu[0] = 1
	
    else:
	if q:
	    #print tmatrix[t-1], type(tmatrix)
	    teila = np.roll(tmatrix[t-1] * pm, 1)
	    teilb = fmatrix[t-1] * (1-ps)
	    tneu = teila + teilb
	
        else:
	    
            tneu =  fmatrix[t-1] * ps +  np.roll(tmatrix[t-1] * (1-pm), 1)

    #print tneu
    return tneu
    
    
 
 
def main():
    startzeit = time.clock()
    
    a = 0
    b = False
    c = np.array([0, 1, 2, 3, 4])

    global tmatrix, fmatrix
    
    fmatrix = []
    tmatrix = []
    
    laenge = 500
    
    for i in range(laenge):
	#print ergebnis, type(ergebnis)
	tmatrix.append(p(i, True, laenge))
	fmatrix.append(p(i, False, laenge))m
    print "t:", (tmatrix[laenge-1])
    print "f:", (fmatrix[laenge-1]) , '\n'
    
    #TODO: Was fang ich jetzt hiermit an?

    ergebnis = p(a, b, c)
    
    #print tmatrix
    
    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 