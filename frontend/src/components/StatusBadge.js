import React from 'react';

const StatusBadge = ({ status }) => {
    const getStyles = () => {
        switch (status?.toLowerCase()) {
            case 'assigned':
                return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800';
            case 'submitted':
                return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800';
            case 'reviewed':
                return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';
            case 'next_assigned':
                return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800';
            default:
                return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700';
        }
    };

    return (
        <span className={`px-2.5 py-1 text-xs font-bold uppercase tracking-wider rounded-full border ${getStyles()}`}>
            {status || 'Unknown'}
        </span>
    );
};

export default StatusBadge;
