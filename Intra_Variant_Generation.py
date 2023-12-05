import Input_Extraction_Definition as IED
import Intra_Variant_Summarization as IAVS
import time
import Super_Variant_Visualization as SVV

def complete_intra_variant_summarization_from_process(process, print_results = False, get_time = False):
    '''
    Given an Object-Centric Event Log, the Intra-Variant Summarizations are generated and sorted by variant.
    :param process: The object-centric event-log in ocel format
    :type process: ocpa.objects.log.ocel.OCEL
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :param get_time: Whether or not the runs should be timed
    :type get_time: bool
    :return: A list of all unique_summarizations, a dictionary mapping variant to it's summarizations and a dictionary mapping a unique summarization to its SummarizedVariant instances
    :rtype: list, dict, dict
    '''
    if(get_time):
        universe, summarization_dictionary, times = get_unique_summarizations_from_process(process, print_results, get_time)
        all_summarizations, summarizations_per_variant = __determine_subsets(universe, summarization_dictionary)
        return all_summarizations, summarizations_per_variant, summarization_dictionary, times

    else:
        universe, summarization_dictionary = get_unique_summarizations_from_process(process, print_results, get_time)
        all_summarizations, summarizations_per_variant = __determine_subsets(universe, summarization_dictionary)
        return all_summarizations, summarizations_per_variant, summarization_dictionary


def complete_intra_variant_summarization_from_variants(process, variants, print_results = False):
    '''
    Given an Object-Centric Event Log, the Intra-Variant Summarizations are generated and sorted by variant.
    :param process: The object-centric event-log in ocel format
    :type process: ocpa.objects.log.ocel.OCEL
    :param variants: a list of variants and their frequencies as tuples
    :type variants: list
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: A list of all unique_summarizations, a dictionary mapping variant to it's summarizations and a dictionary mapping a unique summarization to its SummarizedVariant instances
    :rtype: list, dict, dict
    '''
    universe, summarization_dictionary = get_unique_summarizations_from_variants(process, variants, print_results)
    all_summarizations, summarizations_per_variant = __determine_subsets(universe, summarization_dictionary)
    return all_summarizations, summarizations_per_variant, summarization_dictionary


def get_unique_summarizations_from_process(process, print_results = False, get_time = False):
    '''
    Computes the Intra-Variant Summarizations for each variant of the given event log and determines equality among the resulting summarizations.
    :param process: The object-centric event-log in ocel format
    :type process: ocpa.objects.log.ocel.OCEL
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :param get_time: Whether or not the runs should be timed
    :type get_time: bool
    :return: A list containing all unique summarizations and a dictionary mapping the summarizations to their SummarizedVariant instances and corresponding variants
    :rtype: list, dict
    '''
    from ocpa.visualization.log.variants import factory as variants_visualization_factory
    from tqdm.auto import tqdm

    variant_layouting = variants_visualization_factory.apply(process)
    all_unique_summarizations_dict = dict()
    all_unique_summarizations_set = []
    all_summarizations = []

    if(get_time):
        times = []

    for i in tqdm(range(10)):
        print(' \n' + "Summarizing variant " + str(i) + " of the process...")
        if(get_time):
            time_before_intra = time.perf_counter()
        extracted_variant = IED.extract_lanes(variant_layouting[process.variants[i]], process.variant_frequencies[i])
        #SVV.visualize_variant(extracted_variant,i)

        #if(max([len(extracted_variant.get_lanes_of_type(type)) for type in list(extracted_variant.object_types)]) <= 3):
        if(max([len(interaction_point.interaction_lanes) for interaction_point in list(extracted_variant.interaction_points)]) <= 6):
            extracted_summarizations = IAVS.within_variant_summarization(extracted_variant, print_results)
            if(get_time):
                time_after_intra = time.perf_counter()
                times.append(time_after_intra - time_before_intra)

            for summarization in extracted_summarizations:
                all_summarizations.append(summarization)
                encoding = summarization.encode_lexicographically()

                if(encoding in all_unique_summarizations_dict.keys()):
                    all_unique_summarizations_dict[encoding][0].append(i)
                    all_unique_summarizations_dict[encoding][1].append(summarization)
                    for item in all_unique_summarizations_set:
                        if (item[0] == encoding):
                            item[1].append(summarization)
                else:
                    all_unique_summarizations_dict[encoding] = ([i], [summarization])
                    all_unique_summarizations_set.append((encoding, [summarization]))

        else: 
            if(get_time):
                times.append('NaN')

    if(get_time):
        return all_unique_summarizations_set, all_unique_summarizations_dict, times
    else:
        return all_unique_summarizations_set, all_unique_summarizations_dict


def get_unique_summarizations_from_variants(process, variants, print_results = False):
    '''
    Computes the Intra-Variant Summarizations for each variant of the given event log and determines equality among the resulting summarizations.
    :param process: The object-centric event-log in ocel format
    :type process: ocpa.objects.log.ocel.OCEL
    :param variants: a list of variants and their frequencies as tuples
    :type variants: list
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: A list containing all unique summarizations and a dictionary mapping the summarizations to their SummarizedVariant instances and corresponding variants
    :rtype: list, dict
    '''
    from ocpa.visualization.log.variants import factory as variants_visualization_factory
    from tqdm.auto import tqdm

    variant_layouting = variants_visualization_factory.apply(process)
    all_unique_summarizations_dict = dict()
    all_unique_summarizations_set = []
    all_summarizations = []

    for i in tqdm(range(10)):
        print(' \n' + "Summarizing variant " + str(i) + " of the process...")
        extracted_variant = IED.extract_lanes(variant_layouting[variants[i][0]], variants[i][1])
        if(max([len(interaction_point.interaction_lanes) for interaction_point in list(extracted_variant.interaction_points)]) <= 6):
            extracted_summarizations = IAVS.within_variant_summarization(extracted_variant, print_results)

            for summarization in extracted_summarizations:
                all_summarizations.append(summarization)
                encoding = summarization.encode_lexicographically()

                if(encoding in all_unique_summarizations_dict.keys()):
                    all_unique_summarizations_dict[encoding][0].append(i)
                    all_unique_summarizations_dict[encoding][1].append(summarization)
                    for item in all_unique_summarizations_set:
                        if (item[0] == encoding):
                            item[1].append(summarization)
                else:
                    all_unique_summarizations_dict[encoding] = ([i], [summarization])
                    all_unique_summarizations_set.append((encoding, [summarization]))

    return all_unique_summarizations_set, all_unique_summarizations_dict


def __determine_subsets(universe, unique_summarizations):
    '''
    Sorts the unique summarizations into subsets based on the variants that they summarize.
    :param universe: The set of all unique Intra-Variant Summarizations
    :type universe: set
    :param unique_summarizations: A dictionary mapping the summarizations to their SummarizedVariant instances and corresponding variants
    :type unique_summarizations: dict
    :return: A list containing all unique summarizations and a dictionary containing the sets if Intra-Variant Summarizations for each variant
    :rtype: list, dict
    '''
    universe_T = list(zip(range(len(universe)), universe))
    subsets_S = dict()
    for key in unique_summarizations.keys():
        for variant in unique_summarizations[key][0]:
            if(variant in subsets_S.keys()):
                subsets_S[variant].extend([elem for elem in universe_T if elem[1][0] == key])
            else:
                subsets_S[variant] = [elem for elem in universe_T if elem[1][0] == key]

    return universe_T, subsets_S