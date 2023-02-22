import Super_Variant_Definition as SVD

class VariantLane:
    '''The data structure of a lane of a variant correponding to the activity execution of an object instance'''
    lane_id = 0
    object_type = ""
    lane_name = ""
    activities = []
    horizontal_indices = []
    
    def __init__(self, lane_id, object_type, name, activities, indices):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.activities = activities
        self.horizontal_indices = indices
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}: ["
        for i in range(len(self.activities)):
            result_string += "(Pos: " + str(self.horizontal_indices[i]) + ", " + self.activities[i] + "),"       
        result_string = result_string[:-1]
        return result_string + "]"
    
    def has_type(self, input_type):
        '''
        Determines whether the lane corresponds to an object instances of the given type
        :param self: The lane
        :type self: VariantLane
        :param input_type: The object type label
        :type input_type: str
        :return: Whether the object type of the lane equals the given object type
        :rtype: bool
        '''
        return self.object_type == input_type

    def to_super_lane(self, interactions):
        ''' 
        Converts a variant lane into a Super Lane.
        :param self: The variant lane
        :type self: VariantLane
        :param interactions: The interactions of the variant
        :type interactions: set of type InteractionPoints
        :return: The corresponding Super Lane
        :rtype: SuperLane
        '''
        elements = []
        for i in range(len(self.activities)):
            index = self.horizontal_indices[i]
            position = BasePosition(0, index)
            activity_label = self.activities[i]
            
            is_interacting, interaction_point = is_interaction_point(interactions, self.lane_id, position)

            if(is_interacting):
                elements.append(SVD.InteractionConstruct(activity_label, 1, position, index))

            else:
                elements.append(SVD.CommonConstruct(activity_label, 1, position, index))

        super_lane = SVD.SuperLane(self.lane_id, self.lane_name, self.object_type, elements, "1", 1, [SVD.SuperLane(0, "realization 0", self.object_type, elements, "1", 1, [])])
        return super_lane


class InteractionPoint:
    '''The data structure of an Interaction Point'''
    activity_name = ""
    interaction_lanes = []
    interacting_types = {}
    index_in_lanes = 0
    exact_positions = []
    
    def __init__(self, activity_label, lanes, types, index, positions):
        self.activity_name = activity_label                                                                    
        self.interaction_lanes = lanes                                                                      
        self.interacting_types = types
        self.index_in_lanes = index
        self.exact_positions = positions
        
    def __str__(self):
        return f"Interaction Point: {self.activity_name} at Pos: {self.index_in_lanes}"

class LanePosition:
    '''The data structure for storing element positions in lanes'''

class RecursiveLanePosition(LanePosition):
    '''The recursive data structure for storing element positions in lanes'''

    lane_id = 0
    position = None

    def __init__(self, lane, position):
        self.lane_id = lane
        self.position = position

    def __eq__(self, other):
        return type(self) == type(other) and (self.lane_id == other.lane_id) and (self.position == other.position)

    def __str__(self):
        return "R(" + str(self.lane_id) + ", " + str(self.position) + ")"

    def get_base_index(self):
        ''' 
        Gets the horizontal index of the position element.
        :param self: The position element
        :type self: RecursiveLanePosition
        :return: The recursive result
        :rtype: int
        '''
        return self.position.get_base_index()

    def apply_shift(self, offset):
        ''' 
        Shifts the horizontal index by a given offset.
        :param self: The position element
        :type self: RecursiveLanePosition
        :param offset: The offset
        :type offset: int
        '''
        self.position.apply_shift(offset)

    def get_depth(self):
        ''' 
        Gets the vertical_depth of the element.
        :param self: The position element
        :type self: RecursiveLanePosition
        :return: The nested depth of the element
        :rtype: int
        '''
        return 1 + self.position.get_depth()

    def set_base_position(self, new_position):
        ''' 
        Replaces the base position of the position element.
        :param self: The current position element
        :type self: RecursiveLanePosition
        :param new_position: The new base position element
        :type new_position: BasePosition
        '''
        self.position.set_base_position(new_position)

    def add_level(self, new_position):
        ''' 
        Addes another nested level to the position.
        :param self: The current position element
        :type self: RecursiveLanePosition
        :param new_position: The new base position element
        :type new_position: BasePosition
        '''
        if(isinstance(self.position, BasePosition)):
            added_position = RecursiveLanePosition(self.position.lane_id, new_position)
            self.position = added_position
        else:
            self.position.add_level(new_position)
            

class BasePosition(LanePosition):
    '''The data structure for storing the index of a lane as a position'''
    lane_id = 0
    position = 0

    def __init__(self, lane, position):
        self.lane_id = lane
        self.position = position

    def __eq__(self, other):
        return type(self) == type(other) and (self.lane_id == other.lane_id) and (self.position == other.position)

    def __str__(self):
        return "B(" + str(self.lane_id) + ", " + str(self.position) + ")"

    def get_base_index(self):
        ''' 
        Gets the horizontal index of the position element.
        :param self: The position element
        :type self: BasePosition
        :return: The index of the base position
        :rtype: int
        '''
        return self.position

    def apply_shift(self, offset):
        ''' 
        Shifts the horizontal index by a given offset.
        :param self: The position element
        :type self: BasePosition
        :param offset: The offset
        :type offset: int
        '''
        self.position  += offset


    def get_depth(self):
        ''' 
        Gets the vertical_depth of the element.
        :param self: The position element
        :type self: BasePosition
        :return: The nested depth of the element
        :rtype: int
        '''
        return 1

    def set_base_position(self, new_position):
        ''' 
        Replaces the base position.
        :param self: The position element
        :type self: BasePosition
        :param new_position: The new position element
        :type new_position: BasePosition
        '''
        self = new_position



class ExtractedVariant:
    '''The data structure of a variant with extracted lanes'''
    object_types  = {}
    lanes = []
    interaction_points = {}
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
    
    def get_lanes_of_type(self, object_type):
        '''
        Returns all lanes of the variant that correspond to object instances of the given object type
        :param self: The variant
        :type variant: ExtractedVariant
        :param object_type: The object type label
        :type object_type: str
        :return: A list of type VariantLane
        :rtype: list
        '''
        return [lane for lane in self.lanes if lane.object_type == object_type]
    
    def get_lane(self, lane_id):
        '''
        Returns the lane of the variant with the given lane id
        :param self: The variant
        :type variant: ExtractedVariant
        :param lane_id: The lane id
        :type lane_id: int
        :return: The VariantLane with the given id
        :rtype: VariantLane
        '''
        for lane in self.lanes:
            if (lane.lane_id == lane_id):
                return lane
        return None

    def to_super_variant(self):
        return SVD.SummarizedVariant([lane.to_super_lane(self.interaction_points) for lane in self.lanes], self.object_types, self.interaction_points, self.frequency)


def extract_lanes(variant, frequency):
    '''
    Extracts the variant from the corresponding variant layouting and its frequency
    :param variant: The layouting of a variant
    :type variant: dict
    :param frequency: The relative frequency of the variant
    :type frequency: float
    :return: The extracted variant
    :rtype: ExtractedVariant
    '''

    objects = variant[1]
    events = sorted(variant[0],key=lambda x: (x[1][0]))
    
    extracted_lanes = []
            
    for i in range(len(objects)):
        lane = []
        positions = []
        for j in range(len(events)):
            if(i in events[j][1][1]):
                lane.append(events[j][0])
                positions.append(events[j][1][0][0])    
        
        extracted_lanes.append(VariantLane(i, objects[i][0], objects[i][1], lane, positions))
        
    extracted_interactions = []
    for i in range(len(events)):
        if (len(events[i][1][1]) > 1):
            types = []
            for j in range(len(events[i][1][1])):
                types.append(objects[events[i][1][1][j]][0])
            extracted_interactions.append(InteractionPoint(events[i][0], events[i][1][1], set(types), events[i][1][0][0], [BasePosition(0,events[i][1][0][0]) for event in events[i][1][1]]))
    
    extracted_types = set([object[0] for object in objects.values()])
    extracted_variant = ExtractedVariant(extracted_lanes, extracted_types, extracted_interactions, frequency)
    return extracted_variant


def is_interaction_point(interactions, lane, position):
    '''
    Determines whether the activity in a certain lane at a given position is an interaction point
    :param interactions: The interaction points of the corresponding variant
    :type interaction: list of type InteractionPoint
    :param lane: The lane id
    :type lane: tuple
    :param position: The position index
    :type position: int
    :return: Whether the activity at the position is an interaction point, The corresponding interaction point
    :rtype: bool, InteractionType
    '''
    for interaction in interactions:
        for i in range(len(interaction.interaction_lanes)):
            if(i in range(len(interaction.exact_positions))):
                if ((interaction.interaction_lanes[i] == lane) and (interaction.exact_positions[i] == position)):
                    return True, interaction
    return False, None



def get_interaction_points(interactions, lane, position):
    '''
    Determines all interaction points given at a position in a certain lane.
    :param interactions: The interaction points of the corresponding variant
    :type interaction: list of type InteractionPoint
    :param lane: The lane id
    :type lane: tuple
    :param position: The position index
    :type position: int
    :return: The list of all found interaction points
    :rtype: list
    '''

    result = []
    for interaction in interactions:
        for i in range(len(interaction.interaction_lanes)):
            if(i in range(len(interaction.exact_positions))):
                if ((interaction.interaction_lanes[i] == lane) and (interaction.exact_positions[i] == position)):
                    result.append(interaction)
    return result
