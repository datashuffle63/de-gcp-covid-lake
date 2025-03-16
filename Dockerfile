FROM mageai/mageai:latest

ARG PROJECT_NAME=mage_gcp_covid
ARG MAGE_CODE_PATH=/home/src
ARG USER_CODE_PATH=${MAGE_CODE_PATH}/${PROJECT_NAME}

ENV PYTHONPATH="${PYTHONPATH}:${MAGE_CODE_PATH}"
ENV USER_CODE_PATH=${USER_CODE_PATH}

# set GCP project name here
ENV GCP_PROJECT_NAME=de-gcp-lake-covid

WORKDIR ${MAGE_CODE_PATH}

# Install custom Python libraries
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# make sure gcs supports transfer_manager by installing at least 2.7.0
RUN pip install --upgrade google-cloud-storage>=2.7.0

CMD ["/bin/sh", "-c", "/app/run_app.sh"]