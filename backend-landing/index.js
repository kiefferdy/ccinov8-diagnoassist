require('dotenv').config();

const express = require('express');
const cors = require('cors');
const app = express();
const supabase = require('./supabaseClient');
const PORT = process.env.PORT || 4000;

// Configurable logging system
const LOG_LEVEL = process.env.LOG_LEVEL || 'normal';

const log = {
  error: (msg) => console.error(`[ERROR] ${msg}`),
  info: (msg) => LOG_LEVEL !== 'silent' && console.log(`[INFO] ${msg}`),
  verbose: (msg) => LOG_LEVEL === 'verbose' && console.log(`[VERBOSE] ${msg}`),
  analytics: (msg) => LOG_LEVEL === 'verbose' && console.log(msg)
};

// CORS configuration
const corsOptions = {
  origin: [
    'http://localhost:5173', // Vite dev server
    'http://localhost:3000', // Alternative local port
    process.env.FRONTEND_URL // Railway or production frontend URL
  ].filter(Boolean), // Remove any undefined values
  credentials: true
};

app.use(cors(corsOptions));
app.use(express.json());

app.listen(PORT, () => {
  log.info(`Server is running on port ${PORT}`);
});

app.post('/track-visit', async (req, res) => {
    const {sessionId, timestamp, variant} = req.body;

    const {error} = await supabase.from('sessions').upsert({
        session_id: sessionId,
        start_time: timestamp,
        variant: variant
    }, {onConflict: 'session_id,variant'});
    log.verbose(`visit: ${sessionId} at ${timestamp} (variant: ${variant || 'unknown'})`);

    if (error) {
        log.error(`Supabase error on track-visit: ${error.message}`);
        return res.status(500).json({ error: error.message });
    }

    res.sendStatus(200);
})


app.post('/track-click', async (req, res) => {
  const { type, plan, sessionId, variant } = req.body;

  const { error } = await supabase
    .from('button_clicks')
    .insert({
      session_id: sessionId,
      label: type,
      plan_type: plan?.name || null,
      variant: variant,
      clicked_at: new Date().toISOString(),
    });

  if (error) {
    log.error(`Supabase error on track-click: ${error.message}`);
    return res.status(500).json({ error: error.message });
  }

  log.verbose(`button click: ${type} ${plan?.name || ''} (variant: ${variant || 'unknown'})`);
  res.sendStatus(200);
});

