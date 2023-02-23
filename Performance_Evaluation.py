from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import Super_Variant_Visualization as SVV
import Summarization_Selection as SS
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH
import Inter_Lane_Alignment as ILA
from enum import Enum
import time
import csv
import math
import random

NUMBER_OF_EVENT_LOGS_PER_SIZE = 4

class Setting(Enum):

    # For 3 [5, 25, 100] * NUMBER_OF_EVENT_LOGS_PER_SIZE [Random Samples] Event Logs
    ELOG_N_EXPLORATION_LOG_5 = 1
    ELOG_N_UNIFORM_LOG_5 = 2
    ELOG_N_NORMAL_LOG_5 = 3

    ELOG_NN_EXPLORATION_LOG_5 = 4
    ELOG_NN_UNIFORM_LOG_5 = 5
    ELOG_NN_NORMAL_LOG_5 = 6

    # For all pairs of the top 10 most frequent variants
    TOP_10_PAIRS_INTER_N = 7
    TOP_10_PAIRS_INTER_NN = 8

    # For all single variants 
    ALL_SINGLE_INTRA = 9

    # For entire Event Log 
    ALL_N_EXPLORATION_7_PLUSMINUS_2 = 10
    ALL_N_UNIFORM_7_PLUSMINUS_2 = 11
    ALL_N_NORMAL_7_PLUSMINUS_2 = 12

    ALL_NN_EXPLORATION_7_PLUSMINUS_2 = 13
    ALL_NN_UNIFORM_7_PLUSMINUS_2 = 14
    ALL_NN_NORMAL_7_PLUSMINUS_2 = 15


