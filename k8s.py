from kubernetes import client, config
from time import sleep
import yaml

config.load_kube_config()
api_client = client.ApiClient()
job_api = client.BatchV1Api(api_client)
api_instance = client.CoreV1Api(api_client)

name = "pi-with-ttl"
namespace = "data100-staging"


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

        pod_name = api_response["items"][0]["metadata"]["name"]

        api_response = api_instance.read_namespaced_pod_log(
            pod_name, namespace, follow=True, _preload_content=False
        )
        log_lines = list(api_response.stream())
        log_content = b"".join(log_lines)
        log_content = log_content.decode()
        return {"done": True, "log": log_content, "pod_name": pod_name}


def delete_job(name, namespace, pod_name):
    api_instance.delete_namespaced_pod(
        pod_name, namespace, body=client.V1DeleteOptions()
    )
    job_api.delete_namespaced_job(name, namespace, body=client.V1DeleteOptions())


if __name__ == "__main__":
    with open("ExampleJob.yml", "r") as f:
        create_job_from_str(f.read(), namespace)
    status, log = False, ""
    while status == False:
        print("checking...")
        resp = check_job_status(name, namespace)
        status = resp["done"]
        log = resp["log"]
        sleep(0.5)
    print(log)

    delete_job(name, namespace, resp["pod_name"])
