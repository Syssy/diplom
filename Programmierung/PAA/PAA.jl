
println("Hello World!") 

function emissionProbability(state, emission)
    # Mobil(2) hat immer em 1 und stat(1) hat immer em 0
    if state == (emission)
        return 0.8
    else
        return 0.2
    end
end

function getEmissionCount()
    # Emissionen sind 0 oder 1
    return 2
end

function getStartState()
    # Mobil = 2
    return 2
end

function getStartValue()
    #starte bei null
    return 0
end

function getStateCount()
    # States sind 1 = stat und 2 = mob
    return 2
end    

function getValueCount()
    # Laenge der Saeule
    return 100002
end

function performOperation(state, value, emission)
    # Gehe immer einen vorwaerts, ausser schon im ziel
    if (value + emission < getValueCount() -1)
        return value + emission
    else
        return value
    end
end    
       
function transitionProbability(state, targetState)
    # festlegung der w'keiten fuer ps und pm. nutze gegenw'keit fuer selbstuebergang
    ps = 0.09
    pm = 0.02
    p = 0.0
    if state == 1
        p = ps
    elseif state == 2
        p = pm
    else
        p = 0.0
    end
    if (state == targetState)
        return p
    else 
        return 1-p
    end
end

function getEmission(state)
    # in stat (1) emission 0 und sonst (mobil,2) em 1
    if (state == 1)
        return 1
    else
        return 2
    end
end    

    
#Returns an array of targets of a given state.
#  A state j is containted in getTargets(i) iff transitionProbability(i,j)>0.0.
function getTargets(state)
    targets[state]
end

#passendes Preprocessing
function preprocess_getTargets()
    targets =  Array(Array, 0) 
    #println(targets)
    #gehe alle states durch
    for i = 1:getStateCount()
        push!(targets, Array(Int, 0))
        #gehe alle zielstates durch
        for j = 1:getStateCount()
            if (transitionProbability(i,j) > 0.0)
                #transition gefunden, also in targets reintun
                push!(targets[i], j)
            end
        end
    end                       
    return targets
end

targets = preprocess_getTargets()
tars = getTargets(2)
#println(getTargets(2))  
println(tars)

println("Now start getTargetProbabilities")
        
#         /** Returns array of transition probabilities for outgoing transitions from the
#          *  given state. The returned array is consistent with the result
#          *  of getTargets(i), i.e. getTargetProbabilities(q)[i]
#          *  is the probability if going from state q to state getTargets(q)[i].

function getTargetProbabilities(state)
    targetProbabilities[state]
end

function preprocess_getTargetProbabilities()
    targetProbabilities = Array(Array,0)
    for i = 1:getStateCount()
         targs = getTargets(i)
         push!(targetProbabilities, Array(Float64, length(targs)))
         n = 1
         for j = 1:length(targs)
            targetProbabilities[i][n] = transitionProbability(i,j)
            n += 1
         end    
    end   
    return targetProbabilities
end


println(preprocess_getTargetProbabilities())
targetProbabilities = preprocess_getTargetProbabilities()
println(getTargetProbabilities(2))


println("now start getEmissions")
#                 
#         /** Returns an array of possible emissions of the given state, that is,
#          *  the value z is contained in getEmissions(q) iff
#          *  emissionProbability(q,z)>0.0.


function preprocess_getEmissions()
    emissions = Array(Array, 0)
    for i = 1:getStateCount()
        push!(emissions, Array(Int, 0))
        for e = 1:getEmissionCount()
            if emissionProbability(i,e) > 0.0
                push!(emissions[i], e)
            end
        end
    end
    return emissions
end

function getEmissions(state)
    emissions[state]
end

emissions = preprocess_getEmissions()
println(emissions)
println(getEmission(1))

println("Now start getEmissionProbabilities")

# 
#         /** Returns array of emission probabilities of given state
#          *  The returned array is consistent with the result
#          *  of getEmissions(), i.e. getEmissionProbabilities(q)[i] the
#          *  probability of the emission e = getEmissions(q)[i].
#          */

function preprocess_getEmissionProbabilities()
    emissionProbabilities = Array(Array, 0)
    for i = 1:getStateCount()
        ems = getEmissions(i)
        push!(emissionProbabilities, Array(Float64, length(ems)))
        n = 1
        for e = 1:length(ems)
            emissionProbabilities[i][n] = emissionProbability(i,e)
            n += 1
        end
    end
    return emissionProbabilities
end

function getEmissionProbabilities(state)
    emissionProbabilities[state]
end

emissionProbabilities = preprocess_getEmissionProbabilities()
println(emissionProbabilities)
println(emissionProbabilities[1])
