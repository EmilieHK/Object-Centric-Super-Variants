import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED

ALIGN = True

def join_interaction_mappings(interaction_mappings):
    '''
    Performs a series of pre-processing steps to the multiple interaction mappings necessary for later alignment.
    :param interaction_mappings: A list of the various interaction_mappings for each super lane
    :type interaction_mappings: list of type dict
    :return: A dictionary with each entry corresponding to a unified Interaction Point
    :rtype: dict
    '''
    return __split_interaction_mappings(__merge_interactions(__merge_interaction_mappings(interaction_mappings)))


def get_preliminary_interaction_points(mappings, lanes):
    '''
    Extracts the list of preliminary InteractionPoints from a given mapping and the corresponding Super Lanes.
    :param mappings: A dictionary with each entry corresponding to a unified Interaction Point
    :type mappings: dict
    :param lanes: The summarized lanes of the Super Variant
    :type lanes: list of type SuperLane
    :return: The list of preliminary interactions of the un-aligned lanes
    :rtype: list of type InteractionPoint
    '''

    interaction_points = []
    for mapping in mappings.keys():

        types = set([lane.object_type for lane in lanes if lane.lane_id in mappings[mapping].keys()])
        first_key = list(mappings[mapping].keys())[0]
        element = [lane for lane in lanes if lane.lane_id == first_key][0].get_element(mappings[mapping][first_key])
        activity_label = element.activity

        interaction_point = IED.InteractionPoint(activity_label, list(mappings[mapping].keys()), types, None, list(mappings[mapping].values()))
        interaction_points.append(interaction_point)

    return interaction_points


def __merge_interactions(merged_interactions):
    '''
    Merges the interaction point mappings that are at the same position in the final Super Lane.
    :param merged_interactions: The combined mappings of original interaction points to new indices in the summarized lanes
    :type merged_interactions: dict
    :return: Each interaction point of the final Super Lanes and their current positions in the involved lanes, merged by position
    :rtype: dict
    '''
    result_interactions = dict()
    for key1 in merged_interactions.keys():
        exists = False
        for key2 in result_interactions.keys():
            if (merged_interactions[key1] == result_interactions[key2]):
                exists = True
        if(not exists):
            result_interactions[key1] = merged_interactions[key1]

    return result_interactions

def __merge_interaction_mappings(mappings):
    '''
    Pre-processes the mappings from the summarization for later alignment by merging the mappings for each Super Lane.
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane in the Super Variant
    :type mappings: list of type dict
    :return: Each interaction point of the final Super Lanes and their current positions in the involved lanes
    :rtype: dict
    '''
    merged_mappings = {}
    # merge the individual dictionaries for all lanes
    for i in range(len(mappings)):
        mapping = mappings[i][1]
        for key in mapping.keys():
            positions = {}
            positions[mappings[i][0]] = mappings[i][1][key]
            for k in range(i+1, len(mappings)):
                if(key in list(mappings[k][1].keys())):
                    positions[mappings[k][0]] = mappings[k][1][key]
            if(len(positions.keys()) > 1 and key not in merged_mappings.keys()):
                merged_mappings[key] = positions
    
    return merged_mappings

def __split_interaction_mappings(mappings):
    '''
    Extracts every interaction point based on all combinations of mapped positions.
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane in the Super Variant
    :type mappings: dict 
    :return: Each interaction point of the final Super Lanes and their current positions in the involved lanes
    :rtype: dict
    '''
    import itertools
    new_mappings = dict()

    for interaction in mappings.keys():
        positions = []
        for id in mappings[interaction].keys():
            id_positions = []
            for position in mappings[interaction][id]:
                id_positions.append((id, position))
            positions.append(id_positions)
        
        combinations = list(itertools.product(*positions))
        for i in range(len(combinations)):
            new_positions = dict()
            for item in combinations[i]:
                new_positions[item[0]] = item[1]
            new_mappings[(interaction[0], str(interaction[1]) + " " + str(i))] = new_positions

    #return __combine_interactions(new_mappings)
    return new_mappings


