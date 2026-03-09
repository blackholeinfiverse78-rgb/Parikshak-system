import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Zap } from 'lucide-react';
import { taskService } from '../services/taskService';
import NextTaskCard from '../components/NextTaskCard';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const NextTask = () => {
    const { taskId } = useParams();

    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['nextTask', taskId],
        queryFn: () => taskService.getNextTask(taskId),
        enabled: !!taskId,
    });

    if (isLoading) return <LoadingState message="Generating your next career-defining mission..." />;
    if (isError) return <ErrorState message={error.message} onRetry={refetch} />;

    return (
        <div className="space-y-10">
            <header className="flex flex-col items-center text-center">
                <div className="relative mb-6">
                    <div className="absolute inset-0 bg-blue-500 blur-2xl opacity-20 animate-pulse rounded-full" />
                    <div className="relative p-5 bg-blue-600 text-white rounded-3xl shadow-xl shadow-blue-500/20">
                        <Zap size={40} fill="currentColor" />
                    </div>
                </div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">
                    Task <span className="text-blue-600">Evolution</span>
                </h1>
            </header>

            <NextTaskCard task={data} />
        </div>
    );
};

export default NextTask;
