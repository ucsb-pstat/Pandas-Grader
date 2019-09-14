import jinja2
import yaml
from kubernetes import client, config
from constance import config as constants
from uuid import uuid4
import os


def add_k_workers(k):
    deploy_jobs(
        kwargs=dict(
            name=f"grader-server-{uuid4().hex[:6]}",
            parallelism=constants.PARALLELISM,
            num_jobs=k,
            api_addr=constants.ADDRESS,
        ),
        namespace=constants.NAMESPACE,
    )


def deploy_jobs(kwargs, namespace):
    config.load_kube_config(os.path.expanduser("~/.kube/config"))
    api_client = client.ApiClient()
    job_api = client.BatchV1Api(api_client)

    tmpl = jinja2.Template(raw_str)
    rendered = tmpl.render(**kwargs)
    rendered_yml = yaml.safe_load(rendered)

    job_api_response = job_api.create_namespaced_job(namespace, rendered_yml)
    print("Kube Job metadata")
    print(job_api_response.metadata)

raw_str = """
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ name }}
spec:
  backoffLimit: 0
  parallelism: {{ parallelism }}
  completions: {{ num_jobs }}
  template:
    spec:
      containers:
      - name: {{ name }}
        image: wwhuang/jhub-gofer:latest
        command: [
          "python", "worker.py", 
          "--api-url", "{{ api_addr }}"]
      restartPolicy: Never
      imagePullPolicy: Always
      resources:
        requests:
          memory: "2G"
        limits:
          memory: "4G"
"""