app.get('/stats', async (_, res) => {
  try {
    // Get all clicks with variant data
    const { data: clicks, error: clickError } = await supabase
      .from('button_clicks')
      .select('session_id, label, plan_type, variant');

    // Get all visits with variant data
    const { data: visits, error: visitError } = await supabase
      .from('sessions')
      .select('session_id, variant');

    if (clickError) throw clickError;
    if (visitError) throw visitError;

    // Calculate session analytics
    const uniqueSessions = [...new Set(visits.map(v => v.session_id))];
    
    // Identify cross-variant users (users who tested both variants)
    const sessionVariantMap = {};
    visits.forEach(visit => {
      const sessionId = visit.session_id;
      if (!sessionVariantMap[sessionId]) {
        sessionVariantMap[sessionId] = new Set();
      }
      sessionVariantMap[sessionId].add(visit.variant || 'A');
    });
    
    const crossVariantUsers = Object.keys(sessionVariantMap)
      .filter(sessionId => sessionVariantMap[sessionId].size > 1);
    
    
    // Filter for pure A/B testing (exclude cross-variant users)
    const pureVisits = visits.filter(visit => 
      !crossVariantUsers.includes(visit.session_id)
    );
    
    // Deduplicate clicks by session_id + label + variant + plan_type combination
    // This ensures each user is only counted once per action type per variant per plan
    // Allows users to click multiple plans within same variant
    const uniqueClicks = new Map();
    clicks.forEach(click => {
      const key = `${click.session_id}_${click.label}_${click.variant || 'A'}_${click.plan_type || 'unknown'}`;
      if (!uniqueClicks.has(key)) {
        uniqueClicks.set(key, click);
      }
    });
    const deduplicatedClicks = Array.from(uniqueClicks.values());

    // Calculate variant-specific analytics
    const filteredVariantStats = { A: {}, B: {} };
    const unfilteredVariantStats = { A: {}, B: {} };

    // Initialize variant stats for both filtered and unfiltered
    ['A', 'B'].forEach(variant => {
      filteredVariantStats[variant] = {
        visits: 0,
        clicks: 0,
        interestedUsers: 0,  // Users who clicked any subscribe button
        demoClicks: 0,
        starterClicks: 0,
        proClicks: 0,
        enterpriseClicks: 0,
        conversionRate: 0
      };
      unfilteredVariantStats[variant] = { ...filteredVariantStats[variant] };
    });

    // Count filtered visits by variant (excludes cross-variant users)
    pureVisits.forEach(visit => {
      const variant = visit.variant || 'A'; // Default to A for legacy data
      if (filteredVariantStats[variant]) {
        filteredVariantStats[variant].visits++;
      }
    });

    // Count unfiltered visits by variant (includes all users)
    visits.forEach(visit => {
      const variant = visit.variant || 'A'; // Default to A for legacy data
      if (unfilteredVariantStats[variant]) {
        unfilteredVariantStats[variant].visits++;
      }
    });

    // Separate clicks into filtered and unfiltered for cleaner processing
    const filteredClicks = deduplicatedClicks.filter(click => 
      !crossVariantUsers.includes(click.session_id)
    );
    
    // Per-variant user deduplication (allows cross-variant users in both variants)
    const perVariantUserSubscribeIntentMap = new Map();
    clicks.forEach(click => {
      if (click.label === "subscribe") {
        const key = `${click.session_id}_${click.variant || 'A'}`; // Include variant so cross-variant users count in both
        if (!perVariantUserSubscribeIntentMap.has(key)) {
          perVariantUserSubscribeIntentMap.set(key, click);
        }
      }
    });
    const perVariantUniqueUserSubscribeClicks = Array.from(perVariantUserSubscribeIntentMap.values());
    
    // Filter per-variant deduplication for clean A/B testing
    const filteredPerVariantUserSubscribeClicks = perVariantUniqueUserSubscribeClicks.filter(click => 
      !crossVariantUsers.includes(click.session_id)
    );
    
    
    // Count unfiltered stats - user intent (using per-variant deduplication)
    perVariantUniqueUserSubscribeClicks.forEach(click => {
      const variant = click.variant || 'A';
      if (unfilteredVariantStats[variant]) {
        unfilteredVariantStats[variant].interestedUsers++;
      }
    });
    
    // Count unfiltered stats - plan-specific clicks and other metrics
    deduplicatedClicks.forEach(click => {
      const variant = click.variant || 'A';
      
      if (unfilteredVariantStats[variant]) {
        unfilteredVariantStats[variant].clicks++;
        
        if (click.label === "subscribe") {
          // Plan-specific clicks (allows multiple per user)
          switch(click.plan_type) {
            case "Starter":
              unfilteredVariantStats[variant].starterClicks++;
              break;
            case "Professional":  
              unfilteredVariantStats[variant].proClicks++;
              break;
            case "Enterprise":
              unfilteredVariantStats[variant].enterpriseClicks++;
              break;
          }
        } else {
          unfilteredVariantStats[variant].demoClicks++;
        }
      }
    });
    
    // Count filtered stats - user intent (using per-variant deduplication)
    filteredPerVariantUserSubscribeClicks.forEach(click => {
      const variant = click.variant || 'A';
      if (filteredVariantStats[variant]) {
        filteredVariantStats[variant].interestedUsers++;
      }
    });
    
    // Count filtered stats - plan-specific clicks and other metrics
    filteredClicks.forEach(click => {
      const variant = click.variant || 'A';
      
      if (filteredVariantStats[variant]) {
        filteredVariantStats[variant].clicks++;
        
        if (click.label === "subscribe") {
          // Plan-specific clicks (allows multiple per user)
          switch(click.plan_type) {
            case "Starter":
              filteredVariantStats[variant].starterClicks++;
              break;
            case "Professional":
              filteredVariantStats[variant].proClicks++;
              break;
            case "Enterprise":
              filteredVariantStats[variant].enterpriseClicks++;
              break;
          }
        } else {
          filteredVariantStats[variant].demoClicks++;
        }
      }
    });
    
    // Calculate conversion rates for both filtered and unfiltered stats
    ['A', 'B'].forEach(variant => {
      // Filtered A/B conversion rates (excludes cross-variant users)
      if (filteredVariantStats[variant].visits > 0) {
        filteredVariantStats[variant].conversionRate = 
          (filteredVariantStats[variant].interestedUsers / filteredVariantStats[variant].visits * 100).toFixed(2);
      }
      
      // Unfiltered conversion rates (includes all users)
      if (unfilteredVariantStats[variant].visits > 0) {
        unfilteredVariantStats[variant].conversionRate = 
          (unfilteredVariantStats[variant].interestedUsers / unfilteredVariantStats[variant].visits * 100).toFixed(2);
      }
    });

    // Calculate filtered totals by summing variant stats
    const filteredTotals = {
      sessions: filteredVariantStats.A.visits + filteredVariantStats.B.visits,
      clicks: filteredVariantStats.A.clicks + filteredVariantStats.B.clicks,
      demoClicks: filteredVariantStats.A.demoClicks + filteredVariantStats.B.demoClicks,
      starterClicks: filteredVariantStats.A.starterClicks + filteredVariantStats.B.starterClicks,
      proClicks: filteredVariantStats.A.proClicks + filteredVariantStats.B.proClicks,
      enterpriseClicks: filteredVariantStats.A.enterpriseClicks + filteredVariantStats.B.enterpriseClicks
    };

    // Calculate unfiltered totals by summing variant stats
    const unfilteredTotals = {
      sessions: unfilteredVariantStats.A.visits + unfilteredVariantStats.B.visits,
      clicks: unfilteredVariantStats.A.clicks + unfilteredVariantStats.B.clicks,
      demoClicks: unfilteredVariantStats.A.demoClicks + unfilteredVariantStats.B.demoClicks,
      starterClicks: unfilteredVariantStats.A.starterClicks + unfilteredVariantStats.B.starterClicks,
      proClicks: unfilteredVariantStats.A.proClicks + unfilteredVariantStats.B.proClicks,
      enterpriseClicks: unfilteredVariantStats.A.enterpriseClicks + unfilteredVariantStats.B.enterpriseClicks
    };

    log.analytics("============ A/B TESTING ANALYTICS ============");
    log.analytics("OVERALL:");
    log.analytics("  Raw clicks: " + clicks.length);
    log.analytics("  Clicks: " + deduplicatedClicks.length);
    log.analytics("  Duplicate clicks excluded: " + (clicks.length - deduplicatedClicks.length));
    log.analytics("  Cross-variant sessions: " + crossVariantUsers.length);
    log.analytics("  Contamination rate: " + (crossVariantUsers.length / uniqueSessions.length * 100).toFixed(1) + "%");
    log.analytics("");
    
    log.analytics("FILTERED A/B TEST (excluding cross-variant users):");
    log.analytics("  Sessions: " + filteredTotals.sessions);
    log.analytics("  Clicks: " + filteredTotals.clicks);
    log.analytics("VARIANT A:");
    log.analytics("  Visits: " + filteredVariantStats.A.visits);
    log.analytics("  Interested users: " + filteredVariantStats.A.interestedUsers);
    log.analytics("  Conversion rate: " + filteredVariantStats.A.conversionRate + "%");
    log.analytics("VARIANT B:");
    log.analytics("  Visits: " + filteredVariantStats.B.visits);
    log.analytics("  Interested users: " + filteredVariantStats.B.interestedUsers);
    log.analytics("  Conversion rate: " + filteredVariantStats.B.conversionRate + "%");
    log.analytics("");
    
    log.analytics("UNFILTERED (including all users):");
    log.analytics("  Sessions: " + unfilteredTotals.sessions);
    log.analytics("  Clicks: " + unfilteredTotals.clicks);
    log.analytics("");

    const analytics = {
      overall: {
        rawClicks: clicks.length,
        duplicatesExcluded: clicks.length - deduplicatedClicks.length,
        crossVariantSessions: crossVariantUsers.length,
        contaminationRate: uniqueSessions.length > 0 ? 
          (crossVariantUsers.length / uniqueSessions.length * 100).toFixed(1) : 0,
        dataQuality: {
          isClean: crossVariantUsers.length === 0,
          contaminationLevel: crossVariantUsers.length === 0 ? 'None' : 
                            crossVariantUsers.length / uniqueSessions.length < 0.05 ? 'Low' : 
                            crossVariantUsers.length / uniqueSessions.length < 0.15 ? 'Medium' : 'High'
        }
      },
      filtered: {
        sessions: filteredTotals.sessions,
        clicks: filteredTotals.clicks,
        demoClicks: filteredTotals.demoClicks,
        starterClicks: filteredTotals.starterClicks,
        proClicks: filteredTotals.proClicks,
        enterpriseClicks: filteredTotals.enterpriseClicks,
        variantStats: filteredVariantStats
      },
      unfiltered: {
        sessions: unfilteredTotals.sessions,
        clicks: unfilteredTotals.clicks,
        demoClicks: unfilteredTotals.demoClicks,
        starterClicks: unfilteredTotals.starterClicks,
        proClicks: unfilteredTotals.proClicks,
        enterpriseClicks: unfilteredTotals.enterpriseClicks,
        variantStats: unfilteredVariantStats
      }
    };

    res.json({ analytics });

  } catch (error) {
    log.error(`Stats error: ${error.message}`);
    res.status(500).json({ error: error.message });
   }
});

