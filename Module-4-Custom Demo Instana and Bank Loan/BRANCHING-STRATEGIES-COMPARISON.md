# Branching Strategies Comparison

Perbandingan visual berbagai branching strategies untuk CI/CD deployment.

---

## 📊 Quick Comparison Table

| Strategy | Complexity | Team Size | Release Speed | Merge Conflicts | Best For |
|----------|-----------|-----------|---------------|-----------------|----------|
| **Trunk-Based** | ⭐ Low | 2-10 | ⭐⭐⭐ Fast | ⭐⭐⭐ Rare | ACE, Microservices |
| **GitFlow** | ⭐⭐⭐ High | 10+ | ⭐ Slow | ⭐ Frequent | Enterprise Apps |

---

## 1️⃣ Trunk-Based Development (RECOMMENDED for ACE)

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUNK-BASED DEVELOPMENT                       │
└─────────────────────────────────────────────────────────────────┘

Time: Day 1          Day 2          Day 3          Day 4
      │              │              │              │
      ▼              ▼              ▼              ▼

Developer A:
      feature/A ────┐
                    ├──▶ main ──────────────────────────▶
                    │    (merge)
                    
Developer B:
           feature/B ────┐
                         ├──▶ main ──────────────────▶
                         │    (merge)
                         
Developer C:
                    feature/C ────┐
                                  ├──▶ main ──────▶
                                  │    (merge)

═══════════════════════════════════════════════════════════════════
                         MAIN BRANCH
                    (Always Deployable)
═══════════════════════════════════════════════════════════════════
      │              │              │              │
      ▼              ▼              ▼              ▼
   Deploy         Deploy         Deploy         Deploy
    DEV            DEV            DEV            DEV
