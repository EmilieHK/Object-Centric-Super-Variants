import Input_Extraction_Definition as IED

class SummarizedVariant:
    '''The data structure of the summarization of object-centric variants'''
    object_types = {}
    lanes = []
    interaction_points = []
    frequency = 0 
    
    def __init__(self, lanes, object_types, interaction_points, frequency):
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
        self.frequency = frequency 

    
    def __str__(self):
        result_string = "Lanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string + "Frequency: " + str(self.frequency)

    def get_depth(self):
        '''
        Determines the nested depth of the Super Variant.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :return: The number of nested structures in the Super Variant
        :rtype: int
        '''
        depth = 0
        for lane in self.lanes:
            depth = max(depth, lane.get_depth())
        return depth

    def get_length(self):
        '''
        Determines the total length of the Super Variant.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :return: The highest index in the lanes
        :rtype: int
        '''
        length = 0
        for lane in self.lanes:
            if(isinstance(lane.elements[-1], CommonConstruct)):
                length = max(length, lane.elements[-1].index)
            else:
                length = max(length, lane.elements[-1].index_end)
        return length


    def rename_lane(self, lane_id, new_name):
        '''
        Replaces the name of the lane in the summarized variant with the given lane id with a new name.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param lane_id: The id of the lane that should be renamed
        :type lane_id: tuple
        :param new_name: The new name for the lane
        :type new_name: str
        '''
        for lane in self.lanes:
            if(lane.lane_id == lane_id):
                lane.lane_name = new_name
                break

    
    def equals(self, other):
        '''
        Checks two summarized variants for equality up to lane naming and frequencies.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param other: The other summarized variant
        :type other: SummarizedVariant
        :return: Whether the two summarized variants are equal
        :rtype: bool
        '''
        return ((self.encode_lexicographically()) == (other.encode_lexicographically()))

   
    def encode_lexicographically(self):
        '''
        Converts the summarized variant into an encoding string.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :return: The corresponding lexicographic encoding
        :rtype: str
        '''
        import copy
        # Stores the mapping from original lane_id to the new lane_id based on the enumeration of the encoded lanes
        mapping = {}
        
        # The lanes are sorted by their type and encoded in this alphabetical order
        total_order_objects = [str(object) for object in list(self.object_types)]
        total_order_objects.sort()

        encoded_result = []
        for object in total_order_objects:

            # Determine all lanes for this object type
            object_lanes = [l for l in self.lanes if l.object_type == object]

            # Determine the maximal number of digits for the new lane_id
            power_of_ten = len(str(len(object_lanes)))

            encoded_lanes = []
            id = 0

            # Encode each lane, enumerate the encodings provisionally
            for lane in object_lanes:

                encoding = lane.encode_lexicographically(1)
        
                # Fill up the current id with 0's such that every id has the same number of characters
                full_id = str(id)
                while (len(full_id) < power_of_ten):
                    full_id = str(0) + full_id
                encoded_lanes.append(full_id + encoding)

                # Store a reference between the temporary id and the original lane_id of the lane
                mapping[full_id + encoding] = (lane.lane_id, 0)
                id += 1

            # Sort the encodings aphabetically, excluding its temporary id
            encoded_lanes.sort(key = lambda x: x[power_of_ten:])
            
            # Replace the temporary id with the enumeration of encodings as the new lane_id and add the object type to the prefix
            for i in range(len(encoded_lanes)):
                full_id = str(i)
                while (len(full_id) < power_of_ten):
                    full_id = str(0) + full_id
                lane_id = mapping[encoded_lanes[i]][0]
                mapping[encoded_lanes[i]]= (lane_id, object + " " + full_id)
                self.rename_lane(lane_id, object + " " + full_id)
                encoded_lanes[i] = object + " " + full_id + ": " + encoded_lanes[i][power_of_ten:] + " "

            encoded_result.extend(encoded_lanes)

        # Create dictionary for easy extraction of the new lane_id when encoding the interactions
        mapping = dict((x, y) for x, y in list(mapping.values()))

        interactions_result = []
        for interaction in self.interaction_points:

            # Encode references with the new lane_id and sort alphabetically
            interacting_lanes = [mapping[lane_id] for lane_id in copy.deepcopy(interaction.interaction_lanes)]
            interacting_lanes.sort()
            lanes_encoding = "".join(str(x) + ", " for x in interacting_lanes)
            lanes_encoding = lanes_encoding[:-2]
            encoding = f"IP[{interaction.index_in_lanes},[{lanes_encoding}]] "
            interactions_result.append(encoding)
        
        interactions_result.sort() 

        # Concatenate all encodings
        result = ""
        for encoded_lane in encoded_result:
            result += encoded_lane
        result += "- "
        for encoded_ip in interactions_result:
            result += encoded_ip
        
        # Additionally sort the Super Lane itself
        self.lanes.sort(key = lambda x: x.lane_name)

        return result


    def to_super_variant(self, id):
        '''
        Converts a generic summarized variant into a Super Variant by assigning an id.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param id: The id for the Super Variant
        :type id: int
        :return: The corresponding Super Variant
        :rtype: SuperVariant
        '''
        return SuperVariant(id, self.lanes, self.object_types, self.interaction_points, self.frequency)


    def get_lane(self, id):
        '''
        Finds and returns a lane of the summarized variant with the given id.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param id: The id of the lane
        :type id: int
        :return: The corresponding Super Lane
        :rtype: SuperLane
        '''
        for lane in self.lanes:
            if (lane.lane_id == id):
                return lane
        return None

    def remove_gaps(self):
        '''
        Removes unnecessary gaps from the Super Variant for improved visualization.
        :param self: The summarized variant
        :type self: SummarizedVariant
        '''
        indices_with_no_chevrons = []
        for lane in self.lanes:
            indices_with_no_chevrons.append(lane.get_gaps())

        result = indices_with_no_chevrons[0]
        for k in range(1, len(indices_with_no_chevrons)):
                result = list(set(result) & set(indices_with_no_chevrons[k]))
        
        if(result == []):
            return 
        else:
            #TODO remove gaps and update positions
            return

 
