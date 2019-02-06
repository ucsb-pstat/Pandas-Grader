FROM berkeleydsep/singleuser-data100:ec21b4c
COPY worker.py worker-requirements.txt
RUN pip install -r worker-requirements.txt
