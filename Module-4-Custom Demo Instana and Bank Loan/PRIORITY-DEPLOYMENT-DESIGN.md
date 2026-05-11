# Priority Deployment Design for GitLab Runner

Comprehensive guide untuk implementasi priority-based deployment system pada GitLab CI/CD.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Use Cases](#use-cases)
- [Design Options](#design-options)
- [Implementation Strategies](#implementation-strategies)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)

---

## Overview

### What is Priority Deployment?

Priority deployment adalah sistem yang memungkinkan pipeline tertentu untuk:
- **Dijalankan lebih dulu** dari pipeline lain yang sedang antri
- **Mendapat resource lebih banyak** (dedicated runners)
- **Bypass queue** untuk deployment critical
- **Pre-empt** pipeline dengan prioritas lebih rendah

### Why Priority Deployment?

```yaml
Scenarios:
  - Hotfix production (CRITICAL)
  - Security patches (HIGH)
  - Feature deployment (NORMAL)
  - Scheduled maintenance (LOW)
  
Benefits:
  ✅ Faster response untuk critical issues
  ✅ Better resource utilization
  ✅ Clear deployment hierarchy
  ✅ Reduced downtime
```

---

## Use Cases

### 1. Emergency Hotfix

```
Scenario: Production down, need immediate fix

Priority: CRITICAL (P0)
Expected: Deploy dalam <5 menit
Action: Bypass semua queue, dedicated runner
```

### 2. Security Patch

```
Scenario: CVE discovered, need urgent patch

Priority: HIGH (P1)
Expected: Deploy dalam <15 menit
Action: High priority queue, pre-empt normal jobs
```

### 3. Regular Feature

```
Scenario: New feature deployment

Priority: NORMAL (P2)
Expected: Deploy dalam <30 menit
Action: Standard queue
```

### 4. Scheduled Maintenance

```
Scenario: Non-urgent updates

Priority: LOW (P3)
Expected: Deploy saat idle
Action: Run only when no other jobs
```

---

## Design Options

### Option 1: Tag-Based Priority (RECOMMENDED)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tag-Based Priority System                     │
└─────────────────────────────────────────────────────────────────┘

GitLab Runners:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Runner P0   │  │  Runner P1   │  │  Runner P2   │
│  (Critical)  │  │   (High)     │  │  (Normal)    │
│              │  │              │  │              │
│  Tags:       │  │  Tags:       │  │  Tags:       │
│  - critical  │  │  - high      │  │  - normal    │
│  - hotfix    │  │  - security  │  │  - feature   │
└──────────────┘  └──────────────┘  └──────────────┘
      ▲                 ▲                 ▲
      │                 │                 │
      └─────────────────┴─────────────────┘
                        │
                   .gitlab-ci.yml
                   (job tags)
```

**Pros:**
- ✅ Simple implementation
- ✅ Clear separation
- ✅ Easy to manage
- ✅ GitLab native feature

**Cons:**
- ❌ Need multiple runners
- ❌ Resource overhead

### Option 2: Resource Class Priority

```
┌─────────────────────────────────────────────────────────────────┐
│                Resource Class Priority System                    │
└─────────────────────────────────────────────────────────────────┘

Shared Runner Pool:
┌────────────────────────────────────────────────────────────────┐
│                    GitLab Runner Manager                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Executor │  │ Executor │  │ Executor │  │ Executor │     │
│  │    1     │  │    2     │  │    3     │  │    4     │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                 │
│  Priority Queue:                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ P0: [hotfix-job] ──────────────────────────▶ Execute   │  │
│  │ P1: [security-job] ─────────────────────▶ Wait         │  │
│  │ P2: [feature-job-1, feature-job-2] ───▶ Wait           │  │
│  │ P3: [maintenance-job] ─────────────▶ Wait              │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Efficient resource usage
- ✅ Dynamic allocation
- ✅ Cost effective

**Cons:**
- ❌ Complex setup
- ❌ Requires custom logic

### Option 3: Hybrid Approach (BEST)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hybrid Priority System                        │
└─────────────────────────────────────────────────────────────────┘

Critical Path (Dedicated):
┌──────────────┐
│  Runner P0   │──▶ Hotfix only (always available)
│  (Dedicated) │
└──────────────┘

Shared Pool (Dynamic):
┌────────────────────────────────────────────────────────────────┐
│                    Shared Runner Pool                           │
│                                                                 │
│  Priority Queue:                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ P1: [security-job] ──────────────────────▶ Execute     │  │
│  │ P2: [feature-job-1, feature-job-2] ───▶ Wait           │  │
│  │ P3: [maintenance-job] ─────────────▶ Wait              │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Best of both worlds
- ✅ Guaranteed critical path
- ✅ Efficient for normal jobs
- ✅ Cost optimized

**Cons:**
- ❌ More complex setup
- ❌ Need monitoring

---

## Implementation Strategies

### Strategy 1: GitLab Runner Tags (Simple)

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Runner Configuration                          │
└─────────────────────────────────────────────────────────────────┘

Server 1 (High-spec):
┌──────────────────────────────────────────────────────────────┐
│ Runner: critical-runner                                       │
│ Tags: [critical, hotfix, p0]                                 │
│ Concurrent: 1 (dedicated)                                    │
│ Resources: 4 CPU, 8GB RAM                                    │
└──────────────────────────────────────────────────────────────┘

Server 2 (Medium-spec):
┌──────────────────────────────────────────────────────────────┐
│ Runner: high-priority-runner                                 │
│ Tags: [high, security, p1]                                   │
│ Concurrent: 2                                                │
│ Resources: 2 CPU, 4GB RAM                                    │
└──────────────────────────────────────────────────────────────┘

Server 3 (Standard):
┌──────────────────────────────────────────────────────────────┐
│ Runner: normal-runner                                        │
│ Tags: [normal, feature, p2]                                  │
│ Concurrent: 5                                                │
│ Resources: 1 CPU, 2GB RAM                                    │
└──────────────────────────────────────────────────────────────┘
```

#### Runner Configuration

```toml
# /etc/gitlab-runner/config.toml

# Critical Runner (P0)
[[runners]]
  name = "critical-runner"
  url = "https://gitlab.com/"
  token = "CRITICAL_RUNNER_TOKEN"
  executor = "docker"
  limit = 1  # Only 1 job at a time
  [runners.docker]
    image = "alpine:latest"
    cpus = "4"
    memory = "8g"
    privileged = false
  [runners.cache]
    Type = "s3"
  [[runners.docker.services]]
    name = "docker:dind"

# High Priority Runner (P1)
[[runners]]
  name = "high-priority-runner"
  url = "https://gitlab.com/"
  token = "HIGH_RUNNER_TOKEN"
  executor = "docker"
  limit = 2
  [runners.docker]
    image = "alpine:latest"
    cpus = "2"
    memory = "4g"

# Normal Runner (P2)
[[runners]]
  name = "normal-runner"
  url = "https://gitlab.com/"
  token = "NORMAL_RUNNER_TOKEN"
  executor = "docker"
  limit = 5
  [runners.docker]
    image = "alpine:latest"
    cpus = "1"
    memory = "2g"
```

#### Pipeline Configuration

```yaml
# .gitlab-ci.yml

variables:
  # Priority levels
  PRIORITY_CRITICAL: "critical"
  PRIORITY_HIGH: "high"
  PRIORITY_NORMAL: "normal"

# Critical deployment (P0)
deploy:hotfix:
  stage: deploy
  tags:
    - critical
    - hotfix
  script:
    - echo "CRITICAL: Deploying hotfix"
    - ./deploy-hotfix.sh
  only:
    - /^hotfix\/.*/
  environment:
    name: production
    action: start

# High priority deployment (P1)
deploy:security:
  stage: deploy
  tags:
    - high
    - security
  script:
    - echo "HIGH: Deploying security patch"
    - ./deploy-security.sh
  only:
    - /^security\/.*/
  environment:
    name: production

# Normal deployment (P2)
deploy:feature:
  stage: deploy
  tags:
    - normal
    - feature
  script:
    - echo "NORMAL: Deploying feature"
    - ./deploy-feature.sh
  only:
    - main
  environment:
    name: production
```

### Strategy 2: Resource Class with Priority Queue

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Priority Queue Management System                    │
└─────────────────────────────────────────────────────────────────┘

GitLab API:
┌──────────────────────────────────────────────────────────────┐
│  Pipeline Webhook ──▶ Priority Classifier                    │
│                            │                                  │
│                            ▼                                  │
│                    ┌──────────────┐                          │
│                    │ Redis Queue  │                          │
│                    │              │                          │
│                    │ P0: [job1]   │                          │
│                    │ P1: [job2,3] │                          │
│                    │ P2: [job4-8] │                          │
│                    └──────┬───────┘                          │
│                           │                                   │
│                           ▼                                   │
│                    Queue Processor                           │
│                           │                                   │
│                           ▼                                   │
│                    GitLab Runner API                         │
│                    (Trigger jobs by priority)                │
└──────────────────────────────────────────────────────────────┘
```

#### Implementation (Python)

```python
# priority_queue_manager.py

import redis
import gitlab
from enum import Enum

class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

class PriorityQueueManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
        self.gl = gitlab.Gitlab('https://gitlab.com', 
                               private_token='YOUR_TOKEN')
    
    def classify_pipeline(self, pipeline_id, project_id):
        """Classify pipeline priority based on branch/tags"""
        project = self.gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        
        # Check branch name
        if pipeline.ref.startswith('hotfix/'):
            return Priority.CRITICAL
        elif pipeline.ref.startswith('security/'):
            return Priority.HIGH
        elif pipeline.ref == 'main':
            return Priority.NORMAL
        else:
            return Priority.LOW
    
    def enqueue(self, pipeline_id, project_id):
        """Add pipeline to priority queue"""
        priority = self.classify_pipeline(pipeline_id, project_id)
        
        queue_key = f"queue:p{priority.value}"
        self.redis.rpush(queue_key, f"{project_id}:{pipeline_id}")
        
        print(f"Enqueued pipeline {pipeline_id} with priority {priority.name}")
    
    def process_queue(self):
        """Process queues by priority"""
        for priority in Priority:
            queue_key = f"queue:p{priority.value}"
            
            # Get next job from queue
            job_data = self.redis.lpop(queue_key)
            
            if job_data:
                project_id, pipeline_id = job_data.decode().split(':')
                self.trigger_pipeline(project_id, pipeline_id)
                return True
        
        return False
    
    def trigger_pipeline(self, project_id, pipeline_id):
        """Trigger pipeline execution"""
        project = self.gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        
        # Retry pipeline (this will use available runner)
        pipeline.retry()
        
        print(f"Triggered pipeline {pipeline_id}")

# Usage
manager = PriorityQueueManager()

# Webhook handler
def on_pipeline_created(webhook_data):
    pipeline_id = webhook_data['object_attributes']['id']
    project_id = webhook_data['project']['id']
    
    manager.enqueue(pipeline_id, project_id)

# Queue processor (run as daemon)
import time

def queue_processor_daemon():
    manager = PriorityQueueManager()
    
    while True:
        if not manager.process_queue():
            time.sleep(5)  # Wait if no jobs
        else:
            time.sleep(1)  # Small delay between jobs
```

### Strategy 3: GitLab CI/CD Variables with Resource Groups

#### Configuration

```yaml
# .gitlab-ci.yml

variables:
  DEPLOY_PRIORITY: "normal"  # Default priority

# Override priority for specific branches
workflow:
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^hotfix\//'
      variables:
        DEPLOY_PRIORITY: "critical"
    - if: '$CI_COMMIT_BRANCH =~ /^security\//'
      variables:
        DEPLOY_PRIORITY: "high"
    - if: '$CI_COMMIT_BRANCH == "main"'
      variables:
        DEPLOY_PRIORITY: "normal"

# Critical deployment
deploy:critical:
  stage: deploy
  resource_group: production-critical
  tags:
    - critical
  script:
    - echo "Deploying with CRITICAL priority"
    - ./deploy.sh
  rules:
    - if: '$DEPLOY_PRIORITY == "critical"'
  environment:
    name: production

# High priority deployment
deploy:high:
  stage: deploy
  resource_group: production-high
  tags:
    - high
  script:
    - echo "Deploying with HIGH priority"
    - ./deploy.sh
  rules:
    - if: '$DEPLOY_PRIORITY == "high"'
  environment:
    name: production

# Normal deployment
deploy:normal:
  stage: deploy
  resource_group: production-normal
  tags:
    - normal
  script:
    - echo "Deploying with NORMAL priority"
    - ./deploy.sh
  rules:
    - if: '$DEPLOY_PRIORITY == "normal"'
  environment:
    name: production
```

---

## Configuration Examples

### Example 1: ACE Deployment with Priority

```yaml
# ACE Demos/ace-testing/.gitlab-ci.yml

stages:
  - validate
  - upload
  - deploy-dev
  - deploy-test
  - deploy-prod

variables:
  OCP_SERVER: "https://api.cluster.com:6443"
  OCP_PROJECT: "tools"
  INTEGRATION_RUNTIME_NAME: "ace-database-retrieve"
  
  # Priority configuration
  DEPLOY_PRIORITY: "normal"

# Determine priority based on branch
workflow:
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^hotfix\//'
      variables:
        DEPLOY_PRIORITY: "critical"
        RUNNER_TAG: "critical"
    - if: '$CI_COMMIT_BRANCH =~ /^security\//'
      variables:
        DEPLOY_PRIORITY: "high"
        RUNNER_TAG: "high"
    - if: '$CI_COMMIT_BRANCH == "main"'
      variables:
        DEPLOY_PRIORITY: "normal"
        RUNNER_TAG: "normal"

# Validate stage (all priorities)
validate:bar:
  stage: validate
  image: alpine:latest
  tags:
    - ${RUNNER_TAG}
  script:
    - echo "Priority: ${DEPLOY_PRIORITY}"
    - ls -lh DatabaseRetrieve.bar
  artifacts:
    paths:
      - DatabaseRetrieve.bar
    expire_in: 1 hour

# Upload stage
upload:bar:
  stage: upload
  image: curlimages/curl:latest
  tags:
    - ${RUNNER_TAG}
  script:
    - echo "Uploading with priority: ${DEPLOY_PRIORITY}"
    - curl --header "JOB-TOKEN: ${CI_JOB_TOKEN}" \
           --upload-file DatabaseRetrieve.bar \
           "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/ace-bar/1.0.${CI_PIPELINE_ID}/DatabaseRetrieve.bar"
  dependencies:
    - validate:bar

# Deploy to DEV (auto for all priorities)
deploy:dev:
  stage: deploy-dev
  image: quay.io/openshift/origin-cli:latest
  tags:
    - ${RUNNER_TAG}
  script:
    - echo "Deploying to DEV with priority: ${DEPLOY_PRIORITY}"
    - oc login --token=${OCP_TOKEN} --server=${OCP_SERVER}
    - ./deploy-to-dev.sh
  environment:
    name: development
  dependencies:
    - upload:bar

# Deploy to PROD (priority-based)
deploy:prod:critical:
  stage: deploy-prod
  image: quay.io/openshift/origin-cli:latest
  tags:
    - critical
  resource_group: production-critical
  script:
    - echo "CRITICAL: Deploying to PROD immediately"
    - oc login --token=${OCP_TOKEN} --server=${OCP_SERVER}
    - ./deploy-to-prod.sh
  environment:
    name: production
  rules:
    - if: '$DEPLOY_PRIORITY == "critical"'
      when: manual  # Still require manual trigger for safety
  dependencies:
    - deploy:dev

deploy:prod:normal:
  stage: deploy-prod
  image: quay.io/openshift/origin-cli:latest
  tags:
    - normal
  resource_group: production-normal
  script:
    - echo "NORMAL: Deploying to PROD"
    - oc login --token=${OCP_TOKEN} --server=${OCP_SERVER}
    - ./deploy-to-prod.sh
  environment:
    name: production
  rules:
    - if: '$DEPLOY_PRIORITY == "normal"'
      when: manual
  dependencies:
    - deploy:dev
```

### Example 2: Multi-Project Priority

```yaml
# .gitlab-ci.yml (shared template)

.deploy_template:
  script:
    - echo "Deploying with priority: ${DEPLOY_PRIORITY}"
    - ./deploy.sh ${ENVIRONMENT}

# Include priority logic
include:
  - local: '/templates/priority-config.yml'

# Project-specific overrides
deploy:production:
  extends: .deploy_template
  stage: deploy
  tags:
    - ${RUNNER_TAG}
  environment:
    name: production
  rules:
    - if: '$CI_PROJECT_NAME == "critical-service"'
      variables:
        DEPLOY_PRIORITY: "critical"
        RUNNER_TAG: "critical"
    - if: '$CI_PROJECT_NAME == "payment-service"'
      variables:
        DEPLOY_PRIORITY: "high"
        RUNNER_TAG: "high"
    - when: always
      variables:
        DEPLOY_PRIORITY: "normal"
        RUNNER_TAG: "normal"
```

---

## Best Practices

### 1. Priority Classification

```yaml
Priority Levels:
  P0 (CRITICAL):
    - Production outages
    - Security vulnerabilities (CVE)
    - Data loss prevention
    - SLA breach prevention
    
  P1 (HIGH):
    - Performance degradation
    - Minor security issues
    - Important bug fixes
    - Customer-impacting issues
    
  P2 (NORMAL):
    - Feature deployments
    - Regular updates
    - Non-critical fixes
    - Scheduled releases
    
  P3 (LOW):
    - Documentation updates
    - Maintenance tasks
    - Experimental features
    - Non-urgent changes
```

### 2. Resource Allocation

```yaml
Resource Distribution:
  Critical (P0):
    Runners: 1 dedicated
    CPU: 4 cores
    Memory: 8GB
    Concurrent: 1
    Cost: High
    
  High (P1):
    Runners: 2 shared
    CPU: 2 cores
    Memory: 4GB
    Concurrent: 2
    Cost: Medium
    
  Normal (P2):
    Runners: 5 shared
    CPU: 1 core
    Memory: 2GB
    Concurrent: 5
    Cost: Low
```

### 3. Monitoring and Alerts

```yaml
# prometheus-alerts.yml

groups:
  - name: gitlab_priority_queue
    rules:
      # Alert if critical queue has waiting jobs
      - alert: CriticalQueueBacklog
        expr: gitlab_runner_jobs_queue_duration_seconds{priority="critical"} > 60
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Critical deployment queue backlog"
          description: "Critical jobs waiting for >1 minute"
      
      # Alert if runner is down
      - alert: CriticalRunnerDown
        expr: up{job="gitlab-runner",tags=~".*critical.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Critical runner is down"
          description: "Critical priority runner is not responding"
```

### 4. Queue Management

```python
# queue_monitor.py

import prometheus_client as prom

# Metrics
queue_size = prom.Gauge('gitlab_queue_size', 'Queue size', ['priority'])
queue_wait_time = prom.Histogram('gitlab_queue_wait_seconds', 
                                  'Queue wait time', ['priority'])

def monitor_queues():
    """Monitor queue sizes and wait times"""
    for priority in ['critical', 'high', 'normal', 'low']:
        size = get_queue_size(priority)
        queue_size.labels(priority=priority).set(size)
        
        # Alert if critical queue has backlog
        if priority == 'critical' and size > 0:
            send_alert(f"Critical queue has {size} waiting jobs")
```

### 5. Cost Optimization

```yaml
Cost Optimization Strategies:
  1. Auto-scaling:
     - Scale up runners during peak hours
     - Scale down during off-hours
     - Use spot instances for low priority
  
  2. Resource Sharing:
     - Share runners between P1 and P2
     - Dedicated runner only for P0
     - Dynamic allocation based on load
  
  3. Queue Management:
     - Set max queue time per priority
     - Auto-cancel stale jobs
     - Implement job timeout policies
  
  4. Monitoring:
     - Track runner utilization
     - Monitor queue wait times
     - Analyze cost per deployment
```

---

## Summary

### Recommended Approach for ACE

```yaml
Implementation: Hybrid (Tag-Based + Resource Groups)

Setup:
  1. Dedicated runner for critical (hotfix)
  2. Shared pool for high/normal
  3. Resource groups for production
  4. Branch-based priority classification

Benefits:
  ✅ Simple to implement
  ✅ Cost effective
  ✅ Guaranteed critical path
  ✅ Flexible for normal workloads

Configuration:
  - 1x Critical runner (dedicated)
  - 2x High priority runners (shared)
  - 5x Normal runners (shared)
  
Cost:
  - Critical: $100/month (always on)
  - Shared: $200/month (auto-scale)
  - Total: ~$300/month
```

### Quick Start

```bash
# 1. Setup runners with tags
gitlab-runner register \
  --tag-list "critical,hotfix" \
  --limit 1

# 2. Update .gitlab-ci.yml
# Add priority logic (see examples above)

# 3. Configure monitoring
# Setup Prometheus alerts

# 4. Test priority system
git checkout -b hotfix/critical-fix
git push origin hotfix/critical-fix
# Should use critical runner

git checkout -b feature/new-feature
git push origin feature/new-feature
# Should use normal runner
```

---

**Last Updated**: 2026-02-13  
**Version**: 1.0  
**Recommended for**: Production ACE deployments