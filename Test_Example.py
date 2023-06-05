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


filename = "EventLogs/test_log.jsonocel"
ocel = ocel_import_factory.apply(file_path = filename)

'''
variant_layouting = variants_visualization_factory.apply(ocel)
for i in range(len(ocel.variants)):
    extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[i])
    SVV.visualize_variant(extracted_variant,i)
    if(i != 15):
        extracted_summarizations = IAVS.within_variant_summarization(extracted_variant, True)
        for summarization in extracted_summarizations:
            SVV.visualize_super_variant(summarization.to_super_variant(0))

        print("---------------")
'''

all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
summarizations = SS.intra_variant_summarization_selection(all_summarizations,per_variant_dict,per_encoding_dict)

'''
for summarization in summarizations:
    SVV.visualize_super_variant(summarization)


IEVG.NESTED_STRUCTURES = False
initial_super_variants = summarizations[:10]

hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants, 3, frequency_distribution_type = IEVG.Distribution.UNIFORM)

final_super_variants = final_super_variants[0]
for final_super_variant in final_super_variants:
    SVH.explore_hierarchy_top_down(final_super_variant)
'''


initial_super_variants = summarizations[:11]
IEVG.NESTED_STRUCTURES = False

hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(initial_super_variants,3, frequency_distribution_type=IEVG.Distribution.NORMAL)

final_super_variants = final_super_variants[0]
for final_super_variant in final_super_variants:
    SVH.explore_hierarchy_top_down(final_super_variant)