# Sampling the sets of variants 
'''
filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
ocel_all = ocel_import_factory.apply(file_path = filename)
all_variants = list(zip(ocel_all.variants, ocel_all.variant_frequencies))

sampled_variants = dict()

indices5 = [[381, 89, 437, 140, 263], [274, 19, 276, 303, 90], [90, 347, 129, 220, 165], [286, 394, 27, 391, 320]]
indices25 = [[409, 100, 423, 430, 225, 218, 115, 246, 232, 50, 348, 74, 15, 284, 6, 84, 135, 249, 236, 396, 10, 132, 355, 108, 285], [199, 372, 19, 335, 423, 161, 16, 367, 193, 223, 421, 107, 50, 156, 275, 86, 433, 371, 204, 430, 320, 36, 319, 49, 6], [161, 411, 123, 40, 260, 77, 69, 264, 254, 141, 149, 55, 334, 274, 305, 61, 86, 375, 173, 295, 20, 32, 21, 57, 144], [70, 329, 349, 156, 241, 40, 202, 300, 270, 405, 89, 267, 26, 218, 126, 261, 210, 13, 284, 366, 165, 295, 291, 161, 76]]
indices100 = [[128, 167, 92, 216, 127, 241, 390, 354, 394, 132, 260, 153, 45, 28, 332, 83, 279, 238, 155, 214, 302, 227, 104, 18, 6, 171, 381, 323, 4, 208, 133, 59, 267, 0, 351, 67, 364, 96, 43, 142, 182, 415, 307, 119, 257, 363, 213, 84, 255, 433, 349, 240, 254, 407, 121, 288, 401, 275, 284, 384, 60, 434, 21, 286, 169, 316, 348, 382, 114, 232, 178, 223, 442, 224, 272, 239, 318, 79, 112, 430, 64, 68, 100, 226, 253, 403, 39, 378, 269, 274, 151, 38, 172, 411, 229, 34, 324, 446, 421, 270], [6, 273, 376, 202, 329, 378, 444, 177, 146, 267, 67, 85, 168, 343, 252, 339, 220, 265, 217, 28, 26, 1, 69, 174, 176, 169, 427, 272, 226, 311, 204, 8, 132, 5, 263, 30, 270, 240, 113, 7, 36, 107, 229, 423, 56, 122, 399, 68, 320, 58, 2, 141, 117, 155, 171, 388, 37, 71, 197, 315, 362, 236, 411, 416, 145, 190, 409, 425, 167, 352, 118, 95, 418, 337, 76, 81, 142, 205, 366, 271, 331, 387, 443, 317, 212, 137, 404, 192, 135, 395, 237, 74, 131, 242, 417, 172, 184, 183, 371, 266], [327, 407, 284, 233, 53, 159, 357, 18, 258, 397, 306, 272, 373, 279, 198, 370, 425, 365, 163, 379, 419, 269, 130, 282, 403, 135, 317, 181, 208, 25, 251, 443, 98, 35, 239, 89, 319, 115, 112, 78, 431, 192, 246, 4, 125, 237, 297, 350, 301, 187, 228, 66, 312, 244, 247, 298, 333, 290, 92, 199, 197, 116, 283, 315, 2, 51, 364, 71, 190, 44, 12, 326, 378, 97, 216, 430, 422, 122, 16, 171, 57, 205, 6, 433, 303, 26, 261, 86, 236, 153, 173, 29, 344, 114, 120, 180, 191, 263, 157, 119], [352, 180, 418, 309, 304, 423, 366, 212, 324, 198, 14, 401, 190, 191, 345, 244, 37, 263, 7, 177, 371, 69, 144, 303, 346, 105, 84, 223, 360, 2, 235, 199, 412, 383, 448, 312, 321, 15, 131, 358, 215, 48, 420, 6, 326, 319, 370, 20, 81, 104, 382, 97, 126, 119, 179, 331, 409, 120, 142, 306, 394, 109, 182, 3, 337, 290, 64, 87, 233, 82, 154, 72, 430, 396, 38, 287, 130, 181, 364, 16, 232, 276, 32, 261, 392, 106, 202, 77, 272, 157, 268, 353, 406, 369, 33, 320, 217, 428, 333, 351]]

for i in [5, 25, 100]:
    sampled_variants_i = []


    for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):
        
        sampled_variants_ij = []
        for k in range(len(all_variants)):
            if(i == 5):
                if (k in indices5[j]):
                    sampled_variants_ij.append(all_variants[k])
            elif(i == 25):
                if (k in indices25[j]):
                    sampled_variants_ij.append(all_variants[k])
            elif(i == 100):
                if (k in indices100[j]):
                    sampled_variants_ij.append(all_variants[k])

        sampled_variants_i.append(sampled_variants_ij)
    sampled_variants[i] = sampled_variants_i 
'''




CURRENT_SETTING = Setting.ALL_SINGLE_INTRA

