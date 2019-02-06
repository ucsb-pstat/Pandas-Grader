import logging
import os
import subprocess
import zipfile

import click
import requests

import gofer.ok

GRADING_DIR = "grading"


def gofer_wrangle(res):
    return {"total": sum(r.grade for r in res), "msg": "\n".join(repr(r) for r in res)}


@click.command()
@click.option("--api-url", required=True)
def main(api_url):
    fetched = requests.get(f"{api_url}/api/ag/v1/fetch_job").json()
    if fetched["queue_empty"]:
        logging.error("Request queue is empty, no work to do, quitting")
        return 1
    skeleton_name = fetched["skeleton"]
    skeleton_zip = requests.get(f"{api_url}/api/ag/v1/skeleton/{skeleton_name}")

    os.makedirs(GRADING_DIR)
    with open(f"{GRADING_DIR}/{skeleton_name}", "wb") as f:
        f.write(skeleton_zip.content)

    proc = subprocess.Popen(["unzip", skeleton_name], cwd=GRADING_DIR)
    proc.wait()
    assert proc.returncode == 0, "Unzip failed"

    access_token = fetched["access_token"]
    backup_id = fetched["backup_id"]
    backup_assignment_url = (
        f"https://okpy.org/api/v3/backups/{backup_id}?access_token={access_token}"
    )
    backup_json = requests.get(backup_assignment_url).json()
    file_dict = backup_json["data"]["messages"][0]["contents"]
    files_to_grade = []
    for name, content in file_dict.items():
        if name == "submit":
            continue
        files_to_grade.append(name)
        with open(f"{GRADING_DIR}/{name}", "w") as f:
            f.write(content)
    assert len(files_to_grade) == 1, "Only support grading 1 notebook file"

    os.chdir(GRADING_DIR)
    res = gofer_wrangle(gofer.ok.grade_notebook(files_to_grade[0]))
    score_content = {
        "bid": backup_id,
        "score": res["total"],
        "kind": "Total",
        "message": res["msg"],
    }
    score_endpoint = f"https://okpy.org/api/v3/score/?access_token={access_token}"
    resp = requests.post(score_endpoint, json=score_content)
    assert resp.status_code == 200, resp.json()


if __name__ == "__main__":
    main()
