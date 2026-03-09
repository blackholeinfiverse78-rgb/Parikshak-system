import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ClipboardCheck } from 'lucide-react';
import { taskService } from '../services/taskService';
import ReviewResultCard from '../components/ReviewResultCard';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const ReviewResult = () => {
    const { taskId } = useParams();

    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['review', taskId],
        queryFn: () => taskService.getReview(taskId),
        enabled: !!taskId,
    });

    if (isLoading) return <LoadingState message="Wait while our AI analyzes your submission..." />;
    if (isError) return <ErrorState message={error.message} onRetry={refetch} />;

    return (
        <div className="max-w-5xl mx-auto space-y-10 animate-in fade-in duration-500">
            <header className="flex flex-col items-center text-center space-y-4">
                <div className="p-4 bg-emerald-500/10 text-emerald-600 rounded-3xl">
                    <ClipboardCheck size={48} />
                </div>
                <div>
                    <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
                        Review <span className="text-emerald-500">Result</span>
                    </h1>
                    <p className="text-slate-500 font-medium max-w-lg mt-2">
                        Task ID: <span className="font-mono text-xs">{taskId}</span>
                    </p>
                </div>
            </header>

            <ReviewResultCard review={data} taskId={taskId} />
        </div>
    );
};

export default ReviewResult;
