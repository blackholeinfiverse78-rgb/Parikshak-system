import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Rocket } from 'lucide-react';
import { taskService } from '../services/taskService';
import TaskSubmissionForm from '../components/TaskSubmissionForm';

const SubmitTask = () => {
    const navigate = useNavigate();

    const mutation = useMutation({
        mutationFn: taskService.submitTask,
        onSuccess: (data) => {
            // Lifecycle API returns submission_id
            const taskId = data.submission_id;
            if (taskId) {
                navigate(`/review/${taskId}`);
            }
        },
    });

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="text-center space-y-2">
                <div className="inline-flex p-3 bg-blue-600/10 text-blue-600 rounded-2xl mb-2">
                    <Rocket size={32} />
                </div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white uppercase tracking-tight">
                    Submit <span className="text-blue-600">Task</span>
                </h1>
                <p className="text-slate-500 font-medium">Fill in the details below to trigger the autonomous review engine.</p>
            </div>

            <div className="card p-8 bg-white dark:bg-slate-900 shadow-2xl shadow-blue-500/5">
                <TaskSubmissionForm
                    onSubmit={(data) => mutation.mutate(data)}
                    isLoading={mutation.isLoading}
                />
                {mutation.isError && (
                    <div className="mt-4 p-4 bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 rounded-lg text-sm font-medium border border-red-100 dark:border-red-900/30">
                        Error submitting task: {mutation.error?.response?.data?.message || mutation.error.message}
                    </div>
                )}
            </div>

            <div className="flex items-center justify-between px-6 py-4 bg-slate-100 dark:bg-slate-800/50 rounded-2xl text-xs font-bold text-slate-400 uppercase tracking-widest">
                <span>Registry-Aware Evaluation System</span>
                <span>Dynamic Scoring • Blueprint Validated</span>
            </div>
        </div>
    );
};

export default SubmitTask;
