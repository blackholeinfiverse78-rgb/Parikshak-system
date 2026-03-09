import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, History, Activity, TrendingUp } from 'lucide-react';
import { taskService } from '../services/taskService';
import LoadingState from '../components/LoadingState';
import StatusBadge from '../components/StatusBadge';
import Button from '../components/ui/Button';

const Dashboard = () => {
    const navigate = useNavigate();
    const { data: history, isLoading } = useQuery({
        queryKey: ['taskHistory'],
        queryFn: taskService.getTaskHistory,
    });

    if (isLoading) return <LoadingState message="Syncing workspace data..." />;

    const recentTasks = history?.slice(0, 3) || [];
    const averageScore = history?.length > 0
        ? Math.round(history.reduce((acc, task) => acc + (task.review_score || 0), 0) / history.length)
        : 0;

    return (
        <div className="space-y-10 animate-in fade-in duration-500">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black tracking-tight text-slate-900 dark:text-white">
                        Workspace <span className="text-blue-600">Overview</span>
                    </h1>
                    <p className="text-slate-500 font-medium">Manage your autonomous task lifecycle and track progress.</p>
                </div>
                <div className="flex items-center gap-3">
                    <Button onClick={() => navigate('/history')} variant="secondary">
                        <History size={18} />
                        History
                    </Button>
                    <Button onClick={() => navigate('/submit')}>
                        <Plus size={18} />
                        New Task
                    </Button>
                </div>
            </header>

            <section className="grid md:grid-cols-3 gap-6">
                <div className="card border-b-4 border-b-blue-500 flex items-center gap-4">
                    <div className="p-4 bg-blue-500/10 rounded-2xl text-blue-600">
                        <Activity size={32} />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Total Tasks</div>
                        <div className="text-3xl font-black">{history?.length || 0}</div>
                    </div>
                </div>
                <div className="card border-b-4 border-b-emerald-500 flex items-center gap-4">
                    <div className="p-4 bg-emerald-500/10 rounded-2xl text-emerald-600">
                        <TrendingUp size={32} />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Avg Score</div>
                        <div className="text-3xl font-black">{averageScore}%</div>
                    </div>
                </div>
                <div className="card border-b-4 border-b-indigo-500 flex items-center gap-4">
                    <div className="p-4 bg-indigo-500/10 rounded-2xl text-indigo-600">
                        <History size={32} />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Last Sync</div>
                        <div className="text-lg font-black uppercase text-indigo-600">Just Now</div>
                    </div>
                </div>
            </section>

            <section className="grid lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Activity className="text-blue-600" size={20} />
                            Recent Activity
                        </h2>
                        <button
                            onClick={() => navigate('/history')}
                            className="text-sm font-bold text-blue-600 hover:underline"
                        >
                            View Full History
                        </button>
                    </div>

                    <div className="space-y-3">
                        {recentTasks.length > 0 ? (
                            recentTasks.map((task) => (
                                <div
                                    key={task.id}
                                    onClick={() => navigate(`/review/${task.id}`)}
                                    className="card !p-4 flex items-center justify-between hover:scale-[1.01] transition-all cursor-pointer group"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center font-bold text-blue-600">
                                            {task.review_score || '—'}
                                        </div>
                                        <div>
                                            <div className="font-bold group-hover:text-blue-600 transition-colors uppercase tracking-tight">
                                                {task.task_title}
                                            </div>
                                            <div className="text-xs text-slate-500">{new Date(task.submission_date).toLocaleDateString()}</div>
                                        </div>
                                    </div>
                                    <StatusBadge status={task.status} />
                                </div>
                            ))
                        ) : (
                            <div className="card py-10 text-center border-dashed border-2">
                                <p className="text-slate-500 font-medium">No tasks found. Start by submitting your first task.</p>
                                <Button onClick={() => navigate('/submit')} variant="ghost" className="mt-4">
                                    Go to Submission
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 border-none text-white relative overflow-hidden group shadow-xl shadow-blue-500/20 p-6">
                    <div className="relative z-10 space-y-6">
                        <div className="space-y-2">
                            <h3 className="text-2xl font-black text-white">Ready to level up?</h3>
                            <p className="text-blue-100 text-sm leading-relaxed">
                                Submit your project code for an autonomous AI review. Get instant feedback and your next skill-appropriate task.
                            </p>
                        </div>
                        <Button onClick={() => navigate('/submit')} className="w-full bg-white text-blue-700 hover:bg-blue-50 font-bold shadow-none border-none">
                            Start New Evaluation
                        </Button>
                    </div>
                    {/* Decorative elements */}
                    <div className="absolute top-[-20%] right-[-10%] w-64 h-64 bg-white/10 rounded-full blur-3xl group-hover:bg-white/20 transition-colors" />
                    <div className="absolute bottom-[-10%] left-[-10%] w-32 h-32 bg-indigo-400/20 rounded-full blur-2xl" />
                </div>
            </section>
        </div>
    );
};

export default Dashboard;
