import axios from 'axios';

const BACKEND = 'http://localhost:4000';

export const trackVisit = () => {
    axios.post(`${BACKEND}/track-visit`)
    .then(() => console.log('Visit tracked'))
    .catch(console.error);
}

export const trackClick = (type, plan = null) =>{

    const planType = plan ? plan.name :  '';

    axios.post(`${BACKEND}/track-click`, {type, plan})
    .then(() => console.log(`Button Clicked: ${type} ${planType}`))
    .catch(console.error);
}

