# Module 5 — Deploying Applications to OpenShift

A hands-on workshop module where you deploy a sample Python application to an OpenShift cluster using Bob, your AI assistant.

---

## Before You Start

### 1. Set up your environment file

```powershell
copy .env.example .env
```

Open `.env` and fill in your cluster credentials:

```
OPENSHIFT_API_URL=      # API endpoint, e.g. https://api.<cluster>.<domain>:6443
OPENSHIFT_CONSOLE_URL=  # Console URL
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

## Available Sample Apps

Pick any application from the `sample-app/` folder to deploy:

| File | Description |
|------|-------------|
| `app.py` | Basic Flask app |
| `color-palette.py` | Color palette generator |
| `live-vote.py` | Live voting app |
| `request-inspector.py` | HTTP request inspector |
| `system-dashboard.py` | System info dashboard |

---

## Deploy with Bob

Once your `.env` is filled in and `oc` is installed, open Bob and type:

```
Deploy the sample app @sample-app\<your-chosen-app>.py to OpenShift.
The required credentials are stored in the .env file and read @DEPLOYMENT.md for instructions.
Ensure the application is deployed successfully, runs smoothly, and provide the application URL once the deployment is complete.
```

Bob will handle everything — logging in, building the image, deploying, and giving you the live URL.

---

## What to Expect

1. Bob reads your credentials from `.env`
2. Bob checks for `oc` and downloads it if missing
3. Bob builds a Docker image and pushes it to the OpenShift internal registry
4. Bob deploys the app to the `production` namespace
5. Bob gives you the **live HTTPS URL** once the app is running

---

> For detailed deployment steps and troubleshooting, see [DEPLOYMENT.md](./DEPLOYMENT.md).