```

### Characteristics

```yaml
Branches:
  - main (trunk)           # Only long-lived branch
  - feature/* (1-2 days)   # Short-lived feature branches
  - hotfix/* (<4 hours)    # Emergency fixes only

Workflow:
  1. Create feature branch from main
  2. Develop (max 2 days)
  3. Merge to main (with review)
  4. Auto-deploy to DEV
  5. Manual deploy to TEST/PROD

Pros:
  ✅ Simple and fast
  ✅ Continuous integration
  ✅ Minimal merge conflicts
  ✅ Always deployable main
  ✅ Fast feedback loop

Cons:
  ❌ Requires discipline
  ❌ Need feature flags for incomplete features
  ❌ Requires good test coverage
```

### Detailed Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    Developer Workflow                             │
└──────────────────────────────────────────────────────────────────┘

Step 1: Create Feature Branch
┌──────────┐
│   main   │
└────┬─────┘
     │ git checkout -b feature/ACE-123
     ▼
┌──────────┐
│feature/  │
│ ACE-123  │
└──────────┘

Step 2: Develop (Max 2 Days)
┌──────────┐
│  Local   │──▶ Code ──▶ Test ──▶ Commit
│   Dev    │
└──────────┘

Step 3: Create Merge Request
┌──────────┐     ┌──────────┐     ┌──────────┐
│feature/  │────▶│   MR     │────▶│  Review  │
│ ACE-123  │     │ Created  │     │ Approved │
└──────────┘     └──────────┘     └──────────┘

Step 4: Merge to Main
┌──────────┐
│feature/  │
│ ACE-123  │─────┐
└──────────┘     │
                 ├──▶ Squash & Merge
┌──────────┐     │
│   main   │◀────┘
└────┬─────┘
     │
     ▼ Pipeline Triggered

Step 5: Automated Deployment
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Validate │────▶│  Upload  │────▶│Deploy DEV│
└──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
                                   ┌──────────┐
                                   │  Manual  │
                                   │Deploy TST│
                                   └────┬─────┘
                                        │
                                        ▼
                                   ┌──────────┐
                                   │  Manual  │
                                   │Deploy PRD│
                                   └──────────┘
```

---

## 2️⃣ GitHub Flow

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB FLOW                               │
└─────────────────────────────────────────────────────────────────┘

Time: Week 1         Week 2         Week 3         Week 4
      │              │              │              │
      ▼              ▼              ▼              ▼

Feature Branch (longer-lived):
      feature/login ─────────────────┐
                                     ├──▶ main ──────────▶
                                     │   (merge + deploy)
                                     
Feature Branch:
           feature/api ──────────────┐
                                     ├──▶ main ──────▶
                                     │   (merge + deploy)

═══════════════════════════════════════════════════════════════════
                         MAIN BRANCH
                    (Production Code)
═══════════════════════════════════════════════════════════════════
      │              │              │              │
      ▼              ▼              ▼              ▼
   Deploy         Deploy         Deploy         Deploy
    PROD           PROD           PROD           PROD
```

### Characteristics

```yaml
Branches:
  - main                    # Production code
  - feature/* (1-2 weeks)   # Feature branches

Workflow:
  1. Create feature branch from main
  2. Develop (can be weeks)
  3. Create Pull Request
  4. Review and discuss
  5. Merge to main
  6. Deploy to production immediately

Pros:
  ✅ Simple (only main + features)
  ✅ Good for continuous deployment
  ✅ Clear production state

Cons:
  ❌ No staging environment
  ❌ Longer-lived branches = more conflicts
  ❌ Direct to production (risky)
```

### Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    GitHub Flow Process                            │
└──────────────────────────────────────────────────────────────────┘

┌──────────┐
│   main   │ (Production)
└────┬─────┘
     │
     ├──▶ feature/login ──▶ Develop ──▶ PR ──▶ Review ──┐
     │                                                    │
     ├──▶ feature/api ────▶ Develop ──▶ PR ──▶ Review ──┤
     │                                                    │
     ├──▶ feature/ui ─────▶ Develop ──▶ PR ──▶ Review ──┤
     │                                                    │
     ◀────────────────────── Merge ◀─────────────────────┘
     │
     ▼
  Deploy to Production
```

---

## 3️⃣ GitFlow

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          GITFLOW                                 │
└─────────────────────────────────────────────────────────────────┘

Time: Sprint 1       Sprint 2       Sprint 3       Release
      │              │              │              │
      ▼              ▼              ▼              ▼

┌──────────┐
│  main    │ (Production releases only)
└────┬─────┘
     │                                              ▲
     │                                              │
     ▼                                              │
┌──────────┐                                   ┌────────┐
│ develop  │ (Integration branch)              │release/│
└────┬─────┘                                   │  1.0   │
     │                                          └────────┘
     ├──▶ feature/A ──▶ Develop ──▶ Merge ──▶     │
     │                                  │          │
     ├──▶ feature/B ──▶ Develop ──▶ Merge ──▶     │
     │                                  │          │
     ├──▶ feature/C ──▶ Develop ──▶ Merge ──▶     │
     │                                             │
     ◀─────────────────────────────────────────────┘
     │
     ▼
┌──────────┐
│ hotfix/  │ (Emergency fixes)
│  1.0.1   │
└──────────┘
```

### Characteristics

```yaml
Branches:
  - main              # Production releases
  - develop           # Integration branch
  - feature/*         # Feature development
  - release/*         # Release preparation
  - hotfix/*          # Production fixes

Workflow:
  1. Create feature from develop
  2. Develop feature
  3. Merge back to develop
  4. Create release branch
  5. Test and fix in release
  6. Merge to main and develop
  7. Tag release

Pros:
  ✅ Clear separation of concerns
  ✅ Parallel development
  ✅ Structured releases

Cons:
  ❌ Complex (5 branch types)
  ❌ Frequent merge conflicts
  ❌ Slow release cycle
  ❌ Overhead for small teams
```

### Detailed Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    GitFlow Complete Process                       │
└──────────────────────────────────────────────────────────────────┘

Production:
┌──────────┐
│   main   │ v1.0 ────────────────────▶ v1.1 ──────────▶ v2.0
└────┬─────┘   ▲                         ▲               ▲
     │          │                         │               │
     │          │                         │               │
Integration:    │                         │               │
┌──────────┐    │                         │               │
│ develop  │────┴─────────────────────────┴───────────────┘
└────┬─────┘
     │
     ├──▶ feature/login ──▶ Dev ──▶ Merge
     │                               │
     ├──▶ feature/api ────▶ Dev ──▶ Merge
     │                               │
     ├──▶ feature/ui ─────▶ Dev ──▶ Merge
     │                               │
     ◀───────────────────────────────┘
     │
     ▼
┌──────────┐
│release/  │──▶ Test ──▶ Fix ──▶ Merge to main + develop
│  1.1     │
└──────────┘

Emergency:
┌──────────┐
│ hotfix/  │──▶ Fix ──▶ Merge to main + develop
│  1.0.1   │
└──────────┘
```

---

## 4️⃣ GitLab Flow

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITLAB FLOW                               │
└─────────────────────────────────────────────────────────────────┘

Environment-Based Branches:

┌──────────┐
│   main   │ (Source of truth)
└────┬─────┘
     │
     ├──▶ feature/A ──▶ Dev ──▶ MR ──▶ Merge
     │                               │
     ├──▶ feature/B ──▶ Dev ──▶ MR ──▶ Merge
     │                               │
     ◀───────────────────────────────┘
     │
     ├──▶ pre-production ──▶ Test ──▶ Merge
     │         │
     │         ▼
     │    ┌──────────┐
     │    │   TEST   │
     │    └──────────┘
     │
     └──▶ production ──▶ Deploy
              │
              ▼
         ┌──────────┐
         │   PROD   │
         └──────────┘
```

### Characteristics

```yaml
Branches:
  - main                    # Source of truth
  - feature/*               # Feature development
  - pre-production          # Staging environment
  - production              # Production environment

Workflow:
  1. Create feature from main
  2. Develop and merge to main
  3. Merge main to pre-production
  4. Test in staging
  5. Merge to production
  6. Deploy to production

Pros:
  ✅ Environment-based branches
  ✅ Clear deployment path
  ✅ Good for multiple environments

Cons:
  ❌ Multiple long-lived branches
  ❌ Can be complex
  ❌ Merge overhead
```

### Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    GitLab Flow Process                            │
└──────────────────────────────────────────────────────────────────┘

Development:
┌──────────┐
│   main   │
└────┬─────┘
     │
     ├──▶ feature/A ──▶ MR ──┐
     │                       │
     ├──▶ feature/B ──▶ MR ──┤
     │                       │
     ◀───────────────────────┘
     │
     ▼
Staging:
┌──────────┐
│   pre-   │──▶ Test ──▶ QA Sign-off
│production│
└────┬─────┘
     │
     ▼
Production:
┌──────────┐
│production│──▶ Deploy ──▶ Monitor
└──────────┘
```

---

## 🎯 Recommendation for ACE

### Why Trunk-Based Development?

```
┌─────────────────────────────────────────────────────────────────┐
│              ACE Characteristics vs Strategy Fit                 │
└─────────────────────────────────────────────────────────────────┘

ACE Characteristics:
├─ Binary artifacts (BAR files)
├─ Integration platform (needs fast testing)
├─ Small to medium teams (2-10 developers)
├─ Frequent deployments needed
└─ Simple rollback required

Best Match: TRUNK-BASED DEVELOPMENT ✅

Reasons:
1. Binary files → Less merge conflicts
2. Integration → Fast feedback needed
3. Small teams → Simple workflow better
4. Frequent deploys → Continuous integration
5. Simple rollback → Version in Package Registry
```

### Implementation for ACE

```
┌──────────────────────────────────────────────────────────────────┐
│              ACE Trunk-Based Implementation                       │
└──────────────────────────────────────────────────────────────────┘

Day-to-Day Workflow:

Morning:
  ┌──────────┐
  │Pull main │──▶ Create feature/ACE-123
  └──────────┘

During Day:
  ┌──────────┐
  │ Develop  │──▶ Build BAR ──▶ Test Local
  └──────────┘

End of Day (or max 2 days):
  ┌──────────┐
  │  Commit  │──▶ Push ──▶ Create MR
  └──────────┘

After Review:
  ┌──────────┐
  │  Merge   │──▶ Auto-deploy DEV
  └──────────┘

Pipeline Flow:
  validate ──▶ upload ──▶ deploy-dev ──▶ deploy-test ──▶ deploy-prod
   (auto)      (auto)       (auto)         (manual)        (manual)
```

---

## 📊 Decision Matrix

### Choose Your Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Strategy Selection Guide                      │
└─────────────────────────────────────────────────────────────────┘

IF your project has:
├─ Small team (2-10) + Frequent deploys
│  └─▶ Use: TRUNK-BASED ✅
│
├─ Medium team (5-15) + Web application
│  └─▶ Use: GITHUB FLOW
│
├─ Large team (10+) + Complex releases
│  └─▶ Use: GITFLOW
│
└─ Multiple environments + Staged rollout
   └─▶ Use: GITLAB FLOW

For ACE specifically:
├─ Binary artifacts (BAR files)
├─ Integration testing needed
├─ Small to medium teams
└─▶ TRUNK-BASED DEVELOPMENT ✅✅✅
```

---

## 🔄 Migration Path

### From GitFlow to Trunk-Based

```
┌──────────────────────────────────────────────────────────────────┐
│                    Migration Strategy                             │
└──────────────────────────────────────────────────────────────────┘

Current State (GitFlow):
┌──────────┐
│   main   │
└────┬─────┘
     │
┌────┴─────┐
│ develop  │
└────┬─────┘
     │
     ├─ feature/A
     ├─ feature/B
     └─ feature/C

Step 1: Merge all features to develop
Step 2: Merge develop to main
Step 3: Delete develop branch
Step 4: Update branch protection rules

Target State (Trunk-Based):
┌──────────┐
│   main   │ (trunk)
└────┬─────┘
     │
     ├─ feature/A (short-lived)
     ├─ feature/B (short-lived)
     └─ feature/C (short-lived)

Timeline: 1-2 sprints for full migration
```

---

## 📚 Summary

### Quick Reference

| When to Use | Strategy | Key Benefit |
|-------------|----------|-------------|
| **ACE/Integration** | Trunk-Based | Fast feedback, simple |
| **Web Apps** | GitHub Flow | Continuous deployment |
| **Enterprise** | GitFlow | Structured releases |
| **Multi-env** | GitLab Flow | Environment control |

### For ACE Projects

```yaml
Recommended: Trunk-Based Development

Setup:
  1. Protect main branch
  2. Require PR reviews
  3. Enable CI/CD pipeline
  4. Configure environments (DEV/TEST/PROD)

Daily Workflow:
  1. Pull main
  2. Create feature branch (max 2 days)
  3. Develop and test
  4. Create MR
  5. Merge after review
  6. Auto-deploy to DEV

Success Metrics:
  - Deployment frequency: 5-10/day
  - Lead time: <30 minutes
  - Change failure rate: <5%
  - MTTR: <15 minutes
```

---

**Last Updated**: 2026-02-13  
**Version**: 1.0  
**Recommended for**: ACE CI/CD Implementation