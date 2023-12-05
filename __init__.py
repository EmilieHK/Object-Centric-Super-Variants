from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.filtering.log import variant_filtering

import Super_Variant_Visualization as SVV
import Summarization_Selection as SS
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Intra_Variant_Summarization as IAVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Input_Extraction_Definition as IED

MODE = 9


'''
lanes_1 = []
elements = [SVD.InteractionConstruct("D",1,IED.BasePosition(0,2), 2)]
realization = SVD.SuperLane(0,"realization_0", "customers", elements, "1", 1, [])
lanes_1.append(SVD.SuperLane(0,"customers_1", "customers",elements,"1",1,[realization]))

elements = [SVD.InteractionConstruct("D",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("G",1,IED.BasePosition(0,3),3), SVD.InteractionConstruct("G",1,IED.BasePosition(0,4),4)]
realization = SVD.SuperLane(0,"realization_0", "items", elements, "1", 1, [])
lanes_1.append(SVD.SuperLane(1,"items_1", "items",elements,"1",1,[realization]))

elements = [SVD.InteractionConstruct("D",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("F",1,IED.BasePosition(0,3),3), SVD.InteractionConstruct("G",1,IED.BasePosition(0,4),4)]
realization = SVD.SuperLane(0,"realization_0", "items", elements, "1", 1, [])
lanes_1.append(SVD.SuperLane(2,"items_2", "items",elements,"1",1,[realization]))

elements = [SVD.CommonConstruct("A",1,IED.BasePosition(0,0),0), SVD.CommonConstruct("B",1,IED.BasePosition(0,1),1), SVD.InteractionConstruct("D",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("E",1,IED.BasePosition(0,3),3)]
realization = SVD.SuperLane(0,"realization_0", "orders", elements, "1", 1, [])
lanes_1.append(SVD.SuperLane(3,"orders_1", "orders",elements,"1",1,[realization]))

interaction_points_1 = [IED.InteractionPoint("D", [0,1,2,3], {"customers","items","orders"},2,[IED.BasePosition(0,2),IED.BasePosition(0,2),IED.BasePosition(0,2),IED.BasePosition(0,2)]), IED.InteractionPoint("G", [1,2], {"items"},4,[IED.BasePosition(0,4),IED.BasePosition(0,4)])]

super_variant_1 = SVD.SuperVariant(tuple()+(1,),lanes_1, {"customers","items","orders"}, interaction_points_1, 0.5)

lanes_2 = []
elements = [SVD.InteractionConstruct("C",1,IED.BasePosition(0,2), 2)]
realization = SVD.SuperLane(0,"realization_0", "customers", elements, "1", 1, [])
lanes_2.append(SVD.SuperLane(5,"customers_1", "customers",elements,"1",1,[realization]))

elements = [SVD.InteractionConstruct("C",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("G",1,IED.BasePosition(0,3),3), SVD.InteractionConstruct("G",1,IED.BasePosition(0,4),4)]
realization = SVD.SuperLane(0,"realization_0", "items", elements, "1", 1, [])
lanes_2.append(SVD.SuperLane(6,"items_1", "items",elements,"1",1,[realization]))

elements = [SVD.InteractionConstruct("C",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("G",1, IED.BasePosition(0,3),3), SVD.InteractionConstruct("G",1,IED.BasePosition(0,4),4)]
realization = SVD.SuperLane(0,"realization_0", "items", elements, "1", 1, [])
lanes_2.append(SVD.SuperLane(7,"items_2", "items",elements,"1",1,[realization]))

elements = [SVD.CommonConstruct("A",1,IED.BasePosition(0,0),0), SVD.CommonConstruct("B",1,IED.BasePosition(0,1),1), SVD.InteractionConstruct("C",1,IED.BasePosition(0,2), 2), SVD.CommonConstruct("E",1,IED.BasePosition(0,3),3)]
realization = SVD.SuperLane(0,"realization_0", "orders", elements, "1", 1, [])
lanes_2.append(SVD.SuperLane(8,"orders_1", "orders",elements,"1",1,[realization]))

interaction_points_2 = [IED.InteractionPoint("C", [5,6,7,8], {"customers","items","orders"},2,[IED.BasePosition(0,2),IED.BasePosition(0,2),IED.BasePosition(0,2),IED.BasePosition(0,2)]), IED.InteractionPoint("G", [6,7], {"items"},4,[IED.BasePosition(0,4),IED.BasePosition(0,4)])]

super_variant_2 = SVD.SuperVariant(tuple()+(2,),lanes_2, {"customers","items","orders"}, interaction_points_2, 0.5)

SVV.visualize_super_variant(super_variant_1, mode= SVV.Mode.NO_FREQUENCY)
SVV.visualize_super_variant(super_variant_2, mode= SVV.Mode.NO_FREQUENCY)

super_variant = IEVS.inter_variant_summarization(super_variant_1,super_variant_2,[(0,5),(1,6),(2,7),(3,8)], False, False)

for interaction_point in super_variant.interaction_points:
    print(interaction_point)

#print(super_variant)
SVV.visualize_super_variant(super_variant, mode=SVV.Mode.NO_FREQUENCY)
'''


filename = "EventLogs/Presentation_Example.jsonocel"
ocel = ocel_import_factory.apply(file_path = filename)

variant_layouting = variants_visualization_factory.apply(ocel)
for i in range(len(ocel.variants)):
    extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[i])
    SVV.visualize_variant(extracted_variant,i)

all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, list(zip(ocel.variants[:4],ocel.variant_frequencies[:4])))
summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)


