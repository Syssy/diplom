#using PyPlot

println("Hello World!") 

function updateDistributions!(ps::Float32, pm::Float32, rps, rpm, index)
    #println("do something")
    rs1 = Array(Float32, length(rps))
    rs1 = rps * ps
    rs2 = rpm * (1.0f0-pm)
    unshift!(rs2, 0.0f0)
    push!(rs1, 0.0f0)
        
    rm1 = rps * (1.0f0-ps)
    rm2 = rpm * pm
    unshift!(rm2, 0.0f0)
    push!(rm1, 0.0f0)
        
        #rpm = (push!(rps*(1-ps), 0.0f0)) + (unshift!((rpm*pm), 0.0f0))
    
        #rps = push!(rs1, 0.0f0) + unshift!(rs2, 0.0f0)
        
    rps = rs1 + rs2
    rpm = rm1 + rm2
        
        #zu kleine Werte am Anfang rausschmeissen, damit das array nicht zu gross wird
        #TODO sinnvoller wert?
        #println("rps vorher ", rps)
        #println("rpm vorher ", rpm)
    if (rps[1] < 1.0f-20)  & (rpm[1] < 1.0f-20)
        index += 1
        shift!(rps)
        shift!(rpm)
    end

        #println(rps, rpm)
        #gleiches fuer das Ende
        #TODO ebenfalls ueberpruefen
    if (rps[end] < 1.0f-20) & (rpm[end] < 1.0f-20)
        pop!(rps)
        pop!(rpm)
    end
    return rps, rpm, index        
end


function waitingTimeForValue(ps::Float32, pm::Float32, value, maxTime)
    println("los")
    #result::Vector{Float32}
    #println(result, typeof(result))
    result = zeros(Float32, 1)
    rps = zeros(Float32, 1)
    rpm = ones(Float32, 1)
    #rs1:: Vector{Float32}
    
    #println(result, typeof(result))
    
    index = 1
    
    for i = 1:maxTime
        if !(value>index)
            break
        end
        
        rps, rpm, index = updateDistributions!(ps, pm, rps, rpm, index)
        #println("rps ", rps)
        #println("rpm ", rpm)
        #print("value ", value, " index ", index)        
        if (length(rpm) > value-index)
            #println(" rps ", rps[value-index+1], " rpm ", rpm[value-index+1], " length ", length(rpm))
            push!(result, (rps[value-index+1]+rpm[value-index+1]))
            rpm[value-index+1] = 0
            rps[value-index+1] = 0
        else
            push!(result, 0.0f0)
            #println("FAlse")
        end
        #println("result ", result)
    end
    #println(result)
    return result
end

