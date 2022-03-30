def pytest_addoption(parser):
    parser.addoption(
        "--export_data",
        action="store_true",
        dest="export_data_tests",
        default=False,
        help="enable export_data tests",
    )
    parser.addoption(
        "--neuron_behaviour",
        action="store_true",
        dest="neuron_behaviour_tests",
        default=False,
        help="enable neuron_behaviour tests",
    )


def pytest_configure(config):
    if not config.option.export_data_tests:
        setattr(config.option, "markexpr", "not export_data")
    if not config.option.neuron_behaviour_tests:
        setattr(config.option, "markexpr", "not neuron_behaviour_tests")
