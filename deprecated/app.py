import json
import logging
import os
from uuid import uuid4

import requests
import uvicorn
from sqlitedict import SqliteDict
from starlette.applications import Starlette
from starlette.background import BackgroundTasks
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, Response

from k8s import create_grading_job
from utils import pprint_color_json

config = Config(".env")
DB_PATH = config("DB_PATH", default="kv.db")
DEBUG = config("DEBUG", cast=bool, default=False)
REPORT_PATH = "result.jsonl"

app = Starlette(debug=DEBUG)
app.db: SqliteDict = None
app.job_queue = list()


def _debug_print_json(json):
    if DEBUG:
        pprint_color_json(json)


@app.on_event("startup")
async def start_up():
    app.db = SqliteDict(DB_PATH, autocommit=True, tablename="grading")


@app.on_event("shutdown")
async def shut_down():
    app.db.close()


@app.route("/")
async def index(request):
    return PlainTextResponse(
        "Welcome to DS100 autograder, please contact Simon <xmo@berkeley.edu> for usage."
    )


# Autograder Core
@app.route("/api/ag/v1/skeleton/{assignment}", methods=["POST", "GET"])
async def return_zip_file(request: Request):
    key = request.path_params["assignment"]
    if request.method == "GET":
        if key in app.db:
            retrieved = app.db[key]
            return PlainTextResponse(
                retrieved["body"], media_type=retrieved["media_type"]
            )
        else:
            return JSONResponse({"error": "not found"}, status_code=404)
    else:
        body = await request.body()
        media_type = request.headers["content-type"]
        app.db[key] = {"body": body, "media_type": media_type}
        return JSONResponse({"success": True})


@app.route("/api/ag/v1/report_result", methods=["POST", "GET"])
async def accept_result(request: Request):
    return PlainTextResponse("ok")
    # if request.method == "POST":
    # data = await request.json()
    # app.result_file.write(json.dumps(data))
    # app.result_file.write("\n")
    # return PlainTextResponse("ok")
    # else:
    # return FileResponse(REPORT_PATH)


@app.route("/api/ag/v1/fetch_job")
async def fetch_job(request: Request):
    """
    responses:
      200:
        description: Return a job for worker to run.
        examples:
          {
              "queue_empty": false,
              "skeleton": "lab1.zip",
              "backup_id": "abcdbeF",
              "access_token": "******************"
          }
      410:
        description: Tell worker no job avaiable.
        examples:
          {
              "queue_empty": true
          }
    """
    jobs_queued = app.job_queue

    if len(jobs_queued) == 0:
        return JSONResponse({"queue_empty": True})
    else:
        job_data = jobs_queued.pop(0)

        spec = {
            "queue_empty": False,
            "skeleton": job_data["skeleton"],
            "backup_id": job_data["backup_id"],
            "access_token": job_data["access_token"],
        }
        _debug_print_json(spec)
        return JSONResponse(spec)


async def kick_off_grading_job(assignment_token, submission_id, access_token, job_id):
    data = {
        "skeleton": assignment_token,
        "backup_id": submission_id,
        "access_token": access_token,
        "job_id": job_id,
        "status": "queued",
    }
    app.job_queue.append(data)


# Okpy Frontend
@app.route("/results", methods=["POST"])
async def check_result(request: Request):
    """
    responses:
      200:
        description: Return job status: {failed, queued, finished}
        examples:
          {"job_id_1": {"status": "failed"}}
    """
    return PlainTextResponse("Fail the job!")

    # jobs_ids = await request.json()
    # status = {}
    # for job_id in jobs_ids:
    #     status[job_id] = {'status': "queued"}
    # return JSONResponse(status)


@app.route("/api/ok/v3/grade/batch", methods=["POST"])
async def grade_batch(request: Request):
    """
    responses:
      200:
        description: Return job ids
        examples:
          {
              "jobs": ['id1', 'id2', ...]
          }
    """
    request_data = await request.json()

    logging.info("received batch request")
    _debug_print_json(request_data)

    background_job = BackgroundTasks()
    job_ids = []
    for submission in request_data["subm_ids"]:
        job_id = uuid4().hex
        app.db[f"job_status_{job_id}"] = "QUEUED"
        background_job.add_task(
            kick_off_grading_job,
            assignment_token=request_data["assignment"],
            submission_id=submission,
            access_token=request_data["access_token"],
            job_id=job_id,
        )
        job_ids.append(job_id)

    create_grading_job(
        "GradingJobConfig.yml",
        {
            "name": f"pandas-grader-{job_id}",
            "parallelism": 1000,
            "num_jobs": len(job_ids),
            "api_addr": "http://grading.ds100.org:8080",
        },
    )

    return JSONResponse(
        {"jobs": [job_id for job_id in job_ids]}, background=background_job
    )
