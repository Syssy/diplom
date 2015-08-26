#using PyPlot
# Implementierung eines PAAs fuer 3 Zustaende, sollte mit minimalen Aenderungen (zB init der dist) auf fuer mehr Zustaende funktionieren
# Nur der benoetigte Spezialfall eines PAA

function cut_Distributions(distributions, index)
    # Wenn Werte zu Beginn oder Schluss der Arrays zu klein sind, werden diese abgeschnitten
    # Dazu muessen alle Arrays zu kleine Werte an der entsprechenden Stelle haben  
    vorneschneiden = true
    # Vorne testen, falls ein Wert gross genug ist, wird nicht geschnitten
    for i in 1:length(distributions)
        if distributions[i][1] >= 1.0f-20
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
    
    hintenschneiden = true
    # Hinten testen, wie vorne    
    for i in 1:length(distributions)
        if distributions[i][end] >= 1.0f-20
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
    #= ps, pm: Parameter
       distributions: Matrix die Werte fuer mobil/stat enthaelt (Wert: WKeit an jeweiliger position)
       index: zur spaeteren Verschiebung des Arrays, wird erhoeht, wenn zu kleine Werte abgeschnitten werden
       return: Neue distributions, index
    =#
    #TODO Sind hier neun nötig oder reichen auch 6?
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
    # Erklaerung anschaulich auf dem Zettel vom 10.6.15 TODO muss irgendwie vertextlicht werden/Graphik welches Feld woraus berechnet wird
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
    # Beginne mit quasi leerem ergebnis, wkeitsmasse 1 in mobil und 0 in stat
    result = zeros(Float32, 1)
    #println("Starte Sim")
    #TODO fuer andere anzahl an zustaenden
    distributions = Array[[1],[0],[0]]
    
    #Index noetig, wenn zu kleine W'keiten am Arraybeginn rausgeschmissen werden
    index = 1
    
    # Simuliere jeden Schritt bis maxTime
    for i = 1:maxTime
        # Ziel vorzeitig erreicht
        if  !(value > index)
            println ("break, fertig nach $i Schritten")
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


function combineParams()
    # Verschiedene Parameterkombinationen erstellen
    # Benennung der Wahrscheinlichkeiten: p plus Startzustand, Endzustand, s bei Liste
    # Moegliche Zustaende: m - mobil, a - Adsorbtion, l - Loesung
    # TODO: Aktuell nur Kombination fuer Modell 3a)
    
    #Erstelle zunaechst Listen fuer Einzelwahrscheinlichkeiten fuer mobilen Ausgangszustand...
    pmms = [0.005f0, 0.5f0, 0.99f0]
    pmms = [0.1f0, 0.2f0, 0.3f0, 0.4f0, 0.5f0, 0.6f0]
    #pmms = [0.005f0, 0.01f0, 0.05f0, 0.1f0, 0.15f0, 0.2f0, 0.25f0, 0.3f0, 0.35f0, 0.4f0, 0.45f0, 0.5f0, 0.55f0, 0.6f0, 0.65f0, 0.7f0, 0.75f0, 0.8f0, 0.85f0, 0.9f0]
    #pmms = [0.005f0, 0.007f0, 0.01f0, 0.05f0, 0.1f0, 0.15f0, 0.2f0, 0.25f0, 0.3f0, 0.35f0, 0.4f0, 0.45f0, 0.5f0, 0.55f0, 0.6f0, 0.65f0, 0.7f0, 0.75f0, 0.8f0, 0.85f0, 0.9f0, 0.95f0, 0.99f0]
    # 0.00001f0 ist zu klein, nicht ausreichend teilchen drin, daher kein schönes tailing
    pmls = [0.01f0, 0.001f0, 0.00001f0] 
    pmls = [0.005f0, 0.003f0, 0.001f0, 0.0007f0, 0.0006f0, 0.0005f0, 0.0003f0, 0.0001f0, 0.00005f0] 
    #pmls = [0.01f0, 0.005f0, 0.003f0, 0.001f0, 0.0007f0, 0.0005f0, 0.0003f0, 0.0001f0, 0.00005f0, 0.00003f0, 0.00001f0] 
    pms = Array(Any, 0)
    for pmm in pmms
        for pml in pmls
            pma = 1 - pmm - pml
            push!(pms,([pmm pma pml]))
        end 
    end
    # ... fuer adsorbierten Ausgangszustand...  
    paas = [0.99f0, 0.9992f0, 0.9999f0]   
    paas = [0.999f0, 0.9991f0, 0.9992f0, 0.9993f0, 0.9994f0, 0.9995f0, 0.9996f0]   
    #paas = [0.99f0, 0.995f0, 0.997f0, 0.998f0, 0.9985f0, 0.999f0, 0.9991f0, 0.9992f0, 0.9993f0, 0.9994f0, 0.9995f0, 0.9996f0, 0.9999f0]   
    pas = Array(Any, 0)
    for paa in paas
        pam = 1 - paa
        push!(pas,([pam paa 0.0f0]))
    end
    # ... und fuer geloesten Ausgangszustand
    plls = [0.9999f0, 0.99999f0, 0.999999f0]
    plls = [0.99999f0, 0.999993f0, 0.999995f0, 0.999997f0]
    #0.999999f0 ist zu groß
    #plls = [0.9999f0, 0.999925f0, 0.99995f0, 0.999975f0, 0.999985f0, 0.99999f0, 0.999993f0, 0.999995f0, 0.999996f0, 0.999997f0, 0.999999f0]
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


