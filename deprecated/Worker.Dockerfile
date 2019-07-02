FROM berkeleydsep/singleuser-data100:3c1f8ad
RUN pip uninstall -y okpy
COPY worker.py worker-requirements.txt ./
RUN pip install -r worker-requirements.txt
