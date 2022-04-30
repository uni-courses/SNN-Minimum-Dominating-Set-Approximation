import random


class Radiation_damage:
    """Creates expected properties of the spike_once neuron."""

    def __init__(self, nr_of_neurons, seed):
        self.neuron_decay = 0.1  # % of neurons that will decay.
        # self.synaptic_decay = 0.2  # % of synapses that will decay.
        self.decayed_neuron = "spike_once_0_0"
        self.decayed_neurons = ["spike_once_0_0", "degree_receiver_0_2"]
        self.adaption_decays = False  # specifies if redundant neurons decay.

        # get list of node_indices that will decay.
        # TODO: fill with random nrs based on seed.
        if self.adaption_decays:
            self.nr_of_decaying_neurons = nr_of_neurons * self.neuron_decay * 2
            self.random_int_list = self.get_random_list_of_len_n(
                self.nr_of_decaying_neurons, nr_of_neurons * 2
            )
        else:
            self.nr_of_decaying_neurons = nr_of_neurons * self.neuron_decay
            self.random_int_list = self.get_random_list_of_len_n(
                self.nr_of_decaying_neurons, nr_of_neurons
            )

    def get_random_list_of_len_n(self, n, max_val):
        """Does not include max, only below."""
        randomlist = []
        for i in range(int(0), int(n)):
            n = random.randint(0, max_val)
        randomlist.append(n)
        print(randomlist)
        return randomlist
