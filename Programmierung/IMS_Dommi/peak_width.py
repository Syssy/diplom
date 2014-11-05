# -*- coding: utf-8 -*-

from ims_core import *
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import scipy.optimize
import math
import pickle

# signalwert berechnen
def sig(zahl):
    result = 0
    if zahl != 0:
       result = -zahl
      # result = (-zahl*0.0024617)/4.9456
    
    return result

def normalized(a, axis=-1, order=2):
    summe = sum(a)
    result = None
    if summe > 1:
        result = np.array(a)/summe
    if summe == 1:
        result = 1
    if summe < 1 and summe > 0:
        result = a * (1/summe)
    return result
   # l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
   # l2[l2==0] = 1
   # return a / np.expand_dims(l2, axis)

def ig(x, mu, loc, scale):
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


    # find peak width at half peak height
    # Eingabe times ist eine Zeitenliste, wie sie Ergebnis meiner Sims sein könnte
    # laenge ist die Anzahl der Zeiteinheiten, über die das geht, wird gebraucht, damit der Plot gut aussieht
def fpwahph(times, laenge, show, params = None):
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
    norm = lambda x: np.exp(-(x-loc_n)**2 / (2*scale_n**2)) / math.sqrt(2*math.pi * scale_n**2)
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
def plot_relation(filename):
    points = []
    fig2 = plt.figure()
    ax3 = fig2.add_subplot(1,2,1)
    ax3.set_title("Breite")
    ax4 = fig2.add_subplot(1,2,2)
    ax4.set_title("Skew")
    with open(filename, "rb") as datei:
        #print ("plot", filename)
        peakdaten = pickle.load(datei)
       # print (peakdaten)
        for pd in peakdaten:
           # print (pd)
            (params, (loc, scale), breite, hoehe, skew) = pd
            #print (loc, breite)
            point = ax3.plot([loc], [breite], "ro")
            #text = plt.text(s=params, x= loc,y= breite, fontsize = "xx-small")
            #ax3.annotate(params, (loc, breite))
            t = ax3.text(loc, breite, str(params[0])+'\n'+str(params[1]), size= "xx-small")
            anotherpoint = ax4.plot([loc], [skew], "bx")
           # print("Params:", params, ":", point[0].get_xydata(), "Scale:", scale, "hoehe", hoehe)
            points.extend(point)
    #print (points)        
    plt.show()
        

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("usage: python3 peak_width.py measurement")
        exit()
    filename = sys.argv[1]
    ims_file = ims(filename)
    #print first IMS spectrum+
    #print(ims_file.points[0]) 
    
    chrom = list()
    #print first Chromatogram
    laenge = 39
    for i in range(laenge):
    #RIP bei ca 800, und Peak bei 1744 (example von Dommi)
       # print(ims_file.points[i][1477], end = ",")
        chrom.append(sig(ims_file.points[i+227][1487]))
    
    chrom = np.array(chrom)
    print ("chrom", chrom)
    
    times = []
    for i in range(len(chrom)):
        c = chrom[i]
        for j in range(int(c)):
            times.append(i)

   # print (times)
    
    # peakbreite bei halber höhe berechnen
    # TODO: Was sagen mir jetzt die Zahlen?
    #breite, hoehe = fpwahph(times, laenge, True)
    #print ("Breite", breite, "bei", hoehe)
    
    #Teil 2: 
    
    zeiten = ()
    with open("einetimesliste.p", "rb") as datei:
        zeiten = pickle.load(datei)
    laenge = 74    
    print (len(zeiten), len(set(zeiten)))
    times = (np.array(zeiten)- min(zeiten)) /1000
    #print (times, type(times))
    breite, hoehe = fpwahph(times, laenge, True)
    print ("Breite", breite, "bei", hoehe)    
    
    ''' Sackgasse...
    w = np.array([0.0, 11.11111111111111, 22.22222222222222, 33.333333333333336,
              44.44444444444444, 55.55555555555556, 66.66666666666667,
              77.77777777777777, 88.88888888888889, 100.0])
    v = np.array([0.0, 8.333333333333332, 16.666666666666664, 25.0,
              36.11111111111111, 47.22222222222222, 58.333333333333336,
              72.22222222222221, 86.11111111111111, 100.0])

    print (w)
    w = chrom
    print (w)
    v = np.linspace(0, 500, len(chrom))
    
    poly_coeff = np.polynomial.polynomial.polyfit(w, v, 10)
    poly = np.polynomial.polynomial.Polynomial(poly_coeff)
    print (poly)
    roots = np.polynomial.polynomial.polyroots(poly_coeff - [halfmax, 0, 0, 0, 0, 0, 0, 0, 0,0,0])
    print (roots)

    x = np.linspace(np.max(roots) - 50, np.max(roots) + 50, num=1000)
    plt.plot(x, poly(x), 'r-')
    #plt.plot(x, 99 - x, 'b-')
    plt.plot(x, [halfmax]*len(x), "g-")
    for root in roots:
        plt.plot(root, halfmax, 'ro')
    
    plt.show()'''
    
