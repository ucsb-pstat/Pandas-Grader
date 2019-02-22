FROM berkeleydsep/singleuser-data100:ec21b4c
RUN pip uninstall -y okpy
COPY worker.py worker-requirements.txt ./
RUN pip install -r worker-requirements.txt
