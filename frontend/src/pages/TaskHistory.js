import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { History, Search, Filter } from 'lucide-react';
import { taskService } from '../services/taskService';
import TaskHistoryTable from '../components/TaskHistoryTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const TaskHistory = () => {
    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['taskHistory'],
        queryFn: taskService.getTaskHistory,
    });

    if (isLoading) return <LoadingState message="Retrieving your journey logs..." />;
    if (isError) return <ErrorState message={error.message} onRetry={refetch} />;

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-slate-400 font-bold uppercase tracking-widest text-xs">
                        <History size={14} />
                        Archive
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                        Task <span className="text-slate-400">History</span>
                    </h1>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search tasks..."
                            className="pl-10 pr-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl outline-none focus:ring-2 focus:ring-blue-500/50 text-sm transition-all"
                        />
                    </div>
                    <button className="p-2.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-all">
                        <Filter size={20} />
                    </button>
                </div>
            </header>

            <TaskHistoryTable tasks={data} />
        </div>
    );
};

export default TaskHistory;