app.get('/clicks', async (_, res) => {
  try {
    // Get all raw clicks data
    const { data: clicks, error: clickError } = await supabase
      .from('button_clicks')
      .select('*')
      .order('clicked_at', { ascending: false });

    if (clickError) throw clickError;

    log.info(`Returning ${clicks.length} click records`);
    
    res.json({ clicks, totalRecords: clicks.length });

  } catch (error) {
    log.error(`Clicks error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

app.get('/cross-variant-sessions', async (_, res) => {
  try {
    // Get all visits to identify cross-variant users
    const { data: visits, error: visitError } = await supabase
      .from('sessions')
      .select('session_id, variant, start_time')
      .order('start_time', { ascending: false });

    if (visitError) throw visitError;

    // Group by session_id to find cross-variant users
    const sessionVariantMap = {};
    visits.forEach(visit => {
      const sessionId = visit.session_id;
      if (!sessionVariantMap[sessionId]) {
        sessionVariantMap[sessionId] = [];
      }
      sessionVariantMap[sessionId].push(visit);
    });

    // Filter for sessions that tested multiple variants
    const crossVariantSessions = Object.keys(sessionVariantMap)
      .filter(sessionId => {
        const variants = new Set(sessionVariantMap[sessionId].map(v => v.variant || 'A'));
        return variants.size > 1;
      })
      .map(sessionId => ({
        session_id: sessionId,
        visits: sessionVariantMap[sessionId],
        variants_tested: [...new Set(sessionVariantMap[sessionId].map(v => v.variant || 'A'))]
      }));

    log.info(`Found ${crossVariantSessions.length} cross-variant sessions`);
    
    res.json({ 
      crossVariantSessions, 
      totalSessions: crossVariantSessions.length,
      summary: {
        totalUniqueSessions: Object.keys(sessionVariantMap).length,
        crossVariantCount: crossVariantSessions.length,
        contaminationRate: (crossVariantSessions.length / Object.keys(sessionVariantMap).length * 100).toFixed(1) + '%'
      }
    });

  } catch (error) {
    log.error(`Cross-variant sessions error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});
