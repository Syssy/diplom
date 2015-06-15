using PyPlot

println("Los geht's") 

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
    
    #vorneschneiden = False
    #hintenschneiden = False
    #TODO allgemeiner machen
    
    if (new_dist[1][1] < 1.0f-17)  & (new_dist[2][1]< 1.0f-17)  & (new_dist[3][1] < 1.0f-17) 
        index += 1
        shift!(new_dist[1])
        shift!(new_dist[2])
        shift!(new_dist[3])
        #print ("shift ", length(new_dist[1]))
        #sleep(1)
    end
    
    if (new_dist[1][end] < 1.0f-17)  & (new_dist[2][end]<1.0f-17)  & (new_dist[3][end] < 1.0f-17) 
        pop!(new_dist[1])
        pop!(new_dist[2])
        pop!(new_dist[3])
        #print ("pop", length(new_dist[1]))
        #sleep(1)       
    end

#     for i in 1:num_states
#         if new_dist[i][1] 
#     end
    

    return new_dist, index        
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
    println(distributions)
    
    index = 1
    
    for i = 1:maxTime
        if !(value>index)
            #Ziel erreicht
            println ("break, fertig")
            break
        end
         
#         if (sum(result)) > 1
#             println ("break, summe erreicht")
#             break
#         end
        
        distributions, index = updateDistributions!(params, distributions, index, num_states)
        #println("rps ", rps)
        #println("rpm ", rpm)
        #print("value ", value, " index ", index)        
        #println(distributions[1])
        #println(" ")
    
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
        #println(" result ", length(result))
        end
    #println(result)
    return result
end

# for i = 1:5
#     @time(waitingTimeForValue(0.9992f0, 0.99f0, 1000, 1000000))
# end
laenge = 1000
maxtime = 300000

params = [0.4f0 0.599f0 0.001f0; 0.01f0 0.99f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]
#params = [0.999f0 0.001f0 0.00f0; 0.001f0 0.999f0 0.0f0; 0.00005f0 0.0f0 0.99995f0]

#params = reshape(params, 3,3)
println(params)
res = @time(waitingTimeForValue(params, laenge, maxtime))
#println (res)
# 
# for ps in 0.9997f0:0.0001f0:0.9999f0
#     for pm in 0.2f0:0.05f0:0.9f0
#         println("ps:", ps, " ps: ", pm)
#         res = @time(waitingTimeForValue(ps, pm, laenge, maxtime))
#         #print (dauer)
#         #res = waitingTimeForValue(ps, pm, laenge, maxtime)
println("Summe ", sum(res))
plt.plot(res)
plt.ylabel("")
plt.xlabel("Zeit / Schritten")
plt.title("PAA; Params: $params")
plt.savefig("savefigs_julia/l$laenge/$params .png")
#         plt.clf()
#         writecsv("savedata/l$laenge/$ps _$pm", res)
#     end
# end    
# println("fertig")