if(CURRENT_SETTING == Setting.ELOG_N_EXPLORATION_LOG_5):
    header = ['ID', 'Intra Time', 'Selection Time', 'Inter Time', 'Total Time']

    for i in [5]:
        data = []
        for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):
            time_before_intra = time.perf_counter()
            all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel_all, sampled_variants[i][j])
            time_after_intra = time.perf_counter()

            time_before_selection = time.perf_counter()
            summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
            time_after_selection = time.perf_counter()

            IEVG.NESTED_STRUCTURES = True
            ILA.ALIGN = False

            time_before_inter = time.perf_counter()
            hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, number_of_super_variants = math.log(i, 5), frequency_distribution_type = IEVG.Distribution.EXPLORATION)
            time_after_inter = time.perf_counter()

            
            print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
            print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
            print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        with open('PerformanceResults/Size' + str(i) + '_Exploration_Nested.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

    #CURRENT_SETTING = Setting.ELOG_NN_EXPLORATION_LOG_5

if(CURRENT_SETTING == Setting.ELOG_NN_EXPLORATION_LOG_5):
    header = ['ID', 'Intra Time', 'Selection Time', 'Inter Time', 'Total Time']

    #for i in [5, 25, 100]:
        #data = []
        #for j in range(NUMBER_OF_EVENT_LOGS_PER_SIZE):
    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(ocel_all, sampled_variants[5][0])
    time_after_intra = time.perf_counter()
        #del ocel_all

    time_before_selection = time.perf_counter()
    summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
    time_after_selection = time.perf_counter()

    IEVG.NESTED_STRUCTURES = False
    ILA.ALIGN = False

    time_before_inter = time.perf_counter()
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(summarizations, number_of_super_variants = 2, frequency_distribution_type = IEVG.Distribution.UNIFORM)
    time_after_inter = time.perf_counter()

            
    print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
    print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
    print("Time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
            #data.append([j, time_after_intra - time_before_intra, time_after_selection - time_before_selection, time_after_inter - time_before_inter, time_after_inter - time_before_intra])


        #with open('PerformanceResults/Size' + str(i) + '_Exploration_NotNested.csv', 'w', encoding='UTF8', newline='') as f:
            #writer = csv.writer(f)
            #writer.writerow(header)
            #writer.writerows(data)


#Possibly Align Off
if(CURRENT_SETTING == Setting.TOP_10_PAIRS_INTER_N):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Top10.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    
    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
    time_after_intra = time.perf_counter()

    time_before_selection = time.perf_counter()
    summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
    time_after_selection = time.perf_counter()

    IEVG.NESTED_STRUCTURES = True
    time_before_inter = time.perf_counter()
    times_within_inter = dict()
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            time_before_join = time.perf_counter()
            super_variant, cost = IEVS.join_super_variants(summarizations[i], summarizations[j], True, False)
            time_after_join = time.perf_counter()
            times_within_inter[(i,j)] = (time_before_join, time_after_join)

    time_after_inter = time.perf_counter()

    print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
    print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
    print("Total time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
    
    data = []
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
            data.append([i, j, times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]])

    header = ['Variant i', 'Variant j', 'Time']

    with open('PerformanceResults/Top10Pairs_Nested.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

#Possibly Align Off
if(CURRENT_SETTING == Setting.TOP_10_PAIRS_INTER_NN):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Top10.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)
    
    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
    time_after_intra = time.perf_counter()

    time_before_selection = time.perf_counter()
    summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)
    time_after_selection = time.perf_counter()

    IEVG.NESTED_STRUCTURES = False
    time_before_inter = time.perf_counter()
    times_within_inter = dict()
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            time_before_join = time.perf_counter()
            super_variant, cost = IEVS.join_super_variants(summarizations[i], summarizations[j], False, False)
            time_after_join = time.perf_counter()
            times_within_inter[(i,j)] = (time_before_join, time_after_join)

    time_after_inter = time.perf_counter()

    print("Time for the Intra-Variant-Summarization: " + str(time_after_intra - time_before_intra))
    print("Time for the Intra-Variant-Selection: " + str(time_after_selection - time_before_selection))
    print("Total time for the Inter-Variant-Summarizations: " + str(time_after_inter - time_before_inter))
    
    data = []
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            print("Time for summarizing variants " + str(i) +" and " + str(j) + ": " + str(times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]))
            data.append([i, j, times_within_inter[(i,j)][1] - times_within_inter[(i,j)][0]])

    header = ['Variant i', 'Variant j', 'Time']

    with open('PerformanceResults/Top10Pairs_NotNested.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

if(CURRENT_SETTING == Setting.ALL_SINGLE_INTRA):
    filename = "EventLogs/PerformanceAnalysis/BPI2017-Filtered_80.jsonocel"
    ocel = ocel_import_factory.apply(file_path = filename)

    time_before_intra = time.perf_counter()
    all_summarizations, per_variant_dict, per_encoding_dict, times = IAVG.complete_intra_variant_summarization_from_process(ocel, get_time = True)
    time_after_intra = time.perf_counter()

    data = []
    index = 0
    for t in times:
        data.append([index, t])
        index += 1

    header = ['Variant', 'Time']

    with open('PerformanceResults/All_Intra.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)