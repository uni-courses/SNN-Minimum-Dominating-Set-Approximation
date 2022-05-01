import pickle
import os


def get_results():
    run_results = load_run_results()
    print_neuron_death_probabilities(run_results, False)
    print_neuron_death_probabilities(run_results, True)


def print_neuron_death_probabilities(run_results, has_adaptation):
    neuron_death_probabilities = get_all_neuron_death_probabilities(run_results)

    print(f"has adaptation:{has_adaptation}:neuron_death_probability,robustness")
    for neuron_death_probability in get_all_neuron_death_probabilities(run_results):
        robustness = compute_robustness(
            run_results, has_adaptation, neuron_death_probability, redundancy_level=None
        )

        print(f"{neuron_death_probability},{robustness}")


def get_all_neuron_death_probabilities(run_results):
    neuron_death_probabilities = []
    for run_result in run_results:
        neuron_death_probabilities.append(run_result.neuron_death_probability)
    return list(sorted(set(neuron_death_probabilities)))


def load_run_results():
    run_results = []
    pickle_filepaths = get_pickle_filepaths()
    for filepath in pickle_filepaths:
        G, get_degree, iteration, m, run_result, seed, size = load_pickle_from_file(
            filepath
        )
        run_results.append(run_result)

    return run_results


def get_pickle_filepaths():
    """- [ ] Loop over all output pickles."""
    # Get the list of all files and directories
    path = "pickles/"
    dir_list = os.listdir(path)

    pickle_filepaths = keep_pickle_files_only(dir_list)
    return pickle_filepaths


def keep_pickle_files_only(file_list):
    pickle_files = []
    for filename in file_list:
        if filename[-4:] == ".pkl":
            pickle_files.append(f"pickles/{filename}")
    return pickle_files


def load_pickle_from_file(filepath):
    pickle_off = open(
        filepath,
        "rb",
    )
    [G, get_degree, iteration, m, run_result, seed, size] = pickle.load(pickle_off)
    # print(f"m={m}")
    # print(f"adaptation={run_result.has_adaptation}")
    # print(f"seed={seed}")
    # print(f"size={size}")
    # print(f"m={m}")
    # print(f"iteration={iteration}")
    # print(f"neuron_death_probability={run_result.neuron_death_probability}")
    #
    # print(f"dead_neuron_names={run_result.dead_neuron_names}")
    # print(f"has_passed={run_result.has_passed}")
    # print(f"amount_of_neurons={run_result.amount_of_neurons}")
    # print(f"amount_synapses={run_result.amount_synapses}")
    # print(f"has_adaptation={run_result.has_adaptation}")
    return G, get_degree, iteration, m, run_result, seed, size


def compute_robustness(
    run_results, count_for_adaptation, neuron_death_probability, redundancy_level=None
):
    """
    Input list of run_results.
    output: float, NOT: dictionary keys: redundancy factor
    values: fraction of correct runs/total nr of runs.

     compute:
      # Per radiation death probability:
         # Without adaptation: (Per redundancy level=100%): amount of correct runs/total amount of runs
         # With adaptation: (Per redundancy level=100%): amount of correct runs/total amount of runs
    """
    correct = 0
    incorrect = 0
    found_result = False
    for run_result in run_results:
        if run_result.has_adaptation == count_for_adaptation:
            if run_result.neuron_death_probability == neuron_death_probability:
                found_result = True
                if run_result.has_passed:
                    correct += 1
                else:
                    incorrect += 1
    if found_result:
        return correct / (correct + incorrect)
    else:
        return None


def compute_overcapacity(run_results, redundancy_level=None):
    """
    Input
    output: Dictionary:graph size, neuron overcapacity
    output: Dictionary:graph size, synapse overcapacity
     compute:
      # Per radiation death probability:
         # Without adaptation (Per redundancy level=100%): Nr of neurons
        # With adaptation (Per redundancy level=100%): Nr of neurons
        # divide with by without and print that fraction
    """
    correct = 0
    incorrect = 0
    neuron_overcapacity = []

    run_results_without = get_run_results_without_adaptation(run_results)
    run_results_with = get_run_results_with_adaptation(run_results)

    for run_result_without in run_results_without:
        for run_result_with in run_results_with:
            if set(run_result_without.G.edges()) == set(run_result_with.G.edges()):
                print(f"found graph")
                edges_without_adaptation = len(run_result_with.get_degree.edges())
                edges_with_adaptation = len(run_result_with.get_degree.edges())
                neuron_overcapacity.append(
                    [
                        len(run_result_without.G),
                        edges_without_adaptation,
                        edges_with_adaptation,
                    ]
                )

    return neuron_overcapacity


def get_run_results_without_adaptation(run_results):
    without = []
    for run_result in run_results:
        if not run_result.has_adaptation:
            without.append(run_result)
    return without


def get_run_results_with_adaptation(run_results):
    run_result_with = []
    for run_result in run_results:
        if run_result.has_adaptation:
            run_result_with.append(run_result)
    return run_result_with


def get_get_degree_graphs_without_adaptation(run_results):
    graphs = []
    for run_result in run_results:
        if not run_result.has_adaptation:
            graphs.append(run_result.get_degree)
    return graphs


def get_get_degree_graphs_with_adaptation(run_results):
    graphs = []
    for run_result in run_results:
        if run_result.has_adaptation:
            graphs.append(run_result.get_degree)
    return graphs


# Allow option to recreate
# graph
# alipour graphs
# snn over time


# Without adaptation (Per redundancy level=100%): Nr of spikes
# With adaptation (Per redundancy level=100%): Nr of spikes