class SuperVariant(SummarizedVariant):
    '''The generalized data structure of the summarization of object-centric variants and Super Variants'''
     
    id = 0

    def __init__(self, id, lanes, object_types, interaction_points, frequency):
        self.id = id
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
        self.frequency = frequency

    def __str__(self):
        result_string = "Super Variant " + str(self.id) + "\nLanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string + "Frequency: " + str(self.frequency)
    

class SuperLane:
    '''The data structure of the summarization of lanes and Super Lanes'''
    lane_id = ()
    object_type = ""
    lane_name = ""
    elements = []
    cardinality = "0" 
    frequency = 0
    realizations = []
    
    def __init__(self, lane_id, name, object_type, elements, cardinality, frequency, realizations):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.elements = elements
        self.cardinality = cardinality
        self.frequency = frequency
        self.realizations = realizations
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}, Cardinality: {self.cardinality}:  ["
        for i in range(len(self.elements)):
            result_string += str(self.elements[i]) + ","       
        result_string = result_string[:-1]
        return result_string + "]"

    def get_length(self):
        '''
        Cmputes the length of the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The horizontal length of the Super Lane
        :rtype: int
        '''
        length = 0
        for element in self.elements:
            if (isinstance(element, CommonConstruct)):
                length += 1
            else:
                length += (element.index_end - element.index_start) + 1
        return length


    def get_gaps(self):
        '''
        Returns a list of all horizontal_indices that are not occupied by an activity.
         :param self: The summarizing Super Lane
        :type self: SuperLane
         :return: The list of found indices
        :rtype: list
        '''
        indices_with_no_chevrons = []

        if(type(self.elements[0]) == InteractionConstruct or type(self.elements[0]) == CommonConstruct):
            for j in range(0, self.elements[0].index):
                indices_with_no_chevrons.append(j)
        elif(type(self.elements[0]) == ChoiceConstruct or type(self.elements[0]) == OptionalConstruct):
            for j in range(0, self.elements[0].index_start):
                indices_with_no_chevrons.append(j)

        for i in range(1, len(self.elements)):
            if(type(self.elements[i]) == InteractionConstruct or type(self.elements[i]) == CommonConstruct):
                if(type(self.elements[i-1]) == InteractionConstruct or type(self.elements[i-1]) == CommonConstruct):
                    for j in range(self.elements[i-1].index + 1, self.elements[i].index):
                        indices_with_no_chevrons.append(j)
                elif(type(self.elements[i-1]) == ChoiceConstruct or type(self.elements[i-1]) == OptionalConstruct):
                    for j in range(self.elements[i-1].index_end + 1, self.elements[i].index):
                        indices_with_no_chevrons.append(j)

            elif(type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct):
                if(type(self.elements[i-1]) == InteractionConstruct or type(self.elements[i-1]) == CommonConstruct):
                    for j in range(self.elements[i-1].index + 1, self.elements[i].index_start):
                        indices_with_no_chevrons.append(j)
                elif(type(self.elements[i-1]) == ChoiceConstruct or type(self.elements[i-1]) == OptionalConstruct):
                    for j in range(self.elements[i-1].index_end + 1, self.elements[i].index_start):
                        indices_with_no_chevrons.append(j)

                intermediate_results = []
                for option in self.elements[i].choices:
                    intermediate_results.append(option.get_gaps())

                final_intermediate_result = intermediate_results[0]
                for k in range(1, len(intermediate_results)):
                    final_intermediate_result = list(set(final_intermediate_result) & set(intermediate_results[k]))
                indices_with_no_chevrons.extend(indices_with_no_chevrons)

        return indices_with_no_chevrons



    def get_interaction_points(self, interactions, lane_id):
        '''
        Returns all interaction points in the lane in order of traversal.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        param interactions: The list of interactions of the corresponding Super Variant
        :type interactions: list of type InteractionPoint
        param lane_id: The original lane_id of the high-level lane
        :type lane_id: tuple
        :return: The list of found interaction points
        :rtype: list of type InteractionPoint
        '''
        result = []

        for elem in self.elements:
            if(type(elem) == InteractionConstruct):
                interaction_points = IED.get_interaction_points(interactions, lane_id, elem.position)
                result.extend(interaction_points)

            elif(type(elem) == ChoiceConstruct or type(elem) == OptionalConstruct):
                for choice in elem.choices:
                    result.extend(choice.get_interaction_points(interactions, lane_id))
        return result



    def encode_lexicographically(self, depth, just_elements = False):
        '''
        Converts the Super Lane into an encoding string.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        param depth: The current level in the position
        :type depth: int
        param just_elements: Whether just the lanes elements should be encoded
        :type just_elements: bool
        :return: The corresponding lexicographic encoding
        :rtype: str
        '''

        encoding = ""
        if(not just_elements):
            encoding += f"CAR {self.cardinality}: "

        for element in self.elements:

            if(type(element) == CommonConstruct):
                encoding += f"CO[{element.index}:{element.index}, {element.activity}] "

            elif(type(element) == InteractionConstruct):
                encoding += f"IP[{element.index}:{element.index}, {element.activity}] "
                        
            else:
                        
                # Determine all choice sequences and sort alphabetically
                choices = [choice.encode_lexicographically(depth + 1, just_elements = True) for choice in element.choices]
                choices.sort()
                    
                # Encode all choices
                choices_encoding = ""
                for i in range(len(choices)):
                    choices_encoding += "Option " + str(i) + " "
                    choices_encoding += choices[i]
                    choices_encoding += ", "
                choices_encoding = choices_encoding[:-2]

                if(type(element) == ChoiceConstruct):
                    encoding += f"CH[{element.index_start}:{element.index_end}, [{choices_encoding}]] "
                        
                elif(type(element) == OptionalConstruct):
                    encoding += f"OP[{element.index_start}:{element.index_end}, [{choices_encoding}]] "

        return encoding[:-1]


    def update_lane_id(self, new_lane_id, depth):
        '''
        Updates the positions of a lane after the order of a choice has been changed.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param new_lane_id: The new id of this lane.
        :type new_lane_id: int
        param depth: The current level in the position
        :type depth: int
        '''
        import copy 

        for elem in self.elements:
            if (isinstance(elem, CommonConstruct)):

                positions = [copy.deepcopy(elem.position)]

                for i in range(depth-1):
                    positions.append(positions[-1].position)

                new_position = positions[-1]
                new_position.lane_id = new_lane_id
                
                for i in range(2, depth+1):
                    current_position = positions[-i]
                    current_position.position = new_position
                    new_position = copy.deepcopy(current_position)

                elem.position = new_position

            else:
                positions_start = [copy.deepcopy(elem.position_start)]
                positions_end = [copy.deepcopy(elem.position_end)]

                for i in range(depth-1):
                    positions_start.append(positions_start[-1].position)
                    positions_end.append(positions_end[-1].position)

                new_position_start = positions_start[-1]
                new_position_end = positions_end[-1]
                new_position_start.lane_id = new_lane_id
                new_position_end.lane_id = new_lane_id
                
                for i in range(2, depth+1):
                    current_position_start = positions_start[-i]
                    current_position_end = positions_end[-i]
                    current_position_start.position = new_position_start
                    current_position_end.position = new_position_end
                    new_position_start = copy.deepcopy(current_position_start)
                    new_position_end = copy.deepcopy(current_position_end)

                elem.position_start = new_position_start
                elem.position_end = new_position_end

                for choice in elem.choices:
                    choice.update_lane_id(new_lane_id, depth)


    def same_summarization(self, other):
        '''
        Checks the equality between two Super Lanes.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param other: The other summarizing Super Lane
        :type other: SuperLane
        :return: Whether the Super Lanes have the same object type and elements
        :rtype: bool
        '''
        if(other.object_type != self.object_type or len(self.elements) != len(other.elements)):
            return False
        else:
            result = True
            for i in range(len(self.elements)):
                result = result and self.elements[i] == other.elements[i]
            return result
    
    
    def subsumed_summarization(self, other):
        '''
        Checks whether either of the Super Lanes is subsumed in the other.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param other: The other summarizing Super Lane
        :type other: SuperLane
        :return: Whether the Super Lanes have are subsuming each other
        :rtype: bool
        '''
        import copy 
        if(other.object_type != self.object_type):
            return False

        result = False
        self_contains_choice = any(isinstance(x, ChoiceConstruct) for x in self.elements) or any(isinstance(x, OptionalConstruct) for x in self.elements)
        other_contains_choice = any(isinstance(x, ChoiceConstruct) for x in other.elements) or any(isinstance(x, OptionalConstruct) for x in other.elements)

        if(self_contains_choice and not other_contains_choice):
            realizations = self.get_realizations_normalized()
            normalized_other = copy.deepcopy(other).normalize()
            for realization in realizations:
                result = result or realization.same_summarization(normalized_other)

        elif(not self_contains_choice and other_contains_choice):
            realizations = other.get_realizations_normalized()
            normalized_self = copy.deepcopy(self).normalize()
            for realization in realizations:
                result = result or realization.same_summarization(normalized_self)
        else:
            realizations_self = self.get_realizations_normalized()
            realizations_other = other.get_realizations_normalized()
            subsumed_in_other = True
            subsumed_in_self = True
            for realization in realizations_self:
                subsumed_in_other = subsumed_in_other and any([realization.same_summarization(other) for other in realizations_other])
            for realization in realizations_other:
                subsumed_in_self = subsumed_in_self and any([realization.same_summarization(other) for other in realizations_self])
            result = (subsumed_in_other or subsumed_in_self)
                
        return result

    def normalize(self, offset = 0):
        '''
        Creates an abstraction of the Super Lane, shifting the positions to their normalized values starting from an offset value.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param offset: The starting index of the normalized Super Lane, defaulted at 0
        :type offset: int
        :return: The corresponding normalized Super Lane
        :rtype: SuperLane
        '''
        import copy 
        elements = copy.deepcopy(self.elements)
        index = offset
        for element in elements:
            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                index_before = element.index
                element.index = index
                element.position.apply_shift(index - index_before)
                index += 1
            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                normalized_options = []
                end_index = index
                for option in element.choices:
                    normalized_options.append(option.normalize(index))
                    if(isinstance(normalized_options[-1].elements[-1], CommonConstruct)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].index)
                    elif(isinstance(normalized_options[-1].elements[-1], GeneralChoiceStructure)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].index_end)

                index_start_before = element.index_start
                index_end_before = element.index_start
                element.index_start = index
                element.index_end = end_index
                element.position.apply_shift(index - index_start_before)
                element.position.apply_shift(end_index - index_end_before)
                index += end_index - index + 1
            
        return SuperLane(0, "normalization", self.object_type, elements, self.cardinality, self.frequency, [])


    def normalize_option(self, lane_id, option_id, offset = 0):
        '''
        Creates an abstraction of a Super Lane that is an option in a choice with normalized positions as well as a mapping from interaction points to their new positions.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param offset: The starting index of the normalized Super Lane, defaulted at 0
        :type offset: int
        :return: The corresponding normalized Super Lane and the mapping
        :rtype: SuperLane, dict
        '''
        import copy 
        elements = copy.deepcopy(self.elements)
        positions_mappings = dict()
        index = offset

        for element in elements:
            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):

                position_before = copy.deepcopy(element.position)
                index_before = element.index
                element.index = index
    
                element.position.apply_shift(index - index_before)
                position_after_shift = element.position
                
                if(isinstance(position_after_shift.position, IED.BasePosition)):
                    element.position = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.BasePosition(position_after_shift.position.lane_id, position_after_shift.position.position)))
                else:
                    element.position = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.RecursiveLanePosition(position_after_shift.position.lane_id, position_after_shift.position.position)))
                index += 1

                if(type(element) == InteractionConstruct):
                    positions_mappings[str(position_before)] = element.position

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                normalized_options = []
                end_index = index

                for option in element.choices:
                    new_option = copy.deepcopy(option)
                    normalization, mapping = new_option.normalize_option(lane_id, option_id, index)
                    normalized_options.append(normalization)

                    for key in mapping.keys():
                        positions_mappings[key] = mapping[key]

                    if(isinstance(normalized_options[-1].elements[-1], CommonConstruct)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].index)
                    elif(isinstance(normalized_options[-1].elements[-1], GeneralChoiceStructure)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].index_end)

                element.choices = normalized_options
                index_start_before = element.index_start
                index_end_before = element.index_start
                element.index_start = index
                element.index_end = end_index

                element.position_start.apply_shift(index - index_start_before)
                element.position_end.apply_shift(end_index - index_end_before)
                position_start_after_shift = element.position_start
                position_end_after_shift = element.position_end

                if(isinstance(position_start_after_shift.position, IED.BasePosition)):
                    element.position_start = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.BasePosition(position_end_after_shift.position.lane_id, position_start_after_shift.position.position)))
                    element.position_end = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.BasePosition(position_end_after_shift.position.lane_id, position_end_after_shift.position.position)))
                else:
                    element.position_start = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.RecursiveLanePosition(position_start_after_shift.position.lane_id, position_start_after_shift.position.position)))
                    element.position_end = IED.RecursiveLanePosition(lane_id, IED.RecursiveLanePosition(option_id, IED.RecursiveLanePosition(position_start_after_shift.position.lane_id, position_end_after_shift.position.position)))
                
                index += end_index - index + 1
            
        return SuperLane(self.lane_id, self.lane_name, self.object_type, elements, self.cardinality, self.frequency, []), positions_mappings


    def extract_option(self, new_frequency = None):
        '''
        Updates all positions in a lane by removing the first given option_id corresponding to the second lane_id.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param new_frequency: The updated frequency for the elements
        :type new_frequency: float
        :return: The corresponding lane with adjusted positions and it's mapping
        :rtype: SuperLane, dict
        '''
        import copy 

        mapping = dict()

        for element in self.elements:
            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):

                position_before = copy.deepcopy(element.position)
                element.position = IED.RecursiveLanePosition(0, position_before.position.position)
                if(new_frequency != None):
                    element.frequency = new_frequency

                if(type(element) == InteractionConstruct):
                    mapping[str(position_before)] = element.position

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):

                for i in range(len(element.choices)):

                    updated_choice, recursive_mapping = element.choices[i].extract_option()
                    element.choices[i] = updated_choice

                    for key in recursive_mapping.keys():
                        mapping[key] = recursive_mapping[key]

                    position_start_before = copy.deepcopy(element.position_start)
                    position_end_before = copy.deepcopy(element.position_end)
                    element.position_start = IED.RecursiveLanePosition(0, position_start_before.position.position)
                    element.position_end = IED.RecursiveLanePosition(0, position_end_before.position.position)
   
        return self, mapping


    def get_realizations_normalized(self):
        '''
        Generates all realizations of a Super Lane with normalized positions starting from 0.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The list of all realizations
        :rtype: list of type SuperLane
        '''
        import copy
        realizations = []
        realizations.append([])

        for elem in self.elements:
            element = copy.deepcopy(elem)

            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                realizations = [realization + [element] for realization in realizations]

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                intermediate_result = []
                for i in range(len(element.choices)):
                    for sublist in element.choices[i].get_realizations_normalized(element.start):
                        intermediate_result.extend([realization + sublist.elements for realization in realizations])
                if(type(element) == OptionalConstruct):
                    intermediate_result.extend([realization + [EmptyConstruct(element.empty_frequency)] for realization in realizations])
                realizations = intermediate_result

        result = []
        for i in range(len(realizations)):

            frequency = 1
            for elem in realizations[i]:
                frequency = frequency * elem.frequency
            
            realization_frequency = frequency * self.frequency

            index = 0
            elements = []
            for elem in realizations[i]:
                if(not type(elem) == EmptyConstruct):
                    elements.append(copy.deepcopy(elem))
                    elements[-1].frequency = frequency
                    elements[-1].index = index
                    elements[-1].position = IED.BasePosition(0, index)
                    index += 1
                    
            result.append(SuperLane(i, "realization " + str(i), self.object_type, elements, "1", realization_frequency, []))

        return result

    def get_all_realizations(self):
        '''
        Generates all realizations of a Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The list of all realizations
        :rtype: list of type SuperLane
        '''
        import copy
        realizations = []
        realizations.append([])

        for elem in self.elements:
            element = copy.deepcopy(elem)

            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                realizations = [realization + [copy.deepcopy(element)] for realization in realizations]

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                intermediate_result = []
                for i in range(len(element.choices)):

                    for sublist in element.choices[i].get_all_realizations():
                        intermediate_result.extend([realization + sublist.elements for realization in realizations])

                if(type(element) == OptionalConstruct):
                    intermediate_result.extend([realization + [EmptyConstruct(element.empty_frequency)] for realization in realizations])
                realizations = intermediate_result

        result = []

        for i in range(len(realizations)):
            frequency = 1
            for elem in realizations[i]:
                frequency = frequency * elem.frequency
            
            realization_frequency = frequency * self.frequency
            
            new_elements = []
            for elem in realizations[i]:
                if(not type(elem) == EmptyConstruct):
                    new_elements.append(copy.deepcopy(elem))
                    new_elements[-1].frequency = frequency

            result.append(SuperLane(i, "realization " + str(i), self.object_type, new_elements, self.cardinality, realization_frequency, []))

        return result

    
    def get_valid_realizations(self):
        '''
        Generates all realizations of a Super Lane and cross-references them with the stored realizations.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The list of all valid realizations
        :rtype: list of type SuperLane
        '''
        all_realizations = self.get_all_realizations()
        valid_realizations = []

        for realization in all_realizations:
            is_valid = False
            for comparison in self.realizations:

                if (len(comparison.elements) != len(realization.elements)):
                    continue
                else:

                    is_equivalent = True
                    for i in range(len(realization.elements)):
                        if(type(realization.elements[i]) ==  type(comparison.elements[i])):
                            if(type(realization.elements[i]) == InteractionConstruct and type(comparison.elements[i]) == InteractionConstruct and comparison.elements[i].activity == realization.elements[i].activity):
                                continue
                            elif(type(realization.elements[i]) == CommonConstruct and type(comparison.elements[i]) == CommonConstruct and comparison.elements[i].activity == realization.elements[i].activity):
                                continue
                            else:
                                is_equivalent = False
                                break
                        else:
                            is_equivalent = False
                            break

                    if(is_equivalent):
                        is_valid = True
                        break
            if(is_valid):
                valid_realizations.append(realization)

        return valid_realizations

    def check_identical(self, elements):
        '''
        Checks the elements of the lane againts a list of other elements
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param elements: The list of elements
        :type elements: list of type SummarizationElement
        :return: Whether the elements are identical
        :rtype: bool
        '''
        import copy
        if (len(self.elements) != len(elements)):
            return False, self
        
        else:
            update_self = copy.deepcopy(self)
            for i in range(len(elements)):
                if(type(elements[i]) ==  type(self.elements[i])):
                    if(type(elements[i]) == InteractionConstruct and type(self.elements[i]) == InteractionConstruct and elements[i].activity == self.elements[i].activity):
                        update_self.elements[i].frequency += elements[i].frequency
                        continue
                    elif(type(elements[i]) == CommonConstruct and type(self.elements[i]) == CommonConstruct and elements[i].activity == self.elements[i].activity):
                        update_self.elements[i].frequency += elements[i].frequency
                        continue
                    elif((type(elements[i]) == OptionalConstruct and type(self.elements[i]) == OptionalConstruct) or (type(elements[i]) == ChoiceConstruct and type(self.elements[i]) == ChoiceConstruct)):
                        
                        if(len(elements[i].choices) == 1 and len(self.elements[i].choices) == 1 and elements[i].empty_frequency == self.elements[i].empty_frequency):
                            is_identical, new_choice = self.elements[i].choices[0].check_identical(elements[i].choices[0].elements)
                            
                            if(is_identical):
                                self.elements[i].choices[0] = new_choice
                                self.elements[i].choices[0].cardinality = "n"
                                self.elements[i].choices[0].frequency += elements[i].choices[0].frequency
                        
                        # TODO Handling multiple choices
                        else:
                            return False, self
                else:
                    return False, self
        
        return True, update_self


   
    def get_element(self, position):
        '''
        Extracts the element of the Super Lane at the given position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The position of the element
        :type position: LanePosition
        :return: The element at the given position
        :rtype: SummarizationElement
        ''' 
        unpacked_position = position.position
        is_base_position = isinstance(unpacked_position, int)
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and is_base_position and element.index == unpacked_position):
                return element
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct) and not is_base_position and unpacked_position.get_base_index() >= element.index_start and unpacked_position.get_base_index() <= element.index_end):
                return element.choices[unpacked_position.lane_id].get_element(unpacked_position)
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct) and is_base_position and unpacked_position >= element.index_start and unpacked_position <= element.index_end):
                return element
        return None


    def contains_activity(self, activity_label):
        '''
        Checks whether the given activity label occurs in the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param activity_label: The label of the activity
        :type activity_label: str
        :return: Whether the activity is contained in the Super Lane
        :rtype: bool
        '''
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.activity == activity_label):
                return True
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct)):

                for choice in element.choices:
                    if (choice.contains_activity(activity_label)):
                        return True

        return False

    def count_activity(self, activity_label):
        '''
        Extracts the number of times the given activity label occurs in the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param activity_label: The label of the activity
        :type activity_label: str
        :return: The count of occurences
        :rtype: int
        '''
        count = 0
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.activity == activity_label):
                count += 1
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct)):

                for choice in element.choices:
                    count += choice.count_activity(activity_label)

        return count
    
    def shift_lane(self, start_element, offset, observed_positions, index = None):
        '''
        Shifts the positions of the Super Lane by an offset starting from a given start element.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param start_element: The first element that requires shifting
        :type start_element: SummarizationConstruct
        :param offset: The offset of the shift
        :type offset: int
        :param observed_positions: A dictionary with all other interaction point positions relevant for this shift, these are observed and updated accordingly
        :type observed_positions: dict
        :param index: The index of the starting element in the list of elements and the lane itself
        :type index: int, SuperLane
        :return: The dictionary with the observed updated positions and the lane
        :rtype: dict, SuperLane
        '''
        import copy
        if(index == None):
            index = self.elements.index(start_element)
            
        for i in range(index, len(self.elements)):
            if(type(self.elements[i]) == CommonConstruct or type(self.elements[i]) == InteractionConstruct):
                position_before = copy.deepcopy(self.elements[i].position)
                self.elements[i].index += offset
                self.elements[i].position.apply_shift(offset)
                observed_positions[str(position_before)] = self.elements[i].position

            elif(type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct):
                self.elements[i].index_start += offset
                self.elements[i].index_end += offset 
                self.elements[i].position_start.apply_shift(offset)
                self.elements[i].position_end.apply_shift(offset)

                for choice in self.elements[i].choices:
                    choice, observed_positions = choice.shift_lane(choice.elements[0], offset, observed_positions, 0)

        return self, observed_positions

    def shift_lane_exact(self, start_position, offset, observed_positions, original_position):
        '''
        Shifts the positions of the Super Lane by an offset starting from a given start position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param start_position: The position from which the shifting should begin
        :type start_position: LanePosition
        :param offset: The offset of the shift
        :type offset: int
        :param observed_positions: A dictionary with all other interaction point positions relevant for this shift, these are observed and updated accordingly
        :type observed_positions: dict
        :param original_position: The original position from which the shifting should begin
        :type original_position: LanePosition
        :return: The dictionary with the observed updated positions and the lane
        :rtype: dict, SuperLane
        '''
        import copy
        unpacked_position = copy.deepcopy(start_position.position)
        is_base_position = isinstance(unpacked_position, int)

        for i in range(len(self.elements)):

            # Case 1: Start shifting from a Common Activity
            if((type(self.elements[i]) == InteractionConstruct) and is_base_position and self.elements[i].index == unpacked_position):
                self, observed_positions = self.shift_lane(self.elements[i], offset, observed_positions, i)
                return observed_positions, self
        
            # Case 2: Start shifting from a Generic Choice Structure
            elif((type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct) and not is_base_position and self.elements[i].index_end >= unpacked_position.get_base_index() and self.elements[i].index_start <= unpacked_position.get_base_index()):
                start_index_before_shift = self.elements[i].index_start
                end_index_before_shift = self.elements[i].index_end
                
                observed_positions, self.elements[i].choices[unpacked_position.lane_id] = self.elements[i].choices[unpacked_position.lane_id].shift_lane_exact(unpacked_position, offset, observed_positions, original_position)

                all_start_indices = []
                all_end_indices = []

                for choice in self.elements[i].choices:
                    if(isinstance(choice.elements[0], CommonConstruct)):
                        all_start_indices.append(choice.elements[0].index)
                    elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                        all_start_indices.append(choice.elements[0].index_start)

                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_indices.append(choice.elements[-1].index)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_indices.append(choice.elements[-1].index_end)
                        
                self.elements[i].index_start = min(all_start_indices)
                self.elements[i].index_end = max(all_end_indices)
                self.elements[i].position_start.apply_shift(self.elements[i].index_start - start_index_before_shift)
                self.elements[i].position_end.apply_shift(self.elements[i].index_end - end_index_before_shift)
                
                if(i < len(self.elements) - 1):
                    self, observed_positions = self.shift_lane(self.elements[i+1], self.elements[i].index_end - end_index_before_shift, observed_positions, i+1)
        
                return observed_positions, self

        return observed_positions, self
                


    def remove_non_common_elements(self):
        '''
        Returns the Super Lane with only the elements that are not indicating choices.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The Super Lane with only the desired subset of elements
        :rtype: SuperLane
        '''
        new_elements = []
        for elem in self.elements:
            if(isinstance(elem, CommonConstruct)):
                new_elements.append(elem)
        return SuperLane(self.lane_id, self.lane_name, self.object_type, new_elements, self.cardinality, self.frequency, [])


    def make_optional(self, position, empty_frequency):
        '''
        Makes an element at a certain position optional
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The position of the element that is to be made optional
        :type position: LanePosition
        :param empty_frequency: The counter-frequency of the optional element that is subtracted from the current element frequency
        :type lane: float
        :return: The modified Super Lane and the modified element
        :rtype: SuperLane, OptionalChoiceConstruct
        '''
        unpacked_position = position.position
        is_base_position = isinstance(unpacked_position, int)
        for i in range(len(self.elements)):
            if (isinstance(self.elements[i], InteractionConstruct) and is_base_position and self.elements[i].index == unpacked_position):
                self.elements[i] = self.elements[i].make_optional(self, empty_frequency)
                return self, self.elements[i]
            elif(isinstance(self.elements[i], GeneralChoiceStructure) and not is_base_position and self.elements[i].index_start <= unpacked_position.get_base_index() and self.elements[i].index_end >= unpacked_position.get_base_index()):
                self.elements[i].choices[unpacked_position.lane_id], element = self.elements[i].choices[unpacked_position.lane_id].make_optional(unpacked_position, empty_frequency)
                return self, element
        return self, None


    def add_optional_activity(self, position, activity):
        '''
        Inserts an optional element into the Super Lane at the given position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The position at which the optional element should be inserted
        :type position: LanePosition
        :param activity: The optional element that should be inserted
        :type activity: OptionalConstruct
        :return: The modified Super Lane
        :rtype: SuperLane
        '''
        activity.position_start = position
        activity.position_end = position
        activity.choices[0].elements[0].position = position 
        activity.index_start = position.get_base_index()
        activity.index_end = position.get_base_index()
        activity.choices[0].elements[0].index = position.get_base_index()

        unpacked_position = position.position
        is_base_position = isinstance(unpacked_position, int)

        for i in range(len(self.elements)):
            if ((isinstance(self.elements[i], CommonConstruct) and is_base_position and self.elements[i].index >= unpacked_position) or (isinstance(self.elements[i], GeneralChoiceStructure) and is_base_position and self.elements[i].index_start >= unpacked_position)):
                self.shift_lane(self.elements[i], 1, i)
                predecessors = []
                if(i > 0):
                    predecessors = self.elements[:i]
                successors = self.elements[i:]
                self.elements = predecessors + [activity] + successors
                return self

            elif(isinstance(self.elements[i], GeneralChoiceStructure) and not is_base_position and self.elements[i].index_start <= unpacked_position.get_base_index() and self.elements[i].index_end >= unpacked_position.get_base_index()):

                self.elements[i].choices[unpacked_position.lane_id] = self.elements[i].choices[unpacked_position.lane_id].add_optional_activity(unpacked_position, activity)

                all_end_indices = []
                for choice in self.elements[i].choices:
                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_indices.append(choice.elements[-1].index)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_indices.append(choice.elements[-1].index_end)

                new_end = max(all_end_indices)
                length_difference = new_end - self.elements[i].index_end
                self.elements[i].index_end = new_end
                self.elements[i].position_end.apply_shift(length_difference)

                if(i < len(self.elements)-1):
                    self.shift_lane(self.elements[i+1], length_difference, i+1)

                return self

        self.elements = self.elements + [activity]
        return self

    
    def shift_activities_up(self, up_to = None):
        '''
        Shifts all non-interaction elements up to the next element's position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param up_to: The position to which the lane should be shifted
        :type up_to: int
        :return: The modified Super Lane
        :rtype: SuperLane
        '''
        # Shift last element 
        if(isinstance(self.elements[-1], GeneralChoiceStructure)):
            start_index_before_shift = self.elements[-1].index_start
            end_index_before_shift = self.elements[-1].index_end
        
            for j in range(len(self.elements[-1].choices)):
                if(up_to):
                    self.elements[-1].choices[j] = self.elements[-1].choices[j].shift_activities_up(up_to)
                else: 
                    self.elements[-1].choices[j] = self.elements[-1].choices[j].shift_activities_up(self.elements[-1].index_end)

            all_start_indices = []
            all_end_indices = []

            for choice in self.elements[-1].choices:
                if(isinstance(choice.elements[0], CommonConstruct)):
                    all_start_indices.append(choice.elements[0].index)
                elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                    all_start_indices.append(choice.elements[0].index_start)

                if(isinstance(choice.elements[-1], CommonConstruct)):
                    all_end_indices.append(choice.elements[-1].index)
                elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                    all_end_indices.append(choice.elements[-1].index_end)
                        
            self.elements[-1].index_start = min(all_start_indices)
            self.elements[-1].index_end = max(all_end_indices)
            self.elements[-1].position_start.apply_shift(self.elements[-1].index_start - start_index_before_shift)
            self.elements[-1].position_end.apply_shift(self.elements[-1].index_end - end_index_before_shift)

        elif(not isinstance(self.elements[-1], InteractionConstruct)):
            if(up_to):
                self.elements[-1].position.apply_shift(up_to - self.elements[-1].position.get_base_index())
                self.elements[-1].index = up_to

        # Continue to shift up each element to its successor element
        for i in range(len(self.elements) - 1):
            index = len(self.elements) - 1 - i
            if (isinstance(self.elements[index-1], CommonConstruct) and not isinstance(self.elements[index-1], InteractionConstruct)):

                if (isinstance(self.elements[index], CommonConstruct)):
                    offset = self.elements[index].index - self.elements[index-1].index - 1
                elif (isinstance(self.elements[index], GeneralChoiceStructure)):
                    offset = self.elements[index].index_start - self.elements[index-1].index - 1
                else:
                    offset = 0

                self.elements[index-1].index += offset
                self.elements[index-1].position.apply_shift(offset)


            elif(isinstance(self.elements[index-1], GeneralChoiceStructure)):

                if (isinstance(self.elements[index], CommonConstruct)):
                    offset = self.elements[index].index - self.elements[index-1].index_end - 1
                elif (isinstance(self.elements[index], GeneralChoiceStructure)):
                    offset = self.elements[index].index_start - self.elements[index-1].index_end - 1
                else:
                    offset = 0

                start_index_before_shift = self.elements[index-1].index_start
                end_index_before_shift = self.elements[index-1].index_end

                for j in range(len(self.elements[index-1].choices)):
                    self.elements[index-1].choices[j] = self.elements[index-1].choices[j].shift_activities_up(max(self.elements[index-1].index_end + offset - 1, self.elements[index-1].index_end))

                all_start_indices = []
                all_end_indices = []

                for choice in self.elements[index-1].choices:
                    if(isinstance(choice.elements[0], CommonConstruct)):
                        all_start_indices.append(choice.elements[0].index)
                    elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                        all_start_indices.append(choice.elements[0].index_start)

                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_indices.append(choice.elements[-1].index)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_indices.append(choice.elements[-1].index_end)
                        

                self.elements[index-1].index_start = min(all_start_indices)
                self.elements[index-1].index_end = max(all_end_indices)
                self.elements[index-1].position_start.apply_shift(self.elements[index-1].index_start - start_index_before_shift)
                self.elements[index-1].position_end.apply_shift(self.elements[index-1].index_end - end_index_before_shift)

        return self

    def contains_interaction_point(self):
        '''
        Determines whether the Super Lane contains an interaction point.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: Whether the Super Lane contains an InteractionConstruct element
        :rtype: bool
        '''
        for element in self.elements:
            if (isinstance(element, InteractionConstruct)):
                return True
            elif(isinstance(element, GeneralChoiceStructure)):
                for option in element.choices:
                    if (option.contains_interaction_point()):
                        return True
        return False

    def get_depth(self):
        '''
        Determines the nested depth of the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The number of nested structures in the Super Lane
        :rtype: int
        '''
        depth = 0
        for element in self.elements:
            if(isinstance(element, GeneralChoiceStructure)):
                for choice in element.choices:
                    depth = max(depth, 1 + choice.get_depth())
        return depth



