# Spoof Landing Backend - A/B Testing Analytics API

A Node.js Express backend for tracking and analyzing A/B testing data for DiagnoAssist's spoof landing page

## Getting Started

### Prerequisites

- Node.js 16+
- Supabase account and database
- Environment variables configured

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
FRONTEND_URL=your_frontend_url
PORT=4000
LOG_LEVEL=normal  # Options: silent, normal, verbose
```

### Database Schema

Required Supabase tables:

**sessions**
```sql
CREATE TABLE sessions (
  session_id TEXT,
  variant TEXT,
  start_time TIMESTAMP,
  UNIQUE(session_id, variant)
);
```

**button_clicks**
```sql
CREATE TABLE button_clicks (
  session_id TEXT,
  label TEXT,
  plan_type TEXT,
  variant TEXT,
  clicked_at TIMESTAMP
);
```

### Running the Server

```bash
# Development
npm start
```

## GET API Endpoints

### `GET /stats`
Returns comprehensive A/B testing analytics.

### `GET /raw-clicks`
Returns all raw click data from the database.

### `GET /cross-variant-sessions`
Returns sessions that tested multiple variants.

## Stats Endpoint Response Guide

The `/stats` endpoint returns analytics organized into three main sections:

### 1. Overall Section

Provides raw data context and quality metrics:

```json
{
  "overall": {
    "rawClicks": 150,              // Total clicks before deduplication
    "duplicatesExcluded": 25,      // Number of duplicate clicks removed
    "crossVariantSessions": 3,     // Users who tested both variants
    "contaminationRate": "5.2",    // Percentage of cross-variant users
    "dataQuality": {
      "isClean": false,            // True if no cross-variant users
      "contaminationLevel": "Low"  // None/Low/Medium/High
    }
  }
}
```

**Key Insights:**
- **Contamination Rate**: Higher rates indicate more users tested both variants
- **Data Quality**: "None" = perfect A/B test, "Low" < 5%, "Medium" < 15%, "High" ≥ 15%

### 2. Filtered Section

Clean A/B testing data with cross-variant users excluded:

```json
{
  "filtered": {
    "sessions": 95,                // Total sessions (excludes cross-variant users)
    "clicks": 125,                 // Total clicks (deduplicated)
    "demoClicks": 30,              // Demo button clicks
    "starterClicks": 45,           // Starter plan clicks
    "proClicks": 40,               // Professional plan clicks
    "enterpriseClicks": 10,        // Enterprise plan clicks
    "variantStats": {
      "A": {
        "visits": 48,              // Sessions for variant A
        "clicks": 62,              // Total clicks for variant A
        "interestedUsers": 25,     // Users who clicked any subscribe button
        "demoClicks": 15,          // Demo clicks for variant A
        "starterClicks": 22,       // Starter clicks for variant A
        "proClicks": 20,           // Professional clicks for variant A
        "enterpriseClicks": 5,     // Enterprise clicks for variant A
        "conversionRate": "52.08"  // (interestedUsers / visits) * 100
      },
      "B": { /* similar structure */ }
    }
  }
}
```

**Use Case:** Primary A/B testing analysis and statistical significance testing.

### 3. Unfiltered Section

Complete engagement data including all users:

```json
{
  "unfiltered": {
    "sessions": 100,               // All sessions (includes cross-variant users)
    "clicks": 150,                 // All clicks (deduplicated)
    "demoClicks": 35,              // All demo clicks
    "starterClicks": 50,           // All starter clicks
    "proClicks": 50,               // All professional clicks
    "enterpriseClicks": 15,        // All enterprise clicks
    "variantStats": {
      "A": {
        "visits": 52,              // All sessions that saw variant A
        "clicks": 78,              // All clicks from variant A sessions
        "interestedUsers": 28,     // Users interested in variant A (cross-variant users count in both)
        "conversionRate": "53.85"  // Conversion rate for variant A
      },
      "B": { /* similar structure */ }
    }
  }
}
```

**Use Case:** Understanding overall engagement and user behavior patterns.

## Differences Between Filtered vs Unfiltered

| Aspect | Filtered | Unfiltered |
|--------|----------|------------|
| **Cross-variant users** | Excluded | Included |
| **Use case** | A/B test analysis | Engagement analysis |
| **Interested users** | Per-variant deduplication, excluding cross-variant | Per-variant deduplication, including cross-variant |
| **Statistical validity** | High (clean A/B test) | Lower (contaminated) |

## Understanding the Metrics

### Plan-Specific Clicks
- **Multiple clicks per user allowed**: If a user clicks both Starter and Professional, both are counted
- **Deduplication key**: `session_id + variant + plan_type + label`
- **Purpose**: Measures plan popularity and engagement patterns

### Interested Users
- **One count per user per variant**: User who clicked any subscribe button
- **Cross-variant handling**: 
  - **Filtered**: Excluded entirely
  - **Unfiltered**: Counted in both variants if they tested both
- **Purpose**: Measures conversion intent, not plan popularity

### Conversion Rate
- **Formula**: `(interestedUsers / visits) * 100`
- **Interpretation**: Percentage of visitors who showed purchase intent
- **Note**: Based on user-level conversion, not individual plan clicks
