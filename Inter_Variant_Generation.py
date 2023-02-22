import Inter_Variant_Summarization as IVS
import Super_Variant_Visualization as SVV
from enum import Enum
import copy 
import math

class Distribution(Enum):
    UNIFORM = 1
    NORMAL = 2
    EXPLORATION = 3

NESTED_STRUCTURES = True


def generate_super_variant_hierarchy(initial_super_variant_set, number_of_super_variants = 1, max_number_of_levels = math.inf, frequency_distribution_type = Distribution.EXPLORATION, base = 2, print_results = False):
    '''
    Generates a Super Variant hierarchy for a set of Super Variants.
    :param initial_super_variant_set: The list of sets of Super Variants
    :type initial_super_variant_set: list
    :param number_of_super_variants: The number of desired clusters and final Super Variants per set of Super Variants
    :type number_of_super_variants int
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param frequency_distribution_type: The distribution type used to cluster the Super Variants
    :type frequency_distribution_type: Distribution
    :param base: The logarithmic base, determines how many variants are to be summarized in a single generative step of an exploratory setting
    :type base: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    :rtype: dict, list
    '''
    return generate_super_variant_hierarchy_by_classification([initial_super_variant_set], number_of_super_variants, max_number_of_levels, frequency_distribution_type, base, print_results)


def generate_super_variant_hierarchy_by_classification(initial_super_variant_classification, number_of_super_variants_per_class = 1, max_number_of_levels = math.inf, frequency_distribution_type = Distribution.EXPLORATION, base = 2, print_results = False):
    '''
    Generates a Super Variant hierarchy for each set of Super Variants based on an initial classification.
    :param initial_super_variant_classification: The list of sets of Super Variants
    :type initial_super_variant_classification: list
    :param number_of_super_variants_per_class: The number of desired clusters and final Super Variants per set of Super Variants
    :type number_of_super_variants_per_class: int
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param frequency_distribution_type: The distribution type used to cluster the Super Variants
    :type frequency_distribution_type: Distribution
    :param base: The logarithmic base, determines how many variants are to be summarized in a single generative step of an exploratory setting
    :type base: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    :rtype: dict, list
    '''
    result = []
    final_level_super_variants = []
    for super_variant_set in initial_super_variant_classification:

        if(frequency_distribution_type == Distribution.UNIFORM or frequency_distribution_type == Distribution.NORMAL):
            if(frequency_distribution_type == Distribution.UNIFORM):
                class_result, class_final_level_super_variants = generate_super_variant_hierarchy_uniform(super_variant_set, number_of_super_variants_per_class, max_number_of_levels, print_results)
            else:
                class_result, class_final_level_super_variants = generate_super_variant_hierarchy_normal(super_variant_set, number_of_super_variants_per_class, max_number_of_levels, print_results)

            final_level_super_variants.append(class_final_level_super_variants)

        elif(frequency_distribution_type == Distribution.EXPLORATION):
            class_result = generate_super_variant_hierarchy_exploration(super_variant_set, max_number_of_levels, base, print_results)
            final_level_super_variants.append((max(class_result.items(), key=lambda x:x[0]))[1][0])

        result.append(class_result)

    return result, final_level_super_variants


def generate_super_variant_hierarchy_uniform(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    '''
    Generates a Super Variant hierarchy such that the frequencies of the final Super Variant reflect a uniform distribution.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list
    :param number_of_super_variants: The number of desired clusters and final Super Variants
    :type number_of_super_variants: int
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    :rtype: dict, list
    '''
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, Distribution.UNIFORM, print_results)

def generate_super_variant_hierarchy_normal(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    '''
    Generates a Super Variant hierarchy such that the frequencies of the final Super Variant reflect a normal distribution.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list
    :param number_of_super_variants: The number of desired clusters and final Super Variants
    :type number_of_super_variants: int
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    :rtype: dict, list
    '''
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, Distribution.NORMAL, print_results)

def generate_super_variant_hierarchy_exploration(initial_super_variant_set, max_number_of_levels, base = 2, print_results = False):
    '''
    Generates an exploratory Super Variant hierarchy given a logarithmic base and a maximal number of levels.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param base: The logarithmic base, determines how many variants are to be summarized in a single generative step 
    :type base: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost
    :rtype: dict
    '''
    return generate_super_variant_hierarchy_by_cost([(super_variant, None, None) for super_variant in initial_super_variant_set], max_number_of_levels, 0, base, print_results)


def generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, distribution_type, print_results = False):
    '''
    Creates a grouping of the initial set of Super Variants in accordance with a frequency distribution and then generates a Super Variant hierarchy.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list
    :param number_of_super_variants: The number of desired clusters and final Super Variants
    :type number_of_super_variants: int
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param distribution_type: The distribution type used to cluster the Super Variants
    :type distribution_type: Distribution
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    :rtype: dict, list
    '''
    if(len(initial_super_variant_set) <= number_of_super_variants):
        result = dict()
        result[0] = [(super_variant, None, None) for super_variant in initial_super_variant_set]
        return result
        
    else:
        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant.id] = super_variant

        clusters = cluster_by_frequency(indexed_initial_set, number_of_super_variants, distribution_type, print_results)

        size_largest_cluster = max([len(cluster) for cluster in clusters])
        for i in range(2, max(3, size_largest_cluster)):
            if(math.ceil(math.log(size_largest_cluster, i)) <= max_number_of_levels):
                base = i
                break

        result = []
        final_level_super_variants = []
        for cluster in clusters:
            cluster_result = generate_super_variant_hierarchy_by_cost([(super_variant, None, None) for super_variant in cluster.values()], max_number_of_levels, 0, base, print_results)
            final_level_super_variants.extend((max(cluster_result.items(), key=lambda x:x[0]))[1][0])
            if(print_results):
                print("The following levels have been generated.")
                for level in cluster_result.keys():
                    print(level)
                    for super_variant in cluster_result[level][0]:
                        print(super_variant.id)
                    print("-----------")
            result.append(cluster_result)

        return result, final_level_super_variants
    

def generate_super_variant_hierarchy_by_cost(initial_super_variant_set, max_number_of_level, counter, base, print_results = False):
    '''
    Recursively generates Super Variants based on a initial set up to a desired depth using the minimum cost possible.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list
    :param max_number_of_level: The maximal level reached in the generation of Super Variants
    :type max_number_of_level: int
    :param counter: The current generation level 
    :type counter: int
    :param base: The logarithmic base, determines how many variants are to be summarized in a single generative step 
    :type base: int
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: The set of Super Variants for each level and the levels accumulated cost
    :rtype: dict
    '''
    if(len(initial_super_variant_set) == 1):
        result = dict()
        result[counter] = (initial_super_variant_set, 0)
        return result
        
    else:
        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant[0].id] = super_variant


        distances = dict()
        for i in indexed_initial_set.keys():
            for j in indexed_initial_set.keys():
                if(j>i):
                    mapping, cost = IVS.decide_matching(indexed_initial_set[i][0], indexed_initial_set[j][0], copy.deepcopy(indexed_initial_set[i][0].lanes), copy.deepcopy(indexed_initial_set[j][0].lanes), True, False)
                    distances[i,j] = cost
                else:
                    distances[i,j] = 0

        clusters = cluster_by_size(indexed_initial_set, base, distances, print_results)

        level_result = []
        accumulated_cost = 0
        for cluster in clusters:
            if(print_results):
                print("Summarizing Super Variants with IDs: ")
                for id in cluster:
                    print(id)

            super_variant1 = indexed_initial_set[cluster[0]]
            for i in range(1, len(cluster)):
                super_variant2 = indexed_initial_set[cluster[i]]
                super_variant, cost = IVS.join_super_variants(super_variant1[0], super_variant2[0], NESTED_STRUCTURES, False)
                accumulated_cost += cost
                super_variant1 = (copy.deepcopy(super_variant), copy.deepcopy(super_variant1), copy.deepcopy(super_variant2))
            level_result.append(super_variant1)

        if(max_number_of_level == 1 or len(level_result) == 1):
            result = dict()
        else:
            if(counter == 0):
                result = generate_super_variant_hierarchy_by_cost(level_result, max_number_of_level - 1, counter + 2, base, print_results)
            else:
                result = generate_super_variant_hierarchy_by_cost(level_result, max_number_of_level - 1, counter + 1, base, print_results)
        
        if(counter == 0):
            result[1] = (level_result, accumulated_cost)
            result[0] = (initial_super_variant_set, 0)
        else:
            result[counter] = (level_result, accumulated_cost)
        return result


def cluster_by_frequency(indexed_initial_set, number_of_clusters, distribution_type, print_results = False):
    '''
    Clusteres a set of Super Variants into a number of clusters based on the provided distances.
    :param indexed_initial_set: The set of Super Variants with indices as keys
    :type indexed_initial_set: dict
    :param number_of_clusters: The number of desired clusters
    :type number_of_clusters: int
    :param distribution_type: The distribution type used to cluster the Super Variants
    :type distribution_type: Distribution
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: A list containing a list for every cluster
    :rtype: list
    '''
    accumulated_frequency = sum([indexed_initial_set[index].frequency for index in indexed_initial_set.keys()])

    if (distribution_type == Distribution.UNIFORM):
        ideal_cluster_frequency = [accumulated_frequency/number_of_clusters]*number_of_clusters
    elif(distribution_type == Distribution.NORMAL):
        import scipy.stats as st
        stepsize = 3/number_of_clusters
        ideal_cluster_frequency = []
        for i in range(number_of_clusters):
            ideal_cluster_frequency.append((((st.norm.cdf(i+1*stepsize)- 0.5)*2) - ((st.norm.cdf(i*stepsize)- 0.5)*2))*accumulated_frequency)


    import gurobipy
    model = gurobipy.Model("ClusteringByFrequency")
    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i,elem]=model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype = gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i,elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i,elem] for elem in indexed_initial_set.keys()) >= 1)
    
    model.setObjective(sum( (sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i])*(sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i]) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    if(print_results):
        print('\n Objective value: %g\n' % model.ObjVal)
        print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        if(print_results):
            print("The following Super Variants are clustered. \n")
        cluster = dict()
        accumulated_frequency_cluster = 0
        for elem in indexed_initial_set.keys():
            if(print_results):
                print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster[elem] = indexed_initial_set[elem]
                accumulated_frequency_cluster += indexed_initial_set[elem].frequency
        clusters.append(cluster)
        if(print_results):
            print("With accumulated frequency: " + str(accumulated_frequency_cluster))
            print("The ideal accumulated frequency would be: " + str(ideal_cluster_frequency[i]))
            print("-----------------------------")

    return clusters


