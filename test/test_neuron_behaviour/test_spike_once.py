import array
import unittest
import pytest


from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from lava.magma.core.process.variable import Var
from src.helper_snns import (
    create_spike_once_neuron,
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

        # Get neuron that spikes once and prints its values.
        spike_once = create_spike_once_neuron()
        du = spike_once.du.get()
        dv = spike_once.dv.get()
        bias = spike_once.bias.get()
        vth = spike_once.vth.get()
        print(f"t=0"), print_neuron_properties([spike_once])

        # Assert initialisation values of the spike_once_neurons.
        self.asserts_for_spike_once_at_t_is_0(bias, du, dv, spike_once, vth)

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 100):

            previous_u = spike_once.u.get()
            previous_v = spike_once.v.get()

            # Run the simulation for 1 timestep.
            spike_once.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # Print the values coming into the timestep.
            print(f"t={t}"), print_neuron_properties([spike_once])

            # Compute expected values.
            expected_u = previous_u * (1 - du) + spike_once.u.get() + a_in_spike_once(t)
            expected_v = previous_v * (1 - dv) + spike_once.u.get() + bias

            # Assert neuron values.
            self.redirect_tests(bias, du, dv, spike_once, t, vth)

        spike_once.stop()

    def redirect_tests(self, bias, du, dv, spike_once, t, vth):
        if t == 1:

            self.asserts_for_spike_once_at_t_is_1(bias, du, dv, spike_once, vth)
        elif t == 2:
            self.asserts_for_spike_once_at_t_is_2(bias, du, dv, spike_once, vth)
        elif t == 3:
            self.asserts_for_spike_once_at_t_is_3(bias, du, dv, spike_once, vth)
        elif t == 4:
            self.asserts_for_spike_once_at_t_is_4(bias, du, dv, spike_once, vth)
        elif t > 4:
            self.asserts_for_spike_once_at_t_is_larger_than_4(
                bias, du, dv, spike_once, vth
            )

    def asserts_for_spike_once_at_t_is_0(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=0."""
        self.assertEqual(spike_once.u.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.du.get(), du)  # Custom value.
        self.assertEqual(spike_once.v.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.dv.get(), dv)  # Default initial value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_1(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=1. t=1 occurs after
        one timestep."""

        # u[t=1]=u[t=0]*(1-0)+a_in
        # u[t=1]=0*(1-0)+0
        # u[t=1]=0*1+0
        # u[t=1]=0
        self.assertEqual(spike_once.u.get(), 0)
        # v[t=1] = v[t=0] * (1-dv) + u[t=0] + bias
        # v[t=1] = 0 * (1-2) + 0 + 2
        # v[t=1]_before_spike = 2
        # SPIKES! After spiking, it goes back to 0 [V]:
        # v[t=1]_after_spike = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_2(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=2."""

        # u[t=2]=u[t=1]*(1-du)+a_in
        # u[t=2]=0*(1-0)+-2
        # u[t=2]=0*1-2
        # u[t=2]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=2] = v[t=1] * (1-dv) + u[t=0] + bias
        # v[t=1]_before_spike = 2
        # v[t=1]_after_spike = 0
        # v[t=2] = 0 * (1-2) + -2 + 2
        # v[t=2] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_3(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=3."""

        # u[t=3]=u[t=2]*(1-du)+a_in
        # u[t=3]=-2*(1-0)-0
        # u[t=3]=-2*1-0
        # u[t=3]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=3] = v[t=2] * (1-dv) + u[t=2] + bias
        # v[t=3] = 0 * (1-0) -2 + 2
        # v[t=3] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_4(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=4."""

        # u[t=4]=u[t=3]*(1-du)+a_in
        # u[t=4]=0*(1-0)-1
        # u[t=4]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=4] = v[t=3] * (1-dv) + u[t=2] + bias
        # v[t=4] = 0 * (1-0) -2 + 2
        # v[t=4] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_larger_than_4(
        self, bias, du, dv, spike_once, vth
    ):
        """Assert the values of the spike_once neuron on t=4."""
        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # u[t=x+1]=0*(1-0)-1
        # u[t=x+1]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # The voltage stays constant indefinitely because the current
        # stays constant indefinitely whilst cancelling out the bias.
        # v[t=x+1] = v[t=x] * (1-dv) + u[t=2] + bias
        # v[t=x+1] = 0 * (1-0) -2 + 2
        # v[t=x+1] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.


def a_in_spike_once(t):
    if t == 2:
        return 1
    else:
        return 0
