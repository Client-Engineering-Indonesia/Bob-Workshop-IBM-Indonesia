# ACE CI/CD Quick Reference Guide

Quick reference untuk implementasi Trunk-Based Development CI/CD untuk IBM App Connect Enterprise.

## 📋 Quick Links

- **Full Strategy**: [CICD-STRATEGY-RECOMMENDATION.md](./CICD-STRATEGY-RECOMMENDATION.md)
- **Implementation**: [ace-testing/.gitlab-ci.yml](./ace-testing/.gitlab-ci.yml)
- **Deployment Guide**: [ace-testing/CICD-DEPLOYMENT-GUIDE.md](./ace-testing/CICD-DEPLOYMENT-GUIDE.md)

---

## 🚀 Quick Start

### 1. Branch Strategy (Trunk-Based)

```bash
# Main branch (trunk) - always deployable
main

# Feature branches - max 2 days
feature/JIRA-123-description

# Hotfix branches - emergency only
hotfix/critical-issue
```

### 2. Developer Workflow

```bash
# 1. Create feature branch
git checkout main
git pull origin main
git checkout -b feature/ACE-123-new-flow

# 2. Develop and commit
git add .
git commit -m "feat: Add database retrieve flow"
git push origin feature/ACE-123-new-flow

# 3. Create MR to main
# Via GitLab UI → Request review → Merge after approval

# 4. Auto-deploy to DEV
# Pipeline runs automatically after merge
```

### 3. Pipeline Stages

```yaml
validate → upload → deploy-dev → deploy-test → deploy-prod
  (auto)    (auto)     (auto)       (manual)      (manual)
```

---

## 🔧 Configuration

### Environment Variables

```yaml
# Required in GitLab CI/CD Variables
OCP_TOKEN: "sha256~..."              # OpenShift token
OCP_SERVER: "https://api.cluster..."  # OpenShift API
OCP_PROJECT: "tools"                  # Namespace
INTEGRATION_RUNTIME_NAME: "ace-..."  # Runtime name
```

### Version Format

```yaml
Format: MAJOR.MINOR.PIPELINE_ID
Example: 1.0.85

MAJOR: Breaking changes
MINOR: New features
PIPELINE_ID: Auto from GitLab
```

---

## 📦 Deployment Commands

### Deploy to DEV (Automatic)
```bash
# Happens automatically after merge to main
# No action needed
```

### Deploy to TEST (Manual)
```bash
# Via GitLab UI:
# 1. Go to pipeline
# 2. Click "Deploy to TEST"
# 3. Confirm
```

### Deploy to PROD (Manual + Approval)
```bash
# Via GitLab UI:
# 1. Go to pipeline
# 2. Click "Deploy to PROD"
# 3. Wait for 2 approvals
# 4. Confirm
```

---

## 🔄 Rollback

### Quick Rollback
```bash
# Via GitLab UI:
# 1. Find previous successful pipeline
# 2. Click "Retry" on deploy job
# 3. Confirm

# Via CLI:
oc patch integrationruntime ace-database-retrieve \
   --type='json' \
   -p="[{'op': 'replace', 'path': '/spec/barURL/0', 
         'value': 'https://gitlab.com/.../1.0.84/DatabaseRetrieve.bar'}]"
```

---

## ✅ Best Practices Checklist

### Before Merge
- [ ] Feature branch < 2 days old
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Commit message follows convention
- [ ] BAR file validated locally

### After Merge
- [ ] Pipeline completed successfully
- [ ] DEV deployment verified
- [ ] Integration tests passed
- [ ] No errors in logs

### Before Production
- [ ] Tested in TEST environment
- [ ] QA sign-off received
- [ ] Change ticket created
- [ ] Rollback plan documented
- [ ] 2 approvals obtained

---

## 🎯 Key Metrics

```yaml
Target Metrics:
  Deployment Frequency: 5-10/day to DEV
  Lead Time: <30 min to DEV
  Change Failure Rate: <5%
  MTTR: <15 minutes
  Pipeline Success Rate: >95%
```

---

## 🐛 Common Issues

### Issue: Pipeline fails at validate stage
```bash
Solution: Check BAR file integrity
- Verify BAR file exists
- Check file size > 0
- Rebuild BAR file if corrupted
```

### Issue: barauth Configuration error
```bash
Solution: Ensure JSON format
- Data must be valid JSON
- Must be base64 encoded
- Check credentials are correct
```

### Issue: Deployment timeout
```bash
Solution: Check IntegrationRuntime status
oc get integrationruntime -n tools
oc describe integrationruntime ace-database-retrieve
oc logs <pod-name>
```

---

## 📞 Support

### Documentation
- Strategy: `CICD-STRATEGY-RECOMMENDATION.md`
- Implementation: `ace-testing/`
- Troubleshooting: `ace-testing/CICD-DEPLOYMENT-GUIDE.md`

### Contacts
- DevOps Team: devops@company.com
- ACE Support: ace-support@company.com

---

## 🔗 Useful Commands

### Check Deployment Status
```bash
# Get IntegrationRuntime status
oc get integrationruntime -n tools

# Get pod status
oc get pods -n tools -l app.kubernetes.io/name=ace-database-retrieve

# Check logs
oc logs <pod-name> -n tools --tail=100

# Get service URL
oc get integrationruntime ace-database-retrieve -n tools \
   -o jsonpath='{.status.endpoints[0].uri}'
```

### Package Registry
```bash
# List packages
curl --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
     "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages"

# Download specific version
curl --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
     "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/ace-bar/1.0.85/DatabaseRetrieve.bar" \
     -o DatabaseRetrieve.bar
```

### GitLab Pipeline
```bash
# Trigger pipeline manually
curl --request POST \
     --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
     "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/pipeline"

# Get pipeline status
curl --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
     "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/pipelines/${PIPELINE_ID}"
```

---

**Last Updated**: 2026-02-13  
**Version**: 1.0  
**Based on**: ace-testing implementation