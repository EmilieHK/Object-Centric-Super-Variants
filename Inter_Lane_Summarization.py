import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED

def __inter_lane_summarization(lanes, interactions, print_results, current_lane = 0, offset = 0, intra = False, nested = False):
    '''
    Performs the summarization of the given Super Lanes using the set of defined patterns.
    :param lanes: The Super Lanes that should be summarized
    :type lanes: list of type SuperLane
    :param interactions: The sets of interaction points corresponding to the involved Super Lanes
    :type interactions: list
    :param current_lane: The lane number that is currently summarized (default 0, otherwise the number of choice this lane represents)
    :type current_lane: int
    :param print_results: Whether the results should be output in the console
    :type print_results: bool
    :param offset: The starting index of the horizontal positions
    :type offset: int
    :param intra: Whether the all lanes are from the same variant
    :type intra: bool
    :param intra: Whether the to allow nested structures or not
    :type intra: bool
    :return: The summarizing elements, a mapping from original interaction positions to the new positions
    :rtype: list of type SummarizationElement, dict
    '''
    elements = []
    new_interaction_points_mapping = {}
    current_horizontal_index = offset

    base_lanes = [lane.remove_non_common_elements() for lane in lanes]
    if(not nested):
        realization_lanes = [lane.get_valid_realizations() for lane in lanes]
    
    if(nested):
        all_lanes = []
        for i in range(len(lanes)):
            all_lanes.append((i, lanes[i], len(lanes[i].elements)))
    else:
        all_lanes = []
        for i in range(len(realization_lanes)):
            for realization in realization_lanes[i]:
                all_lanes.append((i, realization, len(realization.elements)))

    base_lanes_indexed = []
    for i in range(len(base_lanes)):
            base_lanes_indexed.append((i, base_lanes[i], len(base_lanes[i].elements)))

    if (intra):
        longest_common_sequence, length, number_of_interactions = __get_longest_common_subsequence(base_lanes_indexed, intra, interactions[0])
    else:
        longest_common_sequence, length, number_of_interactions = __get_longest_common_subsequence(base_lanes_indexed)

    last_positions = [0 for lane in base_lanes]

    for common_element in longest_common_sequence:

        current_positions = []
        for i in range(len(common_element[1])):
            current_positions.append(common_element[1][i][2])


        # Determine all interval subprocesses and summarize them
        interval_subprocesses = []
        for j in range(len(all_lanes)):
            index = all_lanes[j][0]
            if(current_positions[index] - last_positions[index] >= 0):
                subprocess = []
                for elem in all_lanes[j][1].elements:
                    if(isinstance(elem, SVD.CommonConstruct)):
                        if(elem.index >= last_positions[index] and elem.index < current_positions[index]):
                            subprocess.append(elem)
                    else:
                        if(elem.index_start >= last_positions[index] and elem.index_end < current_positions[index]):
                            subprocess.append(elem)

                interval_subprocesses.append((all_lanes[j][0], subprocess))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
    
        
        # Add summarized subprocess to elements
        if(nested):
            interval_elements, interval_length, interval_mapping = __apply_patterns_nested(interval_subprocesses, current_horizontal_index, interactions, base_lanes, current_lane, print_results, intra)
        else:
            interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, current_lane, print_results, intra)
        
        elements.extend(interval_elements)
        new_interaction_points_mapping.update(interval_mapping)
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_results):
            print("\n")
            print("Adding the common activity: " + str(common_element[0]))

        # Get frequency of the event
        element_frequency = 0
        for i in range(len(base_lanes)):
            element_frequency += base_lanes[i].get_element(common_element[2][i][2]).frequency
        element_frequency = element_frequency / len(base_lanes)

        
        # Checks if the common activity is an interaction point
        is_interacting_activity = False
        for i in range(len(base_lanes)):
            is_interacting_activity = is_interacting_activity or isinstance(base_lanes[i].get_element(common_element[2][i][2]), SVD.InteractionConstruct)

        if(print_results):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):

            interaction_points = []
  
            for i in range(len(base_lanes)):
                element = base_lanes[i].get_element(common_element[2][i][2])
                interaction_point_list = IED.get_interaction_points(interactions[i], base_lanes[i].lane_id, element.position)
                interaction_points.extend(interaction_point_list)

            for i in range(len(interaction_points)):
                if(intra):
                    identifier = 0
                else: 
                    identifier = i

                if((identifier, str([str(position) for position in interaction_points[i].exact_positions]), str(interaction_points[i].interaction_lanes)) in new_interaction_points_mapping.keys()):
                    new_interaction_points_mapping[(identifier, str([str(position) for position in interaction_points[i].exact_positions]), str(interaction_points[i].interaction_lanes))].append(IED.BasePosition(current_lane, current_horizontal_index))
                else:
                    new_interaction_points_mapping[(identifier, str([str(position) for position in interaction_points[i].exact_positions]), str(interaction_points[i].interaction_lanes))] = [IED.BasePosition(current_lane, current_horizontal_index)]

            elements.append(SVD.InteractionConstruct(common_element[0], element_frequency, IED.BasePosition(current_lane, current_horizontal_index), current_horizontal_index))

        else:
            elements.append(SVD.CommonConstruct(common_element[0], element_frequency, IED.BasePosition(current_lane, current_horizontal_index), current_horizontal_index))

        current_horizontal_index += 1
        
        # Update indices for the next iteration
        for i in range(len(last_positions)):
            last_positions[i] = current_positions[i] + 1


    # Determine all interval subprocesses and summarize them
    interval_subprocesses = []
    for j in range(len(all_lanes)):
        index = all_lanes[j][0]

        if(isinstance(all_lanes[j][1].elements[-1], SVD.CommonConstruct)):
            current_position = all_lanes[j][1].elements[-1].index + 1
        else:
            current_position = all_lanes[j][1].elements[-1].index_end + 1

        if(current_position - last_positions[index] >= 0):
            subprocess = []
            for elem in all_lanes[j][1].elements:
                if(isinstance(elem, SVD.CommonConstruct)):
                    if(elem.index >= last_positions[index] and elem.index < current_position):
                        subprocess.append(elem)
                else:
                    if(elem.index_start >= last_positions[index] and elem.index_end < current_position):
                        subprocess.append(elem)
            interval_subprocesses.append((all_lanes[j][0], subprocess))
        else:
            interval_subprocesses.append((all_lanes[j][0],[]))

    # Add summarized subprocess to elements
    if(nested):
        interval_elements, interval_length, interval_mapping = __apply_patterns_nested(interval_subprocesses, current_horizontal_index, interactions, base_lanes, current_lane, print_results, intra)
    else:
        interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, current_lane, print_results, intra)
    
    elements.extend(interval_elements)
    new_interaction_points_mapping.update(interval_mapping)
    current_horizontal_index += interval_length
 
    return elements, new_interaction_points_mapping