SVV.visualize_super_variant(all_summarizations[0][1][1][0].to_super_variant(tuple() + (0,)))
SVV.visualize_super_variant(all_summarizations[1][1][1][0].to_super_variant(tuple() + (1,)))
SVV.visualize_super_variant(all_summarizations[2][1][1][0].to_super_variant(tuple() + (1,)))
SVV.visualize_super_variant(all_summarizations[3][1][1][0].to_super_variant(tuple() + (1,)))



super_variant_1, cost = IEVS.join_super_variants(all_summarizations[0][1][1][0].to_super_variant(tuple() + (0,)), all_summarizations[1][1][1][0].to_super_variant(tuple() + (1,)),False, False)
super_variant_2, cost = IEVS.join_super_variants(all_summarizations[2][1][1][0].to_super_variant(tuple() + (0,)), super_variant_1,False, False)
SVV.visualize_super_variant(super_variant_1, mode=SVV.Mode.NO_FREQUENCY)
SVV.visualize_super_variant(super_variant_2, mode=SVV.Mode.NO_FREQUENCY)

#super_variant_3, cost = IEVS.join_super_variants(super_variant_1, super_variant_2,True, False)
#SVV.visualize_super_variant(super_variant_3, mode=SVV.Mode.ACTIVITY_FREQUENCY)


#from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
#filename = "EventLogs/test_log.jsonocel"
#ocel = ocel_import_factory.apply(filename)

#print(len(ocel.process_executions))
#print(len(ocel.variants))

#ocel_filtered = variant_filtering.filter_infrequent_variants(ocel, 0.2)
#print(len(ocel_filtered.variants))
#ocel_export_factory.apply(ocel_filtered, 'EventLogs/PerformanceAnalysis/BPI2017-Filtered_20.jsonocel')




#all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization(ocel)
#summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

#filename = "EventLogs/Thesis_Example.jsonocel"
#ocel = ocel_import_factory.apply(file_path = filename)

#all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
#summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
#print(len(summarizations))
#super_variant, cost = IEVS.join_super_variants(summarizations[0], summarizations[1],True, False)
#SVV.visualize_super_variant(summarizations[0])
#SVV.visualize_super_variant(summarizations[1])
#SVV.visualize_super_variant(super_variant, mode=SVV.Mode.NO_FREQUENCY)

#for super_variant in summarizations:
    #SVV.visualize_super_variant(super_variant)

#variant_layouting = variants_visualization_factory.apply(ocel)
#for i in range(0,11):
    #extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[i])
    #SVV.visualize_variant(extracted_variant)

'''
IEVG.NESTED_STRUCTURES = True
if(MODE == 1):
    initial_super_variants = IEVG.classify_initial_super_variants_by_activity([summarizations[3], summarizations[4], summarizations[6], summarizations[7], summarizations[8], summarizations[9]], "Refuse offer")
    initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(initial_super_variants[1], "Accept offer")
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(initial_super_variants, 1, 3, base = 3)

    for hierarchy in hierarchies:
        SVH.explore_hierarchy_bottom_up(hierarchy)

elif(MODE == 2):
    initial_super_variants = IEVG.classify_initial_super_variants_by_activity([summarizations[3], summarizations[4], summarizations[6], summarizations[7], summarizations[8], summarizations[9]], "Refuse offer")
    initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(initial_super_variants[1], "Accept offer")
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(initial_super_variants, 1, 3, base = 2)
    
    SVH.explore_hierarchy_bottom_up(hierarchies[2])

elif(MODE == 3):
    initial_super_variants = IEVG.classify_initial_super_variants_by_activity([summarizations[3], summarizations[4], summarizations[6], summarizations[7], summarizations[8], summarizations[9]], "Refuse offer")
    initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(initial_super_variants[1], "Accept offer")
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(initial_super_variants, 1, 3, base = 2)
    
    for super_variant in final_super_variants:
        SVH.explore_hierarchy_top_down(super_variant[0])

elif(MODE == 4):
    initial_set = [summarizations[i] for i in range(len(summarizations)) if i != 5]
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_set, 4, frequency_distribution_type = IEVG.Distribution.NORMAL)
    
    for super_variant in final_super_variants[0]:
        SVH.explore_hierarchy_top_down(super_variant)

elif(MODE == 5):
    IEVG.NESTED_STRUCTURES = False
    initial_set = [summarizations[i] for i in range(len(summarizations)) if i not in [0, 2, 5]]
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_set, 1, frequency_distribution_type = IEVG.Distribution.UNIFORM)

    for super_variant in final_super_variants[0]:
        SVH.explore_hierarchy_top_down(super_variant)

elif(MODE == 6):
    super_variant, cost = IEVS.join_super_variants(summarizations[0], summarizations[1], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[6], True, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[7], True, False)

    SVV.visualize_super_variant(super_variant, mode = SVV.Mode.ACTIVITY_FREQUENCY)

elif(MODE == 7):
    super_variant1, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False, False)
    super_variant2, cost = IEVS.join_super_variants(summarizations[9], summarizations[8], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant1, super_variant2, False, False)
    SVV.visualize_super_variant(super_variant, mode = SVV.Mode.LANE_FREQUENCY)

elif(MODE == 8):
    super_variant, cost = IEVS.join_super_variants(summarizations[9], summarizations[5], True, True)
    #super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[7], True, False)
    SVV.visualize_super_variant(super_variant, mode = SVV.Mode.NO_FREQUENCY)
'''
