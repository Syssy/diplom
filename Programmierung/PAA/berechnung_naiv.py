#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Hier versuche ich, die Verteilung der Teilchen statistisch zu berechnen. 
# Ausgangspunkt ist das einfache Modell mit den zwei Zustaenden und Uebergangsw'keiten
# berechne also: p(t, q, s) mit t:Zeitpunkt, q:Zustand, s:Ort
# im zweiten Schritt muss dann auch hier bei s=saeulenlaenge irgendwie gezaehlt werden
# p(0,mobil,0) = 1 ; p(0,stat,0) = 0 ; alle sind erst mal mobil und bei Ort null
# p(t+1, mobil, s) = p(t, mobil, s-1) * pm + p(t, stat, s-1) * 1-ps
# p(t+1, stat, s) = p(t, stat, s-1) * ps  + p(t, mobil, s-1) * 1-pm

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


#naiv!!!
def p(t, q, s):
   # print t, q, s
   # time.sleep(0.51)
    result = 0
    pm = 0.9
    ps = 0.9
    
    
    if t == 0 and q and s == 0:
	#print t, q, s, 1
	return 1
    if t == 0 and not q:
	#print t, q, s, 0
	return 0
    if t == 0 and s!= 0:
	#print t, q, s, 0
	return 0
    
    if q:
	result = p(t-1, q, s-1) * pm +  p(t-1, False, s) * (1-ps)
    else:
	result = p(t-1, q, s) * ps +  p(t-1, True, s-1) * (1-pm)
   # print t, q, s, result
    #time.sleep(1)
    return result

 
def main():
    startzeit = time.clock()
    
    #so klappt das nicht in annehmbarer Zeit, war auch mehr zum ausprobieren gedacht 
    a = 10
    #b = False
    #c = 10
    
    liste = []
    
    for c in range(12):
	for b in [True, False]:
	    ergebnis = p(a, b, c)
	    print a, b, c, ergebnis
	    liste.append(ergebnis)
    
    print sum(liste)  # sollte = 1 sein, ist es auch :)
    
    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 