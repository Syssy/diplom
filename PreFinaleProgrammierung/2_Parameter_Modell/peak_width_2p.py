# -*- coding: utf-8 -*-

import math
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import scipy.optimize

def ig(x, mu, loc, scale):
    """inverse gauss funktion"""
    if not x.all():
        return 0
   # print ("x", x)
    teila = np.sqrt(scale / (2*np.pi*((x-loc)**3))) 
    
    exponent = - ((scale*(((x-loc)-mu)**2))/(2*(x-loc)*(mu**2)))
    #print ("ex", exponent, "math", math.exp(exponent[5]), "np", np.exp(exponent[5]))
    teilb =  np.exp(exponent)
    result = teila * teilb
    return result

# finde Schnittpunkt zweier Funktionen (fun1, fun2) ausgehend vom geschätzten Wert x0
def find_intersection(fun1,fun2,x0):
    return scipy.optimize.fsolve(lambda x : fun1(x) - fun2(x),x0)

def calculate_width(times, laenge, show, params = None):
    """find peak width at half peak height
    Berechne die Breite des durch times gegebenen Peaks an halber Peakhoehe
    Eingabe times ist eine Zeitenliste, wie sie Ergebnis einer Simulation sein könnte
    laenge ist die Anzahl der Zeiteinheiten, über die das geht, wird gebraucht, damit der Plot gut aussieht"""
    
   # laenge = len(set(times))*2 # nicht sicher, wie das bei Löchern später funktioniert...
   
    # Passende Parameter berechnen, damit ich eine Kurve zum scheiden habe
    loc_n, scale_n = scipy.stats.norm.fit(times)
   # mu_ig, loc_ig, scale_ig = scipy.stats.invgauss.fit(times)
    x = np.linspace(min(times)-50, max(times)+50, 1000000)
   # x = np.linspace(90, 250, 100)
    #print ("IG params", mu_ig, loc_ig, scale_ig)
    
   # print ("Scipy", scipy.stats.invgauss.pdf(x, mu_ig, loc_ig, scale_ig))
    #print ("meins", ig(x, mu_ig, loc_ig, scale_ig))
    # halben Maximalwert berechnen
    halfmax = 1/(math.sqrt(2*math.pi)*scale_n *2)
    #print ("halfmax", halfmax)
    
    # plotte die zeiten als histogramm(hellblau), die daraus geschätzte verteilung (grün) und eine linie auf halber höhe (rot)
    if show:
        n, bins, patches = plt.hist(times, laenge, normed = True, color = "lightblue")
       # dist, = plt.plot(x, scipy.stats.invgauss.pdf(x, mu_ig, loc_ig, scale_ig), color = "lightgreen")
        #dist, = plt.plot(x, ig(x, mu_ig, loc_ig, scale_ig), color = "yellow")
        dist, = plt.plot(x, scipy.stats.norm.pdf(x, loc_n, scale_n), color = "green")
        line, = plt.plot(x, [halfmax]*len(x), "r")
        #plt.show()
    
    # zwei Funktionen damit erstellen, die dann für die find intersections genutzt werden. Alle intersections plotten
    # Funktion der Normalverteilung. #TODO: Hier noch andere verteilungen ermöglichen
    # Ist x hier absicht? also damit der linspace fürs plotten gemeint?
    norm_ = lambda x: np.exp(-(x-loc_n)**2 / (2*scale_n**2)) / math.sqrt(2*math.pi * scale_n**2)
    # Funktion einer Linie
    linie = lambda x: halfmax + 0*x
    #print ("max bei", norm(loc), "starte test bei:", loc-scale, loc+scale)
    # finde Schnittpunkte, Startwerte sind median +- standardabweichung
    norm1 = scipy.stats.norm()
    intersections = find_intersection(linie, norm, [loc_n+scale_n, loc_n-scale_n])
    
   # print ("myfuns", norm(x), ig(x, mu_ig, loc_ig, scale_ig), linie)
    #plt.plot(x, scipy.stats.invgauss.pdf(x, mu_ig, loc_ig+1, scale_ig), color = "green")
    #plt.plot(x, ig(x, mu_ig, loc_ig, scale_ig), color="red")
    #print ("intersections", intersections)
    
    # intersections plotten
    if show:
        points = []
        for sect in intersections:
            point = plt.plot([sect],[norm(sect)], "mo")
            points.extend(point)
        plt.suptitle(params)
        #print (line)
        plt.legend([patches[0], dist, line, points[0]], [params, (loc_n, scale_n), halfmax, abs(intersections[1]-intersections[0])])
        plt.show()
    
    # Rueckgabe: Breite als Differenz der groessten und kleinsten Intersection, sowie die halbe Hoehe
    return abs(max(intersections) - min(intersections)), halfmax, (loc_n, scale_n)
    
# Verhältnisse von Ort (median) des Peaks und Breite berechnen  
# Ueberfluessig, tut das gleiche wie widthplot in myplottings
'''def plot_relation(filename, plotwidth = True, plotskew = False):
    fig2 = plt.figure()
    if plotwidth:
        ax3 = fig2.add_subplot(1,2,1)
        ax3.set_title("Breite")
    if plotskew:
        ax4 = fig2.add_subplot(1,2,2)
        ax4.set_title("Skew")
    points = []
    print (filename)
    with open(filename, "rb") as datei:
        print ("plot", filename)
        peakdaten = pickle.load(datei)
        print (peakdaten)
        #TODO: Diese Peakdaten sind nicht kompatibel mit der akutellen simulations-version. 
        for pd in peakdaten:
            print (pd)
            (params, (loc, scale), breite, hoehe, skew) = pd
            print (loc, breite, plotwidth, plotskew)
            if plotwidth:
                point = ax3.plot([loc], [breite], "ro")
                print (breite, loc)
                #text = plt.text(s=params, x= loc,y= breite, fontsize = "xx-small")
                #ax3.annotate(params, (loc, breite))
                t = ax3.text(loc, breite, str(params[0])+'\n'+str(params[1]), size= "xx-small")
            if plotskew:
                anotherpoint = ax4.plot([loc], [skew], "bx")
           # print("Params:", params, ":", point[0].get_xydata(), "Scale:", scale, "hoehe", hoehe)
           # points.extend(point)
    #print (points)        
    plt.show()
'''

if __name__ == "__main__":   
    print("nothing to do... bitte die nicht _2p version nutzen")