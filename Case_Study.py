from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import Input_Extraction_Definition as IED
import Intra_Variant_Generation as IAVG
import Summarization_Selection as SS
import Super_Variant_Visualization as SVV
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH
import Inter_Lane_Alignment as ILA
import Super_Variant_Definition as SVD

def manual_alignment(super_variant,positions,interactions):
    for i in range(len(super_variant.lanes)):
        super_variant.lanes[i] = manual_alignment_l(super_variant.lanes[i], positions[i])

    for k in range(len(super_variant.interaction_points)):
        super_variant.interaction_points[k].index_in_lanes = interactions[k][0]
        for t in range(len(super_variant.interaction_points[k].exact_positions)):
           super_variant.interaction_points[k].exact_positions[t].set_base_index(interactions[k][t])
    return super_variant
        
def manual_alignment_l(lane,positions):
    for j in range(len(lane.elements)):
        if((type(lane.elements[j]) == SVD.CommonConstruct or type(lane.elements[j]) == SVD.InteractionConstruct)):
            lane.elements[j].index = positions[j]
            lane.elements[j].position.set_base_index(positions[j])

        elif((type(lane.elements[j]) == SVD.OptionalConstruct or type(lane.elements[j]) == SVD.ChoiceConstruct)):
            lane.elements[j].index_start = positions[j][0]
            lane.elements[j].position_start.set_base_index(positions[j][0])
            lane.elements[j].index_end = positions[j][1]
            lane.elements[j].position_end.set_base_index(positions[j][1])

            for h in range(len(lane.elements[j].choices)):
                lane.elements[j].choices[h]  = manual_alignment_l(lane.elements[j].choices[h],positions[j][2][h])

    return lane

VISUALIZE_INTERMEDIATE_RESULTS = False
MODE = 4
ILA.ALIGN = False

def custom_alignment(positions, super_variant):
    for lane in super_variant.lanes:
        print()
    

# Import event log
#filename = "EventLogs/BPI2017-Final.csv"
#object_types = ["application","offer"]
#parameters = {"obj_names":object_types,"val_names":[], "act_name":"event_activity","time_name":"event_timestamp","sep":","}
#ocel = ocel_import_factory.apply(file_path = filename, parameters=parameters)
#number_of_processes = len(ocel.process_executions)
#print(number_of_processes)
#for frequency in ocel.variant_frequencies[:10]:
    #print(frequency*number_of_processes)


filename = "EventLogs/P2P.jsonocel"
ocel = ocel_import_factory.apply(file_path = filename)

# Visualize input variants
if(VISUALIZE_INTERMEDIATE_RESULTS):
    variant_layouting = variants_visualization_factory.apply(ocel)
    variants = []
    for i in range(10):
        extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[i])
        variants.append(extracted_variant)
        SVV.visualize_variant(extracted_variant,i)

# Generate and select intra-variant summarizations
all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
intra_variant_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

# Replace with actual frequencies
for i in range(10):
    intra_variant_summarizations[i].frequency = ocel.variant_frequencies[i]

intra_variant_summarizations = intra_variant_summarizations[:10]

# Visualize selected intra-variant summarizations
if(VISUALIZE_INTERMEDIATE_RESULTS):
    for i in range(len(intra_variant_summarizations)):
        SVV.visualize_super_variant(intra_variant_summarizations[i])


' --------------------------------------------------- '

if(MODE == 1):
    # MODE 1 - Frequency Distribution and No Nested Structures
    IEVG.NESTED_STRUCTURES = False
    initial_super_variants = intra_variant_summarizations

    # Generating a 3 hierarchies from the initial super variants with uniform frequency distribution
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, 3, frequency_distribution_type = IEVG.Distribution.UNIFORM)

    # Visualizing each hierarchy top-down
    final_super_variants = final_super_variants[0]
    for final_super_variant in final_super_variants:
        SVH.explore_hierarchy_top_down(final_super_variant)

    # Printing the accumulated summarization costs
    for i in range(len(hierarchies[0])):
        accumulated_cost = 0

        for level in hierarchies[0][i].keys():
            accumulated_cost += hierarchies[0][i][level][1]

        print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))


' --------------------------------------------------- '

