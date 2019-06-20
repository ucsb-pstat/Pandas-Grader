--- ---

Pandas Grader
=============

*Warning*: Consider the code pre-alpha stage quality, use it with
caution.

What is it?
-----------

-   [Okpy](http://okpy.org) compatible autograder that uses [Gofer
    Grader](https://github.com/data-8/Gofer-Grader) underneath
-   It is built for [Data100](http://ds100.org) course at Berkeley.

Who should use it?
------------------

-   If you have a jupyter assignment that only requires small (as in
    &lt;100MB) dataset, you should use [okpy.org](http://okpy.org)
    autograder service.

-   This service is built to accommodate *large scale* grading that also
    depends on big dataset.

    -   The autograding scale-out is implemented by [Kubernetes
        Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
    -   This means you need a jupyterhub kubernetes cluster running in
        the first place and the jupyterhub cluster should have access to
        all the necessary data.·

How to use it?
--------------

-   This repo contains an okpy compatible api server that can receives
    task from okpy and spawn kubernetes jobs.·
-   To use it, you need to build a docker container on top of your
    jupyterhub container, and configure `GradingJobConfig.yml`
    accordingly.
-   Install dependency and start the webserver by `run.sh`

Setup Guide for GCP
-------------------

Virtual Machine Instance
------------------------

1.  Create an Ubuntu 18.04 VM within the same project that your
    Kubernetes Jupyterhub environment is running in.

    ``` {.language-bash}
    gcloud compute instances create grader \
        --image=ubuntu-1804-bionic-v20190514 \
        --image-project=ubuntu-os-cloud \
        --scopes https://www.googleapis.com/auth/gerritcodereview \
        --machine-type=n1-standard-1 \
        --project=<PROJECT_ID> \
        --tags=autograder
    ```

2.  Create ingress rule for port 8000 ( Limit the source IP Addresses to
    a small list )

    ``` {.language-bash}
    gcloud compute firewall-rules create autograder \
        --network default \
        --direction ingress \
        --priority 1000 \
        --action allow \
        --target-tag autograder \
        --source-ranges [CIDR-RANGE] \
        --rules tcp:8000
    ```

3.  Install the following packages on the grader instance

    -   docker, python 3.6 , pip3

    ``` {.language-bash}
     snap install docker
        snap start docker
        sudo apt update && sudo apt install python3-pip
    ```

4.  Link /usr/bin/python with /usr/bin/python3\
    `sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10`

5.  Install python modules in requirements.txt file\
    `pip3 install -r requirements.txt`

6.  Restart your shell to update your environment

Modify the Pandas-Grader files for your environment
---------------------------------------------------

1.  Clone the Pandas-grader git repository\
    `git clone https://github.com/DS-100/Pandas-Grader.git`

2.  Edit the GradingJobConfig.yml file

    -   Search for "image"and modify the image name with your
        single-user image.

3.  Edit the [app.py](http://app.py) file

    -   Search for “api\_addr” and replace the IP address with the
        external ip of your Grader server.
    -   Search for “Welcome” and replace the Welcome message with one
        that is customized for your environment.

4.  Edit the [k8s.py](http://k8s.py) file

    -   Search for “namespace” and modify the namespace name to the
        namespace of your Kubernetes environment

5.  Create the Dockerfile for the Worker Pod by editing the
    Worker.Dockerfile

    -   Search for “FROM” and replace the name of the single-user Docker
        image you use for your course.
    -   Copy Worker.Dockerfile to Dockerfile\
        `cp -v Worker.Dockerfile Dockerfile`

6.  Pull the single-user image you use for your environment (Example
    below)\
    `sudo docker pull eespinosa/pstat134`

7.  Build the image for the Worker ensure the name of the new image is
    different than the name of the image use used in the above step
    (Example below)\
    `sudo docker build --no-cache -t eespinosa/pstat134-worker:v0.5 .`

8.  Push the image that you just created to the docker hub. (Example
    below)

    `sudo docker push eespinosa/pstat134-worker:v0.5`

9.  Install the gcloud sdk and kubectl

    -   Use the steps on the following page\
        `https://cloud.google.com/sdk/install`

10. Configure kubectl command line access by running the following
    command"\
    `gcloud container clusters get-credentials <CLUSTER_NAME> --zone <ZONE_NAME> --project <PROJECT_NAME>`

11. Create Service account that will run the autograder\
    `gcloud iam service-accounts create autograder --display-name "Autograder Service Account"`

12. Verify and note the name of the new account\
    `gcloud iam service-accounts list`

13. Download the Service Account Key\
    `gcloud iam service-accounts keys create ./<NAME_OF_FILE>.json --iam-account <ACCOUNT_CREATED_ABOVE>`

14. Associate the editor role to your service account\
    `gcloud projects add-iam-policy-binding <PROJECT ID> --role <ROLE NAME> --member serviceAccount:<EMAIL ADDRESS>`

15. Activate Service Account\
    `gcloud auth activate-service-account --project=<PROJECT_ID> --key-file=<FILENAME_CREATED_ABOVE>.json`

16. Start the Autograder\
    `bash run.sh`

Issue and Support?
------------------

-   Github issue will be the best place to reach for support.

