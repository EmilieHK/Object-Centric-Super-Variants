import Super_Variant_Definition as SVD
import Inter_Lane_Summarization as ILS
import Inter_Lane_Alignment as ILA
import Input_Extraction_Definition as IED

MINIMUM = True


def join_super_variants(super_variant1, super_variant2, allow_nested_structures = True, print_result = True):
    '''
    Determines the lanes of the two Super Variants are are to be merged and performs the summarization of the Super Variants.
    :param super_variant1: A Super Variant that is to be joined with another Super Variant
    :type super_variant1: SuperVariant
    :param super_variant2: The second Super Variant that is joined
    :type super_variant2: SuperVariant
    :param allow_nested_structures: Whether the resulting Super Variant can contain nested structures
    :type allow_nested_structures: bool
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: The generalizing Super Variant
    :rtype: SuperVariant
    '''
    import copy
    mapping12, cost12 = decide_matching(copy.deepcopy(super_variant1), copy.deepcopy(super_variant2), copy.deepcopy(super_variant1.lanes), copy.deepcopy(super_variant2.lanes), True, print_result)
    mapping21, cost21 = decide_matching(copy.deepcopy(super_variant2), copy.deepcopy(super_variant1), copy.deepcopy(super_variant2.lanes), copy.deepcopy(super_variant1.lanes), True, print_result)
    
    if(cost21 < cost12):
        if(print_result):
            print("The estimated cost of joining these Super Variants is " + str(cost21) + ".")

        return inter_variant_summarization(copy.deepcopy(super_variant2), copy.deepcopy(super_variant1), mapping21, allow_nested_structures, print_result), cost21

    else:
        if(print_result):
            print("The estimated cost of joining these Super Variants is " + str(cost12) + ".")

        return inter_variant_summarization(copy.deepcopy(super_variant1), copy.deepcopy(super_variant2), mapping12, allow_nested_structures, print_result), cost12
    
    

def inter_variant_summarization(summarization1, summarization2, mapping, allow_nested_structures, print_result):
    '''
    Summarizes two Super Variants based on a given mapping of the corresponding Super Lanes and aligns the final Super Variant correctly.
    :param summarization1: The first Super Variant of the summarization
    :type summarization1: SuperVariant
    :param summarization2: The second Super Variant of the summarization
    :type summarization2: SuperVariant
    :param mapping: The mapping from Super Lanes in Super Variant 1 to Super Lanes in Super Variant 2
    :type mapping: list
    :param allow_nested_structures: Whether the resulting Super Variant can contain nested structures
    :type allow_nested_structures: bool
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: The summarization of the two Super Variants
    :rtype: SuperVariant
    '''

    import copy
    intermediate_lanes = []
    intermediate_mappings = []

    for pair in mapping:
        if(pair[0] == None):
            if(print_result):
                print("Lane " + str(pair[1]) + " of the Super Variant 2 is made optional.")
            lane2 = [lane for lane in summarization2.lanes if lane.lane_id == pair[1]][0]
            super_lane, mapping = optional_super_lane(summarization2, lane2, False)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

        elif(pair[1] == None):
            if(print_result):
                print("Lane " + str(pair[0]) + " of the Super Variant 1 is made optional.")
            lane1 = [lane for lane in summarization1.lanes if lane.lane_id == pair[0]][0]
            super_lane, mapping = optional_super_lane(summarization1, lane1, True)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

        else:
            if(print_result):
                print("Lane " + str(pair[0]) + " of the Super Variant 1 and lane " + str(pair[1]) + " of Super Variant 2 are merged.")
            lane1 = [lane for lane in summarization1.lanes if lane.lane_id == pair[0]][0]
            lane2 = [lane for lane in summarization2.lanes if lane.lane_id == pair[1]][0]

            super_lane, mapping = join_super_lanes(summarization1, summarization2, lane1, lane2, allow_nested_structures, print_result)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

    result_lanes, result_interaction_points = ILA.__re_align_lanes(copy.deepcopy(intermediate_lanes), ILA.join_interaction_mappings(intermediate_mappings), print_result, False)
    new_id = list(summarization1.id + summarization2.id)
    new_id.sort()
    super_variant = SVD.SuperVariant(tuple(new_id), copy.deepcopy(result_lanes), summarization1.object_types.union(summarization2.object_types), result_interaction_points, summarization1.frequency + summarization2.frequency)
    if(print_result):
        print(super_variant)
    
    super_variant.encode_lexicographically()
    return super_variant


