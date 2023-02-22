import matplotlib.pyplot as plt
import matplotlib.patches as patches
import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED
from enum import Enum

DEFAULT_CHEVRON_LENGTH = 30.
DEFAULT_CHEVRON_HEIGHT = 15.
OUTLINE_INTERACTIONS = False
MARK_INCORRECT_INTERACTIONS = False

class Mode(Enum):
    LANE_FREQUENCY = 1
    ACTIVITY_FREQUENCY = 2
    NO_FREQUENCY = 3

current_annotations = []

def visualize_super_variant(super_variant, suppression_char = "*", mode = Mode.ACTIVITY_FREQUENCY):
    '''
    Visualizes a Super Variant using sequentially aligned chevrons.
    :param super_variant: The Super Variant that should be visualized
    :type super_variant: SummarizedVariant
    :param suppression_char: The character used to suppress cardinalities greater 1
    :type suppression_char: str
    :param mode: One of the available modes for displaying frequencies
    :type mode: Mode
    '''
    if(len(super_variant.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    else:

        fig, ax = plt.subplots()
        ax, width, height = arrange_super_variant(super_variant, ax, 0, 0, suppression_char, mode, 9, 9, 13)
        ax.set_aspect('equal')
        ax.set_xlim(-20, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')

        if(mode == Mode.LANE_FREQUENCY):

            annotate = ax.annotate("", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50))
            ax.figure.texts.append(ax.texts.pop())

            def hover_tooltip(event):
                annotation_visbility = annotate.get_visible()
                if event.inaxes == ax:
                    
                    event_position = (round(event.xdata), round(event.ydata))
                    positions = [(round(position[0][0]),round(position[0][1])) for position in current_annotations]

                    for i in range(len(positions)):
                        if is_inside(positions[i], 2, event_position):
                            annotate.xy = current_annotations[i][0]
                            annotate.set_text(current_annotations[i][1])
                            annotate.set_fontsize(current_annotations[i][2])
                            annotate.set_visible(True)
                            fig.canvas.draw_idle()

                        elif(annotation_visbility):
                            annotate.set_visible(False)
                            fig.canvas.draw_idle()
                            
            fig.canvas.mpl_connect('motion_notify_event', hover_tooltip)

        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        plt.show()
        fig.savefig("SingleSuperVariants/SuperVariant_" + str(super_variant.id) + ".svg")


def is_inside(circle_xy, rad, xy):
    '''
    Checks if a point is within the radius of another point.
    :param circle_xy: The center of the circle
    :type circle_xy: tuple
    :param rad: The radius of the circle
    :type rad: float
    :param xy: The point coordinates
    :type xy: tuple
    :return: Whether the point is inside the circle
    :rtype: bool
    '''

    return ((xy[0] - circle_xy[0]) * (xy[0] - circle_xy[0]) +
        (xy[1] - circle_xy[1]) * (xy[1] - circle_xy[1]) <= rad * rad)



def visualize_variant(variant, mode = Mode.NO_FREQUENCY):
    '''
    Visualizes a variant using sequentially aligned chevrons.
    :param variant: The variant that should be visualized
    :type variant: ExtractedVariant
    :param mode: One of the available modes for displaying frequencies
    :type mode: mode
    '''
    if(len(variant.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    else:
        super_variant = variant.to_super_variant()
        fig, ax = plt.subplots()
        ax, width, height =  arrange_super_variant(super_variant, ax, 0, 0, "", mode, 9, 9, 13)
        ax.set_aspect('equal')
        ax.set_xlim(-20, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')

        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        plt.show()


def arrange_super_variant(super_variant, ax, vertical_start_position, horizontal_start_position, suppression_char, mode, fontsize_title, fontsize_activities, cut_off_point):
    '''
    Generates the visualization of a Super Variant.
    :param super_variant: The Super Variant that should be visualized
    :type super_variant: SummarizedVariant
    :param ax: The visualization region in which the Super Variant should be visualized
    :type ax: axes
    :param vertical_start_position: The y-value of the lower-left corner of the first activity chevron
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value of the lower-left corner of the first activity chevron
    :type horizontal_start_position: float
    :param suppression_char: The character used to suppress cardinalities greater 1
    :type suppression_char: str
    :param mode: One of the available modes for displaying frequencies
    :type mode: mode
    :param fontsize_title: The fontsize of the title
    :type fontsize_title: float
    :param fontsize_activities: The fontsize of the activity labels
    :type fontsize_activities: float
    :param cut_off_point: The maximal length an activity label can have
    :type cut_off_point: int
    :return: The visualization region with the added Super Variant visualization elements as well as its width and height
    :rtype: axes, float, float
    '''
    import copy
    all_colors = [(1,0.71,0.44), (0.56,0.81,0.56), (0.38,0.57,0.8), (1,0.87,143), (0.56,0.89,0.97)]
    objects = list(super_variant.object_types)
    objects.sort()
    number_of_object_types = len(objects)
    type_colors = all_colors[:number_of_object_types]
    color_assignment_types = dict(zip(objects, type_colors))

    lane_properties = dict()
    maximal_lane_length = 1
    for type in super_variant.object_types:
        type_lanes = [lane for lane in super_variant.lanes if lane.object_type == type]
        color = color_assignment_types[type]
        offset = 0.09
        scale = 0.9
        for lane in type_lanes:
            lane_properties[lane.lane_id] = dict()
            lane_properties[lane.lane_id]["Color"] = scale_lightness(color, scale)
            scale += offset
            vertical_height = 1

            for elem in lane.elements:
                if (isinstance(elem, SVD.GeneralChoiceStructure)):
                    vertical_height = max(vertical_height, elem.get_vertical_height())
                    maximal_lane_length = max(maximal_lane_length, elem.index_end)

                else:
                    maximal_lane_length = max(maximal_lane_length, elem.index)
                    
            lane_properties[lane.lane_id]["Height"] = vertical_height
            lane_properties[lane.lane_id]["IsOptional"] = isinstance(lane, SVD.OptionalSuperLane)
            lane_properties[lane.lane_id]["Frequency"] = lane.frequency

    
    current_vertical_position = vertical_start_position

    for i in range(len(super_variant.lanes)):

        lane_id = super_variant.lanes[i].lane_id
        color = lane_properties[lane_id]["Color"]
        if(super_variant.lanes[i].cardinality != "1"):
            cardinality = suppression_char
        else:
            cardinality = super_variant.lanes[i].cardinality

        ax.text(-20 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, cardinality, zorder = 10, fontsize = fontsize_title)
        split_label = super_variant.lanes[i].lane_name.split(" ")
        if (len(split_label[0]) > 8):
            label = split_label[0][:8] + ". " + split_label[-1]
        else:
            label = super_variant.lanes[i].lane_name

        ax.text(-14 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, label, zorder = 10, fontsize = fontsize_title)
        
        if(lane_properties[lane_id]["IsOptional"]):
            ax.add_patch(patches.Rectangle((-15 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length + 2) * DEFAULT_CHEVRON_LENGTH, lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0, hatch='///'))
        else:
            ax.add_patch(patches.Rectangle((-15 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length + 2) * DEFAULT_CHEVRON_LENGTH, lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0))
        
        properties = copy.deepcopy(lane_properties)
        ax = __visualize_lane_elements(ax, lane_id, super_variant.lanes[i].elements, properties, copy.deepcopy(super_variant.interaction_points), current_vertical_position, horizontal_start_position, mode, fontsize_activities, cut_off_point)
        current_vertical_position += lane_properties[lane_id]["Height"]
    

    ax.text(-15 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.7 * 9 / fontsize_title, "Frequency: " + str(round(super_variant.frequency, 3)), zorder = 10, fontsize = fontsize_title)
    ax.text(-15 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 5 * 9 / fontsize_title, "Super Variant: " +str(super_variant.id), zorder = 10, fontsize = fontsize_title * 1.2, fontweight = 'bold')

    width = (maximal_lane_length + 1) * DEFAULT_CHEVRON_LENGTH - horizontal_start_position
    height = current_vertical_position * DEFAULT_CHEVRON_HEIGHT - vertical_start_position + 5 * 9 / fontsize_title
    return ax, width, height

def __visualize_lane_elements(ax, lane, elements, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, mode, fontsize, cut_off_point, chevron_length = DEFAULT_CHEVRON_LENGTH, chevron_height = DEFAULT_CHEVRON_HEIGHT, offset = 0, frequency = False, original_lane = None, original_lane_properties = None):
    '''
    Generates the chevrons for a single SuperLane at a given position.
    :param ax: The visualization region in which the Super Variant should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given elements, used as a key for the dictionary
    :type lane: int
    :param element: The elements that should be visualized
    :type element: list of type SummarizationElement
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value of the lower-left corner of the first activity chevron
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value of the lower-left corner of the first activity chevron
    :type horizontal_start_position: float
    :param mode: One of the available modes for displaying frequencies
    :type mode: mode
    :param fontsize: The fontsize of the activity labels
    :type fontsize: float
    :param cut_off_point: The maximal length an activity label can have
    :type cut_off_point: int
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param offset: The offset substracted from the element indices
    :type offset: int
    :param frequency: Whether the frequency of the elements should be displayed
    :type frequency: bool
    :return: The visualization region with the added sequential activity chevrons
    :rtype: axes
    '''
    import copy

    if(original_lane == None):
        original_lane = lane
    if(original_lane_properties == None):
        original_lane_properties = lane_properties

    for element in elements:
        properties = copy.deepcopy(lane_properties)
        if(isinstance(element, SVD.InteractionConstruct)):
            ax = __interaction_activity_chevron(ax, lane, element, element.index - offset, properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, original_lane, original_lane_properties, mode, cut_off_point)
        elif(isinstance(element, SVD.CommonConstruct)):
            ax = __common_activity_chevron(ax, lane, element, element.index - offset, properties, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, mode, cut_off_point)
        else:
            ax = __choice_structure_chevron(ax, lane, element, element.index_start - offset, properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, fontsize, original_lane, original_lane_properties, mode, cut_off_point)
    return ax


def __interaction_activity_chevron(ax, lane, element, index, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, original_lane, original_lane_properties, mode, cut_off_point, overall_line_style = '-'):
    '''
    Generates the chevrons for a single InteractionConstruct element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: InteractionConstruct
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param frequency: The frequency label of the activity
    :type frequency: str
    :param fontsize: The fontsize for the activity label
    :type fontsize: bool
    :param original_lane: The high-level id of the lane
    :type original_lane: tuple
    :param original_lane_properties: The properties of the high-level Super Lane
    :type original_lane_properties: dict
    :param mode: One of the available modes for displaying frequencies
    :type mode: mode
    :param cut_off_point: The maximal length an activity label can have
    :type cut_off_point: int
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches
    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'

    outline_color = "black"
    is_interacting, interaction_point = IED.is_interaction_point(interaction_points, original_lane, element.position)
    
    if(not is_interacting):
        interacting_lanes = [[original_lane]]
        print("Interaction not found.")
        outline_color = "red"

    else:
        all_interaction_points = IED.get_interaction_points(interaction_points, original_lane, element.position)
        if(len(all_interaction_points) == 1):
            interacting_lanes = [interaction_point.interaction_lanes]
            if(len(set([position.get_base_index() for position in interaction_point.exact_positions])) > 1):
                outline_color = "red"
        else:
            interacting_lanes = [all_interaction_points[0].interaction_lanes]
            for i in range(1, len(all_interaction_points)):
                interacting_lanes.append(all_interaction_points[i].interaction_lanes)
                if(len(set([position.get_base_index() for position in all_interaction_points[i].exact_positions])) > 1):
                    outline_color = "red"


    label = element.activity
    heigth_offset = 0.3
    length_offset = 2.0

    if(len(label) > cut_off_point):
        label = label[: cut_off_point - 2] + "..."
    sizing_factor = 1

    if(frequency and mode == Mode.ACTIVITY_FREQUENCY):
        label += "\n " + str(round(element.frequency * 100, 2)) + "%"
        heigth_offset += 3 * chevron_length/DEFAULT_CHEVRON_LENGTH

    ax.text(index * chevron_length + length_offset + current_horizontal_position, current_vertical_position * chevron_height + 0.5 * chevron_height * lane_properties[lane]["Height"] - heigth_offset, label, zorder = 15, fontsize = fontsize * sizing_factor)

    if(OUTLINE_INTERACTIONS):
        line_width = 0.25
    else:
        line_width = 0

    sub_height = 1 / len(interacting_lanes)
    current_percentage = 0
    for interacting_lanes_list in interacting_lanes:
        number_sub_chevrons = len(interacting_lanes_list)
        length_sub_chevron = (1 / number_sub_chevrons)
   
        interacting_lanes_list.sort(key = lambda x: original_lane_properties[x]["Color"])

        for i in range(len(interacting_lanes_list)):
            color = original_lane_properties[interacting_lanes_list[i]]["Color"]
            ax.add_patch(patches.PathPatch(__partial_chevron_at_position(current_horizontal_position + index * chevron_length + i * length_sub_chevron * chevron_length, current_vertical_position * chevron_height, length_sub_chevron * chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height, current_percentage, current_percentage + sub_height), facecolor = color, lw = line_width, ls = overall_line_style, zorder = 10))
        
        current_percentage += sub_height

    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = "None", lw = 1.3 * fontsize / 9, ls = overall_line_style, zorder = 12, edgecolor = outline_color))
    
    return ax

def __common_activity_chevron(ax, lane, element, index, lane_properties, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, mode, cut_off_point, overall_line_style = '-'):
    '''
    Generates the chevrons for a single CommonConstruct element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: CommonConstruct
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param frequency: The frequency label of the activity
    :type frequency: bool
    :param fontsize: The fontsize for the activity label
    :type fontsize: int
    :param mode: One of the available modes for displaying frequencies
    :type mode: mode
    :param cut_off_point: The maximal length an activity label can have
    :type cut_off_point: int
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches

    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'
        
    label = element.activity
    height_offset = 0.3
    length_offset = 2.0
    
    if(len(label) > cut_off_point):
        label = label[: cut_off_point - 2] + "..."
    sizing_factor = 1

    if(frequency and mode == Mode.ACTIVITY_FREQUENCY):
        label += "\n " + str(round(element.frequency * 100, 2)) + "%"
        height_offset += 3 * chevron_length/DEFAULT_CHEVRON_LENGTH

    ax.text(current_horizontal_position + index * chevron_length + length_offset, current_vertical_position * chevron_height + 0.5 * chevron_height * lane_properties[lane]["Height"] - height_offset, label, zorder = 15, fontsize = fontsize * sizing_factor)
    
    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = lane_properties[lane]["Color"], lw = 1.3 * fontsize / 9, ls = overall_line_style, zorder = 10))
    return ax


def __choice_structure_chevron(ax, lane, element, index, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, fontsize, original_lane, original_lane_properties, mode, cut_off_point, overall_line_style = '-'):
    '''
    Generates the chevrons for a single GenericChoiceStructure element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: GenericChoiceStructure
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param fontsize: The fontsize for the activity label
    :type fontsize: int
    :param original_lane: The high-level id of the lane
    :type original_lane: tuple
    :param original_lane_properties: The properties of the high-level Super Lane
    :type original_lane_properties: dict
    :param mode: One of the available modes for displaying frequencies
    :type mode: MODE
    :param cut_off_point: The maximal length an activity label can have
    :type cut_off_point: int
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches
    import copy

    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'


    if(isinstance(element, SVD.OptionalConstruct)):
        margin_length = 0.0
    else:
        margin_length = 0.3

    margin_height = chevron_height * 1/12
    
    offset = element.index_start - index

    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, ((element.index_end - element.index_start) + 1) * chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = "None", lw = 1 * fontsize / 9, ls = overall_line_style, zorder = 5))
    
    overall_line_style = "-"

    choice_properties = dict()
    accumulated_height = 0

    for choice in element.choices:

        choice_properties[choice.lane_id] = dict()
        choice_properties[choice.lane_id]["Color"] = lane_properties[lane]["Color"]
        choice_properties[choice.lane_id]["IsOptional"] = isinstance(element, SVD.OptionalConstruct)
        choice_properties[choice.lane_id]["Frequency"] = choice.frequency

        vertical_height = 1
        for elem in choice.elements:
            if (isinstance(elem, SVD.GeneralChoiceStructure)):
                vertical_height = max(vertical_height, elem.get_vertical_height())

        choice_properties[choice.lane_id]["Height"] = copy.deepcopy(vertical_height)
        accumulated_height += vertical_height

    height_factor = (lane_properties[lane]["Height"] / accumulated_height)

    sub_default_chevron_length = ((((element.index_end - element.index_start) + 1) * chevron_length) - 2) / ((element.index_end - element.index_start) + 1)
    sub_default_chevron_length -= margin_length / ((element.index_end - element.index_start) + 1)

    sub_default_chevron_height = chevron_height * height_factor
    sub_default_chevron_height -=  1/6 * chevron_height

    vertical_half = 1/2 * lane_properties[lane]["Height"]  * chevron_height
    chevron_vertical_half = current_vertical_position * chevron_height + vertical_half

    vertical_position = (current_vertical_position * chevron_height)
    for i in range(len(element.choices)):
        choice = element.choices[i].lane_id

        if (vertical_position != current_vertical_position * chevron_height):
            if(vertical_position <= chevron_vertical_half):
                line_offset = (vertical_position - current_vertical_position * chevron_height)/vertical_half * 1.25
            else:
                line_offset = 1.25 - (vertical_position - chevron_vertical_half)/vertical_half * 1.25
            ax.add_patch(patches.PathPatch(__line_at_position(current_horizontal_position  + index * chevron_length + line_offset, vertical_position, ((element.index_end - element.index_start) + 1) * chevron_length / DEFAULT_CHEVRON_LENGTH), lw = 1.1 * fontsize / 9, ls = overall_line_style, zorder = 15))

        horizontal_start_position = current_horizontal_position + (index * chevron_length) + 1 + margin_length

        ax = __visualize_lane_elements(ax, choice, element.choices[i].elements, copy.deepcopy(choice_properties), interaction_points, ((vertical_position + margin_height * choice_properties[choice]["Height"]) / sub_default_chevron_height), horizontal_start_position, mode, fontsize * (sub_default_chevron_length / DEFAULT_CHEVRON_LENGTH), cut_off_point, chevron_length = sub_default_chevron_length, chevron_height = sub_default_chevron_height, offset = offset + index, frequency = True, original_lane = original_lane, original_lane_properties = original_lane_properties)
        
        if(mode == Mode.LANE_FREQUENCY):
            frequency = choice_properties[choice]["Frequency"]/lane_properties[lane]["Frequency"]
            frequency = str(round(frequency * 100, 2)) + "%"
            ax.plot(horizontal_start_position + 0.8 * chevron_length/DEFAULT_CHEVRON_LENGTH, vertical_position + choice_properties[choice]["Height"] * chevron_height * height_factor - 0.8 * chevron_length/DEFAULT_CHEVRON_LENGTH, 'kv', zorder = 25, markersize = 8 * chevron_length/DEFAULT_CHEVRON_LENGTH)
           
            current_annotations.append(((horizontal_start_position + 0.8 * chevron_length/DEFAULT_CHEVRON_LENGTH, vertical_position + choice_properties[choice]["Height"] * chevron_height * height_factor - 1 * chevron_length/DEFAULT_CHEVRON_LENGTH), frequency, 8 * chevron_length/DEFAULT_CHEVRON_LENGTH))
        
        vertical_position += choice_properties[choice]["Height"] * chevron_height * height_factor

    return ax



def scale_lightness(rgb, scale_l):
    '''
    Scales the lightness of a RGB color given a lightness factor.
    :param rgb: The color that is scaled
    :type rgb: tuple
    :param scale_l: The lightness scaling factor
    :type scale_l: float
    :return: The scaled color
    :rtype: tuple
    '''
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, min(1, l * scale_l), s = s)


def __chevron_at_position(horizontal_index, vertical_index, length, height):
    '''
    Generates a vector drawing of a chevron at a given position with a given length and height.
    :param horizontal_index: The x-value of the position
    :type horizontal_index: float
    :param vertical_index: The y-value of the position
    :type vertical_index: float
    :param length: A factor scaling the length of the chevron
    :type length: int
    :param height: A factor scaling the height of the chevron
    :type height: int
    :return: The chevron as a path instance
    :rtype: path
    '''
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),  # Left bottom corner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),  # Right bottom corner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length + 1.25, vertical_index + height / 2), # Outer tip of chevron
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index + height),  # Right top corner
       (horizontal_index, vertical_index + height),  # Left bottom corner
       (horizontal_index + 1.25, vertical_index + height / 2), # Inner tip of chevron
       (horizontal_index, vertical_index),  # Left bottom corner
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]

    return Path(verts, codes)

def __partial_chevron_at_position(horizontal_index, vertical_index, length, height, start_percentage, end_percentage):
    '''
    Generates a vector drawing of a chevron at a given position with a given length and height.
    :param horizontal_index: The x-value of the position
    :type horizontal_index: float
    :param vertical_index: The y-value of the position
    :type vertical_index: float
    :param length: A factor scaling the length of the chevron
    :type length: int
    :param height: A factor scaling the height of the chevron
    :type height: int
    :return: The chevron as a path instance
    :rtype: path
    '''
    from matplotlib.path import Path
    if (start_percentage >= 0.5):
        verts = [
        (horizontal_index + 1.25 - (start_percentage - 0.5) * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        (horizontal_index + 1.25 - (start_percentage - 0.5) * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + start_percentage * height),  # Right bottom corner
        (horizontal_index + 1.25 - (end_percentage - 0.5) * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + end_percentage * height), # Right upper corner
        (horizontal_index + 1.25 - (end_percentage - 0.5) * 2.5, vertical_index + end_percentage * height),  # Left upper corner
        (horizontal_index + 1.25 - (start_percentage - 0.5) * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        ]

        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

    elif (end_percentage <= 0.5):
        verts = [
        (horizontal_index + start_percentage * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        (horizontal_index + start_percentage * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + start_percentage * height),  # Right bottom corner
        (horizontal_index + end_percentage * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + end_percentage * height), # Right upper corner
        (horizontal_index + end_percentage * 2.5, vertical_index + end_percentage * height),  # Left upper corner
        (horizontal_index + start_percentage * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        ]

        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

    else:
        verts = [
        (horizontal_index + start_percentage * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        (horizontal_index + start_percentage * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + start_percentage * height),  # Right bottom corner
        (horizontal_index + DEFAULT_CHEVRON_LENGTH * length + 1.25, vertical_index + height / 2), # Outer tip of chevron
        (horizontal_index + 1.25 - (end_percentage - 0.5) * 2.5 + DEFAULT_CHEVRON_LENGTH * length, vertical_index + end_percentage * height), # Right upper corner
        (horizontal_index + 1.25 - (end_percentage - 0.5) * 2.5, vertical_index + end_percentage * height),  # Left upper corner
        (horizontal_index + 1.25, vertical_index + height / 2), # Inner tip of chevron
        (horizontal_index + 1.25 - (start_percentage - 0.5) * 2.5, vertical_index + start_percentage * height),  # Left bottom corner
        ]

        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

    return Path(verts, codes)


def __line_at_position(horizontal_index, vertical_index, length):
    '''
    Generates a vector drawing of a line at a given position with a given length.
    :param horizontal_index: The x-value of the position
    :type horizontal_index: float
    :param vertical_index: The y-value of the position
    :type vertical_index: float
    :param length: A factor scaling the length of the line
    :type length: int
    :return: The line as a path instance
    :rtype: path
    '''
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
    ]

    return Path(verts, codes)



