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

function combineParams()
    # Erstelle Liste von Parameterkombinationen
    pss = [0.998f0, 0.999f0, 0.9991f0, 0.9992f0, 0.9993f0, 0.9994f0, 0.9995f0, 0.9996f0, 0.9997f0, 0.9998f0]
    pms = [0.05f0, 0.1f0, 0.15f0, 0.2f0, 0.25f0, 0.3f0, 0.35f0, 0.4f0, 0.45f0, 0.5f0, 0.55f0, 0.6f0, 0.65f0, 0.7f0, 0.75f0, 0.8f0, 0.85f0, 0.9f0, 0.95f0]
        # erstelle Liste aller moeglichen Kombinationen
    param_list = Array(Any, 0)
    for ps in pss
        for pm in pms
            params = [ps, pm]
            push!(param_list, params)
        end
    end
    return param_list
end

# main:
column_length = 1000
maxtime = 2400000
param_list = combineParams()
# Simuliere alle Parameterkombinationen
for (ps, pm) in param_list
    filename = "savedata_julia/l$column_length/2_states/Sim_$ps" * "_$pm"
    println("ps:", ps, " pm: ", pm)
    # Simulieren
    res = @time(waitingTimeForValue(ps, pm, column_length, maxtime))
    #Summe zur Kontrolle
    println("Sum ", sum(res))
    #Speichern
    writecsv(filename, res)
    #end
end    
println("fertig")
