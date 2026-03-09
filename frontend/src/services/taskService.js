import apiClient from './apiClient';

export const taskService = {
    submitTask: async (data) => {
        // Construct bundled description for ReviewEngine markers
        let bundledDescription = data.task_description;
        if (data.github_repo_link) {
            bundledDescription += `\n\n--- GitHub Repository Metrics ---\n{ "url": "${data.github_repo_link}" }`;
        }

        const formData = new FormData();
        formData.append('task_title', data.task_title);
        formData.append('task_description', bundledDescription);
        formData.append('submitted_by', data.submitted_by || 'Developer');
        formData.append('github_repo_link', data.github_repo_link || '');

        if (data.previous_task_id) {
            formData.append('previous_task_id', data.previous_task_id);
        }

        if (data.pdf_file) {
            formData.append('pdf_file', data.pdf_file);
        }

        const response = await apiClient.post('/lifecycle/submit', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            }
        });
        return response.data;
    },
    getReview: async (taskId) => {
        const response = await apiClient.get(`/lifecycle/review/${taskId}`);
        return response.data;
    },
    getNextTask: async (taskId) => {
        const response = await apiClient.get(`/lifecycle/next/${taskId}`);
        return response.data;
    },
    getTaskHistory: async () => {
        const response = await apiClient.get('/lifecycle/history');
        return response.data;
    },
    getTtsStream: (text, lang = 'en', tone = 'neutral') => {
        const params = new URLSearchParams({ text, lang, tone });
        // Use the relative path if proxy is configured, or absolute if needed
        const baseUrl = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1';
        return `${baseUrl}/tts/speak?${params.toString()}`;
    },
};
