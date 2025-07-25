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

    const {data, error} = await supabase.from('sessions').upsert({
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

app.get('/stats', async (req, res) => {
  try {
    // Get all clicks with variant data
    const { data: clicks, error: clickError } = await supabase
      .from('button_clicks')
      .select('label, plan_type, variant');

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
    const pureUniqueSessions = [...new Set(pureVisits.map(v => v.session_id))];
    
    // Deduplicate clicks by session_id + label + variant combination
    // This ensures each user is only counted once per action type per variant
    // Allows users to test both variants and have both conversions counted
    const uniqueClicks = new Map();
    clicks.forEach(click => {
      const key = `${click.session_id}_${click.label}_${click.variant || 'A'}`;
      if (!uniqueClicks.has(key)) {
        uniqueClicks.set(key, click);
      }
    });
    const deduplicatedClicks = Array.from(uniqueClicks.values());

    let totalSub = 0, totalDemo = 0, totalStart = 0, totalPro = 0, totalEnterprise = 0;

    // Calculate variant-specific analytics (using pure visits for clean A/B testing)
    const variantStats = { A: {}, B: {} };
    const overallVariantStats = { A: {}, B: {} };

    // Initialize variant stats for both pure and overall
    ['A', 'B'].forEach(variant => {
      variantStats[variant] = {
        visits: 0,
        uniqueClicks: 0,
        subscribeClicks: 0,
        demoClicks: 0,
        starterClicks: 0,
        proClicks: 0,
        enterpriseClicks: 0,
        conversionRate: 0
      };
      overallVariantStats[variant] = { ...variantStats[variant] };
    });

    // Count pure visits by variant (for clean A/B testing)
    pureVisits.forEach(visit => {
      const variant = visit.variant || 'A'; // Default to A for legacy data
      if (variantStats[variant]) {
        variantStats[variant].visits++;
      }
    });

    // Count overall visits by variant (including cross-variant users)
    visits.forEach(visit => {
      const variant = visit.variant || 'A'; // Default to A for legacy data
      if (overallVariantStats[variant]) {
        overallVariantStats[variant].visits++;
      }
    });

    // Count deduplicated clicks by variant
    deduplicatedClicks.forEach(click => {
      const variant = click.variant || 'A'; // Default to A for legacy data
      
      if (variantStats[variant]) {
        variantStats[variant].uniqueClicks++;
        
        if (click.label === "subscribe") {
          variantStats[variant].subscribeClicks++;
          totalSub++;
          
          switch(click.plan_type) {
            case "Starter":
              variantStats[variant].starterClicks++;
              totalStart++;
              break;
            case "Professional":
              variantStats[variant].proClicks++;
              totalPro++;
              break;
            case "Enterprise":
              variantStats[variant].enterpriseClicks++;
              totalEnterprise++;
              break;
          }
        } else {
          variantStats[variant].demoClicks++;
          totalDemo++;
        }
      }
    });

    // Calculate conversion rates
    ['A', 'B'].forEach(variant => {
      if (variantStats[variant].visits > 0) {
        variantStats[variant].conversionRate = 
          (variantStats[variant].subscribeClicks / variantStats[variant].visits * 100).toFixed(2);
      }
    });

    log.analytics("============ A/B TESTING ANALYTICS ============");
    log.analytics("OVERALL:");
    log.analytics("  Total unique sessions: " + uniqueSessions.length);
    log.analytics("  Pure sessions (single-variant): " + pureUniqueSessions.length);
    log.analytics("  Cross-variant sessions: " + crossVariantUsers.length);
    log.analytics("  Contamination rate: " + (crossVariantUsers.length / uniqueSessions.length * 100).toFixed(1) + "%");
    log.analytics("  Raw clicks: " + clicks.length);
    log.analytics("  Unique clicks (deduplicated): " + deduplicatedClicks.length);
    log.analytics("  Duplicate clicks filtered: " + (clicks.length - deduplicatedClicks.length));
    log.analytics("  Unique subscribe clicks: " + totalSub);
    log.analytics("  Unique demo clicks: " + totalDemo);
    log.analytics("");
    
    log.analytics("PURE A/B TEST (excluding cross-variant users):");
    log.analytics("VARIANT A:");
    log.analytics("  Visits: " + variantStats.A.visits);
    log.analytics("  Unique subscribe clicks: " + variantStats.A.subscribeClicks);
    log.analytics("  Conversion rate: " + variantStats.A.conversionRate + "%");
    log.analytics("");
    
    log.analytics("VARIANT B:");
    log.analytics("  Visits: " + variantStats.B.visits);
    log.analytics("  Unique subscribe clicks: " + variantStats.B.subscribeClicks);
    log.analytics("  Conversion rate: " + variantStats.B.conversionRate + "%");
    log.analytics("");

    const analytics = {
      // Overall metrics
      totalRawClicks: clicks.length,
      totalUniqueClicks: deduplicatedClicks.length,
      duplicatesFiltered: clicks.length - deduplicatedClicks.length,
      totalSubscribe: totalSub,
      starterClicks: totalStart,
      proClicks: totalPro,
      enterpriseClicks: totalEnterprise,
      totalDemo: totalDemo,
      
      // Session metrics
      totalUniqueSessions: uniqueSessions.length,
      pureUniqueSessions: pureUniqueSessions.length,
      crossVariantSessions: crossVariantUsers.length,
      contaminationRate: uniqueSessions.length > 0 ? 
        (crossVariantUsers.length / uniqueSessions.length * 100).toFixed(1) : 0,
      
      // Conversion rates
      overallConversionRate: uniqueSessions.length > 0 ? 
        (totalSub / uniqueSessions.length * 100).toFixed(2) : 0,
      pureConversionRate: pureUniqueSessions.length > 0 ? 
        (totalSub / pureUniqueSessions.length * 100).toFixed(2) : 0,
      
      // Variant stats (pure A/B testing)
      variantStats: variantStats,
      
      // Overall variant stats (including cross-variant users)
      overallVariantStats: overallVariantStats,
      
      // Quality metrics
      dataQuality: {
        isClean: crossVariantUsers.length === 0,
        contaminationLevel: crossVariantUsers.length / uniqueSessions.length < 0.05 ? 'Low' : 
                          crossVariantUsers.length / uniqueSessions.length < 0.15 ? 'Medium' : 'High'
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