function updateSims(directory)
    println ("update")
    
end

# for i = 1:5
#     @time(waitingTimeForValue(0.9992f0, 0.99f0, 1000, 1000000))
# end
laenge = 1000
maxtime = 2400000

#params = [0.4f0 0.599f0 0.001f0; 0.01f0 0.99f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#params = [0.8f0 0.195f0 0.005f0; 0.0004f0 0.9996f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
#params = [0.9f0 0.1f0 0.0f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#params[0.5 0.49995 5.0e-5; 0.004999995 0.995 0.0; 1.001358e-5 0.0 0.99999] 

params = [0.5f0 0.1f0 0.0f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
params = [0.4f0 0.59995f0 5.0f-05; 0.002f0 0.998f0 0.0f0; 5.0f-05 0.0f0 0.999995f0]
param_list = Array(Any, 0)
params=[0.7f0 0.29995f0 0.00005f0; 0.005f0 0.995f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
push!(param_list, params)
params=[0.99f0 0.005f0 0.005f0; 0.0004f0 0.9996f0 0.0f0; 0.000025f0 0.0f0 0.999975f0]
push!(param_list, params)
params=[0.99f0 0.0095f0 0.0005f0; 0.005f0 0.995f0 0.0f0; 0.000075f0 0.0f0 0.999925f0]
push!(param_list, params)
params=[0.85f0 0.1493f0 0.0007f0; 0.003f0 0.997f0 0.0f0; 0.000003f0 0.0f0 0.999997f0]
push!(param_list, params)
params=[0.005f0 0.99499f0 0.00001f0; 0.0009f0 0.9991f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
push!(param_list, params)
params=[0.6f0 0.399f0 0.001f0; 0.0004f0 0.9996f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
push!(param_list, params)
params=[0.005f0 0.9947f0 0.0003f0; 0.0009f0 0.9991f0 0.0f0; 0.000003f0 0.0f0 0.999997f0]
push!(param_list, params)
params=[0.5f0 0.499f0 0.001f0; 0.0005f0 0.9995f0 0.0f0; 0.00001f0 0.0f0 0.99999f0]
push!(param_list, params)
params=[0.05f0 0.9495f0 0.0005f0; 0.0009f0 0.9991f0 0.0f0; 0.000005f0 0.0f0 0.99995f0]
push!(param_list, params)
params=[0.2f0 0.7993f0 0.0007f0; 0.0008f0 0.9992f0 0.0f0; 0.000004f0 0.0f0 0.999996f0]
push!(param_list, params)
params=[0.005f0 0.999499f0 0.00001f0; 0.0005f0 0.9995f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
push!(param_list, params)
params=[0.15f0 0.84995f0 0.00005f0; 0.0004f0 0.9996f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
push!(param_list, params)
params=[0.05f0 0.9493f0 0.0007f0; 0.0005f0 0.9995f0 0.0f0; 0.000025f0 0.0f0 0.999975f0]
push!(param_list, params)
params=[0.15f0 0.845f0 0.005f0; 0.0005f0 0.9995f0 0.0f0; 0.000025f0 0.0f0 0.999975f0]
push!(param_list, params)
params=[0.1f0 0.899f0 0.001f0; 0.0007f0 0.9993f0 0.0f0; 0.000001f0 0.0f0 0.999999f0]
push!(param_list, params)
param_list = combineParams()
reverse!(param_list)
println(length(param_list))

# Simulationen starten, vorher testen, ob diese schon exisitert
for params in param_list
    filename = "savedata_julia/l$laenge/Sim"
    for i in 1:3
        for j in 1:3
    #        println (i, " ", params[i, j])
            filename = filename * "_" * string(params[i, j])
            #println (filename)
        end
    end
   if !isfile(filename)
   # if isfile("savedata_julia/l$laenge/$params")
   #    println("Summe ", sum(res))
   #    if (sum(res) < 0.999 )
   #        println("zu gering bei $params")
   #    end
        println (filename, " ")
#         if !isfile(filename)
#             println ("filename: ", filename, " ")
#             res = readcsv("savedata_julia/l$laenge/$params")
#             writecsv(filename, res)
#         end
#        println ("isfile, $params")
#     else
        println(strftime(time()), " starte: ")
        println (params, " ")
       # for i in 1:5
            res = @time(waitingTimeForValue(params, laenge, maxtime))
        #    println("Summe ", sum(res))
        #end
        writecsv(filename, res)
   # end
#     else
#    #     if (sum(res) >= 0.9 )
#             res = readcsv(filename)
#             plt.plot(res)
#             #plt.xticks([0, len(res)], [res[1], (len(res) + res[0]))
#             plt.ylabel("")
#             plt.xlabel("Zeit / Schritten")
#             plt.title("PAA; Params: $params")
#             plt.savefig("savefigs_julia/l$laenge/$params .png")
#             plt.clf()
#        end
    end
end  
println("fertig")