---
# Technical Metadata for HTML Reconstruction
dashboard_type: "IBM watsonx Data Asset Dashboard"
asset_name: "ca_daily_trades"
asset_type: "Table"
catalog: "Enterprise Catalogue Banking"
schema: "techxchange"
database: "ibmclouddb"
layout_system: "responsive-grid"
design_system: "IBM Carbon Design System"
font_family: "IBM Plex Sans"
primary_color: "#0f62fe"
background_color: "#f4f4f4"
max_width: "1584px"
---

# Canada Daily Trading Data Dashboard

## Executive Summary

The **ca_daily_trades** table serves as a critical source for Canada's daily trading activities within the Enterprise Banking Catalogue. This asset maintains a perfect **100% data quality score** and acts as the foundation for downstream trading analytics and reporting systems across the organization.

**Business Impact**: HIGH - This table directly feeds 6 downstream components, making it a cornerstone of the trading data infrastructure.

## Key Performance Indicators

| Metric | Value | Business Meaning |
|--------|-------|------------------|
| **Data Quality Score** | 100% | All data validation checks pass - data is reliable and trustworthy |
| **Downstream Assets** | 6 | Six different systems depend on this data |
| **ETL Jobs** | 2 | Two automated data transformation processes use this table |
| **Dependent Tables** | 3 | Three other database tables rely on this data |

### What This Means for the Business

- **Reliability**: Perfect quality score ensures accurate trading reports and analytics
- **Critical Path**: Changes here ripple through 6 downstream systems
- **Automation**: Two ETL jobs automatically process this data daily
- **Integration**: Three other tables depend on this data for their operations

## Data Lineage & Business Flow

### The Journey of Trading Data

```
📍 START: ca_daily_trades (Canada Daily Trading Data)
    ↓
    Feeds into automated processing
    ↓
⚙️  load_ca_ww_trades_sql (SQL Procedure)
    Aggregates Canadian trades with other regions
    ↓
📊 ww_daily_trades (Worldwide Trading Aggregation)
    Combines all regional trading data
    ↓
    Splits into two transformation paths:
    ↓
    Path 1: Primary ETL Processing
    ├→ 🔧 etl_trades-pg.DataStage job
    │   ├→ 📊 xfm_trades (Transformed Trades)
    │   └→ 📊 otco_trades (Octo Trades)
    │
    Path 2: Secondary Enrichment
    └→ 🔧 load_xfm_trades_pg.DataStage job
        └→ 📊 xfm_trades (Transformed Trades)
```

### Business Context

1. **Source Data**: Canadian daily trading transactions are captured in this table
2. **Regional Aggregation**: Data is combined with other regions (NA, EU, APAC) via SQL procedure
3. **Global View**: Creates worldwide trading picture in ww_daily_trades
4. **Transformation**: Two DataStage jobs apply business rules and enrich the data
5. **Final Output**: Produces transformed trading data for reporting and analytics

## Impact Analysis

### ⚠️ HIGH IMPACT ALERT

Any changes to the ca_daily_trades table will affect **6 downstream components**. Here's what's at risk:

#### Critical Impact (Immediate Action Required)

| Component | Type | Impact Level | Why It Matters |
|-----------|------|--------------|----------------|
| **load_ca_ww_trades_sql** | SQL Procedure | 🔴 HIGH | Directly reads from this table - schema changes break the procedure |
| **ww_daily_trades** | Table | 🔴 HIGH | Receives aggregated data - data quality issues propagate here |

#### Medium Impact (Coordination Required)

| Component | Type | Impact Level | Why It Matters |
|-----------|------|--------------|----------------|
| **etl_trades-pg** | DataStage Job | 🟡 MEDIUM | Processes downstream data - may need job reconfiguration |
| **load_xfm_trades_pg** | DataStage Job | 🟡 MEDIUM | Enrichment logic may need adjustment |

#### Low Impact (Monitor & Verify)

| Component | Type | Impact Level | Why It Matters |
|-----------|------|--------------|----------------|
| **xfm_trades** | Table | 🟢 LOW | End of pipeline - verify final output quality |
| **otco_trades** | Table | 🟢 LOW | Secondary output - ensure data consistency |

## Change Management Recommendations

### Before Making Changes

1. **Test in Development First**
   - Never change production data directly
   - Use development environment to validate changes
   - Run full regression tests on all 6 downstream components

2. **Create Comprehensive Backups**
   - Backup ca_daily_trades table
   - Backup all dependent objects (procedures, jobs, tables)
   - Document current state for rollback

3. **Coordinate with Stakeholders**
   - Notify teams using ww_daily_trades
   - Alert owners of xfm_trades and otco_trades
   - Schedule change window with ETL job owners

### During Changes

4. **Maintain Data Quality**
   - Preserve 100% quality score
   - Validate all data after changes
   - Run quality checks before promoting to production

5. **Monitor Downstream Impact**
   - Verify load_ca_ww_trades_sql executes successfully
   - Check ww_daily_trades receives correct data
   - Confirm both DataStage jobs complete without errors

