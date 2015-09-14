# Implementierung eines PAAs fuer 3 Zustaende, sollte mit minimalen Aenderungen (zB init der dist) auf fuer mehr Zustaende funktionieren
# Nur der benoetigte Spezialfall eines PAA

function cut_Distributions(distributions, index)
    # Wenn Werte zu Beginn oder Schluss der Arrays zu klein sind, werden diese abgeschnitten
    # Dazu muessen alle Arrays zu kleine Werte an der entsprechenden Stelle haben  
    vorneschneiden = true
    # Vorne testen, falls ein Wert gross genug ist, wird nicht geschnitten
    for i in 1:length(distributions)
        if distributions[i][1] >= 1.0f-17
            vorneschneiden = false
            break
        end
    end
    #Vorne abschneiden durch shift! aller Arrays, gleichzeitig Index verschieben
    if vorneschneiden
        index += 1
        for i in 1:length(distributions)
            #distributions[i][1] = 0.0f0
            shift!(distributions[i])
        end
    end
    # Hinten testen, wie vorne    
    hintenschneiden = true
    for i in 1:length(distributions)
        if distributions[i][end] >= 1.0f-17
            hintenschneiden = false
            break
        end
    end
    # Hinten abschneiden durch pop! aller Arrays
    if hintenschneiden
        for i in 1:length(distributions)
            pop!(distributions[i])
        end
    end
    return distributions, index
end

function updateDistributions!(params::Array{Float32,2}, distributions, index, num_states)
    #= Ein Berechnungschritt zur Aktualisierung der beiden Verteilungen
       ps, pm: Parameter
       distributions: Matrix die Werte fuer mobil/stat enthaelt (Wert: WKeit an jeweiliger position)
       index: zur spaeteren Verschiebung des Arrays, wird erhoeht, wenn zu kleine Werte abgeschnitten werden
       return: Neue distributions, index
    =#
    # Erstelle Hilfsmatrix aus Arrays. Jedes Array wird später befüllt aus einer alten Verteilung mal entsprechender Uebergangswahrscheinlichkeit. Bei 3 Zustaenden ergeben sich so 9 Arrays
    hilfsdings = Array(Any, num_states)
    for i in 1:num_states
        hilfsdings[i] = Array(Any, num_states)
    end
    # Inhalte der Hilfsarrays berechnen, Erklaerung siehe Zettel vom 10.6.15.
    for i in 1:num_states
        for j in 1:num_states
            hilfsdings[i][j] = (distributions[i] * params[i, j])
        end
    end
    # Verschieben der mobilen Daten. Als Ausgleich bei den anderen Arrays ein Feld hinten anfuegen, da die Arrays gleiche Laenge brauchen
    for i in 1:num_states
        unshift!(hilfsdings[1][i], 0.0f0)
        for j in 2:num_states
            push!(hilfsdings[j][i], 0.0f0)
        end
    end
    # Zur neuen Verteilung die passenden Arrays aufsummieren
    new_dist = Array(Any, 3)
    for i in 1:num_states
        new_dist[i] = hilfsdings[1][i]
        for j in 2:num_states
            new_dist[i] += hilfsdings[j][i]
        end
    end
    # Zu kleine Werte wegwerfen, um Groesse der Arrays zu beschraenken
    #new_dist, index = cut_Distributions(new_dist, index)
    return new_dist, index        
end

function waitingTimeForValue(params::Array{Float32, 2}, value, maxTime, num_states = 3)
    # Berechnung der Wartezeit auf Wert value, warte maximal bis maxTime
    # Beginne mit quasi leerem ergebnis, wkeitsmasse 1 in mobil und 0 in stat
    result = zeros(Float32, 1)
    #println("Starte Sim")
    distributions = Array[[1],[0],[0]]
    #Index noetig, wenn zu kleine W'keiten am Arraybeginn rausgeschmissen werden
    index = 1
    # Simuliere jeden Schritt bis maxTime
    for i = 1:maxTime
        # Ziel vorzeitig erreicht
        if  !(value > index)
            print ("break, fertig nach $i Schritten ")
            break
        end 
        # Ein Berechungsschritt
        distributions, index = updateDistributions!(params, distributions, index, num_states)
        # Muss jeden Schritt notieren wie viel % der Teilchen ankommen, entweder als Summe ueber die angekommenen Teilchen (if)
        # oder wenn keine angekommen sind (else) 0 reinschieben
        if (length(distributions[1]) > value-index)
            summe = 0
            for i in 1:num_states
                summe += pop!(distributions[i])
            end
            #println("angekommen, $summe")
            push!(result, summe)
        else
            push!(result, 0.0f0)
        end
    end
    return result