def __combine_interactions(mappings):
    '''
    Combines interaction points that share at least one common activity.
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane in the Super Variant
    :type mappings: dict 
    :return: Each combined interaction point of the final Super Lanes and their current positions in the involved lanes
    :rtype: dict
    '''
    new_mappings = dict()
    added_keys = []
    
    for interaction in mappings.keys():
        share_elements = dict()
        share_elements[interaction] = mappings[interaction]

        for other_interaction in mappings.keys():
            if(other_interaction != interaction):

                for lane in mappings[interaction]:
                    if(lane in mappings[other_interaction].keys()):
                        if(mappings[other_interaction][lane] == mappings[interaction][lane]):
                            share_elements[other_interaction] = mappings[other_interaction]
                            break
        if(len(share_elements) == 1):
            new_mappings[interaction] = mappings[interaction]
            added_keys.append(interaction)

        else:
            if(not interaction in added_keys):
                positions = dict()

                for key in share_elements.keys():
                    added_keys.append(key)

                    for lane in share_elements[key]:
                        positions[lane] = share_elements[key][lane]
                
                new_mappings[interaction] = positions

    return new_mappings


def __re_align_lanes(lanes, mappings, print_result, intra = True):
    '''
    Given the summarized Super Lanes and the mappings from original interaction points to new indices, the lanes are aligned according to the interaction points.
    :param lanes: The summarized lanes of the Super Variant
    :type lanes: list of type SuperLane
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane
    :type mappings: dict
    :param print_result: Whether or not the print commands should be executed
    :type print_result: bool
    :return: The Super Lanes with updated horizontal indices and a list of the corresponding interaction points
    :rtype: list of type SuperLane, list of type InteractionPoint
    '''
    # Initialize variables and return values
    import copy
    import math
    #updated_mappings, aligned_lanes = create_duplicate_interactions(copy.deepcopy(mappings), copy.deepcopy(lanes))
    
    updated_mappings, aligned_lanes = copy.deepcopy(mappings), copy.deepcopy(lanes)

    updated_interaction_points = []

    fixed_positions = dict()
    for lane in aligned_lanes:
        fixed_positions[lane.lane_id] = []

    # Align the lanes such that the interaction points have the same horizontal index
    for i in range(len(mappings.keys())):

        earliest_interaction_point = min(updated_mappings.items(), key=lambda x: tuple([position.get_base_index() for position in x[1].values()]))
        relevant_lanes = [copy.deepcopy(l) for l in aligned_lanes if l.lane_id in list(earliest_interaction_point[1].keys())]

        if(print_result):
            print("We have an interaction at the following positions in the interacting lanes:")
            for key in earliest_interaction_point[1].keys():
                print(str(key) + ": " + str(earliest_interaction_point[1][key]))
        
        types = set([l.object_type for l in relevant_lanes])
        element = relevant_lanes[0].get_element(updated_mappings[earliest_interaction_point[0]][relevant_lanes[0].lane_id])
        activity_label = element.activity

        all_positions = list(earliest_interaction_point[1].values())

        if(len(set([value.get_base_index() for value in all_positions])) == 1):
            if(print_result):
                print("No alignment required.")
            position = all_positions[0]
            index = position.get_base_index()
            interacting_lanes = list(earliest_interaction_point[1].keys())
            exact_positions = list(earliest_interaction_point[1].values())

            for lane in relevant_lanes:
                fixed_positions[lane.lane_id].append(str(earliest_interaction_point[1][lane.lane_id]))
                    
        else: 
            target_position = max(all_positions, key = lambda x: x.get_base_index())
            position = target_position
            index = position.get_base_index()

            interacting_lanes = []
            exact_positions = []
            shifted_lanes = []
            
            for lane in relevant_lanes:

                # Shift indices by the offset
                current_position = updated_mappings[earliest_interaction_point[0]][lane.lane_id]
                offset = target_position.get_base_index() - current_position.get_base_index()


                if(offset == 0 or (not ALIGN and not intra)):
                    interacting_lanes.append(lane.lane_id)
                    exact_positions.append(current_position)
                    fixed_positions[lane.lane_id].append(str(current_position))

                else:

                    updated_positions = dict()

                    for key in updated_mappings.keys():
                        if(lane.lane_id in updated_mappings[key].keys()):
                            updated_positions[str(updated_mappings[key][lane.lane_id])] = updated_mappings[key][lane.lane_id]

                    old_positions = copy.deepcopy(updated_positions)

                    updated_positions, new_lane = copy.deepcopy(lane).shift_lane_exact(current_position, offset, copy.deepcopy(updated_positions), current_position)
                    interacting_lanes.append(lane.lane_id)

                    shift_allowed = True
                    for position in fixed_positions[lane.lane_id]:
                        if(position in old_positions.keys() and position in updated_positions.keys()):
                            if(position != str(updated_positions[position])):
                                shift_allowed = False
                                break

                    if(shift_allowed):
                        exact_positions.append(updated_positions[str(current_position)])
                        fixed_positions[lane.lane_id].append(str(updated_positions[str(current_position)]))

                        if(print_result):
                            print("We have shifted lane " + new_lane.lane_name + " by " + str(offset) + " starting from the element at the position " + str(current_position) + ".")

                        # Update all values in the dictionary accordingly
                        for key in updated_mappings.keys():
                            if(new_lane.lane_id in updated_mappings[key].keys()):
                                updated_mappings[key][new_lane.lane_id] = copy.deepcopy(updated_positions[str(updated_mappings[key][new_lane.lane_id])])

                        for interaction_point in updated_interaction_points:
                            for i in range(len(interaction_point.interaction_lanes)):
                                if(i in range(len(interaction_point.exact_positions))):
                                    if (interaction_point.interaction_lanes[i] == lane.lane_id and str(interaction_point.exact_positions[i]) in updated_positions.keys()):
                                        interaction_point.exact_positions[i] = updated_positions[str(interaction_point.exact_positions[i])]
                            
                        shifted_lanes.append(new_lane)
                    else:
                        if(print_result):
                            print("The lane " + new_lane.lane_name + " could not be shifted without influencing an already aligned interaction point.")

                        exact_positions.append(current_position)
                        shifted_lanes.append(lane)

      
        del updated_mappings[earliest_interaction_point[0]]
        updated_interaction_points.append(IED.InteractionPoint(activity_label, interacting_lanes, types, index, exact_positions))
        
        new_aligned_lanes = copy.deepcopy(aligned_lanes)
        for j in range(len(aligned_lanes)):
            for k in range(len(shifted_lanes)):
                if(aligned_lanes[j].lane_id == shifted_lanes[k].lane_id):
                    new_aligned_lanes[j] = copy.deepcopy(shifted_lanes[k])

        aligned_lanes = new_aligned_lanes
        
    final_lanes = []
    for lane in aligned_lanes:
        final_lanes.append(copy.deepcopy(lane).shift_activities_up())

    return final_lanes, updated_interaction_points



