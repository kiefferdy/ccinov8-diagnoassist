import {v4 as uuidv4} from 'uuid';
import Cookies from 'js-cookie';
import axios from 'axios';

const BACKEND = import.meta.env.VITE_BACKEND_LANDING_URL || 'http://localhost:4000';

export const trackVisit = async () => {
    let sessionId = Cookies.get('session_id');

    if(!sessionId) { // first-time visits or Expired session id
        sessionId = uuidv4();
        Cookies.set('session_id', sessionId, {expires: 1});
    }

    await axios.post(`${BACKEND}/track-visit`, {
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
    })
    .then(() => console.log('Visit tracked'))
    .catch(console.error);

    await fetchStats();


};

export const trackClick = async (type, plan = null) => {
    let sessionId = Cookies.get('session_id');

    const planType = plan ? plan.name :  '';

    await axios.post(`${BACKEND}/track-click`, {type, plan, sessionId})
    .then(() => console.log(`Button Clicked: ${type} ${planType}`))
    .catch(console.error);

    await fetchStats();
}

export async function fetchStats() {
  const { data } = await axios.get(`${BACKEND}/stats`);
  const { analytics } = data;
  console.table(analytics);
}

