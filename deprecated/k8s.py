from time import sleep

import jinja2
import yaml
from kubernetes import client, config

config.load_kube_config()
api_client = client.ApiClient()
job_api = client.BatchV1Api(api_client)
api_instance = client.CoreV1Api(api_client)

name = "pandas-grader-worker"
namespace = "data100-staging"


def create_grading_job(tmpl_file, kwargs):
    with open("GradingJobConfig.yml", "r") as f:
        raw_str = f.read()
        tmpl = jinja2.Template(raw_str)
        create_job_from_str(tmpl.render(**kwargs), namespace)


def create_job_from_str(template_str, namespace):
    job_api.create_namespaced_job(namespace, yaml.load(template_str))


def check_job_status(name, namespace):
    job_status = job_api.read_namespaced_job_status(name, namespace).to_dict()
    success = job_status["status"]["succeeded"]
    if success is None:
        return {"done": False, "log": "", "pod_name": ""}
    else:
        c_uid = job_status["spec"]["selector"]["match_labels"]["controller-uid"]

        api_response = api_instance.list_namespaced_pod(
            namespace, label_selector=f"controller-uid={c_uid}"
        ).to_dict()

        all_log = ""
        pod_names = []
        for pod in api_response["items"]:
            pod_name = pod["metadata"]["name"]
            pod_names.append(pod_name)

            api_response = api_instance.read_namespaced_pod_log(
                pod_name, namespace, follow=True, _preload_content=False
            )
            log_lines = list(api_response.stream())
            log_content = b"".join(log_lines)
            log_content = log_content.decode()
            all_log += pod_name + "========\n" + log_content + "\n"
        return {"done": True, "log": all_log, "pod_names": pod_names}


def delete_job(name, namespace, pod_names):
    for pod_name in pod_names:
        api_instance.delete_namespaced_pod(
            pod_name, namespace, body=client.V1DeleteOptions()
        )
    job_api.delete_namespaced_job(name, namespace, body=client.V1DeleteOptions())


if __name__ == "__main__":
    with open("GradingJobConfig.yml", "r") as f:
        raw_str = f.read()
        tmpl = jinja2.Template(raw_str)
        create_job_from_str(
            tmpl.render(name=name, api_addr="http://grading.ds100.org:8080"), namespace
        )

    # status, log = False, ""
    # while status == False:
    #     print("checking...")
    #     resp = check_job_status(name, namespace)
    #     status = resp["done"]
    #     log = resp["log"]
    #     sleep(0.5)
    # print(log)

    # # delete_job(name, namespace, resp["pod_names"])
