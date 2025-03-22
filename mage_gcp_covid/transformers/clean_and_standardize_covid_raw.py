import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

# helper and utility functions
def contains_chars(string: str, chars_to_check) -> bool:
    # checks if input string contains any of the chars in 'chars_to_check'
    return any(char in string for char in chars_to_check)


# Main Decorator blocks
@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    logger = kwargs["logger"]

    # Specify your transformation logic here
    df = data
    logger.info(f"US cases df shape: {df.shape}")
    logger.info(f"Columns: {df.columns}")
    # debug
    # for col in df.columns:
    #     print(col)

    # define all column groups
    meta_cols = [
        "Province_State",
        "Admin2",
        "UID",
        "iso2",
        "iso3",
        "code3",
        "FIPS",
        "Country_Region",
        "Lat",
        "Long_",
        "Combined_Key"        
    ]

    date_cols = [col for col in df.columns if contains_chars(col, "/")]

    logger.info(f"Date Columns: {date_cols}")

    # melt dataframe (unpivot date columns)
    df_date_melted = pd.melt(
        df,
        id_vars=meta_cols,
        value_vars=date_cols,
        var_name="date",
        value_name="confirmed_cases"
    )

    # standardize column names


    # standardize data types


    

    return df_date_melted


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
