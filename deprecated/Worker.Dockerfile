FROM berkeleydsep/singleuser-data100:e053e95
RUN pip uninstall -y okpy
COPY worker.py worker-requirements.txt ./
RUN pip install -r worker-requirements.txt
