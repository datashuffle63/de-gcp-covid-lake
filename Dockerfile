FROM mageai/mageai:latest

ARG PROJECT_NAME=mage_gcp_covid
ARG MAGE_CODE_PATH=/home/src
ARG USER_CODE_PATH=${MAGE_CODE_PATH}/${PROJECT_NAME}

ENV PYTHONPATH="${PYTHONPATH}:${MAGE_CODE_PATH}"
ENV USER_CODE_PATH=${USER_CODE_PATH}

WORKDIR ${MAGE_CODE_PATH}

# Install custom Python libraries
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD ["/bin/sh", "-c", "/app/run_app.sh"]