def __apply_patterns_nested(interval_subprocesses, start_index, interactions, base_lanes, current_lane, print_results, intra = False):
    '''
    Applies the defined patterns "Exclusive Choice Pattern" and "Optional Pattern" to the extracted subsequences of the initial Super Lanes between their common activities, allowing nested structures.
    :param interval_subprocesses: The extracted subprocess for each Super Lane between a pair of common activities
    :type interval_subprocesses: list
    :param interactions: The sets of interaction points corresponding to the involved Super Lanes
    :type interactions: list
    :param base_lanes: The set of Super Lanes with only the corresponding common and interaction elements
    :type base_lanes: list of type SuperLanes
    :param current_lane: The lane to which the patterns are applied
    :type current_lane: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :param intra: Whether the all lanes are from the same variant
    :type intra: bool
    :return: An element summarizing the extracted subprocesses for each initial Super Lane, the length of the element, the mapping from original interaction points to their positions in the element
    :rtype: SummarizationElement, int, dict
    '''
    import copy
    if sum([len(elements[1]) for elements in interval_subprocesses]) == 0:
        return [], 0, dict()
    
    new_mapping = dict()
    if(print_results):
            print("\n")
            print("Applying a pattern to the elements: ")
            for elements in interval_subprocesses:
                print(elements[1])
            
    returned_elements = []
    end_index = start_index

    # Determine choices and their frequencies
    choices = []
    total_frequency = sum([lane.frequency for lane in base_lanes])
    is_optional = False
    empty_frequency = 0
    current_choice = 0
    
    for elements in interval_subprocesses:
        position = start_index
        choice = []

        for i in range(len(elements[1])):
            
            if(isinstance(elements[1][i], SVD.InteractionConstruct) or isinstance(elements[1][i], SVD.GeneralChoiceStructure)):
                if(isinstance(elements[1][i], SVD.InteractionConstruct)):
                    interaction_points = IED.get_interaction_points(interactions[elements[0]], base_lanes[elements[0]].lane_id, elements[1][i].position)
                    for interaction_point in interaction_points:
                        if(intra):
                            identifier = 0
                        else:
                            identifier = elements[0]
                        if((identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes)) in new_mapping.keys()):
                            new_mapping[(identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))].append(IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position)))
                        else:
                            new_mapping[(identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))] = [IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position))]
                    choice.append(SVD.InteractionConstruct(elements[1][i].activity, base_lanes[elements[0]].frequency / total_frequency, IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position)), position))
                    length = 1
                else:
                    new_choices = []
                    length = 1
                    
                    for option in elements[1][i].choices:
                        
                        interaction_points = option.get_interaction_points(interactions[elements[0]], base_lanes[elements[0]].lane_id)
                        normalized_lane, positions_mapping = copy.deepcopy(option).normalize_option(current_lane, current_choice, position)
                        
                        for interaction_point in interaction_points:
                            for j in range(len(interaction_point.interaction_lanes)):
                                if(interaction_point.interaction_lanes[j] == base_lanes[elements[0]].lane_id):
                                    new_position = positions_mapping[str(interaction_point.exact_positions[j])]
                                    if(intra):
                                        identifier = 0
                                    else:
                                        identifier = elements[0]
                                    if((identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes)) in new_mapping.keys()):
                                        new_mapping[(identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))].append(new_position)
                                    else:
                                        new_mapping[(identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))] = [new_position]
                                    break

                        length = max(length, normalized_lane.get_length())
                        new_choices.append(normalized_lane)

                    if(isinstance(elements[1][i], SVD.OptionalConstruct)):
                        choice.append(SVD.OptionalConstruct(new_choices, IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position)), IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position + length - 1)), position, position + length - 1, elements[1][i].empty_frequency))
                    else:
                        choice.append(SVD.ChoiceConstruct(new_choices, IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position)), IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position + length - 1)), position, position + length - 1))
                    
            else:
                choice.append(SVD.CommonConstruct(elements[1][i].activity, base_lanes[elements[0]].frequency / total_frequency, IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_choice, position)), position))
                length = 1

            position += length

        if(choice == []):
            is_optional = True
            empty_frequency += 1

        else:
            duplicate = False
            for j in range(len(choices)):
                is_identical, update_lane = choices[j].check_identical(choice)

                if(is_identical):
                    choices[j] = update_lane
                    choices[j].cardinality = "n"
                    choices[j].frequency += base_lanes[elements[0]].frequency
                    duplicate = True
                    break

            if(not duplicate):
                choices.append(SVD.SuperLane(current_choice, "Option " + str(current_choice), base_lanes[0].object_type, choice, "1", base_lanes[elements[0]].frequency, []))
                current_choice += 1
        
        end_index = max(end_index, position - 1)


    if(len(choices) == 1 and len(choices[0].elements) == 1 and isinstance(choices[0].elements[0], SVD.GeneralChoiceStructure)):

        extracted_choices = []
        id = 0
        for extracted_choice in choices[0].elements[0].choices:
            extracted_elements, extracted_positions_mapping = copy.deepcopy(extracted_choice).extract_option(extracted_choice.frequency / total_frequency)
            extracted_choices.append(SVD.SuperLane(id, "Option " + str(id), base_lanes[0].object_type, extracted_elements.elements, "1", extracted_choice.frequency, []))
            id += 1

            for mapping in new_mapping.keys():
                for i in range(len(new_mapping[mapping])):
                    if(str(new_mapping[mapping][i]) in extracted_positions_mapping.keys()):
                        new_mapping[mapping][i] = extracted_positions_mapping[str(new_mapping[mapping][i])]

        if(print_results):
        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            for choice in extracted_choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")

        if(isinstance(choices[0].elements[0], SVD.OptionalConstruct)):
            empty_frequency = 1 - ((empty_frequency / len(interval_subprocesses)) * choices[0].elements[0].empty_frequency)
        else:
            empty_frequency = empty_frequency / len(interval_subprocesses)

        returned_elements.append(SVD.OptionalConstruct(extracted_choices, IED.BasePosition(current_lane, start_index), IED.BasePosition(current_lane, end_index), start_index, end_index, empty_frequency))
        return returned_elements, end_index - start_index + 1, new_mapping

   
    # Applying Optional Pattern
    if(is_optional):

        if(print_results):
        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")
        empty_frequency = empty_frequency / len(interval_subprocesses)
        returned_elements.append(SVD.OptionalConstruct(choices, IED.BasePosition(current_lane, start_index), IED.BasePosition(current_lane, end_index), start_index, end_index, empty_frequency))

    #Applying Exclusive Choice Pattern Pattern
    else:

        if(print_results):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")

        returned_elements.append(SVD.ChoiceConstruct(choices, IED.BasePosition(current_lane, start_index), IED.BasePosition(current_lane, end_index), start_index, end_index))
            
    return returned_elements, end_index - start_index + 1, new_mapping