end

function combineParams(setsize)
    # Verschiedene Parameterkombinationen fuer Modell 3a erstellen
    # Benennung der Wahrscheinlichkeiten: p plus Startzustand, Endzustand, s bei Liste
    # Moegliche Zustaende: m - mobil, a - Adsorbtion, l - Loesung
    #Erstelle zunaechst Listen fuer Einzelwahrscheinlichkeiten, abhaengig von der gewaehlten kombi
    if setsize == "small"
        #fuer mobilen Ausgangszustand...
        pmms = [0.1f0, 0.5f0, 0.9f0]
        pmls = [0.001f0, 0.005f0, 0.0001f0] 
        # ... fuer adsorbierten Ausgangszustand...  
        paas = [0.999f0, 0.9993f0, 0.9996f0]   
        # ... und fuer geloesten Ausgangszustand
        plls = [0.99995f0, 0.99999f0, 0.999995f0]
    end
    
    if setsize == "medium" 
        pmms = linspace(0.1f0, 0.9f0, 5)
        pmms = append!(pmms, [0.05f0, 0.95f0])
        pmls = [0.001f0, 0.0007f0, 0.0005f0, 0.0003f0, 0.0001f0]
        paas = [0.998f0, 0.999f0, 0.9993f0, 0.9995f0, 0.9996f0]
        plls = [0.99995f0, 0.99999f0, 0.999995f0, 0.999999f0]
    end
    
    if setsize == "large"
        pmms = linspace(0.1f0, 0.9f0, 9)
        pmms = append!(pmms, [0.001f0, 0.01f0, 0.05f0, 0.95f0, 0.99])
        pmls = [0.003f0, 0.001f0, 0.0007f0, 0.0005f0, 0.0003f0, 0.0001f0, 0.00005f0]
        paas = linspace(0.999f0, 0.9997f0, 8)
        paas = append! (paas, [0.997f0, 0.998f0])
        plls = [0.999925f0, 0.99995f0, 0.999975f0, 0.99999f0, 0.999993f0, 0.999995f0, 0.999999f0]
    end
    
    if setsize == "laufzeit"
       pmms = [0.01f0, 0.9f0]
       pmls = [0.00005f0, 0.003f0]
       paas = [0.997f0, 0.9996f0]
       plls = [0.99995f0, 0.999995f0]    
    end
    
    
    if setsize == "elly"
       pmms = [0.5f0]
       pmls = [0.007f0]
       paas = [0.9985f0, 0.999f0, 0.9992f0, 0.9993f0, 0.9995f0, 0.9994f0]
       plls = [0.99995f0]    
    end
    
    println (pmms)
    println (pmls)
    println (paas)
    println (plls)
    
    # Kombiniere Einzelwahrscheinlichkeiten zu einer Liste je Ausgangszustand 
    pms = Array(Any, 0)
    for pmm in pmms
        for pml in pmls
            pma = 1 - pmm - pml
            push!(pms,([pmm pma pml]))
        end 
    end
    pas = Array(Any, 0)
    for paa in paas
        pam = 1 - paa
        push!(pas,([pam paa 0.0f0]))
    end
    pls = Array(Any, 0)
    for pll in plls
        plm = 1 - pll
        push!(pls,([plm 0.0f0 pll]))
    end
    # erstelle Liste aller moeglichen Kombinationen
    param_list = Array(Any, 0)
    for pm in pms, pa in pas, pl in pls
                push!(param_list,([pm, pa, pl])) 
    end
    return param_list
end    
    
    
# main
# Rahmenparameter einstellen
column_length = 1000
maxtime = 2400000
# Parameterkombination wählen
param_list = combineParams("elly")
#reverse!(param_list)
# Simulationen starten, vorher testen, ob diese schon exisitert, dazu den passenden filename aufbauen
for params in param_list
    filename = "savedata_julia/3a/l$column_length/Sim"
    for i in 1:3
        for j in 1:3
            filename = filename * "_" * string(params[i, j])
        end
    end
# nur simulieren, falls nicht vorhanden
if !isfile(filename)
        println (strftime(time()), " starte: ")
        println (params, " ")
        # Starte Simulation fuer params
        res = []
        #for i in 1:1
            res = @time(waitingTimeForValue(params, column_length, maxtime))
        #end
        # summe zur kontrolle
        println("summe ", sum(res))
        # abspeichern
        writecsv(filename, res)
    end
end  

println("Fertig, zum Anzeigen der Ergebnisse bitte \n python3 process_simulations.py -l", column_length, " -m 3a -o  aufrufen und evtl. anschließend mit \n python3 plottigs_PAA.py und die gewünschten Plots erzeugen")