# TODO Finish implementation, used to create Interaction Point duplicates
def create_duplicate_interaction(mappings, lanes):

    import copy
    new_mappings = copy.deepcopy(mappings)
    duplicates = []

    for i in range(len(list(mappings.keys()))):
        mapping1 = list(mappings.keys())[i]
        duplicate_mappings = dict()
        lane_id = 0

        # Find the sets of interaction points that map to the same positions in one lane
        for key1 in mappings[mapping1].keys():
            position1 = mappings[mapping1][key1]

            for j in range(i+1,len(list(mappings.keys()))):
                mapping2 = list(mappings.keys())[j]

                for key2 in mappings[mapping2].keys():
                    position2 = mappings[mapping2][key2]

                    if(key1 == key2 and position1 == position2):
                         del new_mappings[mapping1]
                         del new_mappings[mapping2]
                         duplicate_mappings[mapping1] = mappings[mapping1]
                         duplicate_mappings[mapping2] = mappings[mapping2]
                         lane_id = key1

        if (len(duplicate_mappings)):
            duplicates.append((duplicate_mappings, lane_id))
    
    new_lanes = []

    # For each set of interaction points sharing the same positions in one lane, but not in another lane, split the element at the shared position such that every interaction point can be aligned with one copy
    for duplicate in duplicates:

        # Determine the element that requires duplication and create a modified copy of the lane with that element being optional
        earliest_interaction_point = min(duplicate[0].items(), key=lambda x: min([position.get_base_index() for position in x[1].values()]))
        del duplicate[0][earliest_interaction_point[0]]
        for lane in lanes:
            if (lane.lane_id == duplicate[1]):
                position = earliest_interaction_point[1][duplicate[1]]
                original_element = lane.get_element(position)
                empty_frequency = original_element.frequency - (original_element.frequency / (len(duplicate[0]) + 1))
                new_lane, new_element = copy.deepcopy(lane).make_optional(position, empty_frequency)
                new_mappings[earliest_interaction_point[0]] = earliest_interaction_point[1]
                break
 
        # Create a duplicate of the element for each other interaction and find a suitable position
        for i in range(len(duplicate[0])):

            current_interaction_point = min(duplicate[0].items(), key=lambda x: min([position.get_base_index() for position in x[1].values()]))
            del duplicate[0][current_interaction_point[0]]

            # Default position is directly with the original element
            suitable_position = copy.deepcopy(new_element).position_end.apply_shift(1)
            watchlist = list(current_interaction_point[1].keys())
            observed_interactions = dict()

            # For every other interaction in that lane, check whether its position is after the lower_bound 
            for key in mappings.keys():
                if(key != earliest_interaction_point[0] and key != current_interaction_point[0]):
                    if(duplicate[1] in mappings[key].keys() and new_lane.greater_than(suitable_position, mappings[key][duplicate[1]])):

                        #observed_interactions[key] = 

                        # For the counterparts of such an interaction position in the relevant lanes, check whether they are happening before or after the current investigated interaction
                        for lane_id in mappings[key].keys():
                            if(lane_id != duplicate[1] and lane_id in watchlist):
                                
                                if(lane_id in [lane.lane_id for lane in new_lanes]):
                                    current_lane = [lane.lane_id for lane in new_lanes if lane.lane_id == lane_id][0]
                                else:
                                    current_lane = [lane.lane_id for lane in lanes if lane.lane_id == lane_id][0]

                                changes_position = current_lane.greater_than(earliest_interaction_point[1][lane_id], mappings[key][lane_id])

                                if(not changes_position):
                                    watchlist = [id for id in watchlist if id != lane_id]

                                else:
                                    print("Update suitable position")
                                    #TODO
                                    #if(mappings[key][key2][1] < current_interaction_point[1][key2][1]):
                                    #lower_bound = max(mappings[key][duplicate[1]][1] + 1, lower_bound)

            # Update all mappings due to the shift of element positions
            new_mappings[current_interaction_point[0]] = current_interaction_point[1]
            new_mappings[current_interaction_point[0]][duplicate[1]] = suitable_position
            new_lane = new_lane.add_optional_activity(suitable_position, copy.deepcopy(new_element))
            
            #TODO update mappings
            #for key in new_mappings.keys():
                #if(key != earliest_interaction_point[0] and key != current_interaction_point[0]):
                    #if(duplicate[1] in mappings[key].keys() and mappings[key][duplicate[1]][1] > lower_bound):
                        #old_position = new_mappings[key][duplicate[1]]
                        #new_mappings[key][duplicate[1]] = (old_position[0], old_position[1]+1)
                        
        new_lanes.append(new_lane)
        

    # Append the remaining lanes that required no modification
    for lane in lanes:
        if (lane.lane_id not in [new_lane.lane_id for new_lane in new_lanes]):
            new_lanes.append(lane)

    return new_mappings, new_lanes