### After Changes

6. **Verify End-to-End Flow**
   - Trace data from ca_daily_trades to final outputs
   - Validate xfm_trades and otco_trades contain expected data
   - Review data quality reports

7. **Update Documentation**
   - Document schema changes
   - Update data dictionary
   - Revise ETL job documentation

8. **Implement Rollback Plan**
   - Keep rollback scripts ready
   - Test rollback procedure
   - Define rollback triggers and decision points

## Quick Reference

### Asset Information

- **Asset Type**: Database Table
- **Catalog**: Enterprise Catalogue Banking
- **Schema**: techxchange
- **Database**: ibmclouddb
- **Tags**: techxchange
- **Added**: May 06, 2026, 12:12 AM

### Access Points

- **View Asset Details**: [Asset in Catalog](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-70a7-9758-dfb75d208612?context=df)
- **Data Quality Report**: [Quality Dashboard](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-70a7-9758-dfb75d208612/data-quality)
- **Interactive Lineage**: [Lineage Graph](https://ca-tor.dai.cloud.ibm.com/lineage?assetsIds=6bfdecc63bcea9994be4e7e4894c6043b9d9cd52b56b3f5b4b75b9f1adad25bd&startingAssetDirection=upstreamDownstream&featureFiltersScopeSettingsCloud=false&numberOfHops=50&context=df)
- **Browse Catalog**: [Enterprise Catalogue Banking](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba?context=df)

---

## Technical Specifications for HTML Reconstruction

### Page Structure

```
HTML Document
├── Head
│   ├── Meta: charset=UTF-8, viewport
│   ├── Title: "ca_daily_trades - IBM watsonx"
│   ├── Font: IBM Plex Sans (Google Fonts)
│   └── Embedded CSS (lines 8-491)
│
└── Body
    ├── IBM Header (sticky, z-index: 1000)
    │   ├── Logo: "IBM watsonx"
    │   ├── Search Bar (max-width: 400px)
    │   └── Actions: Notifications, User, Location
    │
    ├── Breadcrumb Navigation
    │   └── Path: Catalogs / Enterprise Catalogue Banking / ca_daily_trades
    │
    └── Main Container (max-width: 1584px, padding: 32px)
        ├── Page Header (border-left: 3px solid #0f62fe)
        │   ├── H1: "ca_daily_trades"
        │   ├── Subtitle: "Table • Canada Daily Trading Data"
        │   └── Tags: 4 tags (1 primary, 3 secondary)
        │
        ├── Tabs (5 tabs: Overview active, Data quality, Lineage, Profile, Access control)
        │
        ├── Stats Grid (4 stat cards, responsive grid)
        │   ├── Data Quality Score: 100%
        │   ├── Downstream Assets: 6
        │   ├── ETL Jobs: 2
        │   └── Dependent Tables: 3
        │
        ├── Main Grid (3 columns, responsive)
        │   ├── Data Quality Card
        │   │   ├── Score Ring (SVG, 120x120px)
        │   │   ├── Success Notification
        │   │   ├── Quality Metrics Table
        │   │   └── CTA Button: "View detailed report"
        │   │
        │   ├── Asset Information Card
        │   │   ├── Information Table (6 rows)
        │   │   └── CTA Button: "View in catalog"
        │   │
        │   └── Impact Analysis Card
        │       ├── Warning Notification
        │       ├── Affected Components List (6 items)
        │       └── Impact Levels: High (2), Medium (2), Low (2)
        │
        ├── Data Lineage Flow (full-width card)
        │   ├── ASCII Art Lineage Diagram
        │   └── CTA Button: "View interactive lineage graph"
        │
        ├── Change Management Recommendations (full-width card)
        │   └── Recommendation List (8 items with lightbulb icons)
        │
        └── Quick Actions (full-width card)
            └── Button Group (4 buttons: 3 primary, 1 secondary)
```

### CSS Design Tokens

#### Colors (IBM Carbon Design System)

```css
/* Primary Colors */
--primary-blue: #0f62fe;
--primary-blue-hover: #0353e9;
--dark-background: #161616;
--light-background: #f4f4f4;
--white: #ffffff;

/* Text Colors */
--text-primary: #161616;
--text-secondary: #525252;

/* Border Colors */
--border-subtle: #e0e0e0;
--border-strong: #0f62fe;

/* Status Colors */
--success-bg: #defbe6;
--success-text: #0e6027;
--success-border: #24a148;

--warning-bg: #fcf4d6;
--warning-text: #684e00;
--warning-border: #f1c21b;

--error-bg: #ffd7d9;
--error-text: #750e13;
--error-border: #da1e28;

--info-bg: #d0e2ff;
--info-text: #0043ce;
--info-border: #0f62fe;

/* Interactive States */
--hover-background: #f4f4f4;
--active-border: #0f62fe;
```

#### Typography

```css
/* Font Family */
font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;

/* Font Sizes */
--heading-1: 32px;
--heading-2: 20px;
--body: 14px;
--small: 12px;
--stat-value: 48px;
--score-value: 32px;

/* Font Weights */
--regular: 400;
--medium: 500;
--semibold: 600;
```

#### Spacing

```css
/* Container Spacing */
--container-padding: 32px;
--card-padding: 24px;
--grid-gap: 16px;

/* Component Spacing */
--header-height: 48px;
--breadcrumb-padding: 16px 32px;
--tab-padding: 16px 24px;
--button-padding: 12px 16px;
```

#### Layout

```css
/* Grid System */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 16px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

/* Responsive Breakpoint */
@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr; }
    .container { padding: 16px; }
}
```

### Component Specifications

#### IBM Header Component

```html
<div class="ibm-header">
  <!-- Background: #161616, Height: 48px, Position: sticky -->
  <div class="ibm-header-logo">IBM watsonx</div>
  <div class="ibm-header-search">
    <input type="text" placeholder="Search in your workspaces">
    <!-- Pseudo-element: 🔍 icon -->
  </div>
  <div class="ibm-header-actions">
    <span>🔔</span>
    <span class="ibm-header-user">3117131 - ilz-saas-448</span>
    <span>Toronto ▼</span>
  </div>
</div>
```

#### Quality Score Ring (SVG)

```html
<div class="score-ring">
  <svg width="120" height="120">
    <circle class="bg" cx="60" cy="60" r="45" 
            fill="none" stroke="#e0e0e0" stroke-width="8"></circle>
    <circle class="progress" cx="60" cy="60" r="45" 
            fill="none" stroke="#24a148" stroke-width="8" 
            stroke-linecap="round" stroke-dasharray="283" 
            stroke-dashoffset="0" transform="rotate(-90 60 60)"></circle>
  </svg>
  <div class="score-value">100%</div>
</div>
```

#### Status Badge Component

```html
<span class="status-badge [success|warning|error|info]">
  [Badge Text]
</span>
```

#### Button Component

```html
<a href="[URL]" class="btn [secondary]" target="_blank">
  [Button Text]
</a>
```

### Interactive Elements

#### Tab Functionality (JavaScript)

```javascript
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
    });
});
```

#### Smooth Scroll (JavaScript)

```javascript
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
```

### Data Content

#### Stats Values
- Data Quality Score: 100%
- Downstream Assets: 6
- ETL Jobs: 2
- Dependent Tables: 3

#### Impact Analysis Components
1. load_ca_ww_trades_sql (Procedure) - HIGH
2. ww_daily_trades (Table) - HIGH
3. etl_trades-pg (DataStage Job) - MEDIUM
4. load_xfm_trades_pg (DataStage Job) - MEDIUM
5. xfm_trades (Table) - LOW
6. otco_trades (Table) - LOW

#### Lineage Flow (ASCII Art)
```
📍 ca_daily_trades (Source Table)
    ↓ feeds into
⚙️ load_ca_ww_trades_sql (SQL Procedure)
    ↓ populates
📊 ww_daily_trades (Worldwide Aggregation Table)
    ↓ ↓ splits into two paths
    ├→ 🔧 etl_trades-pg.DataStage job
    │     ↓ ↓ produces
    │     ├→ 📊 xfm_trades (Transformed Trades)
    │     └→ 📊 otco_trades (Octo Trades)
    │
    └→ 🔧 load_xfm_trades_pg.DataStage job
          ↓ produces
       📊 xfm_trades (Transformed Trades)
```

### External Links

1. Asset Details: `https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-70a7-9758-dfb75d208612?context=df`
2. Data Quality Report: `https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-70a7-9758-dfb75d208612/data-quality`
3. Lineage Graph: `https://ca-tor.dai.cloud.ibm.com/lineage?assetsIds=6bfdecc63bcea9994be4e7e4894c6043b9d9cd52b56b3f5b4b75b9f1adad25bd&startingAssetDirection=upstreamDownstream&featureFiltersScopeSettingsCloud=false&numberOfHops=50&context=df`
4. Browse Catalog: `https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba?context=df`

---

## Reconstruction Guide

To rebuild the HTML from this markdown:

1. **Create HTML5 document** with IBM Plex Sans font from Google Fonts
2. **Embed CSS** using the design tokens and component specifications above
3. **Build header** with sticky positioning and IBM branding
4. **Add breadcrumb** navigation with proper links
5. **Create main container** with max-width 1584px
6. **Build page header** with title, subtitle, and tags
7. **Add tabs** with active state on "Overview"
8. **Create stats grid** with 4 stat cards
9. **Build main grid** with 3 cards (Quality, Information, Impact)
10. **Add full-width cards** for Lineage, Recommendations, and Quick Actions
11. **Include JavaScript** for tab switching and smooth scrolling
12. **Apply all URLs** from the External Links section
13. **Use exact data values** from the Data Content section
14. **Style with IBM Carbon** design system colors and spacing