FROM ucsb/pstat-134:v191012

COPY worker.py worker-requirements.txt ./

## conda activate workaround from
## https://github.com/ContinuumIO/docker-images/issues/89

## okpy environment for executing notebooks
RUN conda create -y --name okpy --clone base && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate okpy && \
    pip install okpy

## gofer environment for autograder
RUN conda create -y --name gofer --clone base && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate gofer && \
    pip uninstall -y okpy && \
    pip install -r worker-requirements.txt

