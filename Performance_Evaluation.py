from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory

import Intra_Variant_Generation as IAVG
import Summarization_Selection as SS
import Inter_Variant_Generation as IEVG

import Inter_Variant_Summarization as IEVS
import Intra_Variant_Summarization as IAVS
import Input_Extraction_Definition as IED

from enum import Enum
import time
import csv
import random
import copy
import math


# Always take maximal generalization
class Setting(Enum):

    # For all pairs of the randomly sampled 10 variants
    ALL_SINGLE_INTER = 1

    # For all single variants 
    ALL_SINGLE_INTRA = 2


CURRENT_SETTING = Setting.ALL_SINGLE_INTRA


# Experiment 1: Various Intra-Variant Summarizations
if(CURRENT_SETTING == Setting.ALL_SINGLE_INTRA):

    # Load data
    filename = "EventLogs/P2P.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    variant_layouting = variants_visualization_factory.apply(ocel)

    # Measure times for all intra-variant summarizations
    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict, times = IAVG.complete_intra_variant_summarization_from_process(ocel, get_time = True)
    time_after_intra = time.perf_counter()

    time_before_hitting = time.perf_counter()
    selected_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
    time_after_hitting = time.perf_counter()
    print(time_after_hitting - time_before_hitting)
    # Store and print results and statistics on the input
    #data = []
    #for i in range(len(times)):
        #print("Writing data for variant: " + str(i))
        #number_events = len(variant_layouting[ocel.variants[i]][0])
        #number_application = len([value for value in list(variant_layouting[ocel.variants[i]][1].values()) if value[0] == 'application'])
        #number_offer = len([value for value in list(variant_layouting[ocel.variants[i]][1].values()) if value[0] == 'offer'])
        #extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], 0)
        #candidates = IAVS.get_candidates(extracted_variant.lanes, extracted_variant.interaction_points)
        #maximal_merging_size = max(len(l) for l in candidates)
        #largest_interaction_point = max([len(interaction_point.interaction_lanes) for interaction_point in list(extracted_variant.interaction_points)])
        #if(largest_interaction_point <= 6):
            #extracted_summarizations = IAVS.within_variant_summarization(extracted_variant, False)
            #data.append([i, times[i], number_events, number_application, number_offer, maximal_merging_size, len(extracted_summarizations),largest_interaction_point])
        #else:
            #data.append([i, times[i], number_events, number_application, number_offer, maximal_merging_size, 0,largest_interaction_point])

    #print("Total time for the Intra-Variant-Summarizations: " + str(time_after_intra - time_before_intra))

    # Write results into files
    #header = ['Variant', 'Total Time', 'Number of Events', 'Number of Application', 'Number of Offer', 'Size of Maximal Merging Candidate', 'Number of Summarizations', 'Largest Interaction Point']

    #with open('PerformanceResults/P2P_Intra_Statistics.csv', 'w', encoding='UTF8', newline='') as f:
        #writer = csv.writer(f)
        #writer.writerow(header)
        #writer.writerows(data)

    with open('PerformanceResults/P2P_HittingSet.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Total Time Hitting Set'])
        writer.writerows([str(time_after_hitting - time_before_hitting)])

