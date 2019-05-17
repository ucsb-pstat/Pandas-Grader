---


---

<h1 id="pandas-grader">Pandas Grader</h1>
<p><em>Warning</em>: Consider the code pre-alpha stage quality, use it with caution.</p>
<h2 id="what-is-it">What is it?</h2>
<ul>
<li><a href="http://okpy.org">Okpy</a> compatible autograder that uses <a href="https://github.com/data-8/Gofer-Grader">Gofer Grader</a> underneath</li>
<li>It is built for <a href="http://ds100.org">Data100</a> course at Berkeley.</li>
</ul>
<h2 id="who-should-use-it">Who should use it?</h2>
<ul>
<li>
<p>If you have a jupyter assignment that only requires small (as in &lt;100MB) dataset, you should use <a href="http://okpy.org">okpy.org</a> autograder service.</p>
</li>
<li>
<p>This service is built to accommodate <em>large scale</em> grading that also depends on big dataset.</p>
<ul>
<li>The autograding scale-out is implemented by <a href="https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/">Kubernetes Jobs</a></li>
<li>This means you need a jupyterhub kubernetes cluster running in the first place and the jupyterhub cluster should have access to all the necessary data.·</li>
</ul>
</li>
</ul>
<h2 id="how-to-use-it">How to use it?</h2>
<ul>
<li>This repo contains an okpy compatible api server that can receives task from okpy and spawn kubernetes jobs.·</li>
<li>To use it, you need to build a docker container on top of your jupyterhub container, and configure <code>GradingJobConfig.yml</code> accordingly.</li>
<li>Install dependency and start the webserver by <code>run.sh</code></li>
</ul>
<h2 id="setup-guide-for-gcp">Setup Guide for GCP</h2>
<h2 id="virtual-machine-instance">Virtual Machine Instance</h2>
<ol>
<li>
<p>Create an Ubuntu 18.04 VM within the same project that your Kubernetes Jupyterhub environment is running in.</p>
<pre class=" language-bash"><code class="prism  language-bash">gcloud compute instances create grader \
	--image<span class="token operator">=</span>ubuntu-1804-bionic-v20190514 \
	--image-project<span class="token operator">=</span>ubuntu-os-cloud \
	--scopes https://www.googleapis.com/auth/gerritcodereview \
	--machine-type<span class="token operator">=</span>n1-standard-1 \
	--project<span class="token operator">=</span><span class="token operator">&lt;</span>PROJECT_ID<span class="token operator">&gt;</span> \
	--tags<span class="token operator">=</span>autograder
</code></pre>
</li>
<li>
<p>Create ingress rule for port 8000 ( Limit the source IP Addresses to a small list )</p>
<pre class=" language-bash"><code class="prism  language-bash">gcloud compute firewall-rules create autograder \
    --network default \
    --direction ingress \
    --priority 1000 \
    --action allow \
    --target-tag autograder \
    --source-ranges <span class="token punctuation">[</span>CIDR-RANGE<span class="token punctuation">]</span> \
    --rules tcp:8000
</code></pre>
</li>
<li>
<p>Install the following packages on the grader instance</p>
<ul>
<li>docker, python 3.6 , pip3</li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">	snap <span class="token function">install</span> docker
	snap start docker
	<span class="token function">sudo</span> apt update <span class="token operator">&amp;&amp;</span> <span class="token function">sudo</span> apt <span class="token function">install</span> python3-pip
</code></pre>
</li>
<li>
<p>Link /usr/bin/python with /usr/bin/python3<br>
<code>sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10</code></p>
</li>
<li>
<p>Install python modules in requirements.txt file<br>
<code>pip3 install -r requirements.txt</code></p>
</li>
<li>
<p>Restart your shell to update your environment</p>
</li>
</ol>
<h2 id="modify-the-pandas-grader-files-for-your-environment">Modify the Pandas-Grader files for your environment</h2>
<ol>
<li>
<p>Clone the Pandas-grader git repository<br>
<code>git clone https://github.com/DS-100/Pandas-Grader.git</code></p>
</li>
<li>
<p>Edit the GradingJobConfig.yml file</p>
<ul>
<li>Search for "image"and modify the image name with your single-user image.</li>
</ul>
</li>
<li>
<p>Edit the <a href="http://app.py">app.py</a> file</p>
<ul>
<li>Search for “api_addr” and replace the IP address with the external ip of your Grader server.</li>
<li>Search for “Welcome” and replace the Welcome message with one that is customized for your environment.</li>
</ul>
</li>
<li>
<p>Edit the <a href="http://k8s.py">k8s.py</a> file</p>
<ul>
<li>Search for “namespace” and modify the namespace name to the namespace of your Kubernetes environment</li>
</ul>
</li>
<li>
<p>Create the Dockerfile for the Worker Pod by editing the Worker.Dockerfile</p>
<ul>
<li>Search for “FROM” and replace the name of the single-user Docker image you use for your course.</li>
<li>Copy Worker.Dockerfile to Dockerfile<br>
<code>cp -v Worker.Dockerfile Dockerfile</code></li>
</ul>
</li>
<li>
<p>Pull the single-user image you use for your environment (Example below)<br>
<code>sudo docker pull eespinosa/pstat134</code></p>
</li>
<li>
<p>Build the image for the Worker ensure the name of the new image is different than the name of the image use used in the above step  (Example below)<br>
<code>sudo docker build --no-cache -t eespinosa/pstat134-worker:v0.5 .</code></p>
</li>
<li>
<p>Push the image that you just created to the docker hub. (Example below)</p>
<p><code>sudo docker push eespinosa/pstat134-worker:v0.5</code></p>
</li>
<li>
<p>Install the gcloud sdk and kubectl</p>
<ul>
<li>Use the steps on the following page<br>
<code>https://cloud.google.com/sdk/install</code></li>
</ul>
</li>
<li>
<p>Configure kubectl command line access by running the following command"<br>
<code>gcloud container clusters get-credentials &lt;CLUSTER_NAME&gt; --zone &lt;ZONE_NAME&gt; --project &lt;PROJECT_NAME&gt;</code></p>
</li>
<li>
<p>Create Service account that will run the autograder<br>
<code>gcloud iam service-accounts create autograder --display-name "Autograder Service Account"</code></p>
</li>
<li>
<p>Verify and note the name of the new account<br>
<code>gcloud iam service-accounts list</code></p>
</li>
<li>
<p>Download the Service Account Key<br>
<code>gcloud iam service-accounts keys create ./&lt;NAME_OF_FILE&gt;.json --iam-account &lt;ACCOUNT_CREATED_ABOVE&gt;</code></p>
</li>
<li>
<p>Associate the editor role to your service account<br>
<code>gcloud projects add-iam-policy-binding &lt;PROJECT ID&gt; --role &lt;ROLE NAME&gt; --member serviceAccount:&lt;EMAIL ADDRESS&gt;</code></p>
</li>
<li>
<p>Activate Service Account<br>
<code>gcloud auth activate-service-account --project=&lt;PROJECT_ID&gt; --key-file=&lt;FILENAME_CREATED_ABOVE&gt;.json</code></p>
</li>
<li>
<p>Start the Autograder<br>
<code>bash run.sh</code></p>
</li>
</ol>
<h2 id="issue-and-support">Issue and Support?</h2>
<ul>
<li>Github issue will be the best place to reach for support.</li>
</ul>

