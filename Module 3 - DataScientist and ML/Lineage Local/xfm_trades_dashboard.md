---
# Technical Metadata for HTML Reconstruction
dashboard_type: "IBM watsonx Data Asset Dashboard"
asset_name: "xfm_trades"
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

# Transformed Trading Data Dashboard

## Executive Summary

The **xfm_trades** table is the enterprise's consolidated repository for transformed trading data from all global regions. This critical asset aggregates and enriches trading information from **4 regional sources** (Canada, North America, Europe, and Asia-Pacific) and maintains a perfect **100% data quality score**.

**Business Impact**: CRITICAL - This table represents the final, authoritative source of transformed trading data used across the organization for reporting, analytics, and regulatory compliance.

## Key Performance Indicators

| Metric | Value | Business Meaning |
|--------|-------|------------------|
| **Data Quality Score** | 100% | All validation checks pass - data is production-ready |
| **Upstream Assets** | 9 | Nine different data sources feed into this table |
| **ETL Jobs** | 2 | Two DataStage jobs transform and load data |
| **Regional Tables** | 4 | Consolidates data from four global trading regions |

### What This Means for the Business

- **Global Coverage**: Combines trading data from CA, NA, EU, and APAC regions
- **Data Enrichment**: Enhanced with ISIN master reference data for complete security information
- **Dual Processing**: Two independent ETL paths ensure data completeness and redundancy
- **Enterprise Standard**: Serves as the single source of truth for transformed trading data

## Multi-Regional Data Architecture

### Regional Data Sources

The xfm_trades table consolidates trading information from four major global regions:

| Region | Source Table | Coverage | Business Purpose |
|--------|--------------|----------|------------------|
| 🇨🇦 **Canada** | ca_daily_trades | Canadian markets | Toronto Stock Exchange, TSX Venture |
| 🇺🇸 **North America** | na_daily_trades | US markets | NYSE, NASDAQ, regional exchanges |
| 🇪🇺 **Europe** | eu_daily_trades | European markets | LSE, Euronext, Deutsche Börse |
| 🌏 **Asia-Pacific** | apac_daily_trades | APAC markets | Tokyo, Hong Kong, Singapore, Sydney |

### Reference Data Integration

| Reference Table | Purpose | Business Value |
|-----------------|---------|----------------|
| **isin_master** | Security Master Data | Provides complete security identification, classification, and attributes |

## Data Lineage & Business Flow

### The Complete Transformation Journey

```
STAGE 1: REGIONAL DATA COLLECTION
📍 ca_daily_trades (Canada)
📍 na_daily_trades (North America)
📍 eu_daily_trades (Europe)
📍 apac_daily_trades (Asia-Pacific)
    ↓ ↓ ↓ ↓
    Each region feeds into its own aggregation procedure
    ↓ ↓ ↓ ↓

STAGE 2: REGIONAL AGGREGATION
⚙️  load_ca_ww_trades_sql (Canada Procedure)
⚙️  load_na_ww_trades_sql (North America Procedure)
⚙️  load_eu_ww_trades_sql (Europe Procedure)
⚙️  load_apac_ww_trades_sql (Asia-Pacific Procedure)
    ↓ ↓ ↓ ↓
    All regional data flows into worldwide aggregation
    ↓ ↓ ↓ ↓

STAGE 3: WORLDWIDE CONSOLIDATION
📊 ww_daily_trades (Global Trading Aggregation)
    ↓
    Splits into two parallel transformation paths
    ↓

STAGE 4: DUAL TRANSFORMATION PATHS

Path 1: Primary ETL Processing
├→ 🔧 etl_trades-pg.DataStage job
│   ├─ Applies business rules
│   ├─ Data cleansing and validation
│   └─ Outputs to → 📊 xfm_trades (TARGET)
│

Path 2: Reference Data Enrichment
└→ 🔧 load_xfm_trades_pg.DataStage job
    ├─ Enriches with 📋 isin_master reference data
    ├─ Adds security information
    └─ Outputs to → 📊 xfm_trades (TARGET)
```

### Business Context

1. **Regional Collection**: Daily trading data captured from 4 global regions
2. **Regional Processing**: Each region's data processed through dedicated SQL procedures
3. **Global Aggregation**: All regional data consolidated into worldwide view
4. **Dual Transformation**: Two independent ETL jobs ensure data completeness
   - **Primary Path**: Core business rules and data cleansing
   - **Enrichment Path**: Reference data lookup and security information
5. **Final Output**: Single, authoritative transformed trading dataset

## ETL Processing Pipeline

### 🔧 Primary ETL Job: etl_trades-pg.DataStage

**Purpose**: Core transformation and business rule application

**Processing Steps**:
- ✓ Processes worldwide daily trades from ww_daily_trades
- ✓ Applies trading business rules and calculations
- ✓ Performs data cleansing and validation
- ✓ Standardizes data formats across regions
- ✓ Outputs clean, transformed data to xfm_trades

**Business Value**: Ensures consistent data quality and business rule compliance across all regions

### 🔧 Secondary ETL Job: load_xfm_trades_pg.DataStage

**Purpose**: Reference data enrichment and security information

