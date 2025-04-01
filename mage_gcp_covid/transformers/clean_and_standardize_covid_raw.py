import pandas as pd
import gc                   # garbage collection

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

    logger.debug(f"Date Columns: {date_cols}")

    # melt dataframe (unpivot date columns)
    df_date_melted = pd.melt(
        df,
        id_vars=meta_cols,
        value_vars=date_cols,
        var_name="date",
        value_name="confirmed_cases"
    )

    # release memory
    del df
    gc.collect()

    # basic cleaning
    df_date_melted = df_date_melted.drop_duplicates()

    logger.info(f"US cases df_melted shape: {df_date_melted.shape}")

    # standardize column names
    df_date_melted.columns = (df_date_melted.columns
        .str.lower()                                        # lowercase
        .str.replace(' ', '_')                              # spaces to underscore
        .str.replace('#', 'nr')                             # pound sign signifies 'number'
        .str.replace(r'[\(\)\{\}\[\]<>]', '', regex=True)   # remove brackets/parentheses
        .str.replace(r'[^a-z0-9_]', '', regex=True)         # remove any other special chars
        .str.replace(r'_{2,}', '_', regex=True)             # replace multiple underscores with single
        .str.strip('_')                                     # remove leading/trailing underscores
    )

    # standardize data types

    # standard columns
    data_types: dict = {
        "province_state" :  "string",
        "admin2" :          "string",
        "uid" :             "string",
        "iso2" :            "string",
        "iso3" :            "string",
        "code3" :           "string",
        "fips" :            "string",
        "country_region" :  "string",
        "lat" :             "float64",
        "long" :            "float64",
        "combined_key" :    "string",
        "confirmed_cases" : "int64"
    }
    df_date_melted = df_date_melted.astype(data_types)

    # date columns
    df_date_melted["date"] = pd.to_datetime(
                                df_date_melted["date"],
                                format="%m/%d/%y",
                                errors="coerce")

    # debug negative cases
    # df_negative_cases = df_date_melted[df_date_melted["confirmed_cases"] < 0]
    # if len(negative_cases) > 0:
    #     logger.warning(f"Found {len(df_negative_cases)} records with negative `confirmed_cases`")

    #     # sample
    #     logger.info(f"Sample negative cases:\n f{df_negative_cases.head(5)}")


    return df_date_melted


@test
def test_output(output, *args) -> None:
    """
    Test the quality and structure of the Silver layer COVID data.
    """
    # Basic data validation
    assert output is not None, 'The output is undefined'
    assert len(output) > 0, 'Transformed data has no rows'
    
    # Data type validation
    assert pd.api.types.is_datetime64_dtype(output['date']), 'Date column is not datetime type'
    assert pd.api.types.is_numeric_dtype(output['confirmed_cases']), 'Confirmed cases is not numeric'
    
    # Data quality validation
    assert output['date'].isna().sum() == 0, 'There are missing dates after transformation'
    assert output.duplicated().sum() == 0, 'There are duplicate rows in the output'
    assert (output['confirmed_cases'] < 0).sum() == 0, 'There are negative case counts'
    
    # Business validation
    min_date = output['date'].min()
    max_date = output['date'].max()
    assert min_date >= pd.Timestamp('2020-01-01'), 'Data contains dates before expected range'
    assert max_date <= pd.Timestamp.now(), 'Data contains future dates'