class OptionalSuperLane(SuperLane):
    '''The data structure of a subclass of Super Lanes that is entirely optional'''

    def __str__(self):
        result_string = f"Optional ID: {self.lane_id}, Name: {self.lane_name}, Cardinality: {self.cardinality}:  ["
        for i in range(len(self.elements)):
            result_string += str(self.elements[i]) + ","       
        result_string = result_string[:-1]
        return result_string + "]"



class SummarizationElement:
    '''The data structure the elements of a summarized variant'''

class EmptyConstruct(SummarizationElement):
    frequency = 0

    def __init__(self, frequency):
        self.frequency = frequency


class CommonConstruct(SummarizationElement):
    '''The data structure of common activities in a summarized variant'''
    activity = ""
    frequency = 0
    position = None
    index = 0

    def __init__(self, activity, frequency, position, index):
        self.activity = activity
        self.frequency = frequency
        self.position = position
        self.index = index
        
    def __str__(self):
        return "(Pos " + str(self.position) + ": " + str(self.activity) + ")"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

    def make_optional(self, lane, empty_frequency):
        '''
        Converts the element to an element within an optional construct.
        :param self: The common or interaction element
        :type self: CommonConstruct
        :param lane The corresponding SuperLane 
        :type lane: SuperLane
        :param empty_frequency: The counter-frequency of the optional element that is subtracted from the current element frequency
        :type lane: float
        :return: the optional element
        :rtype: OptionalConstruct
        '''
        self.frequency -= empty_frequency
        option = SuperLane(0, "option 0", lane.object_type, [self], 1, self.frequency*lane.frequency, [])
        return OptionalConstruct([option], self.position, self.position, self.index, self.index, empty_frequency)


