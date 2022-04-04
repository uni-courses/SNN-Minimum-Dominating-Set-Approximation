import unittest
import pytest


from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.helper_snns import (
    create_spike_once_neuron,
    create_two_neurons,
    print_neuron_properties,
)


# Include marker ensuring these tests only run on argument: neuron_behaviour
neuron_behaviour_test = pytest.mark.skipif(
    "not config.getoption('neuron_behaviour_tests')"
)


class Test_spike_once(unittest.TestCase):
    """ """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_spike_once, self).__init__(*args, **kwargs)

    # v[t] = v[t-1] * (1-dv) + u[t] + bias
    # v represents the voltage in a neuron.
    @neuron_behaviour_test
    def test_spike_once(self):
        """ """
        du = 0
        dv = 0
        bias = 1
        vth = 1

        # Get neuron that spikes once and prints its values.
        spike_once = create_spike_once_neuron()
        print(f"t=0"), print_neuron_properties([spike_once])

        # Assert initialisation values of the spike_once_neurons.
        self.asserts_for_spike_once_at_t_is_0(bias, du, dv, spike_once, vth)

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 10):

            # Print the values coming into the timestep.
            print(f"t={t}"), print_neuron_properties([spike_once])
            previous_u = spike_once.u.get()
            previous_v = spike_once.v.get()

            # Run the simulation for 1 timestep.
            spike_once.run(
                condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg()
            )

            # Compute expected values.
            expected_u = (
                previous_u * (1 - du)
                + spike_once.u.get()
                + self.a_in_spike_once(t)
            )
            expected_v = previous_v * (1 - dv) + spike_once.u.get() + bias

            # Assert neuron values.

        spike_once.stop()

    def a_in_spike_once(self, t):
        if t == 2:
            return 1
        else:
            return 0

    def redirect_tests(self, previous_u, previous_v, spike_once, t):
        if t == 1:

            self.asserts_for_spike_once_at_t_is_1(
                previous_u, previous_v, spike_once
            )
        elif t == 2:
            self.asserts_for_spike_once_at_t_is_2(
                previous_u, previous_v, spike_once
            )
        elif t == 3:
            self.asserts_for_spike_once_at_t_is_3(
                previous_u, previous_v, spike_once
            )
        elif t == 4:
            self.asserts_for_spike_once_at_t_is_4(
                previous_u, previous_v, spike_once
            )

    def asserts_for_spike_once_at_t_is_0(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=0."""
        self.assertEqual(spike_once.v.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.u.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.du.get(), du)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_1(
        self, previous_u, previous_v, spike_once
    ):
        """Assert the values of the spike_once neuron on t=1. t=1 occurs after
        one timestep."""

        # u[t=2]=u[t=1]*(1-du)+a_in
        # u[t=2]=0*(1-0)+0
        # u[t=2]=0
        self.assertEqual(spike_once.u.get(), 0)
        # v[t=2] = v[t=1] * (1-dv) + u[t=2] + bias
        # v[t=2] = 0 * (1-0) -1 + +1
        # v[t=2] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), 0)  # Custom Value.
        self.assertEqual(spike_once.vth.get(), 1)  # Custom value.

    def asserts_for_spike_once_at_t_is_2(
        self, previous_u, previous_v, spike_once
    ):
        """Assert the values of the spike_once neuron on t=2."""

        # u[t=2]=u[t=1]*(1-du)+a_in
        # u[t=2]=0*(1-0)-1
        # u[t=2]=-1
        self.assertEqual(spike_once.u.get(), -1)
        # v[t=2] = v[t=1] * (1-dv) + u[t=2] + bias
        # v[t=2] = 0 * (1-0) -1 + +1
        # v[t=2] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), 0)  # Custom Value.
        self.assertEqual(spike_once.vth.get(), 1)  # Custom value.

    def asserts_for_spike_once_at_t_is_3(
        self, previous_u, previous_v, spike_once
    ):
        pass

    def asserts_for_spike_once_at_t_is_4(
        self, previous_u, previous_v, spike_once
    ):
        pass