@time(waitingTimeForValue(0.99f0, 0.99f0, 100, 500))
#res = waitingTimeForValue(0.99f0, 0.99f0, 10000, 50000)
#println(res)
println("ende")
# 
# function myPAA(ps::Float32, pm::Float32, len::Int64)
#     rps = zeros(Float32, 1)
#     rpm = ones(Float32, 1)
# 
#     index = 1
# 
#     for i = 1:len
#         rs1 = rps * ps
#         rs2 = rpm * (1-pm)
#         unshift!(rs2, 0.0f0)
#         push!(rs1, 0.0f0)
#         
#         rm1 = rps * (1-ps)
#         rm2 = rpm * pm
#         unshift!(rm2, 0.0f0)
#         push!(rm1, 0.0f0)
#         
#         rpm = (push!(rps*(1-ps), 0.0f0)) + (unshift!((rpm*pm), 0.0f0))
#         
#         
#         rps = rs1 + rs2
#         #rpm = rm1 + rm2
#         
#         #zu kleine Werte am Anfang rausschmeissen, damit das array nicht zu gross wird
#         #TODO sinnvoller wert?
#         if (rps[1] < 1.0f-20)  & (rpm[1] < 1.0f-20)
#             index += 1
#             shift!(rps)
#             shift!(rpm)
#         end
#         #println(rps, rpm)
#         #gleiches fuer das Ende
#         #TODO ebenfalls ueberpruefen
#         if (rps[end] < 1.0f-20) & (rpm[end] < 1.0f-20)
#             pop!(rps)
#             pop!(rpm)
#         end
#         
#     end
# 
#     println("laengen ", length(rps), " ", length(rpm))
# 
#     println("verschiebung um ", index)
# 
#     println("Summe ", sum(rps+rpm))
#     
#     println(typeof(rpm[1]))
# 
#     return(unshift!((rpm+rps), index*0))
#     
# end
# 
# 
# #result = myPAA(0.9f0, 0.9f0, 200)   
# #println (result)
# #plot(result)    
# 
#     
# 
# function emissionProbability(state, emission)
#     # Mobil(2) hat immer em 1 und stat(1) hat immer em 0
#     if state == (emission)
#         return 1.0
#     else
#         return 0.0
#     end
# end
# 
# function getEmissionCount()
#     # Emissionen sind 0 oder 1
#     return 2
# end
# 
# function getStartState()
#     # Mobil = 2
#     return 2
# end
# 
# function getStartValue()
#     #starte bei null
#     return 1
# end
# 
# function getStateCount()
#     # States sind 1 = stat und 2 = mob
#     return 2
# end    
# 
# function getValueCount()
#     # Laenge der Saeule
#     return 102
# end
# 
# function performOperation(state, value, emission)
#     # Gehe immer einen vorwaerts, ausser schon im ziel
#     if (value + emission < getValueCount() -1)
#         return value + emission
#     else
#         return value
#     end
# end    
#        
# function transitionProbability(state, targetState)
#     # festlegung der w'keiten fuer ps und pm. nutze gegenw'keit fuer selbstuebergang
#     ps = 0.09
#     pm = 0.02
#     p = 0.0
#     if state == 1
#         p = ps
#     elseif state == 2
#         p = pm
#     else
#         p = 0.0
#     end
#     if (state == targetState)
#         return p
#     else 
#         return 1-p
#     end
# end
# 
# function getEmission(state)
#     # in stat (1) emission 0 und sonst (mobil,2) em 1
#     if (state == 1)
#         return 1
#     else
#         return 2
#     end
# end    
# 
#     
# #Returns an array of targets of a given state.
# #  A state j is containted in getTargets(i) iff transitionProbability(i,j)>0.0.
# function getTargets(state)
#     targets[state]
# end
# 
# #passendes Preprocessing
# function preprocess_getTargets()
#     targets =  Array(Array, 0) 
#     #println(targets)
#     #gehe alle states durch
#     for i = 1:getStateCount()
#         push!(targets, Array(Int, 0))
#         #gehe alle zielstates durch
#         for j = 1:getStateCount()
#             if (transitionProbability(i,j) > 0.0)
#                 #transition gefunden, also in targets reintun
#                 push!(targets[i], j)
#             end
#         end
#     end                       
#     return targets
# end
# 
# targets = preprocess_getTargets()
# tars = getTargets(2)
# #println(getTargets(2))  
# println(tars)
# 
# println("Now start getTargetProbabilities")
#         
# #         /** Returns array of transition probabilities for outgoing transitions from the
# #          *  given state. The returned array is consistent with the result
# #          *  of getTargets(i), i.e. getTargetProbabilities(q)[i]
# #          *  is the probability if going from state q to state getTargets(q)[i].
# 
# function getTargetProbabilities(state)
#     targetProbabilities[state]
# end
# 
# function preprocess_getTargetProbabilities()
#     targetProbabilities = Array(Array,0)
#     for i = 1:getStateCount()
#          targs = getTargets(i)
#          push!(targetProbabilities, Array(Float64, length(targs)))
#          n = 1
#          for j = 1:length(targs)
#             targetProbabilities[i][n] = transitionProbability(i,j)
#             n += 1
#          end    
#     end   
#     return targetProbabilities
# end
# 
# 
# println(preprocess_getTargetProbabilities())
# targetProbabilities = preprocess_getTargetProbabilities()
# println(getTargetProbabilities(2))
# 
# 
# println("now start getEmissions")
# #                 
# #         /** Returns an array of possible emissions of the given state, that is,
# #          *  the value z is contained in getEmissions(q) iff
# #          *  emissionProbability(q,z)>0.0.
# 
# 
# function preprocess_getEmissions()
#     emissions = Array(Array, 0)
#     for i = 1:getStateCount()
#         push!(emissions, Array(Int, 0))
#         for e = 1:getEmissionCount()
#             if emissionProbability(i,e) > 0.0
#                 push!(emissions[i], e)
#             end
#         end
#     end
#     return emissions
# end
# 
# function getEmissions(state)
#     emissions[state]
# end
# 
# emissions = preprocess_getEmissions()
# println(emissions)
# println(getEmission(1))
# 
# println("Now start getEmissionProbabilities")
# 
# # 
# #         /** Returns array of emission probabilities of given state
# #          *  The returned array is consistent with the result
# #          *  of getEmissions(), i.e. getEmissionProbabilities(q)[i] the
# #          *  probability of the emission e = getEmissions(q)[i].
# #          */
# 
# function preprocess_getEmissionProbabilities()
#     emissionProbabilities = Array(Array, 0)
#     for i = 1:getStateCount()
#         ems = getEmissions(i)
#         push!(emissionProbabilities, Array(Float64, length(ems)))
#         n = 1
#         for e = 1:length(ems)
#             emissionProbabilities[i][n] = emissionProbability(i,e)
#             n += 1
#         end
#     end
#     return emissionProbabilities
# end
# 
# function getEmissionProbabilities(state)
#     emissionProbabilities[state]
# end
# 
# emissionProbabilities = preprocess_getEmissionProbabilities()
# println(emissionProbabilities)
# println(emissionProbabilities[1])
# 
# #         /** Returns the joint distribution of state and value at time 0, that is,
# #          *  before any state transition has been done. By default this is the
# #          *  Dirac distribution assigning probability one to start state and
# #          *  start value. This methods might be overwritten by deriving classes to
# #          *  change this behaviour, e.g. to start from an equilibrium distribution.
# #          */
# #          //needed
# #         public double[][] stateValueStartDistribution() {
# #                 double[][] result = new double[getStateCount()][getValueCount()];
# #                 result[getStartState()][getStartValue()] = 1.0;
# #                 return result;
# #         }
# 
# println("now start stateValueStartDistribution")
# 
# # TODO: Die Dist wird schon sehr gross, hier besser schon sparse matrix verwenden
# function stateValueStartDistribution()
#     dist = Array(Array, 0)
#     for i = 1:getStateCount()
#         println( " state ", i)
#         push!(dist, zeros(getValueCount()))
#     end
#     dist[getStartState()][getStartValue()] = 1.0
#     return dist
# end
# 
# println(stateValueStartDistribution())