class InteractionConstruct(CommonConstruct):
    
    def __str__(self):
        return "(Pos " + str(self.position) + ": Interaction " + str(self.activity) + ")"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

    
class GeneralChoiceStructure(SummarizationElement):
    '''The data structure of an choices of activity sequences in a summarized variant'''
    choices = []
    position_start = None
    position_end = None
    index_start = 0
    index_end = 0
    
    def __init__(self, choices, start, end, index_start, index_end):
        self.choices = choices
        self.position_start = start
        self.position_end = end
        self.index_start = index_start
        self.index_end = index_end
    
    def __eq__(self, other):
        import copy
        if isinstance(other, self.__class__):
            self_encoded_choices = copy.deepcopy(self.choices)
            self_encoded_choices = [choice.encode_lexicographically() for choice in self_encoded_choices]
            self_encoded_choices.sort()

            other_encoded_choices = copy.deepcopy(other.choices)
            other_encoded_choices = [choice.encode_lexicographically() for choice in other_encoded_choices]
            other_encoded_choices.sort()
            
            if(len(self_encoded_choices) != len(other_encoded_choices)):
                return False

            equal = True
            for i in range(len(self_encoded_choices)):
                equal = equal and (self_encoded_choices[i] == other_encoded_choices[i])
            return equal
            
        return False


    def get_vertical_height(self):
        vertical_height = len(self.choices)

        for choice in self.choices:
            maximal_choice_height = 1
            for element in choice.elements:
                if(isinstance(element, GeneralChoiceStructure)):
                    maximal_choice_height = max(maximal_choice_height, element.get_vertical_height())
            vertical_height += maximal_choice_height - 1
        
        return vertical_height



