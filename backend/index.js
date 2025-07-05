const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

app.post('/track-visit', (req, res) => {
    console.log(`[visit] at ${new Date().toISOString()}`);
    res.sendStatus(200);
})

app.post('/track-click', (req, res) => {
    const {type, plan} = req.body;
    if(plan)
        console.log(`[button click] ${type} ${plan.name}`);
    else
        console.log(`[button click] ${type}`);    

    res.sendStatus(200);
})