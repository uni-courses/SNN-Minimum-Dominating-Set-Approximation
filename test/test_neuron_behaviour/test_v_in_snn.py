import unittest
import pytest


from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.helper_snns import create_two_neurons, print_vars


# Include marker ensuring these tests only run on argument: neuron_behaviour
neuron_behaviour_test = pytest.mark.skipif(
    "not config.getoption('neuron_behaviour_tests')"
)


class Test_neuron_u(unittest.TestCase):
    """ """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_neuron_u, self).__init__(*args, **kwargs)

    # v[t] = v[t-1] * (1-dv) + u[t] + bias
    # v represents the voltage in a neuron.
    @neuron_behaviour_test
    def test_constant_v(self):
        """ """

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(du_1=3)

        # Simulate SNN and assert values inbetween timesteps.
        print(f"t=0"), print_vars(lif1)
        self.assertEqual(lif1.v.get(), 0)  # Default initial value.
        self.assertEqual(lif1.u.get(), 0)  # Default initial value.
        self.assertEqual(lif1.du.get(), 3)  # Custom value.
        self.assertEqual(lif1.vth.get(), 10)  # Default value.

        for i in range(10):
            print(f"t={i+1}"), print_vars(lif1)
            lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # v[t] = v[t-1] * (1-dv) + u[t] + bias
            # Constant with v[t=0]=0,u=0,bias=0
            self.assertEqual(lif1.v.get(), 0)
            # u(t=1)=u(t=0)*(1-du), u(t=0)=0 so 0*(1-3)=0*(-2)=0
            self.assertEqual(lif1.u.get(), 0)
            self.assertEqual(lif1.du.get(), 3)  # Should stay constant.
            self.assertEqual(lif1.vth.get(), 10)  # Default value.

        lif1.stop(), lif2.stop()

    # tests unit test  u[t] = u[t-1] * (1-du) + a_in with a_in=0
    # u represents the current in a neuron.
    @neuron_behaviour_test
    def test_constant_despite_dv(self):
        """ """

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(du_1=3, dv_1=4)

        # Simulate SNN and assert values inbetween timesteps.
        print(f"t=0"), print_vars(lif1)
        self.assertEqual(lif1.v.get(), 0)  # Default initial value.
        self.assertEqual(lif1.u.get(), 0)  # Default initial value.
        self.assertEqual(lif1.du.get(), 3)  # Custom value.
        self.assertEqual(lif1.vth.get(), 10)  # Default value.

        for i in range(10):
            print(f"t={i+1}"), print_vars(lif1)
            lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # v[t] = v[t-1] * (1-dv) + u[t] + bias
            # Constant with v[t=0]=0,u=0,bias=0
            self.assertEqual(lif1.v.get(), 0)
            self.assertEqual(lif1.v.get(), 0)
            # u(t=1)=u(t=0)*(1-du), u(t=0)=0 so 0*(1-3)=0*(-2)=0
            # Constant with u[t=0]=0,u=0,a_in=0
            self.assertEqual(lif1.u.get(), 0)
            self.assertEqual(lif1.du.get(), 3)  # Should stay constant.
            self.assertEqual(lif1.vth.get(), 10)  # Default value.

        lif1.stop(), lif2.stop()

    # tests unit test  u[t] = u[t-1] * (1-du) + a_in with a_in=0
    # u represents the current in a neuron.
    @neuron_behaviour_test
    def test_growing_v(self):
        """Tests whether the voltage of lif1 grows as expected, when a
        non-zero bias is used. The current u is kept constant for lif1. If the
        voltage EXCEEDS(not equals) the (default) threshold vth=10, then the neuron spikes
        and the voltage is reset to 0 (Regardless if it is 15 [V] over or 1 [V]
        over the threshold).
        #"""
        du_1 = 3
        dv_1 = 4
        bias = 1

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(du_1=du_1, dv_1=dv_1, bias_1=bias)

        # Simulate SNN and assert values inbetween timesteps.
        print(f"t=0"), print_vars(lif1)
        self.assertEqual(lif1.v.get(), 0)  # Default initial value.
        self.assertEqual(lif1.u.get(), 0)  # Default initial value.
        self.assertEqual(lif1.du.get(), 3)  # Custom value.
        self.assertEqual(lif1.vth.get(), 10)  # Default value.

        for t in range(1, 10):

            v_previous = lif1.v.get()
            lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            print(f"t={t}"), print_vars(lif1)
            # v[t] = v[t-1] * (1-dv) + u[t] + bias
            # Constant with v[t=0]=0,u=0,bias=0
            expected_voltage = v_previous * (1 - dv_1) + lif1.u.get() + bias
            if expected_voltage <= lif1.vth.get():
                self.assertEqual(lif1.v.get(), expected_voltage)
            else:
                # The neuron has spiked, the voltage is reset to 0 [V].
                self.assertEqual(lif1.v.get(), 0)

            # u(t=1)=u(t=0)*(1-du), u(t=0)=0 so 0*(1-3)=0*(-2)=0
            # Constant with u[t=0]=0,u=0,a_in=0
            self.assertEqual(lif1.u.get(), 0)
            self.assertEqual(lif1.du.get(), 3)  # Should stay constant.
            self.assertEqual(lif1.vth.get(), 10)  # Default value.
        lif1.stop(), lif2.stop()
