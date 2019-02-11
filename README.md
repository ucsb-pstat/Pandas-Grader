Pandas Grader
============

*Warning*: Consider the code pre-alpha stage quality, use it with caution. 

## What is it?
 - [Okpy](http://okpy.org) compatible autograder that uses [Gofer Grader](https://github.com/data-8/Gofer-Grader) underneath
 - It is built for [Data100](http://ds100.org) course at Berkeley.

## Who should use it?
- If you have a jupyter assignment that only requires small (as in <100MB) dataset, you should use okpy.org's autograder service. 
- This service is built to accomdate _large scale_ grading that also depends on big dataset. 
   - The autograding scale-out is implemented by [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
   - This means you need a jupyterhub kubernetes cluster running in the first place and the jupyterhub cluster should have access to all the necessary data. 

## How to use it?
- This repo contains an okpy compatible api server that can receives task from okpy and spawn kubernetes jobs. 
- To use it, you need to build a docker container on top of your jupyterhub container, and configure `GradingJobConfig.yml` accordingly.  
- Install depenency and start the webserver by `run.sh`

## Issue and Support?
- Github issue will be the best place to reach for support. 
