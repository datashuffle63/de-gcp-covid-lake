import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

import pandas as pd
from pathlib import Path


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # set block logger
    logger = kwargs.get("logger")

    # set Kaggle dataset path and download
    api = KaggleApi()
    api.authenticate()

    dataset_path: str = kwargs["dataset_ep"]
    dump_path: str = kwargs["dump_dir"]
    logger.debug("Path to dataset files:", dataset_path)

    # download to local
    Path(dump_path).mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(dataset_path, path=dump_path, unzip=True)


    return {}


@test
def test_output(output, *args, **kwargs) -> None:
    """
    Template code for testing the output of the block.
    """
    dump_path: str = kwargs["dump_dir"]
    file_list: list = [
        "CONVENIENT_global_confirmed_cases.csv",
        "CONVENIENT_global_deaths.csv",
        "CONVENIENT_global_metadata.csv",
        "CONVENIENT_us_confirmed_cases.csv",
        "CONVENIENT_us_deaths.csv",
        "CONVENIENT_us_metadata.csv",
        "RAW_global_confirmed_cases.csv",
        "RAW_global_deaths.csv",
        "RAW_us_confirmed_cases.csv",
        "RAW_us_deaths.csv",
    ]

    # check existence of all files in dump folder
    dict_dump: dict = check_files_exist(dump_dir=dump_path, file_list=file_list)

    # assert output is not None, 'The output is undefined'
    assert len(dict_dump["list_missing"]) == 0, f"Expected dataset files are missing: {dict_dump['list_missing']}"


def check_files_exist(dump_dir: str, file_list: list) -> dict:

    # creact dict with filename and existence status
    dict_results: dict = {file: Path(f"{dump_dir}/{file}").is_file() for file in file_list}

    list_exists: list = [file for file in file_list if Path(f"{dump_dir}/{file}").is_file()]
    list_missing: list = [file for file in file_list if not Path(f"{dump_dir}/{file}").is_file()]

    return {
        "dict_results": dict_results,
        "list_exists": list_exists,
        "list_missing": list_missing
    }