**Processing Steps**:
- ✓ Enriches trades with ISIN master data
- ✓ Adds complete security identification
- ✓ Performs reference data lookups
- ✓ Appends security classifications and attributes
- ✓ Outputs enriched data to xfm_trades

**Business Value**: Provides complete security context for regulatory reporting and analytics

## Impact Analysis

### 🔄 Upstream Dependencies

Changes to xfm_trades may require coordination with **9 upstream components**:

#### Regional Source Tables (4)
| Component | Region | Impact |
|-----------|--------|--------|
| ca_daily_trades | Canada | Schema changes must be compatible |
| na_daily_trades | North America | Data format consistency required |
| eu_daily_trades | Europe | Timezone and currency considerations |
| apac_daily_trades | Asia-Pacific | Market-specific rules must align |

#### Regional Procedures (4)
| Component | Purpose | Impact |
|-----------|---------|--------|
| load_ca_ww_trades_sql | Canada aggregation | May need procedure updates |
| load_na_ww_trades_sql | NA aggregation | Aggregation logic may change |
| load_eu_ww_trades_sql | EU aggregation | Regional rules may need adjustment |
| load_apac_ww_trades_sql | APAC aggregation | Market hours logic may change |

#### Consolidation & Reference (2)
| Component | Purpose | Impact |
|-----------|---------|--------|
| ww_daily_trades | Global aggregation | Worldwide view must remain consistent |
| isin_master | Security reference | Reference data integrity critical |

### ⚙️ ETL Job Dependencies

Both DataStage jobs must be updated simultaneously:

| Job | Update Priority | Coordination Required |
|-----|----------------|----------------------|
| etl_trades-pg | HIGH | Business rules must align with schema |
| load_xfm_trades_pg | HIGH | Reference data mappings must be updated |

## Change Management Recommendations

### Strategic Considerations

1. **Multi-Regional Coordination**
   - Changes affect 4 regional data sources
   - Coordinate with regional data teams (CA, NA, EU, APAC)
   - Consider timezone differences for deployment windows
   - Account for regional market hours and trading calendars

2. **Upstream Impact Assessment**
   - Evaluate impact on all 9 upstream components
   - Test with data from each region independently
   - Verify regional procedures handle changes correctly
   - Ensure worldwide aggregation remains accurate

3. **Reference Data Integrity**
   - Maintain compatibility with isin_master reference table
   - Verify security lookups continue to work
   - Test reference data enrichment logic
   - Validate security classifications remain accurate

### Tactical Implementation

4. **Dual ETL Job Coordination**
   - Update both DataStage jobs simultaneously
   - Test each job independently first
   - Verify both jobs produce consistent results
   - Ensure no data conflicts between the two paths

5. **Data Quality Monitoring**
   - Maintain 100% quality score throughout changes
   - Implement comprehensive validation checks
   - Monitor data quality across all regions
   - Set up alerts for quality degradation

6. **Worldwide Aggregation Verification**
   - Verify ww_daily_trades aggregation logic
   - Test with data from all 4 regions
   - Validate regional totals match worldwide totals
   - Check for data loss or duplication

### Operational Excellence

7. **Comprehensive Backup Strategy**
   - Backup all 9 upstream components
   - Backup both DataStage jobs
   - Backup xfm_trades table
   - Document current state for rollback

8. **Coordinated Rollback Plan**
   - Prepare rollback for entire data pipeline
   - Test rollback procedure in development
   - Define rollback triggers and decision points
   - Ensure 24/7 support coverage during deployment

### Testing Requirements

9. **Regional Data Validation**
   - Test with real data from each region
   - Verify currency conversions (if applicable)
   - Validate timezone handling
   - Check market-specific business rules

10. **End-to-End Testing**
    - Trace data from each regional source to final output
    - Verify data completeness across all regions
    - Validate reference data enrichment
    - Confirm regulatory reporting requirements met

## Quick Reference

### Asset Information

- **Asset Type**: Database Table
- **Catalog**: Enterprise Catalogue Banking
- **Schema**: techxchange
- **Database**: ibmclouddb
- **Tags**: techxchange
- **Purpose**: Consolidated transformed trades from all regions

### Data Sources Summary

- **Regional Sources**: 4 tables (CA, NA, EU, APAC)
- **Regional Procedures**: 4 SQL procedures
- **Global Aggregation**: 1 table (ww_daily_trades)
- **Reference Data**: 1 table (isin_master)
- **ETL Jobs**: 2 DataStage jobs
- **Total Upstream Assets**: 9 components

### Access Points

