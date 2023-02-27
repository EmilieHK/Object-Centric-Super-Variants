from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import Super_Variant_Visualization as SVV
import Summarization_Selection as SS
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH
import Inter_Lane_Alignment as ILA
import Input_Extraction_Definition as IED
import Intra_Variant_Summarization as IAVS
from enum import Enum
import time
import csv
import random
import copy
import pandas
import math

NUMBER_OF_EVENT_LOGS_PER_SIZE = 4

# Always take maximal generalization
class Setting(Enum):

    # For 3 [5, 20, 50] * NUMBER_OF_EVENT_LOGS_PER_SIZE [Random Samples] Event Logs
    ELOG_N_EXPLORATION = 1
    ELOG_NN_EXPLORATION = 2

    ELOG_N_DISTRIBUTION_LOG_2 = 3
    ELOG_NN_DISTRIBUTION_LOG_2 = 4

    # For all pairs of the randomly sampled 50 variants
    PAIRS_INTER_N = 5
    PAIRS_INTER_NN = 6

    # For all single variants 
    ALL_SINGLE_INTRA = 7


CURRENT_SETTING = Setting.ELOG_NN_DISTRIBUTION_LOG_2
CURRENT_SIZE = 20


if(CURRENT_SETTING == Setting.PAIRS_INTER_N):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)

    selected_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    summarizations = random.sample(selected_summarizations, 50)

    super_variant_statistics = dict()
    for i in range(len(summarizations)):
        super_variant_statistics[i] = [summarizations[i].get_number_of_events(), len(summarizations[i].get_lanes_of_type('application')), len(summarizations[i].get_lanes_of_type('offer')), max(len(summarizations[i].get_lanes_of_type('application')), len(summarizations[i].get_lanes_of_type('offer')))]

    IEVG.NESTED_STRUCTURES = True
    time_before_inter = time.perf_counter()
    times_within_inter = dict()
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print(str(i) + "|" + str(j))

            time_before_mapping = time.perf_counter()
            mapping12, cost12 = IEVS.decide_matching(copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i].lanes), copy.deepcopy(summarizations[j].lanes))
            mapping21, cost21 = IEVS.decide_matching(copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j].lanes), copy.deepcopy(summarizations[i].lanes))
            time_after_mapping = time.perf_counter()

            if(cost21 < cost12):
                time_before_join = time.perf_counter()
                super_variant = IEVS.inter_variant_summarization(copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i]), mapping21, True, False), cost21
                time_after_join = time.perf_counter()
                cost = cost21

            else:
                time_before_join = time.perf_counter()
                super_variant = IEVS.inter_variant_summarization(copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j]), mapping12, True, False), cost12
                time_after_join = time.perf_counter()
                cost = cost12

            times_within_inter[(i,j)] = (time_after_join - time_before_join, time_after_mapping - time_before_mapping, cost)

    time_after_inter = time.perf_counter()

    print("Total time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
    
    data = []
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
            data.append([i, j, times_within_inter[(i,j)][0] + times_within_inter[(i,j)][1], times_within_inter[(i,j)][0], times_within_inter[(i,j)][1], super_variant_statistics[i][0] + super_variant_statistics[j][0], (super_variant_statistics[i][1] + super_variant_statistics[j][1]) / 2, (super_variant_statistics[i][3] + super_variant_statistics[j][3]) / 2, max(super_variant_statistics[i][3], super_variant_statistics[j][3]), times_within_inter[(i,j)][2], int(super_variant_statistics[i][3] != super_variant_statistics[j][3])])

    header = ['Variant i', 'Variant j', 'Total Time', 'Summarization Time', 'Mapping Time', 'Number of Events', 'Average Number of Application', 'Average Number of Offer', 'Largest Type Object Set', 'Cost', 'Lane Optionality']

    with open('PerformanceResults/BPI2017_80_Random_50_Inter_Statistics_Nested.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


elif(CURRENT_SETTING == Setting.PAIRS_INTER_NN):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)

    selected_summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    summarizations = random.sample(selected_summarizations, 50)

    super_variant_statistics = dict()
    for i in range(len(summarizations)):
        super_variant_statistics[i] = [summarizations[i].get_number_of_events(), len(summarizations[i].get_lanes_of_type('application')), len(summarizations[i].get_lanes_of_type('offer')), max(len(summarizations[i].get_lanes_of_type('application')), len(summarizations[i].get_lanes_of_type('offer')))]

    IEVG.NESTED_STRUCTURES = False
    time_before_inter = time.perf_counter()
    times_within_inter = dict()
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print(str(i) + "|" + str(j))

            time_before_mapping = time.perf_counter()
            mapping12, cost12 = IEVS.decide_matching(copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i].lanes), copy.deepcopy(summarizations[j].lanes))
            mapping21, cost21 = IEVS.decide_matching(copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j].lanes), copy.deepcopy(summarizations[i].lanes))
            time_after_mapping = time.perf_counter()

            if(cost21 < cost12):
                time_before_join = time.perf_counter()
                super_variant = IEVS.inter_variant_summarization(copy.deepcopy(summarizations[j]), copy.deepcopy(summarizations[i]), mapping21, False, False), cost21
                time_after_join = time.perf_counter()
                cost = cost21

            else:
                time_before_join = time.perf_counter()
                super_variant = IEVS.inter_variant_summarization(copy.deepcopy(summarizations[i]), copy.deepcopy(summarizations[j]), mapping12, False, False), cost12
                time_after_join = time.perf_counter()
                cost = cost12

            times_within_inter[(i,j)] = (time_after_join - time_before_join, time_after_mapping - time_before_mapping, cost)

    time_after_inter = time.perf_counter()

    print("Total time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
    
    data = []
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
            data.append([i, j, times_within_inter[(i,j)][0] + times_within_inter[(i,j)][1], times_within_inter[(i,j)][0], times_within_inter[(i,j)][1], super_variant_statistics[i][0] + super_variant_statistics[j][0], (super_variant_statistics[i][1] + super_variant_statistics[j][1]) / 2, (super_variant_statistics[i][3] + super_variant_statistics[j][3]) / 2, max(super_variant_statistics[i][3], super_variant_statistics[j][3]), times_within_inter[(i,j)][2], int(super_variant_statistics[i][3] != super_variant_statistics[j][3])])

    header = ['Variant i', 'Variant j', 'Total Time', 'Summarization Time', 'Mapping Time', 'Number of Events', 'Average Number of Application', 'Average Number of Offer', 'Largest Type Object Set', 'Cost', 'Lane Optionality']

    with open('PerformanceResults/BPI2017_80_Random_50_Inter_Statistics_NotNested.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


elif(CURRENT_SETTING == Setting.ALL_SINGLE_INTRA):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    variant_layouting = variants_visualization_factory.apply(ocel)

    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict, times = IAVG.complete_intra_variant_summarization_from_process(ocel, get_time = True)
    time_after_intra = time.perf_counter()

    data = []
    for i in range(len(times)):
        print("Writing data for variant: " + str(i))
        number_events = len(variant_layouting[ocel.variants[i]][0])
        number_application = len([value for value in list(variant_layouting[ocel.variants[i]][1].values()) if value[0] == 'application'])
        number_offer = len([value for value in list(variant_layouting[ocel.variants[i]][1].values()) if value[0] == 'offer'])
        extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], 0)
        candidates = IAVS.get_candidates(extracted_variant.lanes, extracted_variant.interaction_points)
        maximal_merging_size = max(len(l) for l in candidates)
        if(len(extracted_variant.lanes) <= 4):
            extracted_summarizations = IAVS.within_variant_summarization(extracted_variant, False)
            data.append([i, times[i], number_events, number_application, number_offer, maximal_merging_size, len(extracted_summarizations)])
        else:
            data.append([i, times[i], number_events, number_application, number_offer, maximal_merging_size, 0])

    print("Total time for the Intra-Variant-Summarizations: " + str(time_after_intra - time_before_intra))

    header = ['Variant', 'Total Time', 'Number of Events', 'Number of Application', 'Number of Offer', 'Size of Maximal Merging Candidate', 'Number of Summarizations']

    with open('PerformanceResults/BPI2017_80_Intra_Statistics.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

else:
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)

    sampled_5_file = pandas.read_csv("EventLogs/PerformanceAnalysis/Statistics/Sample_Size5_Statistics.csv")
    sampled_20_file = pandas.read_csv("EventLogs/PerformanceAnalysis/Statistics/Sample_Size20_Statistics.csv")
    sampled_50_file = pandas.read_csv("EventLogs/PerformanceAnalysis/Statistics/Sample_Size50_Statistics.csv")

    samples_5 = []
    samples_20 = []
    samples_50 = []

    for i in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):
        sample_5_i = []
        sample_20_i = []
        sample_50_i = []

        for k in range(5):
            index_label = "Index " + str(k)
            index = int(sampled_5_file.iloc[i][index_label])
            sample_5_i.append((ocel.variants[index], ocel.variant_frequencies[index]))

        for k in range(20):
            index_label = "Index " + str(k)
            index = int(sampled_20_file.iloc[i][index_label])
            sample_20_i.append((ocel.variants[index], ocel.variant_frequencies[index]))

        for k in range(50):
            index_label = "Index " + str(k)
            index = int(sampled_50_file.iloc[i][index_label])
            sample_50_i.append((ocel.variants[index], ocel.variant_frequencies[index]))
        
        samples_5.append(sample_5_i)
        samples_20.append(sample_20_i)
        samples_50.append(sample_50_i)

    if(CURRENT_SETTING == Setting.ELOG_NN_DISTRIBUTION_LOG_2):
        header = ['ID', 'Total Intra-Variant Summarization Time', 'Total Selection Time', 'Total Inter-Variant Summarization Time', 'Total Time']

        data = []
        for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):

            time_before_intra = time.perf_counter()
            if(CURRENT_SIZE == 5):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_5[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_20[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_50[j])
            time_after_intra = time.perf_counter()
 

            time_before_selection = time.perf_counter()
            summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
            time_after_selection = time.perf_counter()

            IEVG.NESTED_STRUCTURES = False
            ILA.ALIGN = True

            time_before_inter = time.perf_counter()
            number_of_super_variants = math.trunc(math.log(CURRENT_SIZE, 2))
            hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, number_of_super_variants = number_of_super_variants, frequency_distribution_type = IEVG.Distribution.UNIFORM, print_results = True)
            time_after_inter = time.perf_counter()

                    
            print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
            print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
            print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        with open('PerformanceResults/Size' + str(CURRENT_SIZE) + '_Distribution_NotNested.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)


    if(CURRENT_SETTING == Setting.ELOG_NN_EXPLORATION):
        header = ['ID', 'Total Intra-Variant Summarization Time', 'Total Selection Time', 'Total Inter-Variant Summarization Time', 'Total Time']

        data = []
        for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):

            time_before_intra = time.perf_counter()
            if(CURRENT_SIZE == 5):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_5[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_20[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_50[j])
            time_after_intra = time.perf_counter()
 

            time_before_selection = time.perf_counter()
            summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
            time_after_selection = time.perf_counter()

            IEVG.NESTED_STRUCTURES = False
            ILA.ALIGN = True

            time_before_inter = time.perf_counter()
            hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, frequency_distribution_type = IEVG.Distribution.EXPLORATION, print_results = True)
            time_after_inter = time.perf_counter()

            print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
            print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
            print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        with open('PerformanceResults/Size' + str(CURRENT_SIZE) + '_Exploration_NotNested.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)


    if(CURRENT_SETTING == Setting.ELOG_N_DISTRIBUTION_LOG_2):
        header = ['ID', 'Total Intra-Variant Summarization Time', 'Total Selection Time', 'Total Inter-Variant Summarization Time', 'Total Time']

        data = []
        for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):

            time_before_intra = time.perf_counter()
            if(CURRENT_SIZE == 5):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_5[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_20[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_50[j])
            time_after_intra = time.perf_counter()
 

            time_before_selection = time.perf_counter()
            summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
            time_after_selection = time.perf_counter()

            IEVG.NESTED_STRUCTURES = True
            ILA.ALIGN = True

            time_before_inter = time.perf_counter()
            number_of_super_variants = math.trunc(math.log(CURRENT_SIZE, 2))
            hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, number_of_super_variants = number_of_super_variants, frequency_distribution_type = IEVG.Distribution.UNIFORM, print_results = True)
            time_after_inter = time.perf_counter()

                    
            print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
            print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
            print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        with open('PerformanceResults/Size' + str(CURRENT_SIZE) + '_Distribution_Nested.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)


    if(CURRENT_SETTING == Setting.ELOG_N_EXPLORATION):
        header = ['ID', 'Total Intra-Variant Summarization Time', 'Total Selection Time', 'Total Inter-Variant Summarization Time', 'Total Time']

        data = []
        for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):

            time_before_intra = time.perf_counter()
            if(CURRENT_SIZE == 5):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_5[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_20[j])
            elif(CURRENT_SIZE == 20):
                all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel, samples_50[j])
            time_after_intra = time.perf_counter()
 

            time_before_selection = time.perf_counter()
            summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
            time_after_selection = time.perf_counter()

            IEVG.NESTED_STRUCTURES = True
            ILA.ALIGN = True

            time_before_inter = time.perf_counter()
            hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, frequency_distribution_type = IEVG.Distribution.EXPLORATION, print_results = True)
            time_after_inter = time.perf_counter()

            print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
            print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
            print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        with open('PerformanceResults/Size' + str(CURRENT_SIZE) + '_Exploration_Nested.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
        