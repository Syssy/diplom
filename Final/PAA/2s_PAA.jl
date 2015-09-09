# Implementierung des PAA mit eingeschraenkten Funktionen
# 2 Zustaende Modell

function updateDistributions!(ps::Float32, pm::Float32, stationaryVector, mobileVector, index)
    #= ps, pm: Parameter
       stationaryVector, mobileVector: Arrays die Werte fuer mobil/stat enthalten (Wert: WKeit an jeweiliger position)
       index: zur spaeteren Verschiebung des Arrays
       return: Neue stationaryVector, mobileVector, index
    =#
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
        
    stationaryVector = rs1 + rs2
    mobileVector = rm1 + rm2
    #zu kleine Werte am Anfang rausschmeissen, damit das array nicht zu gross wird
    # Dann auch passend den Index verschieben
    if (stationaryVector[1] < 1.0f-17)  & (mobileVector[1] < 1.0f-17)
        index += 1
        # shift! loescht am Anfang
        shift!(stationaryVector)
        shift!(mobileVector)
    end
    #gleiches fuer das Ende, Indexverschiebung hier nicht noetig
    if (stationaryVector[end] < 1.0f-17) & (mobileVector[end] < 1.0f-17)
        #pop! loescht am Ende
        pop!(stationaryVector)
        pop!(mobileVector)
    end
    return stationaryVector, mobileVector, index        
end

function waitingTimeForValue(ps::Float32, pm::Float32, value, maxTime)
    # Berechne Wartezeit für Wert value. Maximale Wartezeit durch maxTime gegeben
    # ps und pm W'keiten, stationär bzw mobil zu bleiben
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
            # break, sonst Fehler (Bounds Exception) beim push ins result, da Laenge der mobileVector zu kurz ist
            # Ausserdem ist halt das Ziel erreicht
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

function combineParams(setsize)
    # Erstelle Liste von Parameterkombinationen
    pss = Array(Any, 0)
    pms = Array(Any, 0)
    
    if setsize == "small"
        pss = [0.998f0, 0.999f0, 0.9993f0, 0.9996f0, 0.9999f0]
        pms = [0.1f0, 0.3f0, 0.5f0, 0.7f0, 0.9f0]
    end
    
    if setsize == "medium"
        pss = [0.997f0, 0.998f0, 0.999f0, 0.9991f0, 0.9992f0, 0.9993f0, 0.9995f0, 0.9996f0]
        pms = linspace(0.1f0, 0.9f0, 9)
    end
    
    if setsize == "large"
        pss = linspace(0.999f0, 0.9999f0, 10)
        pss = append!(pss, [0.99f0, 0.995f0, 0.997f0, 0.998f0])
        pms = linspace(0.05f0, 0.999999f0, 20)
        pms = append! (pms, [0.001f0, 0.01f0, 0.99f0, 0.999f0])
    end
    
    # erstelle Liste aller moeglichen Kombinationen
    param_list = Array(Any, 0)
    for ps in pss
        for pm in pms
            params = [round(ps,5), round(pm,5)]
            push!(param_list, params)
        end
    end
    return param_list
end

# main:
function main()
    # Simulationseinstellungen
    column_length = 1000
    maxtime = 2400000
    param_list = combineParams("large")
    # Simuliere alle Parameterkombinationen
    for (ps, pm) in param_list
        filename = "savedata_julia/2s/l$column_length/Sim_$ps" * "_$pm"
        #nur simulieren, wenn nicht schon vorhanden
        if !isfile(filename) 
            print("ps:", ps, " pm: ", pm, " ")
            # Simulieren
            res = waitingTimeForValue(ps, pm, column_length+1, maxtime)
            #Summe zur Kontrolle
            println("Sum ", sum(res))
            #Speichern
            writecsv(filename, res)
        end
    end   
end

main()
println("fertig")
