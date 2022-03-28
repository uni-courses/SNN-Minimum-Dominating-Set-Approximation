def pytest_addoption(parser):
    parser.addoption(
        "--export_data",
        action="store_true",
        dest="export_data_tests",
        default=False,
        help="enable export_data tests",
    )


def pytest_configure(config):
    if not config.option.export_data_tests:
        setattr(config.option, "markexpr", "not export_data")
