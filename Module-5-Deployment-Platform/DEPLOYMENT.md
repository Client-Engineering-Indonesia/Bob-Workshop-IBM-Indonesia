# OpenShift Deployment Instructions

Instructions for Bob (AI agent) to follow when deploying a sample application to OpenShift.

---

## Prerequisites

Before starting, ensure the following are in place:

### 1. Copy the environment file

```powershell
copy .env.example .env
```

Then open `.env` and fill in the cluster credentials:

```
OPENSHIFT_API_URL=      # e.g. https://api.<cluster>.<domain>:6443
OPENSHIFT_CONSOLE_URL=  # e.g. https://console-openshift-console.apps.<cluster>.<domain>
OPENSHIFT_USERNAME=     # e.g. kubeadmin
OPENSHIFT_PASSWORD=     # your cluster password
```

---

### 2. Install the OpenShift CLI (`oc`)

**Windows**
```powershell
Invoke-WebRequest -Uri "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-windows.zip" -OutFile "$env:TEMP\oc.zip" -UseBasicParsing
Expand-Archive -Path "$env:TEMP\oc.zip" -DestinationPath "C:\oc" -Force
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\oc", "Machine")
oc version
```

**macOS**
```bash
brew install openshift-cli
oc version
```

**Linux**
```bash
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/
oc version
```

---

## Deployment Instructions for Bob

When deploying a sample app, Bob must follow these steps in order:

### Step 1 — Read credentials
Read the `.env` file to extract `OPENSHIFT_API_URL`, `OPENSHIFT_USERNAME`, and `OPENSHIFT_PASSWORD`.

### Step 2 — Install `oc` if not available
Check if `oc` is available via `where.exe oc` (Windows) or `which oc` (Linux/macOS).  
If not found, download and extract the OpenShift CLI from the mirror above for the current OS.

### Step 3 — Log in to the cluster
```bash
oc login <OPENSHIFT_API_URL> --username=<OPENSHIFT_USERNAME> --password=<OPENSHIFT_PASSWORD> --insecure-skip-tls-verify=true
```

### Step 4 — Use the `production` namespace
Always deploy into the existing `production` namespace:
```bash
oc project production
```

### Step 5 — Prepare build files
In the same directory as the sample app, create:

**`Dockerfile`**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY <app-file>.py .
ENV PORT=8080
ENV ENVIRONMENT=production
ENV APP_VERSION=1.0.0
EXPOSE 8080
CMD ["python", "<app-file>.py"]
```

**`requirements.txt`**  
Include only the dependencies the app actually uses (e.g. `flask==3.0.3`).

### Step 6 — Enable the internal image registry (if not running)
Check if the registry is active:
```bash
oc get configs.imageregistry.operator.openshift.io cluster -o jsonpath='{.spec.managementState}'
```
If the output is `Removed`, enable it by writing a patch file `registry-patch.json`:
```json
{"spec":{"managementState":"Managed","storage":{"emptyDir":{}},"replicas":1}}
```
Then apply:
```bash
oc patch configs.imageregistry.operator.openshift.io cluster --type=merge --patch-file=registry-patch.json
```
Wait for the registry pod to reach `Running` status in the `openshift-image-registry` namespace before proceeding.

### Step 7 — Create a BuildConfig and build the image
```bash
oc new-build --binary --strategy=docker --name=<app-name> -n production
```
Verify the ImageStream resolves (output must not be empty):
```bash
oc get imagestream <app-name> -n production -o jsonpath='{.status.dockerImageRepository}'
```
Then start the binary build from the app's directory:
```bash
oc start-build <app-name> --from-dir=./sample-app --follow -n production
```

### Step 8 — Deploy the app
```bash
oc new-app <app-name>:latest --name=<app-name> -n production
```

### Step 9 — Expose with a TLS route
Do **not** use plain `oc expose`. Always create an `edge` route to match the cluster's HTTPS enforcement:
```bash
oc create route edge <app-name> --service=<app-name> --port=8080-tcp --insecure-policy=Redirect -n production
```

### Step 10 — Verify and report
1. Wait for the rollout: `oc rollout status deployment/<app-name> -n production`
2. Check the pod is `1/1 Running`: `oc get pods -n production -l deployment=<app-name>`
3. Hit the `/health` endpoint using `curl -sk https://<route-host>/health` — expect `{"status":"healthy"}`
4. Report the full HTTPS application URL to the user.

---

## Available Sample Apps

Pick any of the following from the `sample-app/` folder:

| File | Description |
|------|-------------|
| `app.py` | Basic Flask app |
| `color-palette.py` | Color palette generator |
| `live-vote.py` | Live voting app |
| `request-inspector.py` | HTTP request inspector |
| `system-dashboard.py` | System info dashboard |

---

## Notes for Bob

- Always use **`edge/Redirect` TLS termination** for routes — plain HTTP routes will show "Application is not available" on this cluster.
- If a BuildConfig was created before the image registry was ready, **delete and recreate it** — do not retry the old one.
- The build log stream may drop with an `http2: GOAWAY` error at the very end — this is benign if the push was successful.
- Always confirm the `/health` endpoint returns HTTP 200 before reporting success.
