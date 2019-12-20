FROM ucsb/pstat-134:v191121

USER $NB_UID

COPY worker.py worker-requirements.txt ./

## conda activate workaround from
## https://github.com/ContinuumIO/docker-images/issues/89
RUN  . /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda install -y defaults::nb_conda_kernels

## okpy environment for executing notebooks
RUN conda create -y --name okpy --clone base && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate okpy && \
    conda install -y ipykernel && \
    pip install okpy

## gofer environment for autograder
RUN conda create -y --name gofer --clone base && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate gofer && \
    conda install -y ipykernel && \
    pip uninstall -y okpy && \
    pip install -r worker-requirements.txt

