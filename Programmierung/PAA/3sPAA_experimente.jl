using PyPlot


function cut_Distributions(distributions, index)
    # Wenn Werte zu Beginn oder Schluss der Arrays zu klein sind, werden diese abgeschnitten
    # Dazu muessen alle Arrays zu kleine Werte an der entsprechenden Stelle haben
    
    if (length(distributions[1]) < 200)
       return distributions, index
     end
    while length(distributions[1]) > 200     
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
        else
            break
        end
    end
    while length(distributions[1]) > 200
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
        else
            break
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
#     for i in 1:num_states
#         if new_dist[i][1] 
#     end
    

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
    
    for i = 1:maxTime
        if sum(result) > 1
            #Ziel erreicht
            println ("break, fertig nach $i Schritten")
            #println (distributions)
            break
        end
         
#         if (sum(result)) > 1
#             println ("break, summe erreicht")
#             break
#         end
        for i in 1:10
            distributions, index = updateDistributions!(params, distributions, index, num_states)
            
            if (length(distributions[1]) > value-index)
                #println(" d1 ", length(distributions[1]), " length ", (value-index+1) )
                
            # push!(result, (rps[value-index+1]+rpm[value-index+1]))
                summe = 0
                for i in 1:num_states
                    summe += pop!(distributions[i])
                    #println(distributions[i][end])
                    #println (pop!(distributions[i]))
                end
                push!(result, summe)
            #  rpm[value-index+1] = 0
            #  rps[value-index+1] = 0
            else
                #das wird im prinzip nicht benoetigt, wenn man den index nutzt
                push!(result, 0.0f0)
                #println("FAlse")
            end
        end
        new_dist, index = cut_Distributions(new_dist, index)
        #println(" result ", length(result))
        end
    #println(result)
    return result
end

function combineParams()
    pmms = [0.5f0, 0.7f0, 0.9f0, 0.99f0]
    pmls = [ 0.005f0, 0.001f0, 0.0005f0, 0.0001f0, 0.0005f0] 
    pms = Array(Any, 0)
    for pmm in pmms
        for pml in pmls
            pma = 1 - pmm - pml
            push!(pms,([pmm pma pml]))
        end 
    end
       
    paas = [0.999f0, 0.9993f0, 0.9996f0, 0.9999f0]   
    pas = Array(Any, 0)
    for paa in paas
        pam = 1 - paa
        push!(pas,([pam paa 0.0f0]))
    end
    #print (pas)
    
    plls = [0.99995f0, 0.99999f0, 0.999995f0]
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


# for i = 1:5
#     @time(waitingTimeForValue(0.9992f0, 0.99f0, 1000, 1000000))
# end
laenge = 100
maxtime = 240000