if(MODE == 2):
    # MODE 2 - Pre-Classification and Nested Structures
    IEVG.NESTED_STRUCTURES = True
    initial_super_variants = IEVG.classify_initial_super_variants_by_activity(intra_variant_summarizations, "Cancel application")

    if(VISUALIZE_INTERMEDIATE_RESULTS):
        # All initial super variants that contain a "Cancel application" activity
        for summarization in initial_super_variants[0]:
            SVV.visualize_super_variant(summarization)

        # All initial super variants that do not contain a "Cancel application" activity
        for summarization in initial_super_variants[1]:
            SVV.visualize_super_variant(summarization)

    # Generating a hierarchy for both classes of initial super variants
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(initial_super_variants)

    # Visualizing each hierarchy top-down
    for final_super_variant in final_super_variants:
        SVH.explore_hierarchy_top_down(final_super_variant[0])

    # Printing the accumulated summarization costs
    for i in range(len(hierarchies)):
        accumulated_cost = 0

        for level in hierarchies[i].keys():
            accumulated_cost += hierarchies[i][level][1]

        print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))


' --------------------------------------------------- '

if(MODE == 3):
    # MODE 1 - Ultimate Super Variant and Nested Structures
    IEVG.NESTED_STRUCTURES = True
    SVH.MODE = SVH.MODE.NO_FREQUENCY
    initial_super_variants = intra_variant_summarizations

    # Generating a 3 hierarchies from the initial super variants with uniform frequency distribution
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, base = 3)

    for hierarchy in hierarchies:
        SVH.explore_hierarchy_bottom_up(hierarchy)

    # Printing the accumulated summarization costs
    for i in range(len(hierarchies)):
        accumulated_cost = 0

        for level in hierarchies[i].keys():
            accumulated_cost += hierarchies[i][level][1]

        print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))


' --------------------------------------------------- '

