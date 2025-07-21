require('dotenv').config();

const express = require('express');
const cors = require('cors');
const app = express();
const supabase = require('./supabaseClient');
const PORT = 4000;

app.use(cors());
app.use(express.json());



app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

app.post('/track-visit', async (req, res) => {
    const {sessionId, timestamp} = req.body;

    const {data, error} = await supabase.from('sessions').upsert({
        session_id: sessionId,
        start_time: timestamp
    }, {onConflict: 'session_id'});
    console.log(`[visit] ${sessionId} at ${timestamp}`);

    res.sendStatus(200);
})


app.post('/track-click', async (req, res) => {
  const { type, plan, sessionId } = req.body;

  const { error } = await supabase
    .from('button_clicks')
    .insert({
      session_id: sessionId,
      label: type,
      plan_type: plan?.name || null,
      clicked_at: new Date().toISOString(),
    });

  if (error) {
    console.error('Supabase error on track-click:', error.message);
    return res.status(500).json({ error: error.message });
  }

  
  // console.log(`[button click] ${type} ${plan?.name || ''}`);
  res.sendStatus(200);
});

app.get('/stats', async (req, res) => {
  try {
    // Count clicks by type and plan
    const { data: clicks, error: clickError } = await supabase
      .from('button_clicks')
      .select('label, plan_type');

    const { data: visits, error: visitError } = await supabase
      .from('sessions')
      .select('session_id');

    //console.log(visits[0]);
    const uniqueSessions = [...new Set(visits)];

    if (clickError) throw clickError;

    //ANALYTICS:
     let len = clicks.length;

    let sub = 0, pro = 0, start = 0, enterprise = 0, demo = 0;
    for(let i =0; i < len; i++){
        if(clicks[i].label == "subscribe"){
            sub++; 
            switch(clicks[i].plan_type){
                case "Starter":
                    start++;
                    break;
                case "Professional":
                    pro++;
                    break;
                case "Enterprise":
                    enterprise++;
                    break;
            };
        }else
            demo++;
    };
    
    console.log("============ ANALYTICS ============")
    console.log("Total visits: " + uniqueSessions.length);

    console.log("Total button clicks: " + len);
    console.log(">Total subscribe clicks: " + sub);
    console.log("   Starter: " + start);
    console.log("   Professional: " + pro);
    console.log("   Enterprise: " + enterprise);
    console.log(">Total demo clicks: " + demo);
    console.log();

    // inside /stats route after you finish counting
    const analytics = {
      totalClicks    : clicks.length,
      totalSubscribe : sub,
      starterClicks  : start,
      proClicks      : pro,
      enterpriseClicks: enterprise,
      totalDemo      : demo,
    };

    res.json({ clicks, analytics });

  } catch (error) {
    console.error('Stats error:', error.message);
    res.status(500).json({ error: error.message });
   }
});