def optional_super_lane(summarization, lane, first):
    '''
    Creates a new normalized lane from the given Super Lane and makes it optional.
    :param summarization: The Super Variant corresponding to the given lane
    :type summarization: SuperVariant
    :param lane: The Super Lane that is made optional
    :type lane: SuperLane
    :param first: Whether the given Super Lane relates to Super Variant 1 of the joining process
    :type first: bool
    :return: The optional equivalence to the lane
    :rtype: OptionalSuperLane
    '''

    new_lane, new_interaction_points_mapping = new_super_lane(summarization, lane, first)

    return SVD.OptionalSuperLane(tuple(lane.lane_id), lane.object_type + " i", new_lane.object_type, new_lane.elements, new_lane.cardinality, new_lane.frequency, new_lane.realizations), new_interaction_points_mapping


def new_super_lane(summarization, lane, first, start_index = 0, outer_position = None, option = 0):
    '''
    Creates a new normalized lane from a given Super Lane and stores the new mappings to the new interaction points
    :param summarization: The Super Variant corresponding to the given lane
    :type summarization: SuperVariant
    :param lane: The Super Lane that is normalized
    :type lane: SuperLane
    :param first: Whether the given Super Lane relates to Super Variant 1 of the joining process
    :type first: bool
    :param start_index: The horizontal start value for the normalized positions
    :type start_index: int
    :return: The normalized equivalence to the lane
    :rtype: SuperLane
    '''
    import copy
    elements = []
    object_type = lane.object_type
    lane_name = lane.lane_name
    lane_id = lane.lane_id
    cardinality = lane.cardinality
    lane_frequency = lane.frequency
    realizations = lane.realizations

    new_interaction_points_mapping = {}
    current_horizontal_index = start_index

    for elem in lane.elements:

        if(isinstance(elem, SVD.CommonConstruct) or isinstance(elem, SVD.InteractionConstruct)):
            activity = elem.activity
            frequency = elem.frequency

            if(outer_position):
                position = copy.deepcopy(outer_position)
                position.set_base_position(IED.BasePosition(option, current_horizontal_index))
            else:
                position = IED.BasePosition(option, current_horizontal_index)

            if(not isinstance(elem, SVD.InteractionConstruct)):
                elements.append(SVD.CommonConstruct(activity, frequency, position, current_horizontal_index))
            else:
                elements.append(SVD.InteractionConstruct(activity, frequency, position, current_horizontal_index))

                current_interaction_points = IED.get_interaction_points(summarization.interaction_points, lane.lane_id, elem.position)
                for current_interaction_point in current_interaction_points:
                    if(first):
                        new_interaction_points_mapping[(0, str([str(position) for position in current_interaction_point.exact_positions]), str(current_interaction_point.interaction_lanes))] = [position]
                    else:
                        new_interaction_points_mapping[(1, str([str(position) for position in current_interaction_point.exact_positions]), str(current_interaction_point.interaction_lanes))] = [position]

            current_horizontal_index += 1
                
        else:          
            new_choices = []
            length = 0

            for i in range(len(elem.choices)):
                index = current_horizontal_index

            if(outer_position):
                new_outer_position = outer_position.add_level(IED.BasePosition(i, current_horizontal_index))
            else:
                new_outer_position = IED.RecursiveLanePosition(option, IED.BasePosition(i, current_horizontal_index))

                new_choice, new_choice_mapping = new_super_lane(summarization, elem.choices[i], first, index, new_outer_position, i)

                for mapping in new_choice_mapping.keys():
                    new_interaction_points_mapping[mapping] = new_choice_mapping[mapping]

                new_choices.append(new_choice)
                if(isinstance(new_choice.elements[0], SVD.CommonConstruct) or isinstance(new_choice.elements[0], SVD.InteractionConstruct)):
                    start_position = new_choice.elements[0].position.get_base_index()
                else:
                    start_position = new_choice.elements[0].position_end.get_base_index()

                if(isinstance(new_choice.elements[-1], SVD.CommonConstruct) or isinstance(new_choice.elements[-1], SVD.InteractionConstruct)):
                    end_position = new_choice.elements[-1].position.get_base_index()
                else:
                    end_position = new_choice.elements[-1].position_end.get_base_index()
                

                length = max(length, end_position - start_position + 1)

            if(isinstance(elem, SVD.ChoiceConstruct)):
                elements.append(SVD.ChoiceConstruct(new_choices, IED.BasePosition(option, current_horizontal_index), IED.BasePosition(option, current_horizontal_index + length-1), current_horizontal_index, current_horizontal_index + length-1))
            else:
                elements.append(SVD.OptionalConstruct(new_choices, IED.BasePosition(option, current_horizontal_index), IED.BasePosition(option, current_horizontal_index + length-1), current_horizontal_index, current_horizontal_index + length-1, elem.empty_frequency))

            current_horizontal_index += length

    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality, lane_frequency, realizations), new_interaction_points_mapping



