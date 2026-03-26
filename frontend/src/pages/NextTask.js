import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Target, CheckCircle, AlertTriangle, Calendar, Zap, ArrowRight } from 'lucide-react';
import LoadingState from '../components/LoadingState';

const NextTask = () => {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const [nextTaskData, setNextTaskData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchNextTaskData();
    }, [taskId]);

    const fetchNextTaskData = async () => {
        try {
            const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
            const response = await fetch(`${backendUrl}/api/v1/lifecycle/next/${taskId}`);
            
            if (response.ok) {
                const data = await response.json();
                setNextTaskData(data);
            } else {
                setError(`Failed to load next task: ${response.status}`);
            }
        } catch (err) {
            setError(`Network error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingState message="Loading next task assignment..." />;
    
    if (error) {
        return (
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="card text-center py-12">
                    <AlertTriangle className="mx-auto text-red-500 mb-4" size={48} />
                    <h3 className="text-xl font-bold mb-2">Error Loading Next Task</h3>
                    <p className="text-slate-600 dark:text-slate-400 mb-4">{error}</p>
                    <button 
                        onClick={() => navigate('/')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    if (!nextTaskData) {
        return (
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="card text-center py-12">
                    <AlertTriangle className="mx-auto text-yellow-500 mb-4" size={48} />
                    <h3 className="text-xl font-bold mb-2">Next Task Not Found</h3>
                    <p className="text-slate-600 dark:text-slate-400">Based on Task ID: {taskId}</p>
                </div>
            </div>
        );
    }

    const getTaskTypeColor = (taskType) => {
        switch (taskType?.toLowerCase()) {
            case 'advancement':
                return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
            case 'reinforcement':
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
            case 'correction':
                return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
            default:
                return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400';
        }
    };

    const getDifficultyColor = (difficulty) => {
        switch (difficulty?.toLowerCase()) {
            case 'beginner':
                return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
            case 'intermediate':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
            case 'advanced':
                return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
            default:
                return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400';
        }
    };

    const getTaskTypeIcon = (taskType) => {
        switch (taskType?.toLowerCase()) {
            case 'advancement':
                return <CheckCircle className="text-green-600" size={24} />;
            case 'reinforcement':
                return <Target className="text-blue-600" size={24} />;
            case 'correction':
                return <AlertTriangle className="text-orange-600" size={24} />;
            default:
                return <Zap className="text-slate-600" size={24} />;
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button 
                    onClick={() => navigate(`/review/${taskId}`)}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                        Next Task Assignment
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400">
                        Based on review: {taskId}
                    </p>
                </div>
            </div>

            {/* Main Task Card */}
            <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
                <div className="flex items-start gap-6">
                    <div className="p-4 bg-blue-600 rounded-2xl text-white">
                        {getTaskTypeIcon(nextTaskData.task_type)}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTaskTypeColor(nextTaskData.task_type)}`}>
                                {nextTaskData.task_type}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(nextTaskData.difficulty)}`}>
                                {nextTaskData.difficulty}
                            </span>
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                            {nextTaskData.title}
                        </h2>
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed mb-4">
                            {nextTaskData.objective}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                            <div className="flex items-center gap-1">
                                <Target size={16} />
                                <span>Focus: {nextTaskData.focus_area}</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <Calendar size={16} />
                                <span>Assigned: {new Date(nextTaskData.assigned_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Task Details */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                        <Target className="text-blue-600" size={20} />
                        Task Details
                    </h3>
                    <div className="space-y-3">
                        <div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Task ID</div>
                            <div className="font-mono text-sm">{nextTaskData.next_task_id}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Task Type</div>
                            <div className="capitalize">{nextTaskData.task_type}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Difficulty Level</div>
                            <div className="capitalize">{nextTaskData.difficulty}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Focus Area</div>
                            <div className="capitalize">{nextTaskData.focus_area?.replace('_', ' ')}</div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                        <AlertTriangle className="text-orange-600" size={20} />
                        Assignment Reason
                    </h3>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                        {nextTaskData.reason}
                    </p>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
                <button 
                    onClick={() => navigate('/submit')}
                    className="flex-1 px-6 py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                    <ArrowRight size={20} />
                    Start New Task Submission
                </button>
                <button 
                    onClick={() => navigate('/history')}
                    className="px-6 py-4 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg font-medium hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
                >
                    View Task History
                </button>
            </div>

            {/* Task Flow Indicator */}
            <div className="card bg-slate-50 dark:bg-slate-800/50">
                <h3 className="font-bold mb-4">Task Assignment Flow</h3>
                <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">1</div>
                        <span>Task Submitted</span>
                    </div>
                    <ArrowRight className="text-slate-400" size={16} />
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">2</div>
                        <span>Review Complete</span>
                    </div>
                    <ArrowRight className="text-slate-400" size={16} />
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">3</div>
                        <span>Next Task Assigned</span>
                    </div>
                    <ArrowRight className="text-slate-400" size={16} />
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-slate-300 dark:bg-slate-600 text-slate-600 dark:text-slate-400 rounded-full flex items-center justify-center font-bold">4</div>
                        <span>Ready for Submission</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NextTask;