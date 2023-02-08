#from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Intra_Variant_Summarization as IAVS
import Summarization_Selection as SS
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH


filename = "EventLogs/BPI2017-Top10.jsonocel"
parameters = {"execution_extraction": "leading_type",
              "leading_type": "application"}
ocel = ocel_import_factory.apply(file_path = filename , parameters = parameters)
#filename = "EventLogs/order_process.jsonocel"
#ocel = ocel_import_factory.apply(file_path = filename)
#variant_layouting = variants_visualization_factory.apply(ocel)
#extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[2]], ocel.variant_frequencies[1])
#SVV.visualize_variant(extracted_variant)
all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization(ocel, print_results = False)
summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

#print(summarizations[0])
#print(summarizations[0].interaction_points)
#for interaction in summarizations[0].interaction_points:
    #for position in interaction.exact_positions:
        #print(position)
    #print("------")

#for i in range(len(summarizations)-1):
    #for j in range(i+1, len(summarizations)):
        #super_variant, cost = IEVS.join_super_variants(summarizations[i], summarizations[j], False, False)
        #print(i)
        #print(j)
        #print(super_variant)
        #SVV.visualize_super_variant(super_variant)

SVV.visualize_super_variant(summarizations[5])
#SVV.visualize_super_variant(summarizations[8])

#super_variant_49, cost = IEVS.join_super_variants(summarizations[1], summarizations[7], False)
super_variant_59, cost = IEVS.join_super_variants(summarizations[5], summarizations[8], True, False)
#super_variant_67, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False)
#super_variant_8, cost = IEVS.join_super_variants(super_variant_59, summarizations[3], False, False)
#super_variant, cost = IEVS.join_super_variants(super_variant_8, summarizations[8], True, False)
#print(super_variant)

#SVV.visualize_super_variant(super_variant)
# SVH.visualize_Super_Variant_layer([super_variant_59, super_variant])

#'''
for interaction in summarizations[5].interaction_points:

    print(str([str(position) for position in interaction.exact_positions]), str(interaction.interaction_lanes))
    print("----")

#for interaction in summarizations[6].interaction_points:

    #print(str([str(position) for position in interaction.exact_positions]), str(interaction.interaction_lanes))
    #print("----")

for lane in summarizations[5].lanes:
    print(lane)
#'''

#SVV.visualize_super_variant(summarizations[5])
#SVV.visualize_super_variant(summarizations[7])
#SVV.visualize_super_variant(summarizations[5])
#super_variant_459, cost = IEVS.join_super_variants(super_variant_49, summarizations[4], False)
#SVV.visualize_super_variant(super_variant)
#SVV.visualize_super_variant(summarizations[6])
#SVV.visualize_super_variant(super_variant_59)
#SVV.visualize_super_variant(summarizations[7])
#SVV.visualize_super_variant(super_variant)
#hierarchy = IEVG.generate_super_variant_hierarchy_uniform(summarizations[0:7], 3)
#classification = SVG.classify_initial_super_variants_by_expression(summarizations[0:8], SVG.containes_3_payment_reminder)
#classification = SVG.classify_initial_super_variants_by_activity(summarizations[0:8], "Payment Reminder")
#hierarchy = IEVG.generate_super_variant_hierarchy(summarizations[0:7], 3, print_results = False , frequency_distribution_type = IEVG.Distribution.UNIFORM)
#for summarization in summarizations:
 #   SVV.visualize_super_variant(summarization)

#variant_layouting = variants_visualization_factory.apply(ocel)
#extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[5]], ocel.variant_frequencies[5]) # Extract the variants frequency
#extracted_summarizations = WVSU.within_variant_summarization(extracted_variant, False)
#for summarization in extracted_summarizations:
    #SVV.visualize_super_variant(summarization)

#for i in range(len(summarizations)):
    #for j in range(i+1, len(summarizations)):
        #super_variant_ij, cost = BVS.join_super_variants(summarizations[i], summarizations[j], False)
        #SVV.visualize_super_variant(super_variant_ij)
#SVV.visualize_super_variant(summarizations[4])

#SVV.visualize_super_variant(summarizations[1])
#SVV.visualize_super_variant(summarizations[10])
#super_variant_14, cost = BVS.join_super_variants(summarizations[3], summarizations[5], True)
#super_variant_12, cost = BVS.join_super_variants(summarizations[7], summarizations[8], True)
#super_variant_1214, cost = BVS.join_super_variants(super_variant_14, super_variant_12, True)