def __apply_patterns(interval_subprocesses, start_index, interactions, base_lanes, current_lane, print_results, intra = False):
    '''
    Applies the defined patterns "Exclusive Choice Pattern" and "Optional Pattern" to the extracted subsequences of the initial Super Lanes between their common activities.
    :param interval_subprocesses: The extracted subprocess for each Super Lane between a pair of common activities
    :type interval_subprocesses: list
    :param interactions: The sets of interaction points corresponding to the involved Super Lanes
    :type interactions: list
    :param base_lanes: The set of Super Lanes with only the corresponding common and interaction elements
    :type base_lanes: list of type SuperLanes
    :param current_lane: The lane to which the patterns are applied
    :type current_lane: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :param intra: Whether the all lanes are from the same variant
    :type intra: bool
    :return: An element summarizing the extracted subprocesses for each initial Super Lane, the length of the element, the mapping from original interaction points to their positions in the element
    :rtype: SummarizationElement, int, dict
    '''
    import copy
    if sum([len(elements[1]) for elements in interval_subprocesses]) == 0:
        return [], 0, dict()
    
    new_mapping = dict()
    if(print_results):
            print("\n")
            print("Applying a pattern to the elements: ")
            for elements in interval_subprocesses:
                print(elements[1])
            
    returned_elements = []
    end_index = start_index

    # Determine choices and their frequencies
    choices = []
    frequencies = []
    is_optional = False
    empty_frequency = 0
    
    for elements in interval_subprocesses:
        position = start_index
        choice = []
        current_mappings = dict()
        contains_interaction = False

        for i in range(len(elements[1])):
            
            if(isinstance(elements[1][i], SVD.InteractionConstruct)):
                interaction_points = IED.get_interaction_points(interactions[elements[0]], base_lanes[elements[0]].lane_id, elements[1][i].position)
                for interaction_point in interaction_points:
                    if(intra):
                        identifier = 0
                    else: 
                        identifier = elements[0]
                    
                    current_mappings[(identifier, str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))] = start_index + i
                    contains_interaction = True
                choice.append(SVD.InteractionConstruct(elements[1][i].activity, elements[1][i].frequency, IED.BasePosition(current_lane, position), position))
            else:
                choice.append(SVD.CommonConstruct(elements[1][i].activity, elements[1][i].frequency, IED.BasePosition(current_lane, position), position))

            position += 1

        if(choice == []):
            is_optional = True
            empty_frequency += 1

        else:
            duplicate = False
            for i in range(len(choices)):

                equal = (not contains_interaction) or (elements[0] in choices[i][3])
                if(len(choices[i][0]) == len(choice)):
                    for j in range(len(choices[i][0])):
                        equal = equal and ((type(choices[i][0][j]) == type(choice[j])) and (choices[i][0][j].activity == choice[j].activity))

                        if(not equal):
                            break
                else:
                    equal = False

                if(equal):
                    duplicate = True
                    cardinality = "n"
                    frequencies[i] += 1
                    corresponding_lanes = choices[i][3]
                    corresponding_lanes.add(elements[0])

                    choices[i] = (choices[i][0], cardinality, frequencies[i], corresponding_lanes)
                    break

            if(not duplicate):
                frequencies.append(1)
                current_index = len(choices)
                for elem in choice:
                    horizontal_position = elem.position.get_base_index()
                    elem.position = IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_index, horizontal_position))
                    end_index = max(end_index, horizontal_position)
                choices.append(tuple((choice, "1", 1, set([elements[0]]))))
                for key in current_mappings.keys():
                    if not key in new_mapping:
                        new_mapping[key] = [IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_index, current_mappings[key]))]
                    else:
                        new_mapping[key].append(IED.RecursiveLanePosition(current_lane, IED.BasePosition(current_index, current_mappings[key])))

    for i in range(len(choices)):
        for elem in choices[i][0]:
            elem.frequency = choices[i][2] / len(interval_subprocesses)
        choices[i] = SVD.SuperLane(i, "Option " + str(i), base_lanes[0].object_type, choices[i][0], choices[i][1], choices[i][2], [])
   
    # Applying Optional Pattern
    if(is_optional):
        if(print_results):

        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")
        empty_frequency = empty_frequency / len(interval_subprocesses)
        returned_elements.append(SVD.OptionalConstruct(choices, IED.BasePosition(current_lane, start_index), IED.BasePosition(current_lane, end_index), start_index, end_index, empty_frequency))

    #Applying Exclusive Choice Pattern Pattern
    else:

        if(print_results):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")

        returned_elements.append(SVD.ChoiceConstruct(choices, IED.BasePosition(current_lane, start_index), IED.BasePosition(current_lane, end_index), start_index, end_index))
            
    return returned_elements, end_index - start_index + 1, new_mapping