if(MODE == 4):
    # MODE 1 - Ultimate Super Variant and No Nested Structures
    IEVG.NESTED_STRUCTURES = False
    SVH.MODE = SVH.MODE.NO_FREQUENCY
    initial_super_variants = intra_variant_summarizations

    # Generating a 3 hierarchies from the initial super variants with uniform frequency distribution
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, base = 2)


    #positions = [[3,4,5,[6,6,[[6]]],7],[4,5,[6,6,[[6]]],7],[[6,6,[[6]]],7],[1,2,3,[6,6,[[6]]],7],[0],[0,1,2]]
    #interactions = [[0,0],[4,4],[1,1],[5,5],[3,3],[2,2],[6,6,6,6],[7,7,7,7]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][2][0][0][0],positions,interactions))

    #positions = [[5,6,7,8],[6,7,8],[0,[1,1,[[1],[1]]]],[8],[3,4,5,8],[0,[1,1,[[1],[1]]],2],[2,3,4]]
    #interactions = [[0,0],[6,6],[2,2],[3,3],[1,1],[1,1],[7,7],[5,5],[4,4],[8,8,8,8]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][2][0][2][0],positions,interactions))

    #positions = [[5,6,7,8],[6,7,8],[0,1],[8],[3,4,5,8],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[6,6],[2,2],[3,3],[1,1],[7,7],[5,5],[4,4],[8,8,8,8]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][1][0][0][0],positions,interactions))

    #positions = [[[5,9,[[5,6,7,8],[7,8,9]]],10],[6,7,[8,9,[[8],[8,9]]],10],[0,1],[[8,8,[[8]]],10],[3,4,5,[7,8,[[8],[7]]],10],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[6,6],[8,8],[2,2],[3,3],[1,1],[7,7],[9,9],[5,5],[4,4],[7,7],[8,8,8,8],[10,10,10,10]]
    #super_variant = manual_alignment(hierarchies[0][1][0][2][0],positions,interactions)
    #for i in range(len(super_variant.interaction_points)):
        #if(i ==2):
            #(super_variant.interaction_points)[i].exact_positions = [IED.RecursiveLanePosition(0,IED.BasePosition(1,8)),(hierarchies[0][1][0][2][0].interaction_points)[i].exact_positions[1]]
        #elif(i==7):
            #(super_variant.interaction_points)[i].exact_positions = [IED.RecursiveLanePosition(0,IED.BasePosition(1,9)),(hierarchies[0][1][0][2][0].interaction_points)[i].exact_positions[1]]
    #SVV.visualize_super_variant(super_variant)

    #positions = [[[5,9,[[5,6,7],[7,8,9]]],10],[6,7,8,9,10],[0,1],[10],[3,4,5,7,10],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[6,6],[2,2],[3,3],[1,1],[7,7],[5,5],[7,7],[4,4],[8,8],[9,9],[10,10,10,10]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][1][0][3][0],positions,interactions))

    #positions = [[5,6,7,8],[6,7,8],[0,1],[8],[3,4,5,8],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[6,6],[2,2],[3,3],[1,1],[7,7],[5,5],[4,4],[8,8,8,8]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][1][0][4][0],positions,interactions))

    #positions = [[[5,9,[[7,8,9],[5,6,7]]],10],[6,7,8,9,10],[0,1],[10],[3,4,5,7,10],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[0,0],[3,3],[5,5],[7,7],[1,1],[1,1],[2,2],[4,4],[6,6],[8,8],[7,7],[9,9],[10,10,10,10],[10,10,10,10]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][0][0][5][0],positions,interactions))

    #positions = [[[5,9,[[7,8,9],[5,6,7]]],10],[6,7,8,9,10],[0,1],[10],[3,4,5,7,10],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[0,0],[0,0],[3,3],[5,5],[7,7],[1,1],[1,1],[1,1],[2,2],[4,4],[6,6],[8,8],[7,7],[9,9],[10,10,10,10],[10,10,10,10]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][0][0][8][0],positions,interactions))

    #positions = [[[5,9,[[7,8,9],[5,6,7]]],10],[6,7,8,9,10],[0,1],[10],[3,4,5,7,10],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[0,0],[3,3],[7,7],[5,5],[1,1],[1,1],[2,2],[4,4],[8,8],[9,9],[6,6],[7,7],[10,10,10,10],[10,10,10,10]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][0][0][6][0],positions,interactions))

    #positions = [[5,6,7,8],[6,7,8],[0,1],[8],[3,4,5,8],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[0,0],[3,3],[5,5],[1,1],[1,1],[2,2],[4,4],[6,6],[7,7],[8,8,8,8]]
    #SVV.visualize_super_variant(manual_alignment(hierarchies[0][0][0][9][0],positions,interactions))

    #positions = [[5,6,7,8],[6,7,8],[0,1],[8],[3,4,5,8],[0,1,2],[2,3,4]]
    #interactions = [[0,0],[0,0],[3,3],[5,5],[1,1],[1,1],[2,2],[4,4],[6,6],[7,7],[8,8,8,8]]
    #VV.visualize_super_variant(manual_alignment(hierarchies[0][0][0][2][0],positions,interactions))


    for i in range(len(hierarchies[0][2][0][1][0].interaction_points)):
        print((hierarchies[0][2][0][1][0].interaction_points)[i])
    #for i in range(10):
    SVV.visualize_super_variant(hierarchies[0][2][0][1][0])

    positions = [
    [[5,11,[[7,8,9,11],[9,10,11],[5,6,7]]],12]
    ,[[6,7,[[6,7]]],8,9,[10,11,[[11],[10,11]]],12]
    ,[0,1]
    ,[[11,11,[[11]]],12]
    ,[3,4,[5,5,[[5]]],7,[9,11,[[11],[9]]],12]
    ,[0,1,2]
    ,[2,3,4]]
    interactions = [[0,0],[6,6],[2,2],[3,3],[1,1],[7,7],[5,5],[4,4],[8,8],[7,7],[9,9],[9,9],[11,11,11,11],[12,12,12,12]]
    super_variant = manual_alignment(hierarchies[0][2][0][1][0],positions,interactions)
    #super_variant.interaction_points.append(IED.InteractionPoint('Create Invoice Receipt',lanes,('invoice receipt','goods receipt'),10,[IED.]))
    SVV.visualize_super_variant(super_variant)





    # Visualizing each hierarchy bottom-up
    #for hierarchy in hierarchies:
        #SVH.explore_hierarchy_bottom_up(hierarchy)

    # Printing the accumulated summarization costs
    #for i in range(len(hierarchies)):
        #accumulated_cost = 0

        #for level in hierarchies[i].keys():
            #accumulated_cost += hierarchies[i][level][1]

        #print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))



                
                    