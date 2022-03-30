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
        print(f"hi")

    # tests unit test  u[t] = u[t-1] * (1-du) + a_in with a_in=0
    # u represents the current in a neuron.
    @neuron_behaviour_test
    def test_constant_u(self):
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
            self.assertEqual(lif1.v.get(), 0)  # Should stay constant without input.
            # u(t=1)=u(t=0)*(1-du), u(t=0)=0 so 0*(1-3)=0*(-2)=0
            self.assertEqual(lif1.u.get(), 0)
            self.assertEqual(lif1.du.get(), 3)  # Should stay constant.
            self.assertEqual(lif1.vth.get(), 10)  # Default value.

        lif1.stop(), lif2.stop()

    # tests unit test  u[t] = u[t-1] * (1-du) + a_in with a_in=0
    # u represents the current in a neuron.
    @neuron_behaviour_test
    def test_growing_u_without_a(self):
        """ """

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(u_1=10, du_1=3)

        # Simulate SNN and assert values inbetween timesteps.
        print(f"t=0"), print_vars(lif1)
        # NOTE, the u is not set to 1 because always initialises to
        # 0, even if you specify u=10
        self.assertEqual(lif1.u.get(), 0)  # Custom initial value.

        lif1.stop(), lif2.stop()