class OptionalConstruct(GeneralChoiceStructure):
    '''The data structure of an optional choices of activity sequences in a summarized variant'''

    empty_frequency = 1

    def __init__(self, choices, start, end, index_start, index_end, empty_frequency):
        self.choices = choices
        self.position_start = start
        self.position_end = end
        self.index_start = index_start
        self.index_end = index_end
        self.empty_frequency = empty_frequency
    
    def __str__(self):
        result_string = f"(Pos: {self.position_start} - {self.position_end}: Optional Choices "
        result_string += "("
        for choice in self.choices:
            result_string += str(choice) + ", "
        result_string = result_string[:-2] + ")"
        return result_string

class ChoiceConstruct(GeneralChoiceStructure):
    '''The data structure of a choice of activities in a summarized variant'''
    
    def __str__(self):
        result_string = f"(Pos: {self.position_start} - {self.position_end}: Choices "
        result_string += "("
        for choice in self.choices:
            result_string += str(choice) + ", "
        result_string = result_string[:-2] + ")"
        return result_string


def summarized_variant_layouting(summarized_variant):
    '''
    Formats a summarized vatriant into a visualization layout.
    :param summarized_variant: The summarized variant that requires reformatting
    :type summarized_variant: SummarizedVariant
    :return: A list of all elements and their positions with references to the involved lanes
    :rtype: list
    '''
    items = {}
    
    # Create dictionary of objects
    for type in summarized_variant.object_types:
        object_lanes = [lane for lane in summarized_variant.lanes if lane.object_type == type]
        for lane in object_lanes:
            items[lane.lane_id] = (type, lane.lane_name, lane.cardinality)
    
    # Create list of activities and their indices
    activities = []
    for lane in summarized_variant.lanes:
        for elem in lane.elements:

            interactions = [lane.lane_id]

            if(isinstance(elem, InteractionConstruct)):
                for interactionPoint in summarized_variant.interaction_points:
                    for i in range(len(interactionPoint.interaction_lanes)):
                        if(lane.lane_id in interactionPoint.interaction_lanes and elem.index == interactionPoint.exact_positions[i]):
                            interactions.extend(interactionPoint.interaction_lanes)

            if(isinstance(elem, CommonConstruct) or isinstance(elem, InteractionConstruct)):
                activities.append([elem,[[elem.index, elem.index], list(set(interactions))]])
            else:
                activities.append([elem,[[elem.index_start, elem.index_end], list(set(interactions))]])
    
    # Remove duplicate activities that are interaction points
    unique_activities = []
    for activity in activities:
        identical_activities = [u_activity for u_activity in unique_activities if activity[1][0][0] == u_activity[1][0][0] and activity[1][1] == u_activity[1][1]]
        if (len(identical_activities) < 1):
            unique_activities.append(activity)
    
    return[unique_activities,items]