def join_super_lanes(summarization1, summarization2, lane1, lane2, allow_nested_structures, print_result = True):
    '''
    Summarizes two lanes of two Super Variants.
    :param summarization1: The Super Variant corresponding to the first lane
    :type summarization1: SuperVariant
    :param summarization2: The Super Variant corresponding to the second lane
    :type summarization2: SuperVariant
    :param lane1: The first Super Lane that should be summarized
    :type lane1: SuperLane
    :param lane2: The second Super Lane that should be summarized
    :type lane2: SuperLane
    :param allow_nested_structures: Whether the resulting Super Variant can contain nested structures
    :type allow_nested_structures: bool
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: The summarization of the two Super Lanes
    :rtype: SuperLane
    '''
    object_type = lane1.object_type
    lane_name = lane1.object_type + " i"
    lane_id = (lane1.lane_id, lane2.lane_id)
    frequency = lane1.frequency + lane2.frequency
    if(lane1.cardinality == lane2.cardinality):
        cardinality = lane1.cardinality
    else:
        cardinality = "1..n"

    realizations = lane1.realizations + lane2.realizations
    for i in range(len(realizations)):
        realizations[i].lane_id = i
        realizations[i].lane_name = "realization " + str(i)

    elements, mappings =  ILS.__inter_lane_summarization([lane1, lane2], [summarization1.interaction_points, summarization2.interaction_points], print_result, nested = allow_nested_structures)
    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality, frequency, realizations), mappings