def cluster_by_size(indexed_initial_set, cluster_size, distances, print_results = False):
    '''
    Clusteres a set of Super Variants into a number of clusters based on the provided distances.
    :param indexed_initial_set: The set of Super Variants with indices as keys
    :type indexed_initial_set: dict
    :param cluster_size: The number of Super Variants per cluster
    :type cluster_size: int
    :param distances: The distance for each pair of Super Variants
    :type distances: dict
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :return: A list containing a list for every cluster
    :rtype: list
    '''
    number_of_clusters = math.ceil(len(indexed_initial_set)/cluster_size)

    import gurobipy
    model = gurobipy.Model("ClusteringBySize")

    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i,elem]=model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype = gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i,elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i,elem] for elem in indexed_initial_set.keys()) >= 1)
    
    model.setObjective(sum( (sum(sum(x[i,elem1]*x[i,elem2]*distances[elem1,elem2] for elem2 in indexed_initial_set.keys()) for elem1 in indexed_initial_set.keys()) / cluster_size) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    if(print_results):
        print('\n Objective value: %g\n' % model.ObjVal)
        print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        if(print_results):
            print("The following Super Variants are clustered. \n")
        cluster = []
        accumulated_distances = 0
        for elem in indexed_initial_set.keys():
            if(print_results):
                print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster.append(elem)
                for elem2 in indexed_initial_set.keys():
                    if(x[i,elem2].X == 1.0):
                        accumulated_distances += distances[elem, elem2]

        clusters.append(cluster)
        if(print_results):
            print("With average distance/cost: " + str(accumulated_distances/cluster_size))
            print("-----------------------------")

    return clusters


def classify_initial_super_variants_by_activity(initial_super_variant_set, activity_label, object_types = set()): 
    '''
    Given an activity_label, this method classifies a set of Super Variants into classes depending on whether that activity label is performed in the specified object instances.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list of type SummarizedVariant
    :param activity_label: The name of the activity
    :type activity_label: string
    :param object_types: The names of the considered object types
    :type object_types: set
    :return: A list containing a list with all Super Variants classes
    :rtype: list
    '''
    if(object_types == set()):
        for super_variant in initial_super_variant_set:
            object_types = object_types.union(super_variant.object_types)

    result = [[],[]]

    for super_variant in initial_super_variant_set:
        activity_containted = False
        for lane in super_variant.lanes:
            if(lane.object_type in object_types):
                if(lane.contains_activity(activity_label)):
                    activity_containted = True
                    break

        if activity_containted:
            result[0].append(super_variant)
        else: 
            result[1].append(super_variant)

    return result


def classify_initial_super_variants_by_object_cardinality(initial_super_variant_set, object_type):
    '''
    Given an object type, this method classifies a set of Super Variants into classes depending on the number of involved objects of that type.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list of type SummarizedVariant
    :param object_type: The name of the object type
    :type object_type: string
    :return: A list containing a list with all Super Variants classes
    :rtype: list
    '''

    result = dict()

    for super_variant in initial_super_variant_set:
        cardinality = 0
        for lane in super_variant.lanes:
            if(lane.object_type == object_type):
                cardinality += 1

        if cardinality in result.keys():
            result[cardinality].append(super_variant)

        else: result[cardinality] = [super_variant]

    return list(result.values())


def classify_initial_super_variants_by_expression(initial_super_variant_set, boolean_expression):
    '''
    Given a boolean expression, this method classifies a set of Super Variants into two classes.
    :param initial_super_variant_set: The set of Super Variants
    :type initial_super_variant_set: list of type SummarizedVariant
    :param boolean_expression: The function evaluating a boolean expression on a Super Variant
    :type boolean_expression: func
    :return: A list containing a list with all Super Variants for which the boolean expression yields true or false, respectively
    :rtype: list
    '''
    result = [[],[]]
    for super_variant in initial_super_variant_set:

        if boolean_expression(super_variant):
            result[0].append(super_variant)
        else: 
            result[1].append(super_variant)

    return result


def containes_3_payment_reminder(super_variant):
    '''
    Determines whether a given Super Variant contains at least 3 occurences of an activity with the label "Payment Reminder".
    :param super_variant: The Super Variant
    :type super_variant: SummarizedVariant
    :return: The boolean result of the evaluation
    :rtype: bool
    '''
    count = 0
    for lane in super_variant.lanes:
        count += lane.count_activity("Payment Reminder")

    return count >= 3
