FROM airbyte/base-python:dev

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="destination_custom_python"

RUN pip install pandas
RUN pip install requests
WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
COPY main.py ./
RUN pip install .

ENTRYPOINT ["python3", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-custom-python

