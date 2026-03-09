import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const LIFECYCLE_API = `${BACKEND_URL.replace('/api/v1/task', '')}/api/v1/lifecycle`;

const api = axios.create({
    baseURL: LIFECYCLE_API,
    timeout: 30000,
});

export const lifecycleAPI = {
    // Submit task for review and get next task assignment
    submitTask: async (taskData) => {
        const response = await api.post('/submit', {
            task_title: taskData.title,
            task_description: taskData.description,
            submitted_by: taskData.submittedBy,
            previous_task_id: taskData.previousTaskId || null
        });
        return response.data;
    },

    // Get task history
    getHistory: async () => {
        const response = await api.get('/history');
        return response.data;
    },

    // Get review details by submission ID
    getReview: async (submissionId) => {
        const response = await api.get(`/review/${submissionId}`);
        return response.data;
    },

    // Get next task details by submission ID
    getNextTask: async (submissionId) => {
        const response = await api.get(`/next/${submissionId}`);
        return response.data;
    }
};

export const checkBackendHealth = async () => {
    try {
        const healthUrl = `${BACKEND_URL.replace('/api/v1/task', '')}/health`;
        const response = await axios.get(healthUrl, { timeout: 5000 });
        return response.status === 200;
    } catch {
        return false;
    }
};