def decide_matching(summarization1, summarization2, remaining_lanes1, remaining_lanes2, propagate = True, print_result = False):
    '''
    Performs a mapping between the lanes of one Super Variant to the lanes of the other Super Variant based on the Levenshtein distance.
    :param summarization1: The Super Variant corresponding to the first set of lanes
    :type summarization1: SuperVariant
    :param summarization2: The Super Variant corresponding to the second set of lanes
    :type summarization2: SuperVariant
    :param remaining_lanes1: The set of Super Lanes of Super Variant 1 that have not yet been mapped
    :type remaining_lanes1: list of type SuperLanea
    :param remaining_lanes2: The set of Super Lanes of Super Variant 2 that have not yet been mapped
    :type remaining_lanes2: list of type SuperLane
    :param propagate: Whether the decision made should be propagated among the interacting lanes
    :type propagate: bool
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: A list containing the decided mappings and the accumulated cost
    :rtype: list, int
    '''
    import math

    # Base case 1: All lanes of summarization1 are matched
    if(len(remaining_lanes1) == 0):
        if(print_result):
            print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes2:
            if(print_result):
                print("Lane " + str(lane.lane_id) + " of Super Variant 2 has no matching partner and is optional.")
            result.append((None, lane.lane_id))
            cost += len(lane.elements)
        return result, cost
    
    # Base case 2: All lanes of summarization2 are matched
    elif(len(remaining_lanes2) == 0):
        if(print_result):
            print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes1:
            if(print_result):
                print("Lane " + str(lane.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            result.append((lane.lane_id, None))
            cost += len(lane.elements)
        return result, cost

    else:
        current_matching_candidate_1 = remaining_lanes1.pop()
        matching_candidates_2 = [lane for lane in remaining_lanes2 if lane.object_type == current_matching_candidate_1.object_type]

        # Fallback case: no corresponding matching
        if(len(matching_candidates_2) == 0):
            
            if(print_result):
                print("Lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            matching = [(current_matching_candidate_1.lane_id, None)]
            cost = len(current_matching_candidate_1.elements)
            new_remaining_lanes2 = remaining_lanes2
            propagation_matching, propagation_cost, new_remaining_lanes1 = propagate_optionality(summarization1, remaining_lanes1, current_matching_candidate_1, print_result)
            least_cost = propagation_cost + cost

        # Otherwise evaluate decision options
        else:
            least_cost = math.inf
            least_cost_matching = []
            least_cost_propagation_matching = []
            least_cost_new_remaining_lanes1 = []
            least_cost_new_remaining_lanes2 = []

            for candidate_2 in matching_candidates_2:
                if(print_result):
                    print("Evaluating the decision of matching lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 with the lane " + str(candidate_2.lane_id) + " of Super Variant 2.")
                intermediate_matching = [(current_matching_candidate_1.lane_id, candidate_2.lane_id)]
                intermediate_cost = levenshtein_distance(current_matching_candidate_1, candidate_2)
                if(isinstance(current_matching_candidate_1, SVD.OptionalSuperLane) and not isinstance(candidate_2, SVD.OptionalSuperLane)):
                    intermediate_cost += len(candidate_2.elements)
                elif(not isinstance(current_matching_candidate_1, SVD.OptionalSuperLane) and isinstance(candidate_2, SVD.OptionalSuperLane)):
                    intermediate_cost += len(current_matching_candidate_1.elements)
                intermediate_remaining_lanes2_now = [lane for lane in remaining_lanes2 if lane.lane_id != candidate_2.lane_id]

                if(propagate):

                    if(print_result):
                        print("Propagating.")

                    # Determine lanes that require immediate propagation for both summarizations
                    interacting_lanes1 = []
                    for interaction_point in summarization1.interaction_points:
                        if (current_matching_candidate_1.lane_id in interaction_point.interaction_lanes):
                            interacting_lanes1.extend(interaction_point.interaction_lanes)
                    interacting_lanes1 = list(set(interacting_lanes1))

                    interacting_lanes2 = []
                    for interaction_point in summarization2.interaction_points:
                        if (candidate_2.lane_id in interaction_point.interaction_lanes):
                            interacting_lanes2.extend(interaction_point.interaction_lanes)
                    interacting_lanes2 = list(set(interacting_lanes2))
                    
                    propagation_lanes1 = [lane for lane in remaining_lanes1 if lane.lane_id in interacting_lanes1]
                    propagation_lanes2 = [lane for lane in intermediate_remaining_lanes2_now if lane.lane_id in interacting_lanes2]

                    # Propagate decision
                    intermediate_propagation_matching, intermediate_propagation_cost, intermediate_remaining_lanes1, intermediate_remaining_lanes2 = propagate_decision(summarization1, summarization2, remaining_lanes1, intermediate_remaining_lanes2_now, propagation_lanes1, propagation_lanes2, print_result = print_result)

                else:
                    if(print_result):
                        print("Not propagating.")
                    intermediate_propagation_matching = []
                    intermediate_propagation_cost = 0 
                    intermediate_remaining_lanes1 = remaining_lanes1
                    intermediate_remaining_lanes2 = intermediate_remaining_lanes2_now

                # Update the best evaluated choice
                if(intermediate_propagation_cost + intermediate_cost < least_cost):
                    if(print_result):
                        print("This is so far the most optimal decision.")
                    least_cost = intermediate_propagation_cost + intermediate_cost
                    least_cost_matching = intermediate_matching
                    least_cost_propagation_matching = intermediate_propagation_matching
                    least_cost_new_remaining_lanes1 = intermediate_remaining_lanes1
                    least_cost_new_remaining_lanes2 = intermediate_remaining_lanes2

            # Determine final decision
            matching = least_cost_matching
            propagation_matching = least_cost_propagation_matching
            new_remaining_lanes1 = least_cost_new_remaining_lanes1
            new_remaining_lanes2 = least_cost_new_remaining_lanes2

        if(print_result):
            print("------------------------------------")

        # Continue matching
        if(len(new_remaining_lanes1) == 0 and len(new_remaining_lanes2) == 0):
            following_matching = []
            following_cost = 0
        else:
            following_matching, following_cost = decide_matching(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2, print_result = print_result)
        return matching + propagation_matching + following_matching, least_cost + following_cost


def propagate_decision(summarization1, summarization2, all_remaining_lanes1, all_remaining_lanes2, current_candidates_lanes1, current_candidates_lanes2, print_result):
    '''
    Propagates a mapping between two Super Lanes among the corresponding interacting lanes and evaluates the propagative cost.
    :param summarization1: The Super Variant corresponding to the first set of lanes
    :type summarization1: SuperVariant
    :param summarization2: The Super Variant corresponding to the second set of lanes
    :type summarization2: SuperVariant
    :param all_remaining_lanes1: The set of Super Lanes of Super Variant 1 that have not yet been mapped
    :type all_remaining_lanes1: list of type SuperLane
    :param all_remaining_lanes2: The set of Super Lanes of Super Variant 2 that have not yet been mapped
    :type all_remaining_lanes2: list of type SuperLane
    :param current_candidates_lanes1: The set of Super Lanes of Super Variant 1 among which the decision is propagation
    :type current_candidates_lanes1: list of type SuperLane
    :param current_candidates_lanes2: The set of Super Lanes of Super Variant 2 among which the decision is propagation
    :type current_candidates_lanes2: list of type SuperLane
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: A list containing the propagated mappings, the propagative cost, the list of remainining non-mapped lanes of Super Variant 1 and 2, respectively
    :rtype: list, int, list, list
    '''
    import copy

    if(print_result):
        print("Propagating the last decision among " + str(current_candidates_lanes1) + " and " + str(current_candidates_lanes2) +".")
    new_remaining_lanes1 = copy.deepcopy(all_remaining_lanes1)
    new_remaining_lanes2 = copy.deepcopy(all_remaining_lanes2)

    matching_result, matching_cost = decide_matching(summarization1, summarization2, current_candidates_lanes1, current_candidates_lanes2, False, print_result)

    # Remove matched lanes from lists
    for pair in matching_result:
        if(pair[0]):
            new_remaining_lanes1 = [lane for lane in new_remaining_lanes1 if lane.lane_id != pair[0]]
        if(pair[1]):
            new_remaining_lanes2 = [lane for lane in new_remaining_lanes2 if lane.lane_id != pair[1]]

    for pair in matching_result:

        if(print_result):
            print("Propagating.")
        # Determine lanes that require immediate propagation for both summarizations
        interacting_lanes1 = []
        for interaction_point in summarization1.interaction_points:
            if (pair[0] and pair[0] in interaction_point.interaction_lanes):
                interacting_lanes1.extend(interaction_point.interaction_lanes)
        interacting_lanes1 = list(set(interacting_lanes1))

        interacting_lanes2 = []
        for interaction_point in summarization2.interaction_points:
            if (pair[1] and pair[1] in interaction_point.interaction_lanes):
                interacting_lanes2.extend(interaction_point.interaction_lanes)
        interacting_lanes2 = list(set(interacting_lanes2))

        propagation_lanes1 = [lane for lane in new_remaining_lanes1 if lane.lane_id in interacting_lanes1]
        propagation_lanes2 = [lane for lane in new_remaining_lanes2 if lane.lane_id in interacting_lanes2]

        propagation_matching, propagation_cost, new_propagation_lanes1, new_propagation_lanes2 = propagate_decision(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2, propagation_lanes1, propagation_lanes2, print_result)
        
        matching_result.extend(propagation_matching)
        matching_cost += propagation_cost
        new_remaining_lanes1 = new_propagation_lanes1
        new_remaining_lanes2 = new_propagation_lanes2        

    return matching_result, matching_cost, new_remaining_lanes1, new_remaining_lanes2


def propagate_optionality(summarization, remaining_lanes, current_candidate, print_result):
    '''
    Propagates the decision of making a Super Lane optional among the interacting lanes.
    :param summarization: The Super Variant among which the optimality of a Super Lane should be propagated
    :type summarization: SuperVariant
    :param all_remaining_lanes: The set of Super Lanes of the Super Variant that have not yet been mapped
    :type all_remaining_lanes: list of type SuperLane
    :param current_candidate: The Super Lane that is made optional
    :type current_candidate: SuperLane
    :param print_result: Whether the results should be output in the console
    :type print_result: bool
    :return: A list containing the propagated mappings, the propagative cost, the list of remainining non-mapped lanes of the Super Variant 
    :rtype: list, int, list
    '''
    import copy 

    # Initialize propagation variables
    propagation_result = []
    propagation_cost = 0

    returned_remaining_lanes = copy.deepcopy(remaining_lanes)

    # Extract all lanes that interact with the current candidate
    interacting_lanes = []
    for interaction_point in summarization.interaction_points:
        if (current_candidate.lane_id in interaction_point.interaction_lanes):
            interacting_lanes.extend(interaction_point.interaction_lanes)
    interacting_lanes = list(set(interacting_lanes))

    propagation_lanes = [lane for lane in remaining_lanes if lane in interacting_lanes]

    while propagation_lanes:
        current_lane = interacting_lanes.pop()
        if(print_result):
            print("Lane " + str(current_lane.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
        propagation_result.append(tuple(current_lane.lane_id, None))
        propagation_cost += len(current_lane.elements)
        returned_remaining_lanes = [lane for lane in returned_remaining_lanes if lane.lane_id != current_lane.lane_id]

        new_interacting_lanes = []
        for interaction_point in summarization.interaction_points:
            if (current_lane.lane_id in interaction_point.interaction_lanes):
                new_interacting_lanes.extend(interaction_point.interaction_lanes)
        new_interacting_lanes = list(set(new_interacting_lanes))

        propagation_lanes.extend([lane for lane in remaining_lanes if lane in new_interacting_lanes])
        propagation_lanes = list(set(propagation_lanes))

    return propagation_result, propagation_cost, returned_remaining_lanes


def levenshtein_distance(lane1, lane2):
    '''
    Computes the Levenshtein distance between two Super Lanes.
    :param lane1: The first Super Lane
    :type lane1: SuperLane
    :param lane1: The second Super Lane
    :type lane1: SuperLane
    :return: The least number of edits needed to convert one realization of the first Super Variant into the a realization of the other Super Variant.
    :rtype: int
    '''
    import math
    realizations1 = lane1.get_valid_realizations()
    realizations2 = lane2.get_valid_realizations()
    minimum = math.inf

    if(len(realizations1) >= len(realizations2)):
        longer_realization_set = realizations1
        shorter_realization_set = realizations2
    else:
        longer_realization_set = realizations2
        shorter_realization_set = realizations1

    distances = dict()
    for realization1 in longer_realization_set:
        distances[(realization1.lane_id, "None")] = len(realization1.elements)

        for realization2 in shorter_realization_set:
            distance = __levenshtein_distance_realizations(realization1.elements, realization2.elements)
            minimum = min(minimum, distance)
            distances[(realization1.lane_id, realization2.lane_id)] = distance

    if(MINIMUM):
        return minimum
    else:

        nodes = []
        nodes.append([realization.lane_id for realization in longer_realization_set])
        nodes.append([realization.lane_id for realization in shorter_realization_set])
        nodes.append(["None"])

        cost = find_best_matching(nodes, distances)

    return cost


def find_best_matching(nodes, arcs):
    '''
    Computes an optimal matching in a graph with the given limited arcs and nodes.
    that interaction points between multiple lanes have the same horizontal index
    :param nodes: The set of nodes
    :type nodes: list
    :param arcs: The arcs of the matching
    :type arcs: dict
    :return: The list of node pairs that have been matched
    :rtype: list
    '''
    import gurobipy
    model = gurobipy.Model("limitedMatching")
    
    x = {}
    for key in arcs.keys():
        x[key] = model.addVar(name="x_%s, %s" % (key[0], key[1]), vtype = gurobipy.GRB.BINARY)

    model.update()

    for i in range(len(nodes[0])):
        i_keys = []
        for key in x.keys():
            if(nodes[0][i] == key[0]):
                i_keys.append(key)

        model.addConstr(sum(x[key] for key in i_keys) == 1)

    for i in range(len(nodes[1])):
        i_keys = []
        for key in x.keys():
            if(nodes[1][i] == key[1]):
                i_keys.append(key)

        model.addConstr(sum(x[key] for key in i_keys) == 1)

    
    model.setObjective(sum(x[key] * arcs[key] for key in x.keys()))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    cost = 0
    
    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    for key in arcs.keys():
        print(str(key) + ": " + str(x[key].X))
        if(x[key].X == 1.0 and key[1] != "None"):
            cost += arcs[key]
    print("-----------------------------")
    return cost


def __levenshtein_distance_realizations(lane1, lane2):
    '''
    Computes the Levenshtein distance between two realizations of Super Lanes.
    :param lane1: The elements of the first realization, contains only CommonConstructs
    :type lane1: list of type CommonConstruct
    :param lane1: The elements of the second realization, contains only CommonConstructs
    :type lane1: list of type CommonConstruct
    :return: The number of edits needed to convert one realization into the other.
    :rtype: int
    '''
    if(len(lane2) == 0):
        return len(lane1)
    elif(len(lane1) == 0):
        return len(lane2)
    elif(type(lane1[0]) == type(lane2[0]) and lane1[0].activity == lane2[0].activity):
        return __levenshtein_distance_realizations(lane1[1:],lane2[1:])
    else:
        return 1 + min(__levenshtein_distance_realizations(lane1[1:],lane2[1:]), __levenshtein_distance_realizations(lane1,lane2[1:]),__levenshtein_distance_realizations(lane1[1:],lane2))
