using PyPlot

function updateDistributions!(ps::Float32, pm::Float32, stationaryVector, mobileVector, index)
    #= ps, pm: Parameter
       stationaryVector, mobileVector: Arrays die Werte fuer mobil/stat enthalten (Wert: WKeit an jeweiliger position)
       index: zur spaeteren Verschiebung des Arrays
       return: Neue stationaryVector, mobileVector, index
    =#
    #rs1 = Array(Float32, length(stationaryVector))
    # rs/m1/2 sind hilfsarrays, aus denen die neuen stationaryVector und mobileVector berechnet werden
    rs1 = stationaryVector * ps
    rs2 = mobileVector * (1.0f0-pm)
    # unshift! fuegt am Anfang ein
    unshift!(rs2, 0.0f0)
    # push! fuegt am Ende ein
    push!(rs1, 0.0f0)
        
    rm1 = stationaryVector * (1.0f0-ps)
    rm2 = mobileVector * pm
    unshift!(rm2, 0.0f0)
    push!(rm1, 0.0f0)
        
        #mobileVector = (push!(stationaryVector*(1-ps), 0.0f0)) + (unshift!((mobileVector*pm), 0.0f0))
    
        #stationaryVector = push!(rs1, 0.0f0) + unshift!(rs2, 0.0f0)
        
    stationaryVector = rs1 + rs2
    mobileVector = rm1 + rm2
        
        #zu kleine Werte am Anfang rausschmeissen, damit das array nicht zu gross wird
        # Dann auch passend den Index verschieben
        #TODO sinnvoller wert?
        #println("stationaryVector vorher ", stationaryVector)
        #println("mobileVector vorher ", mobileVector)
    if (stationaryVector[1] < 1.0f-17)  & (mobileVector[1] < 1.0f-17)
        index += 1
        # shift! loescht am Anfang
        shift!(stationaryVector)
        shift!(mobileVector)
    end

        #println(stationaryVector, mobileVector)
        #gleiches fuer das Ende
        #TODO ebenfalls ueberpruefen
    if (stationaryVector[end] < 1.0f-17) & (mobileVector[end] < 1.0f-17)
        #pop! loescht am Ende
        pop!(stationaryVector)
        pop!(mobileVector)
    end
    return stationaryVector, mobileVector, index        
end

# Berechne Wartezeit für Wert value. Maximale Wartezeit durch maxTime gegeben
# ps und pm W'keiten, stationär bzw mobil zu bleiben
function waitingTimeForValue(ps::Float32, pm::Float32, value, maxTime)
    # Beginne mit leerem ergebnis
    result = zeros(Float32, 1)
    # stationaryVector ist der Vektor für die stat. Phase, enthält zu Beginn an Stelle 0 0% der Teilchen
    # mobileVector ist der Vektor für die mobile Phase, enthält zu Beginn an Stelle 0 100% der Teilchen
    # Da weitere Stellen noch nicht interessieren: Laenge 1
    stationaryVector = zeros(Float32, 1)
    mobileVector = ones(Float32, 1)
    # Index zur Verschiebung der gekürzten Arrays
    index = 1  
    # Hauptschleife: Betrachte jeden Zeitpunkt bis maxTime
    for i = 1:maxTime
        # Vorzeitiger Abbruch möglich?
        if !(value>index)
            # break, sonst Fehler (Bounds Ex) beim push ins result, da laenge der mobileVector zu kurz ist
            # Ausserdem ist halt das Ziel erreicht
            #print("break, mobileVector ", mobileVector, " stationaryVector ", stationaryVector)
            println ("break, fertig")
            break
        end
        # Einen Schritt simulieren: Verteilungen aktualisieren
        stationaryVector, mobileVector, index = updateDistributions!(ps, pm, stationaryVector, mobileVector, index)      
        # Wenn Bedingung erfüllt, hat Teil der Masse die Ziellänge erreicht
        if (length(mobileVector) > value-index)
            # Angekommene Wahrscheinlichkeiten ins Ergebnis
            push!(result, (stationaryVector[value-index+1]+mobileVector[value-index+1]))
            mobileVector[value-index+1] = 0
            stationaryVector[value-index+1] = 0
        else
            # Sonst keine Teilchen angekommen, 0 ins Ergebnis
            push!(result, 0.0f0)
        end
    end
    #println(result)
    return result
end

# for i = 1:5
#     @time(waitingTimeForValue(0.9992f0, 0.99f0, 1000, 1000000))
# end
ps = 0.9995f0
pm = 0.9f0
laenge = 1000
maxtime = 2400000
pss = [0.997f0, 0.999f0, 0.9992f0, 0.9995f0, 0.9999f0]
pms = [0.01f0, 0.3f0, 0.9f0, 0.999f0]
param_list = Array(Any, 0)
for ps in pss
    for pm in pms
        params = [ps, pm]
        push!(param_list, params)
    end
end

for (ps, pm) in param_list

    println("ps:", ps, " pm: ", pm)
    #for i in 1:5
        res = @time(waitingTimeForValue(ps, pm, laenge, maxtime))
        #print (dauer)
        #res = waitingTimeForValue(ps, pm, laenge, maxtime)
        println("Summe ", sum(res))
        plt.plot(res)
        plt.ylabel("")
        plt.xlabel("Zeit / Schritten")
        plt.title("PAA; Params: ps:$ps, pm:$pm")
        plt.savefig("savefigs_julia/l$laenge/$ps __$pm .png")
        plt.clf()
#         writecsv("savedata_julia/l$laenge/$ps _$pm", res)
    #end
end    
println("fertig")
