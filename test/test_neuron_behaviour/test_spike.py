import unittest
import pytest

from pprint import pprint

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
            0  # LavaPyType(int, np.uint16, precision=12)=Unsigned integer (0 to 65535)
        )
        bias = 2

        # Get neurons that are fully connected.
        lif1, dense, lif2 = create_two_neurons(du_1=du_1, dv_1=dv_1, bias=bias)

        # Simulate SNN and assert values inbetween timesteps.
        print(f"t=0"), print_vars(lif1)
        self.assertEqual(lif1.v.get(), 0)  # Default initial value.
        self.assertEqual(lif1.u.get(), 0)  # Default initial value.
        self.assertEqual(lif1.du.get(), 3)  # Custom value.
        self.assertEqual(lif1.vth.get(), 10)  # Default value.

        for t in range(1, 10):

            v_previous = lif1.v.get()
            lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # v[t] = v[t-1] * (1-dv) + u[t] + bias
            # Constant with v[t=0]=0,u=0,bias=0
            expected_voltage = v_previous * (1 - dv_1) + lif1.u.get() + bias
            print(f"t={t}"), print(f"expected_voltage={expected_voltage}"), print_vars(
                lif1
            )

            if expected_voltage <= lif1.vth.get():
                self.assertEqual(lif1.v.get(), expected_voltage)
                
                # Verify the current at lif2 is zero.
                self.assertEqual(lif2.u.get(), 0)
            elif t == 6:
                # Assert the neuron spikes, the voltage is reset to 0 [V].
                #self.assertEqual(lif1.s_out, True)
                #self.assertEqual(lif1.s_out[0], True)
                #self.assertEqual(lif1.s_out.shape, True)

                pprint(dir(lif1.s_out))
                # The neuron spikes, assert the voltage is reset to 0 [V].
                #self.assertEqual(lif1.v.get(), 0)

                # Verify the spike signal comes in at dense().

                # Verify the spike signal comes goes out from dense().
                
                pprint(dir(dense.in_ports.s_in))
                pprint(f'dense.in_ports.s_in.in_connections={dir(dense.in_ports.s_in.in_connections)}')
                pprint(f'dense.in_ports.s_in.in_connections={dir(dense.in_ports.s_in.in_connections.__str__)}')
                pprint(f'dense.in_ports.s_in.in_connections={dense.in_ports.s_in.in_connections.__str__}')
                print(f'dense.in_ports.s_in={dense.in_ports}')
                #self.assertEqual(dense.in_ports.s_in,True)
                self.assertEqual(dense.in_ports.s_in,True)
            elif t==7:
                # Verify the spike signal comes in at lif2.
                self.assertEqual(lif2.u.get(), 1)
            elif t==8:
                # u(t=8)=u(t=7)*(1-du), u(t=7)=1 so 1*(1-3)=1*(-2)=-2
                self.assertEqual(lif2.u.get(), -2)
            else:
                raise Exception(
                    "Error, the neuron spiked even though it was not expected to spike."
                )
        lif1.stop(), lif2.stop()
