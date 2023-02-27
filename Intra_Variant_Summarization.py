import Super_Variant_Definition as SVD
import Inter_Lane_Summarization as ILS
import Inter_Lane_Alignment as ILA

def get_candidates(lanes, interactions):
    '''
    Yields all maximal merging candidate sets for a set of lanes, thus, all sets of lanes that share all interactions with other lanes.
    :param lanes: The lanes of the variant
    :type lanes: list of type VariantLane
    :param interactions: The interactions of the variant
    :type interactions: list of type InteractionPoint
    :return: A list of sets of lanes that can be merged
    :rtype: list
    '''
    result = []
    
    for lane1 in lanes:
        candidate_set = {lane1}
        candidate_interactions = []
        for interaction in interactions:
            if (lane1.lane_id in interaction.interaction_lanes):
                candidate_interactions.extend(interaction.interaction_lanes)
                
        for lane2 in lanes:
            if (lane1 != lane2 and lane1.object_type == lane2.object_type):
                comparison_interactions = []
                for interaction in interactions:
                     if (lane2.lane_id in interaction.interaction_lanes):
                        comparison_interactions.extend(interaction.interaction_lanes)
                if (set(candidate_interactions) == set(comparison_interactions)):
                    candidate_set.add(lane2)
        
        if(candidate_set not in result):
            result.append(candidate_set)
        
    return result

def __branch_on_candidates(variant, remaining_candidates, init_summarization, level, print_results):
    '''
    Visits one node in the candidate tree, summarizes the current merging candidate and recurses on the subtrees.
    :param variant: The variant to be summarized
    :type variant: ExtractedVariant
    :param remaining_candidates: The merging candidates that have not yet been merged
    :type remaining_candidates: list
    :param init_summarization: Stores the current state of the within-variant summarization, namely the summarized lanes thus far and the corresponding mappings of interaction points
    :type init_summarization: dict
    :param level: The current depth in the tree
    :type level: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The summarization of the current candidate joined with the results from the child nodes
    :rtype: list
    '''
    import copy
    current_summarization = copy.deepcopy(init_summarization)
    new_lanes = []
    new_mappings = []
    if(print_results):
        print("------------------------------------------")
        print("Current Level: " + str(level))
    for partition in current_summarization["Candidate"]:
        if(print_results):
            print("----")
            print("Summarizing Lanes: " + str([lane.lane_id for lane in partition]))

        object_type = partition[0].object_type
        lane_name = partition[0].object_type + " i"
        lane_id = tuple([lane.lane_id for lane in partition])
        cardinality = "1"
        if len(partition) > 1:
            cardinality = "n"
        elements, new_intermediate_mappings = ILS.__inter_lane_summarization([lane.to_super_lane(variant.interaction_points) for lane in partition], [variant.interaction_points for lane in partition], print_results = print_results, intra = True, nested = False)
        
        realizations = []
        for i in range(len(partition)):
            realizations.extend(partition[i].to_super_lane(variant.interaction_points).realizations)
            
        for i in range(len(realizations)):
            realizations[i].lane_name = "realization " + str(i)
            realizations[i].lane_id = i

        super_lane = SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality, len(partition), realizations)
        
        new_lanes.append(super_lane)
        new_mappings.append((super_lane.lane_id, new_intermediate_mappings))

    # Check for redundancies
        for i in range(len(new_lanes)):
            for j in range(i+1, len(new_lanes)):
                summary1 = new_lanes[i]
                summary2 = new_lanes[j]
                if(summary1.same_summarization(summary2) or summary1.subsumed_summarization(summary2)):
                    if(print_results):
                        print("----")
                        print("Redundancy found, pruning subtree!")
                        print("\n")
                    return None

    current_summarization["Lanes"].extend(new_lanes)
    current_summarization["Mappings"].extend(new_mappings)

    # Recursive call
    if (len(remaining_candidates) == 0):
        if(print_results):
            print("----")
            print("Leaf node reached!")
            print("\n")
        return [current_summarization]

    else:
        result = []
        for candidate in get_partitions(remaining_candidates[0]):
            current_summarization["Candidate"] = candidate
            subtree_result = __branch_on_candidates(variant, remaining_candidates[1:], (current_summarization), level+1, print_results)
            if(subtree_result != None):
                result.extend(subtree_result)
        if(print_results):
            print("\n")
        return result


def within_variant_summarization(variant, print_results = False):
    '''
    Yields all unique valid summarizations of a given variant.
    :param variant: The variant that is to be generalized
    :type variant: ExtractedVariant
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: A list of all unique valid summarizations of the variant
    :rtype: list of type SummarizedLane
    '''

    # Initialize candidate parameters 
    all_candidates = get_candidates(variant.lanes, variant.interaction_points)
    first_choice =  get_partitions(all_candidates[0])
    all_summarizations = []
    init_summary = {}
    init_summary["Lanes"] = []
    init_summary["Mappings"] = []

    # Traverse tree of candidates
    for partition in first_choice:
        init_summary["Candidate"] = partition
        subtree_result = __branch_on_candidates(variant, all_candidates[1:], init_summary, 1, print_results)
        if(subtree_result != None):
            all_summarizations.extend(subtree_result)

    # Re-align summarizations
    result = []
    for summarization in all_summarizations:

        result_lanes, result_interaction_points = ILA.__re_align_lanes(summarization["Lanes"], ILA.join_interaction_mappings(summarization["Mappings"]), print_results)
        result.append(SVD.SummarizedVariant(result_lanes, variant.object_types, result_interaction_points, variant.frequency))
        result[-1].encode_lexicographically()

        if(print_results):
            print(result[-1])
            print("-------------------")

    return result


def __partition(set):
    '''
    Computes all partitions of a set.
    :param set: The list of elements in the set
    :type set: list
    :return: All partitions of the initial set
    :rtype: list 
    '''
    if len(set) == 1:
        yield [set]
        return

    first = set[0]
    for recursive_partition in __partition(set[1:]):
        for n, subset in enumerate(recursive_partition):
            yield recursive_partition[:n] + [[first] + subset]  + recursive_partition[n+1:]
        yield [[first]] + recursive_partition


def get_partitions(candidate):
    '''
    Extracts all partitions of a candidate set.
    :param candidate: The candidate set
    :type candidate: list
    :return: A list of all partitions of the candidate
    :rtype: list 
    '''
    partitions = []
    for n, partition in enumerate(__partition(list(candidate)), 1):
        partitions.append(partition)
    partitions.reverse()
    return partitions