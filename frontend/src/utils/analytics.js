import {v4 as uuidv4} from 'uuid';
import Cookies from 'js-cookie';
import axios from 'axios';

const BACKEND = 'http://localhost:4000';

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
};

export const trackClick = (type, plan = null) =>{

    const planType = plan ? plan.name :  '';

    axios.post(`${BACKEND}/track-click`, {type, plan})
    .then(() => console.log(`Button Clicked: ${type} ${planType}`))
    .catch(console.error);
}