params = [0.4f0 0.599f0 0.001f0; 0.01f0 0.99f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#params = [0.999f0 0.001f0 0.00f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]

param_list = combineParams()

for params in param_list
   println(strftime(time()))
   println (params)
   if isfile("savedata_julia/l$laenge/$params")
       res = readcsv("savedata_julia/l$laenge/$params")
       if (sum(res) < 1 )
           println("Summe ", sum(res))
           println("zu gering bei $params")
       end
   else
        #for i in 1:10
        res = @time(waitingTimeForValue(params, laenge, maxtime))
        println("Summe ", sum(res))
        #end
        if (sum(res) >= 0.9 )
            plt.plot(res)
            plt.ylabel("")
            plt.xlabel("Zeit / Schritten")
            plt.title("PAA; Params: $params")
            plt.savefig("savefigs_julia/l$laenge/$params .png")
            plt.clf()
        end
        writecsv("savedata_julia/l$laenge/$params", res)
   end
end  
# println("fertig")using PyPlot

function updateDistributions!(params::Array{Float32,2}, distributions, index, num_states)
    #= ps, pm: Parameter
       distributions: Matrix die Werte fuer mobil/stat enthaelt (Wert: WKeit an jeweiliger position)
       index: zur spaeteren Verschiebung des Arrays
       return: Neue distributions, index
    =#
    # Erstelle Hilfsmatrix aus Arrays. Jedes Array wird später befüllt aus einer alten Verteilung mal entsprechender Uebergangswahrscheinlichkeit. Bei 3 Zustaenden ergeben sich so 9 Arrays
    hilfsdings = Array(Any, num_states)
    for i in 1:num_states
        hilfsdings[i] = Array(Any, num_states)
    end
    #TODO: besser das hilfsarray anlegen... Array(Any, (3,3)) klappt nicht
    
    # Inhalte der Hilfsarrays berechnen -> TODO Formel dafuer aufschreiben, > schreiben, s.u.
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

    return new_dist, index        
end


function cut_Dist(distributions, index, num_states)    
    # Wenn Werte zu Beginn oder Schluss der Arrays zu klein sind, werden diese abgeschnitten
    # Dazu muessen alle Arrays zu kleine Werte an der entsprechenden Stelle haben
    
    if  (length(distributions[1]) < 2)
        return distributions, index
    end
    while length(distributions[1]) > 1
        vorneschneiden = true
        # Vorne testen
        for i in 1:num_states
            if distributions[i][1] >= 1.0f-17
                vorneschneiden = false
                break
            end
        end
        #Vorne abschneiden
        if vorneschneiden
            index += 1
            #println ("shift")
            for i in 1:num_states
                shift!(distributions[i])
            end
        else
            break
        end
    end #while
    
    while length(distributions[1]) > 1
        hintenschneiden = true
        # Hinten testen    
        for i in 1:num_states
            if distributions[i][end] >= 1.0f-17
                hintenschneiden = false
                break
            end
        end
        # Hinten abschneiden
        if hintenschneiden
            for i in 1:num_states
                pop!(distributions[i])
            end
        else
            break
        end
    end #while true    
    return distributions, index
end

function waitingTimeForValue(params::Array{Float32, 2}, value, maxTime, num_states = 3)
    # Beginne mit quasi leerem ergebnis, wkeitsmasse 1 in mobil und 0 in stat
    println ("params ", params)
    result = zeros(Float32, 1)
    distributions = ones(Float32,1)
    rps = zeros(Float32, 1)
    rpm = ones(Float32, 1)
    
    
    #append!(distributions, ones(Float32,1))
    for i = 2:num_states
        r = zeros(Float32,1)
        append!(distributions, r)
    end    
    #distributions = reshape(distributions, 3,1)
    #TODO fuer andere anzahl an zustaenden
    distributions = Array[[1],[0],[0]]
    #println(distributions)
    
    index = 1
    #Main loop
    for i = 1:10:maxTime
        #print ("i ", i, " ", length(distributions[1]), "   ")
        if !(value>index)
            #Ziel erreicht
            println ("break, fertig")
            break
        end
        distributions, index = updateDistributions!(params, distributions, index, num_states)
        # ein Berechnungsschritt
        for j = 1:10
        distributions, index = cut_Dist(distributions, index, num_states)
            #print("value ", value, " index ", index)        
            #println(distributions[1])
            if (length(distributions[1]) > value-index)
                #println(" d1 ", length(distributions[1]), " length ", (value-index+1) )
                summe = 0
                for i in 1:num_states
                    summe += pop!(distributions[i])
                    #println(distributions[i][end])
                    #println (pop!(distributions[i]))
                end
                push!(result, summe)
            else
                #das wird im prinzip nicht benoetigt, wenn man den index nutzt
                push!(result, 0.0f0)
                #println("FAlse")
            end #if-else
            #println(" result ", length(result))
        end # for inner loop
    end #for main loop
            #println(result)
    return result
end


function combineParams()
    pmms = [0.5f0, 0.7f0, 0.9f0, 0.99f0]
    pmls = [ 0.005f0, 0.001f0, 0.0005f0, 0.0001f0, 0.0005f0] 
    pms = Array(Any, 0)
    for pmm in pmms
        for pml in pmls
            pma = 1 - pmm - pml
            push!(pms,([pmm pma pml]))
        end 
    end
       
    paas = [0.999f0, 0.9993f0, 0.9996f0, 0.9999f0]   
    pas = Array(Any, 0)
    for paa in paas
        pam = 1 - paa
        push!(pas,([pam paa 0.0f0]))
    end
    #print (pas)
    
    plls = [0.99995f0, 0.99999f0, 0.999995f0]
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


# for i = 1:5
#     @time(waitingTimeForValue(0.9992f0, 0.99f0, 1000, 1000000))
# end
laenge = 1000
maxtime = 2400000

params = [0.3f0 0.699f0 0.01f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#params = [0.999f0 0.001f0 0.00f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#println(params)
params =[0.4f0 0.599f0 0.001f0; 0.01f0 0.99f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]

param_list = combineParams()


#for params in param_list
    println(strftime(time()))
 #   if isfile("savedata_julia/l$laenge/$params")
 #       res = readcsv("savedata_julia/l$laenge/$params")
 #       if (sum(res) < 1 )
 #           println("Summe ", sum(res))
 #           println("zu gering bei $params")
 #       end
 #   else
        res = @time(waitingTimeForValue(params, laenge, maxtime))
        println("Summe ", sum(res))
        if (sum(res) >= 0.9 )
            plt.plot(res)
            plt.ylabel("")
            plt.xlabel("Zeit / Schritten")
            plt.title("PAA; Params: $params")
            plt.savefig("savefigs_julia/l$laenge/$params .png")
            plt.clf()
        end
        writecsv("savedata_julia/l$laenge/$params", res)
 #   end
#end
# end    
# println("fertig")
