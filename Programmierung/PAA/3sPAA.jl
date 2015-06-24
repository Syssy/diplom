using PyPlot


function cut_Distributions(distributions, index)
    # Wenn Werte zu Beginn oder Schluss der Arrays zu klein sind, werden diese abgeschnitten
    # Dazu muessen alle Arrays zu kleine Werte an der entsprechenden Stelle haben
#     if (length(distributions[1]) < 200)
#        return distributions, index
#      end
    vorneschneiden = true
    # Vorne testen
    for i in 1:length(distributions)
        if distributions[i][1] >= 1.0f-17
            vorneschneiden = false
            break
        end
    end
    #Vorne abschneiden
    if vorneschneiden
        index += 1
        #println ("shift", (distributions[1]))
        for i in 1:length(distributions)
        #    print (" ", distributions[i][1])
            shift!(distributions[i])
        #    println (" ", distributions[i][1])
        end
    end
    hintenschneiden = true
    # Hinten testen    
    for i in 1:length(distributions)
        if distributions[i][end] >= 1.0f-17
            hintenschneiden = false
            break
        end
    end
    # Hinten abschneiden
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
       index: zur spaeteren Verschiebung des Arrays
       return: Neue distributions, index
    =#
    # Erstelle Hilfsmatrix aus Arrays. Jedes Array wird später befüllt aus einer alten Verteilung mal entsprechender Uebergangswahrscheinlichkeit. Bei 3 Zustaenden ergeben sich so 9 Arrays
    hilfsdings = Array(Any, num_states)
    #println ("hilfsdings beim befuellen ", hilfsdings, typeof(hilfsdings))
    for i in 1:num_states
        hilfsdings[i] = Array(Any, num_states)
    end
    
    # Inhalte der Hilfsarrays berechnen
    for i in 1:num_states
        for j in 1:num_states
            #print ("dist $i ", distributions[i])
            #print (" params $i $j ", params[i, j])
            #println (" multipiziert ", distributions[i] * params[i, j])
            #println("hilfsdings i ", hilfsdings[1])
            hilfsdings[i][j] = (distributions[i] * params[i, j])
            #println ("hilfsdingsij ", hilfsdings[i][j])
        end
    end
    #println("hilfsdings ", hilfsdings)
    
    # Verschieben der mobilen Daten. Als Ausgleich bei den anderen Arrays ein Feld hinten anfuegen
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
    new_dist, index = cut_Distributions(new_dist, index)

    return new_dist, index        
end


function waitingTimeForValue(params::Array{Float32, 2}, value, maxTime, num_states = 3)
    # Beginne mit quasi leerem ergebnis, wkeitsmasse 1 in mobil und 0 in stat
    #println ("params ", params)
    result = zeros(Float32, 1)

    #TODO fuer andere anzahl an zustaenden
    distributions = Array[[1],[0],[0]]
    #println(distributions)
    
    index = 1
    zeitverschiebung = 0
    
    for i = 1:maxTime
        if  !(value > index)
            #Ziel erreicht
            println ("break, fertig nach $i Schritten")
            #println (distributions)
            break
        end
        distributions, index = updateDistributions!(params, distributions, index, num_states)
        if (length(distributions[1]) > value-index)
            summe = 0
            for i in 1:num_states
                summe += pop!(distributions[i])
            end
            push!(result, summe)
        else
            #das wird im prinzip nicht benoetigt, wenn man den index nutzt
            # TODO: Drüber nachdenken, das mit dem Index stimmt nämlich nicht
            #push!(result, 0.0f0)
            zeitverschiebung += 1
            #println("FAlse")
        end
        end
    unshift!(result, zeitverschiebung)
    println("index ", result[1])
    return result
end

function combineParams()
    pmms = [0.005f0, 0.007f0, 0.01f0, 0.05f0, 0.1f0, 0.2f0, 0.3f0]
    #pmms = [0.005f0, 0.007f0, 0.01f0, 0.1f0, 0.2f0, 0.3f0, 0.5f0, 0.7f0, 0.9f0, 0.99f0]
    # 0.00001f0 ist zu klein, nicht ausreichend teilchen drin, daher kein schönes tailing
    pmls = [0.001f0, 0.0007f0, 0.0005f0, 0.0003f0, 0.0001f0] 
    #pmls = [0.01f0, 0.005f0, 0.001f0, 0.0007f0, 0.0005f0, 0.0003f0, 0.0001f0, 0.00003f0, 0.00005f0, 0.00001f0] 
    pms = Array(Any, 0)
    for pmm in pmms
        for pml in pmls
            pma = 1 - pmm - pml
            push!(pms,([pmm pma pml]))
        end 
    end
       
    paas = [0.999f0, 0.9991f0, 0.9992f0, 0.9993f0]   
    #paas = [0.994f0, 0.995f0, 0.997f0, 0.998f0, 0.999f0, 0.9991f0, 0.9992f0, 0.9993f0, 0.9994f0, 0.9995f0, 0.9996f0, 0.9999f0]   
    pas = Array(Any, 0)
    for paa in paas
        pam = 1 - paa
        push!(pas,([pam paa 0.0f0]))
    end
    #print (pas)
    
    #0.999999f0 ist zu groß
    plls = [0.99995f0, 0.99999f0, 0.999993f0, 0.999995f0, 0.999996f0, 0.999997f0]
    #plls = [0.9999f0, 0.999925f0, 0.99995f0, 0.999975f0, 0.99999f0, 0.999993f0, 0.999995f0, 0.999996f0, 0.999997f0, 0.999999f0]
    pls = Array(Any, 0)
    for pll in plls
        plm = 1 - pll
        push!(pls,([plm 0.0f0 pll]))
    end
    
  #  println("pms", pms)
  #  println("pas", pas)
  #  println("pls", pls)
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
params = [0.9f0 0.1f0 0.0f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]

param_list = combineParams()
#reverse!(param_list)
println(length(param_list))

#for params in param_list
    println(strftime(time()))
    println (params)
#     if isfile("savedata_julia/l$laenge/$params")
#    #    println("Summe ", sum(res))
#    #    if (sum(res) < 0.999 )
#    #        println("zu gering bei $params")
#    #    end
#         filename = "savedata_julia/l$laenge/Sim"
#         #println (filename, " ")
#         for i in 1:3
#             for j in 1:3
#         #        println (i, " ", params[i, j])
#                 filename = filename * "_" * string(params[i, j])
#                 #println (filename)
#             end
#         end
#         if !isfile(filename)
#             println ("filename: ", filename, " ")
#             res = readcsv("savedata_julia/l$laenge/$params")
#             writecsv(filename, res)
#         end
#         #println ("isfile, $params")
#     else
        #for i in 1:10
        res = @time(waitingTimeForValue(params, laenge, maxtime))
        println("Summe ", sum(res))
#         #end
        writecsv("savedata_julia/l$laenge/$params", res)
        if (sum(res) >= 0.9 )
            plt.plot(res[2:end])
            #plt.xticks([0, len(res)], [res[1], (len(res) + res[0]))
            plt.ylabel("")
            plt.xlabel("Zeit / Schritten")
            plt.title("PAA; Params: $params")
            plt.savefig("savefigs_julia/l$laenge/$params .png")
            plt.clf()
#        end
#    end
end  
# println("fertig")