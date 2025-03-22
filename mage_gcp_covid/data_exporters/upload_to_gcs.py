from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader

from typing import Any

# gcs related
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud.storage import Client, transfer_manager

from pandas import DataFrame
from os import path, environ
import yaml

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

def upload_many_blobs_with_transfer_manager(
        bucket_name: str, 
        filenames: list, 
        file_prefix: str = "", 
        source_directory: str = "", 
        workers: int = 8,
        logger: Any = None
    ):
    """Upload every file in a list to a bucket, concurrently in a process pool.

    Each blob name is derived from the filename, not including the
    `source_directory` parameter. For complete control of the blob name for each
    file (and other aspects of individual blob metadata), use
    transfer_manager.upload_many() instead.
    """

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # A list (or other iterable) of filenames to upload.
    # filenames = ["file_1.txt", "file_2.txt"]

    # The directory on your computer that is the root of all of the files in the
    # list of filenames. This string is prepended (with os.path.join()) to each
    # filename to get the full path to the file. Relative paths and absolute
    # paths are both accepted. This string is not included in the name of the
    # uploaded blob; it is only used to find the source files. An empty string
    # means "the current working directory". Note that this parameter allows
    # directory traversal (e.g. "/", "../") and is not intended for unsanitized
    # end user input.
    # source_directory=""

    # The maximum number of processes to use for the operation. The performance
    # impact of this value depends on the use case, but smaller files usually
    # benefit from a higher number of processes. Each additional process occupies
    # some CPU and memory resources until finished. Threads can be used instead
    # of processes by passing `worker_type=transfer_manager.THREAD`.
    # workers=8

    # Configuration
    gcs_config = {
        'project_name':environ["GCP_PROJECT_NAME"],
        'bucket_name': bucket_name,
        'landing_prefix': file_prefix
    }

    # debug
    logger.debug(f"project_name: {gcs_config['project_name']}")

    storage_client = Client(
        project=gcs_config["project_name"],
        credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    # file_prefix: str = "01_bronze_landing/covid"

    results = transfer_manager.upload_many_from_filenames(
                    bucket, 
                    filenames,
                    blob_name_prefix=file_prefix, 
                    source_directory=source_directory, 
                    max_workers=workers
    )

    for name, result in zip(filenames, results):
        # The results list is either `None` or an exception for each filename in
        # the input list, in order.

        if isinstance(result, Exception):
            print("Failed to upload {} due to exception: {}".format(name, result))
            logger.error(Exception)
        else:
            print("Uploaded {} to {}.".format(name, bucket.name))


def get_gcp_sa_key_config(yaml_path: str, config_profile: str = "default") -> str:
    """
    Get the relevant service account file path from the config yaml file
    """
    # config_path = path.join(get_repo_path(), 'io_config.yaml')
    # config_profile = 'dev'

    with open(yaml_path, 'r') as file:
        try:
            # Load the YAML contents
            yaml_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            raise
    
    try:
        yaml_profile = yaml_data[config_profile]
    except:
        print(f"Profile {config_profile} not found...")
        raise

    try:
        sa_file_path = yaml_profile["GOOGLE_SERVICE_ACC_KEY_FILEPATH"]
        return sa_file_path
    except:
        print(f"No relevant Service Account found.")
        raise


# Get correct service account from io_config
config_path: str = path.join(get_repo_path(), 'io_config.yaml')
config_profile: str = 'dev'
sa_path: str = get_gcp_sa_key_config(config_path, config_profile)

# debug
# print(f"sa_path: {sa_path}")

# Configure service account with GCS scope
credentials = service_account.Credentials.from_service_account_file(
    sa_path,
    scopes=['https://www.googleapis.com/auth/devstorage.full_control']
)

# Main decorated blocks
@data_exporter
def export_data_to_google_cloud_storage(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a Google Cloud Storage bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#googlecloudstorage
    """
    # set block logger
    logger = kwargs.get("logger")

    bucket_name = 'covid-medallion-lake'
    object_prefix = '01_bronze_landing/covid/'
    src_path_local = kwargs["dump_dir"]

    # upload relevant files to gcs (only raw)
    file_list: list = [
        "RAW_global_confirmed_cases.csv",
        "RAW_global_deaths.csv",
        "RAW_us_confirmed_cases.csv",
        "RAW_us_deaths.csv",
    ]
    upload_many_blobs_with_transfer_manager(
        bucket_name=bucket_name,
        filenames=file_list,
        file_prefix=object_prefix,
        source_directory=src_path_local,
        workers=8,
        logger=logger
    )
