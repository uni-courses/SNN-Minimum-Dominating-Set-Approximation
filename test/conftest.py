def pytest_addoption(parser):
    """
    Parses CLI arguments to run specific (groups of) tests. Running:
    python -m pytest runs the default tests pertaining to the main code of
    this project. Including the argument --export_data runs the main code
    tests as well as tests that test the export_data code. Including the
    argument --neuron_behaviour runs the main code tests as well as tests that
    test the neuron and synaptic behaviours.
    :param parser: The object containing the arguments that are passed from the
    command line interface (CLI).

    """
    # Runs tests of main code, as well as tests pertaining to export_data code.
    parser.addoption(
        "--export_data",
        action="store_true",
        dest="export_data_tests",
        default=False,
        help="enable export_data tests",
    )

    # Runs tests of main code, as well as tests pertaining to neuron and
    # synaptic behaviour.
    parser.addoption(
        "--neuron_behaviour",
        action="store_true",
        dest="neuron_behaviour_tests",
        default=False,
        help="enable neuron_behaviour tests",
    )


def pytest_configure(config):
    """
    Sets the keywords, like @export_data_tests and/or @neuron_behaviour_tests
    that are used to run or not run (groups of) tests.

    :param config: Object representing which tests are and are not ran by
    pytest.

    """
    if not config.option.export_data_tests:
        setattr(config.option, "markexpr", "not export_data")
    if not config.option.neuron_behaviour_tests:
        setattr(config.option, "markexpr", "not neuron_behaviour_tests")
