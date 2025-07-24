require('dotenv').config();

const express = require('express');
const cors = require('cors');
const app = express();
const supabase = require('./supabaseClient');
const PORT = process.env.PORT || 4000;

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
  console.log(`Server is running on port ${PORT}`);
});

app.post('/track-visit', async (req, res) => {
    const {sessionId, timestamp, variant} = req.body;

    const {data, error} = await supabase.from('sessions').upsert({
        session_id: sessionId,
        start_time: timestamp,
        variant: variant
    }, {onConflict: 'session_id'});
    console.log(`[visit] ${sessionId} at ${timestamp} (variant: ${variant || 'unknown'})`);

    if (error) {
        console.error('Supabase error on track-visit:', error.message);
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
    console.error('Supabase error on track-click:', error.message);
    return res.status(500).json({ error: error.message });
  }

  console.log(`[button click] ${type} ${plan?.name || ''} (variant: ${variant || 'unknown'})`);
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

    // Calculate overall analytics
    const uniqueSessions = [...new Set(visits.map(v => v.session_id))];
    
    // Deduplicate clicks by session_id + label combination
    // This ensures each user is only counted once per action type (subscribe/demo)
    // Prevents multiple clicks from same user inflating conversion metrics
    const uniqueClicks = new Map();
    clicks.forEach(click => {
      const key = `${click.session_id}_${click.label}`;
      if (!uniqueClicks.has(key)) {
        uniqueClicks.set(key, click);
      }
    });
    const deduplicatedClicks = Array.from(uniqueClicks.values());

    let totalSub = 0, totalDemo = 0, totalStart = 0, totalPro = 0, totalEnterprise = 0;

    // Calculate variant-specific analytics
    const variantStats = { A: {}, B: {} };

    // Initialize variant stats
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
    });

    // Count visits by variant
    visits.forEach(visit => {
      const variant = visit.variant || 'A'; // Default to A for legacy data
      if (variantStats[variant]) {
        variantStats[variant].visits++;
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

    console.log("============ A/B TESTING ANALYTICS ============");
    console.log("OVERALL:");
    console.log("  Total visits: " + uniqueSessions.length);
    console.log("  Raw clicks: " + clicks.length);
    console.log("  Unique clicks (deduplicated): " + deduplicatedClicks.length);
    console.log("  Duplicate clicks filtered: " + (clicks.length - deduplicatedClicks.length));
    console.log("  Unique subscribe clicks: " + totalSub);
    console.log("  Unique demo clicks: " + totalDemo);
    console.log();
    
    console.log("VARIANT A:");
    console.log("  Visits: " + variantStats.A.visits);
    console.log("  Unique subscribe clicks: " + variantStats.A.subscribeClicks);
    console.log("  Conversion rate: " + variantStats.A.conversionRate + "%");
    console.log();
    
    console.log("VARIANT B:");
    console.log("  Visits: " + variantStats.B.visits);
    console.log("  Unique subscribe clicks: " + variantStats.B.subscribeClicks);
    console.log("  Conversion rate: " + variantStats.B.conversionRate + "%");
    console.log();

    const analytics = {
      totalRawClicks: clicks.length,
      totalUniqueClicks: deduplicatedClicks.length,
      duplicatesFiltered: clicks.length - deduplicatedClicks.length,
      totalSubscribe: totalSub,
      starterClicks: totalStart,
      proClicks: totalPro,
      enterpriseClicks: totalEnterprise,
      totalDemo: totalDemo,
      totalVisits: uniqueSessions.length,
      conversionRate: uniqueSessions.length > 0 ? (totalSub / uniqueSessions.length * 100).toFixed(2) : 0,
      variantStats: variantStats
    };

    res.json({ clicks, analytics });

  } catch (error) {
    console.error('Stats error:', error.message);
    res.status(500).json({ error: error.message });
   }
});