def __get_longest_common_subsequence(lanes, intra = False, interactions = None):
    '''
    Computes the Longest Common Subsequence among the activity sequences of a set of Super Lanes.
    that interaction points between multiple lanes have the same horizontal index
    :param lanes: The lanes among which the longest common subsequence should be computed
    :type lanes: List of type SuperLane
    :param intra: Whether or not the input lanes are from the same variant. Used to check for shared interacion points.
    :type intra: bool
    :param interactions: The interaction points of the variant for a Intra-Variant Summarization setting
    :type interactions: List of type InteractionPoint
    :return: The Longest Common Subsequence and the corresponding positions in the lanes, the length of the longest_common_subsequence, the number of common interactions in the subsequence
    :rtype: list, int, int
    '''
    base_element = lanes[0][1].elements[lanes[0][2]-1]

    if any([lane[2] == 0 for lane in lanes]):
        return [], 0, 0

    else:
        intra_valid = False
        if (all((type(lane[1].elements[lane[2]-1]) == type(base_element) and lane[1].elements[lane[2]-1].activity == base_element.activity) for lane in lanes)):
            intra_valid = True
            
            if(intra and type(base_element) == SVD.InteractionConstruct):
                is_interacting, interaction_point = IED.is_interaction_point(interactions, lanes[0][1].lane_id, base_element.position)
                all_lanes_contained = True
                for lane in lanes:
                    if (not lane[1].lane_id in interaction_point.interaction_lanes):
                        all_lanes_contained = False
                        break
                intra_valid = all_lanes_contained


        if (intra_valid):
            
            recursive_result, recursive_value, recursive_interactions = __get_longest_common_subsequence([(lane[0], lane[1], lane[2]-1) for lane in lanes], intra, interactions)
            indices = [(lane[0], lane[1], lane[1].elements[lane[2]-1].index) for lane in lanes]
            positions = [(lane[0], lane[1], lane[1].elements[lane[2]-1].position) for lane in lanes]
            
            if(type(base_element) == SVD.InteractionConstruct):
                recursive_interactions = recursive_interactions + 1
            return recursive_result + [(base_element.activity, indices, positions)], recursive_value + 1, recursive_interactions

        else:
            maximum_value = -1
            maximum_result = []
            maximum_interaction = -1

            for i in range(1, pow(2,len(lanes))-1):
                binary = list(bin(i)[2:].zfill(len(lanes)))
                recursive_call_lanes = []
                for i in range(len(lanes)):
                    if (binary[i] == '1'):
                        recursive_call_lanes.append((lanes[i][0], lanes[i][1], lanes[i][2]-1))
                    else:
                        recursive_call_lanes.append(lanes[i])

                recursive_result, recursive_value, recursive_interactions = __get_longest_common_subsequence(recursive_call_lanes, intra, interactions)

                if ((recursive_value > maximum_value) or (recursive_value == maximum_value and recursive_interactions > recursive_interactions)):
                    maximum_value = recursive_value
                    maximum_result = recursive_result
                    maximum_interaction = recursive_interactions


            return maximum_result, maximum_value, maximum_interaction
