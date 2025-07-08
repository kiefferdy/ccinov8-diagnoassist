require('dotenv').config();

console.log('SUPABASE_URL:', process.env.SUPABASE_URL);
console.log('SUPABASE_SERVICE_ROLE_KEY:', process.env.SUPABASE_SERVICE_ROLE_KEY);


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
//   const sessionId = req.headers['cookie']?.match(/session_id=([^;]+)/)?.[1];

//   console.log("HELLOOOO" + sessionId);
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

  
  console.log(`[button click] ${type} ${plan?.name || ''}`);
  res.sendStatus(200);
});