# Experiment 2: Various Inter-Lane Summarizations
elif(CURRENT_SETTING == Setting.ALL_SINGLE_INTER):

    SAMPLE_SIZE = 8
    NUMBER_REPETITIONS = 10

    # Load data
    filename = "EventLogs/P2P.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    
    # Initial Super Variant Generati on and Selection
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
    selected_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    data_nested = []
    data_nnested = []

    # Repeat experiment NUMBER_REPETITIONS times
    for iteration in range(NUMBER_REPETITIONS):

        # Sample initial set of super variants (the same for both modes)
        super_variants = selected_summarizations
        sample_nested = super_variants[:SAMPLE_SIZE]
        sample_nnested = sample_nested

        # Summarize super variants with increasing range of variants
        for number in [2,4,8,16,32]:

            print("Starting iteration for sets of " + str(number))
            print("-------------------------------")
            print("Nested")

            # Sample first super variants to ensure the same sample for both modes
            sample = sample_nested[:SAMPLE_SIZE]
            # Store some statistics on the input super variants
            super_variant_statistics = dict()
            for i in range(len(sample)):
                super_variant_statistics[i] = [sample[i].get_number_of_events(), len(sample[i].lanes), len(sample[i].get_lanes_of_type('material'))]

            # Match and summarize all pairs of super variants as well as store times and results
            IEVG.NESTED_STRUCTURES = True
            time_before_inter = time.perf_counter()
            times_within_inter = dict()
            results_nested = []
            for i in range(len(sample)-1):
                for j in range(i+1, len(sample)):
                    print(str(i) + "|" + str(j))
                    
                    try:
                        time_before_mapping = time.perf_counter()
                        mapping12, cost12 = IEVS.decide_matching(copy.deepcopy(sample[i]), copy.deepcopy(sample[j]), copy.deepcopy(sample[i].lanes), copy.deepcopy(sample[j].lanes))
                        mapping21, cost21 = IEVS.decide_matching(copy.deepcopy(sample[j]), copy.deepcopy(sample[i]), copy.deepcopy(sample[j].lanes), copy.deepcopy(sample[i].lanes))
                        time_after_mapping = time.perf_counter()

                        if(cost21 < cost12):
                            try:
                                time_before_join = time.perf_counter()
                                super_variant, c = IEVS.inter_variant_summarization(copy.deepcopy(sample[j]), copy.deepcopy(sample[i]), mapping21, True, False), cost21
                                results_nested.append(super_variant)
                                time_after_join = time.perf_counter()
                                cost = cost21
                            except:
                                time_before_join = 0
                                time_after_join = 0
                                cost = "NaN"

                        else:
                            try:
                                time_before_join = time.perf_counter()
                                super_variant, c = IEVS.inter_variant_summarization(copy.deepcopy(sample[i]), copy.deepcopy(sample[j]), mapping12, True, False), cost12
                                results_nested.append(super_variant)
                                time_after_join = time.perf_counter()
                                cost = cost12
                            except:
                                time_before_join = 0
                                time_after_join = 0
                                cost = "NaN"
                    except:
                        time_before_mapping = 0
                        time_after_mapping = 0
                        time_before_join = 0
                        time_after_join = 0
                        cost = "NaN"

                    times_within_inter[(i,j)] = (time_after_join - time_before_join, time_after_mapping - time_before_mapping, cost)

            time_after_inter = time.perf_counter()

            print("Total time for the Inter-Variant-Summarizations with nested operators: " + str(time_after_inter - time_before_inter))
            
            # Store measured times
            for i in range(len(sample)-1):
                for j in range(i+1, len(sample)):
                    print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
                    data_nested.append([i, j, times_within_inter[(i,j)][0] + times_within_inter[(i,j)][1], times_within_inter[(i,j)][0], times_within_inter[(i,j)][1], super_variant_statistics[i][0] + super_variant_statistics[j][0], (super_variant_statistics[i][1] + super_variant_statistics[j][1]) / 2, (super_variant_statistics[i][2] + super_variant_statistics[j][2]) / 2, max(super_variant_statistics[i][2], super_variant_statistics[j][2]), times_within_inter[(i,j)][2], int(super_variant_statistics[i][2] != super_variant_statistics[j][2]), number])

            # Update Input
            sample_nested = results_nested

            print("-------------------------------")
            print("Not nested")

            # Sample first super variants to ensure the same sample for both modes
            sample = sample_nnested[:SAMPLE_SIZE]

            # Store some statistics on the input super variants
            super_variant_statistics = dict()
            for i in range(len(sample)):
                super_variant_statistics[i] = [sample[i].get_number_of_events(), len(sample[i].lanes), len(sample[i].get_lanes_of_type('material'))]

            # Match and summarize all pairs of super variants as well as store times and results
            IEVG.NESTED_STRUCTURES = False
            time_before_inter = time.perf_counter()
            times_within_inter = dict()
            results_nnested = []
            for i in range(len(sample)-1):
                for j in range(i+1, len(sample)):
                    print(str(i) + "|" + str(j))

                    time_before_mapping = time.perf_counter()
                    mapping12, cost12 = IEVS.decide_matching(copy.deepcopy(sample[i]), copy.deepcopy(sample[j]), copy.deepcopy(sample[i].lanes), copy.deepcopy(sample[j].lanes))
                    mapping21, cost21 = IEVS.decide_matching(copy.deepcopy(sample[j]), copy.deepcopy(sample[i]), copy.deepcopy(sample[j].lanes), copy.deepcopy(sample[i].lanes))
                    time_after_mapping = time.perf_counter()

                    if(cost21 < cost12):
                        try:
                            time_before_join = time.perf_counter()
                            super_variant, c = IEVS.inter_variant_summarization(copy.deepcopy(sample[j]), copy.deepcopy(sample[i]), mapping21, True, False), cost21
                            results_nnested.append(super_variant)
                            time_after_join = time.perf_counter()
                            cost = cost21
                        except:
                            time_before_join = 0
                            time_after_join = 0
                            cost = "NaN"

                    else:
                        try:
                            time_before_join = time.perf_counter()
                            super_variant, c = IEVS.inter_variant_summarization(copy.deepcopy(sample[i]), copy.deepcopy(sample[j]), mapping12, True, False), cost12
                            results_nnested.append(super_variant)
                            time_after_join = time.perf_counter()
                            cost = cost12
                        except:
                            time_before_join = 0
                            time_after_join = 0
                            cost = "NaN"

                    times_within_inter[(i,j)] = (time_after_join - time_before_join, time_after_mapping - time_before_mapping, cost)

            time_after_inter = time.perf_counter()

            print("Total time for the Inter-Variant-Summarizations without nested operators: " + str(time_after_inter - time_before_inter))
            
            # Store measured times
            for i in range(len(sample)-1):
                for j in range(i+1, len(sample)):
                    print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
                    data_nnested.append([i, j, times_within_inter[(i,j)][0] + times_within_inter[(i,j)][1], times_within_inter[(i,j)][0], times_within_inter[(i,j)][1], super_variant_statistics[i][0] + super_variant_statistics[j][0], (super_variant_statistics[i][1] + super_variant_statistics[j][1]) / 2, (super_variant_statistics[i][2] + super_variant_statistics[j][2]) / 2, max(super_variant_statistics[i][2], super_variant_statistics[j][2]), times_within_inter[(i,j)][2], int(super_variant_statistics[i][2] != super_variant_statistics[j][2]), number])

            # Update Input
            sample_nnested = results_nnested

    # Write results into files
    header = ['Variant i', 'Variant j', 'Total Time', 'Summarization Time', 'Mapping Time', 'Number of Events', 'Average Number of Object Instances', 'Average Number of Materials', 'Largest Type Object Set', 'Cost', 'Lane Optionality', 'n']

    with open('PerformanceResults/P2P_Random_10_Inter_Statistics_Nested_E_5.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_nested)

    with open('PerformanceResults/P2P_Random_10_Inter_Statistics_NNested_E_5.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_nnested)

 # Experiment 3: Super Variant Hierarchy Construction
else:

    NUMBER_REPETITIONS = 5

    # Load data
    filename = "EventLogs/P2P.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)

    # Initial Super Variant Generation and Selection
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
    selected_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    for size in [16,32]:
        print("Input size: " + str(size))
        print("---------------------------------------")

        data = []
        for iteration in range(NUMBER_REPETITIONS):

            # Sample input super variants 
            super_variants = [summarization for summarization in selected_summarizations if len(summarization.get_lanes_of_type('offer')) < 4]
            sample = random.sample(super_variants, size)

            # Default values
            IEVG.NESTED_STRUCTURES = False 

            # Construct hierarchy
            try:
                time_before_hierarchy = time.perf_counter()
                hierarchies, times = IEVG.generate_super_variant_hierarchy_by_cost([(super_variant, None, None) for super_variant in sample], math.inf, 0, 2, meassure_times = True, times = dict())
                time_after_hierarchy = time.perf_counter()

                print("Total time for the Super Variant Hierarchy Generation: " + str(time_after_hierarchy - time_before_hierarchy))
                        
                # Store measured times
                for level in times.keys():
                    print("Total time for level " + str(level) +": " + str(times[level][0]))
                    data.append([level] + times[level])

            except:
                print("Hierarchy construction not successful")


        # Write into file
        header = ['Level', 'Total Time', 'Mapping Time', 'Clustering Time', 'Summarization Time', 'Size', 'Number of Summarizations', 'Average Number of Offers']

        with open('PerformanceResults/P2P_Random_' + str(size) + '_hierarchy_f.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

 

    
        