- **View Asset Details**: [Asset in Catalog](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-7740-90bb-84b9cfeafeb5?context=df)
- **Data Quality Report**: [Quality Dashboard](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-7740-90bb-84b9cfeafeb5/data-quality)
- **Interactive Lineage**: [Lineage Graph](https://ca-tor.dai.cloud.ibm.com/lineage?assetsIds=f62bd0ad86d3197d964765dd05bccb08a34884d0470460b3bc0cde38abd568a7&startingAssetDirection=upstreamDownstream&featureFiltersScopeSettingsCloud=false&numberOfHops=50&context=df)
- **Browse Catalog**: [Enterprise Catalogue Banking](https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba?context=df)

---

## Technical Specifications for HTML Reconstruction

### Page Structure

```
HTML Document
├── Head
│   ├── Meta: charset=UTF-8, viewport
│   ├── Title: "xfm_trades - IBM watsonx"
│   ├── Font: IBM Plex Sans (Google Fonts)
│   └── Embedded CSS (lines 8-485)
│
└── Body
    ├── IBM Header (sticky, z-index: 1000)
    │   ├── Logo: "IBM watsonx"
    │   ├── Search Bar (max-width: 400px)
    │   └── Actions: Notifications, User, Location
    │
    ├── Breadcrumb Navigation
    │   └── Path: Catalogs / Enterprise Catalogue Banking / xfm_trades
    │
    └── Main Container (max-width: 1584px, padding: 32px)
        ├── Page Header (border-left: 3px solid #0f62fe)
        │   ├── H1: "xfm_trades"
        │   ├── Subtitle: "Table • Transformed Trading Data"
        │   └── Tags: 4 tags (1 primary, 3 secondary)
        │
        ├── Tabs (5 tabs: Overview active, Data quality, Lineage, Profile, Access control)
        │
        ├── Stats Grid (4 stat cards, responsive grid)
        │   ├── Data Quality Score: 100%
        │   ├── Upstream Assets: 9
        │   ├── ETL Jobs: 2
        │   └── Regional Tables: 4
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
        │   └── Data Sources Card
        │       ├── Info Notification
        │       ├── Regional Sources List (4 items)
        │       └── Reference Data List (1 item)
        │
        ├── Data Lineage Flow (full-width card)
        │   ├── ASCII Art Lineage Diagram
        │   └── CTA Button: "View interactive lineage graph"
        │
        ├── ETL Processing Pipeline (full-width card)
        │   └── Grid with 2 ETL Job Descriptions
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
--heading-3: 16px;
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
<span class="status-badge [success|warning|info]">
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
- Upstream Assets: 9
- ETL Jobs: 2
- Regional Tables: 4

#### Regional Sources (4)
1. ca_daily_trades (Canada) - Source
2. na_daily_trades (North America) - Source
3. eu_daily_trades (Europe) - Source
4. apac_daily_trades (Asia-Pacific) - Source

#### Reference Data (1)
1. isin_master (Security Master) - Reference

#### ETL Jobs (2)
1. **etl_trades-pg.DataStage job**
   - Processes worldwide daily trades
   - Applies business rules
   - Data cleansing and validation
   - Outputs to xfm_trades

2. **load_xfm_trades_pg.DataStage job**
   - Enriches with ISIN master data
   - Adds security information
   - Reference data lookup
   - Outputs to xfm_trades

#### Lineage Flow (ASCII Art)
```
REGIONAL SOURCES (4 Tables)
    📍 ca_daily_trades (Canada)
    📍 na_daily_trades (North America)
    📍 eu_daily_trades (Europe)
    📍 apac_daily_trades (Asia-Pacific)
        ↓ ↓ ↓ ↓ feed into regional procedures
    ⚙️ load_ca_ww_trades_sql
    ⚙️ load_na_ww_trades_sql
    ⚙️ load_eu_ww_trades_sql
    ⚙️ load_apac_ww_trades_sql
        ↓ ↓ ↓ ↓ aggregate into
    📊 ww_daily_trades (Worldwide Aggregation)
        ↓ splits into two transformation paths
        ├→ 🔧 etl_trades-pg.DataStage job
        │     ↓ produces
        │     📊 xfm_trades (TARGET)
        │
        └→ 🔧 load_xfm_trades_pg.DataStage job
              ↓ enriched with
          📋 isin_master (Reference Data)
              ↓ produces
          📊 xfm_trades (TARGET)
```

### External Links

1. Asset Details: `https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-7740-90bb-84b9cfeafeb5?context=df`
2. Data Quality Report: `https://ca-tor.dai.cloud.ibm.com/data/catalogs/019df3df-d65f-7603-8e47-4731370f0bba/asset/019df920-0c3d-7740-90bb-84b9cfeafeb5/data-quality`
3. Lineage Graph: `https://ca-tor.dai.cloud.ibm.com/lineage?assetsIds=f62bd0ad86d3197d964765dd05bccb08a34884d0470460b3bc0cde38abd568a7&startingAssetDirection=upstreamDownstream&featureFiltersScopeSettingsCloud=false&numberOfHops=50&context=df`
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
9. **Build main grid** with 3 cards (Quality, Information, Data Sources)
10. **Add full-width cards** for Lineage, ETL Processing, Recommendations, and Quick Actions
11. **Include JavaScript** for tab switching and smooth scrolling
12. **Apply all URLs** from the External Links section
13. **Use exact data values** from the Data Content section
14. **Style with IBM Carbon** design system colors and spacing
15. **Add regional sources list** with 4 items and info badges
16. **Add reference data list** with 1 item
17. **Create ETL processing grid** with 2 job descriptions
18. **Use multi-regional lineage diagram** with 4 regional sources