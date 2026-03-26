import axios from 'axios';

const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_BASE 
        || 'https://task-review-agent-full-product-evolution-wyki.onrender.com/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
