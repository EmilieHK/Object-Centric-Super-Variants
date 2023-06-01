from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import Input_Extraction_Definition as IED
import Intra_Variant_Generation as IAVG
import Summarization_Selection as SS
import Super_Variant_Visualization as SVV
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH
import Inter_Lane_Alignment as ILA

VISUALIZE_INTERMEDIATE_RESULTS = False
MODE = 4
ILA.ALIGN = True


# Import event log
filename = "EventLogs/BPI2017-Top10.jsonocel"
ocel = ocel_import_factory.apply(file_path = filename)

# Visualize input variants
if(VISUALIZE_INTERMEDIATE_RESULTS):
    variant_layouting = variants_visualization_factory.apply(ocel)
    variants = []
    for i in range(len(ocel.variants)):
        extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[i])
        variants.append(extracted_variant)
        SVV.visualize_variant(extracted_variant,i)

# Generate and select intra-variant summarizations
all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
intra_variant_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

# Replace with actual frequencies
global_frequencies = [0.069,0.05,0.047,0.03,0.025,0.019,0.019,0.018,0.017,0.016]
for i in range(len(intra_variant_summarizations)):
    intra_variant_summarizations[i].frequency = global_frequencies[i]

# Visualize selected intra-variant summarizations
if(VISUALIZE_INTERMEDIATE_RESULTS):
    for i in range(len(intra_variant_summarizations)):
        SVV.visualize_super_variant(intra_variant_summarizations[i])

if(VISUALIZE_INTERMEDIATE_RESULTS):
    # Visualize intra-variant summarizations of variant v_3
    SVV.MARK_INCORRECT_INTERACTIONS = False
    SVV.visualize_variant(all_summarizations[3][1][1][0],3)
    SVV.visualize_variant(all_summarizations[4][1][1][0],3)
    SVV.MARK_INCORRECT_INTERACTIONS = True


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
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, base = 4)

    # Visualizing each hierarchy bottom-up
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
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, base = 4)

    # Visualizing each hierarchy bottom-up
    for hierarchy in hierarchies:
        SVH.explore_hierarchy_bottom_up(hierarchy)

    # Printing the accumulated summarization costs
    for i in range(len(hierarchies)):
        accumulated_cost = 0

        for level in hierarchies[i].keys():
            accumulated_cost += hierarchies[i][level][1]

        print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))
