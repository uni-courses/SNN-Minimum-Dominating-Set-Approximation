import unittest
import pytest

from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.helper_snns import (
    create_two_neurons,
    print_neuron_properties,
)


# Include marker ensuring these tests only run on argument: neuron_behaviour.
neuron_behaviour_test = pytest.mark.skipif(
    "not config.getoption('neuron_behaviour_tests')"
)


class Test_neuron_u(unittest.TestCase):
    """ """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_neuron_u, self).__init__(*args, **kwargs)

        # tests unit test  u[t] = u[t-1] * (1-du) + a_in with a_in=0

    # u represents the current in a neuron.
    @neuron_behaviour_test
    def test_spike(self):
        """Tests whether a spike occurs when the neuron voltage exceeds the
        threshold. Then verifies the spike signal is propagated correctly from
        lif1 to lif2. Also verifies the voltage of lif1 grows as expected, when a
        non-zero bias is used. The current u is kept constant for lif1. If the
        voltage exceeds the (default) threshold vth=10, then the neuron spikes
        and the voltage is reset to 0 (Regardless if it is 15 [V] over or 1 [V]
        over the threshold).
        #"""
        # Regarding the value ranges:
        # https://jakevdp.github.io/PythonDataScienceHandbook/02.01-understanding-data-types.html
        du_1 = 3
        dv_1 = (
            0  # LavaPyType(int, np.uint16, precision=12)=Unsigned integer (0
            # to 65535)
        )
        bias_1 = 2

        du_2 = 2
        dv_2 = (
            1  # LavaPyType(int, np.uint16, precision=12)=Unsigned integer (0
            # to 65535)
        )
        bias_2 = 4

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(
            du_1=du_1,
            dv_1=dv_1,
            bias_1=bias_1,
            du_2=du_2,
            dv_2=dv_2,
            bias_2=bias_2,
        )

        # Simulate SNN and assert values inbetween timesteps.
        # print("t=0"), print_neuron_properties(lif1)

        self.assertEqual(lif1.v.get(), 0)  # Default initial value.
        self.assertEqual(lif1.u.get(), 0)  # Default initial value.
        self.assertEqual(lif1.du.get(), 3)  # Custom value.
        self.assertEqual(lif1.vth.get(), 10)  # Default value.

        lif1_has_spiked = False
        for t in range(1, 10):

            # Get the voltage of the lif1 neuron at the last timestep.
            v_previous = lif1.v.get()

            # Simulate the snn for 1 timestep
            lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Compute expected voltage of neuron 1
            # v[t] = v[t-1] * (1-dv) + u[t] + bias_1
            # Constant with v[t=0]=0,u=0,bias_1=0
            expected_voltage = v_previous * (1 - dv_1) + lif1.u.get() + bias_1
            if expected_voltage > lif1.vth.get():
                lif1_has_spiked = True

            # Print neuron properties for each timestep
            print(f"t={t}"), print(f"expected_voltage={expected_voltage}")
            print_neuron_properties([lif1, lif2], [1, 2])

            # Verify the voltage of lif1 is as expected as long as it has not
            # spiked.
            if expected_voltage <= lif1.vth.get() and not lif1_has_spiked:
                self.assertEqual(lif1.v.get(), expected_voltage)

                # Verify the current at lif2 is zero.
                self.assertEqual(lif2.u.get(), 0)
            if t == 5:
                self.assertFalse(lif1_has_spiked)
                self.assertEqual(lif2.u.get(), 0)  # Default initial value.
                self.assertEqual(lif2.du.get(), 2)  # Custom initial value.
                # v[t] = v[t-1] * (1-dv) + u[t] + bias_2
                self.assertEqual(lif2.v.get(), 4)
            if t == 6:
                self.assertTrue(lif1_has_spiked)
                # Verify the lif2 neuron has not yet received a spike when
                # neuron1 spikes.
                self.assertEqual(lif2.u.get(), 0)  # Default initial value.
                self.assertEqual(lif2.du.get(), 2)  # Custom initial value.
                # v[t] = v[t-1] * (1-dv) + u[t] + bias_2
                # v[t] = 4 * (1-1) + 0 + 4=4
                self.assertEqual(lif2.v.get(), 4)  # Default initial value.
            elif t == 7:
                # Verify the spike signal comes in at lif2.
                self.assertEqual(lif2.u.get(), 3)
                # v[t] = v[t-1] * (1-dv) + u[t] + bias_2
                # v[t] = 4 * (1-1) + 3 + 4=7
                self.assertEqual(lif2.v.get(), lif2.u.get() + bias_2)
            elif t == 8:
                # u(t=8)=u(t=7)*(1-du)+a_in, u(t=7)=3 so 3*(1-2)=3*(-1)=-3
                self.assertEqual(lif2.u.get(), -3)
        lif1.stop()
