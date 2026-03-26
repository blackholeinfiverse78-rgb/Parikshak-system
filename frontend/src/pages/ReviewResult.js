import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, XCircle, AlertTriangle, FileText, Target, TrendingUp, BarChart3, Settings, Github } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import StatusBadge from '../components/StatusBadge';

const ReviewResult = () => {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const [reviewData, setReviewData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchReviewData();
    }, [taskId]);

    const fetchReviewData = async () => {
        try {
            const { taskService } = await import('../services/taskService');
            const data = await taskService.getReview(taskId);
            setReviewData(data);
        } catch (err) {
            const status = err.response?.status;
            setError(`Failed to load review: ${status || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingState message="Loading review results..." />;
    
    if (error) {
        return (
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="card text-center py-12">
                    <XCircle className="mx-auto text-red-500 mb-4" size={48} />
                    <h3 className="text-xl font-bold mb-2">Error Loading Review</h3>
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

    if (!reviewData) {
        return (
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="card text-center py-12">
                    <AlertTriangle className="mx-auto text-yellow-500 mb-4" size={48} />
                    <h3 className="text-xl font-bold mb-2">Review Not Found</h3>
                    <p className="text-slate-600 dark:text-slate-400">Task ID: {taskId}</p>
                </div>
            </div>
        );
    }

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-green-600';
        if (score >= 50) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getScoreBgColor = (score) => {
        if (score >= 80) return 'bg-green-100 dark:bg-green-900/30';
        if (score >= 50) return 'bg-yellow-100 dark:bg-yellow-900/30';
        return 'bg-red-100 dark:bg-red-900/30';
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button 
                    onClick={() => navigate('/')}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                        Review Results
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400">
                        Task ID: {taskId}
                    </p>
                </div>
            </div>

            {/* Main Score Card */}
            <div className={`card ${getScoreBgColor(reviewData.score)} border-l-4 ${reviewData.score >= 80 ? 'border-l-green-500' : reviewData.score >= 50 ? 'border-l-yellow-500' : 'border-l-red-500'}`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <div className="text-center">
                            <div className={`text-4xl font-black ${getScoreColor(reviewData.score)}`}>
                                {reviewData.score}
                            </div>
                            <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
                                Overall Score
                            </div>
                        </div>
                        <div className="h-16 w-px bg-slate-300 dark:bg-slate-600"></div>
                        <div>
                            <StatusBadge status={reviewData.status} />
                            <div className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                                Readiness: {reviewData.readiness_percent}%
                            </div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-slate-500 dark:text-slate-400">
                            Reviewed on
                        </div>
                        <div className="font-medium">
                            {new Date(reviewData.reviewed_at).toLocaleDateString()}
                        </div>
                    </div>
                </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid md:grid-cols-3 gap-6">
                <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                            <FileText className="text-blue-600 dark:text-blue-400" size={20} />
                        </div>
                        <h3 className="font-bold">Title Analysis</h3>
                    </div>
                    <div className="text-2xl font-bold mb-1">{reviewData.title_score}/20</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                        Technical keywords, clarity, alignment
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                            <BarChart3 className="text-green-600 dark:text-green-400" size={20} />
                        </div>
                        <h3 className="font-bold">Description Analysis</h3>
                    </div>
                    <div className="text-2xl font-bold mb-1">{reviewData.description_score}/40</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                        Content depth, structure, completeness
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                            <Github className="text-purple-600 dark:text-purple-400" size={20} />
                        </div>
                        <h3 className="font-bold">Repository Analysis</h3>
                    </div>
                    <div className="text-2xl font-bold mb-1">{reviewData.repository_score}/40</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                        Code quality, architecture, documentation
                    </div>
                </div>
            </div>

            {/* Detailed Analysis */}
            <div className="grid lg:grid-cols-2 gap-8">
                {/* Failure Reasons & Improvements */}
                <div className="space-y-6">
                    {reviewData.failure_reasons && reviewData.failure_reasons.length > 0 && (
                        <div className="card">
                            <h3 className="font-bold text-red-600 dark:text-red-400 mb-4 flex items-center gap-2">
                                <XCircle size={20} />
                                Issues Found
                            </h3>
                            <ul className="space-y-2">
                                {reviewData.failure_reasons.map((reason, index) => (
                                    <li key={index} className="flex items-start gap-2 text-sm">
                                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                                        <span>{reason}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {reviewData.improvement_hints && reviewData.improvement_hints.length > 0 && (
                        <div className="card">
                            <h3 className="font-bold text-blue-600 dark:text-blue-400 mb-4 flex items-center gap-2">
                                <Target size={20} />
                                Improvement Suggestions
                            </h3>
                            <ul className="space-y-2">
                                {reviewData.improvement_hints.map((hint, index) => (
                                    <li key={index} className="flex items-start gap-2 text-sm">
                                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                        <span>{hint}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Technical Metrics */}
                <div className="space-y-6">
                    <div className="card">
                        <h3 className="font-bold mb-4 flex items-center gap-2">
                            <TrendingUp size={20} />
                            Technical Metrics
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-sm">Feature Coverage</span>
                                <span className="font-medium">{Math.round(reviewData.feature_coverage * 100)}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-sm">Architecture Score</span>
                                <span className="font-medium">{Math.round(reviewData.architecture_score)}/100</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-sm">Code Quality</span>
                                <span className="font-medium">{Math.round(reviewData.code_quality_score)}/100</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-sm">Documentation</span>
                                <span className="font-medium">{Math.round(reviewData.documentation_score)}/100</span>
                            </div>
                        </div>
                    </div>

                    {reviewData.missing_features && reviewData.missing_features.length > 0 && (
                        <div className="card">
                            <h3 className="font-bold text-orange-600 dark:text-orange-400 mb-4">
                                Missing Features
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {reviewData.missing_features.map((feature, index) => (
                                    <span key={index} className="px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400 rounded text-xs">
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Registry Validation */}
            {reviewData.registry_validation && (
                <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                    <h3 className="font-bold text-blue-800 dark:text-blue-400 mb-4 flex items-center gap-2">
                        <Settings size={20} />
                        Registry Validation
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">Module ID</div>
                            <div className="font-mono text-sm">{reviewData.registry_validation.module_id}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">Schema Version</div>
                            <div className="font-mono text-sm">{reviewData.registry_validation.schema_version}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">Validation Status</div>
                            <div className={`text-sm font-medium ${
                                reviewData.registry_validation.validation_passed 
                                    ? 'text-green-600 dark:text-green-400' 
                                    : 'text-red-600 dark:text-red-400'
                            }`}>
                                {reviewData.registry_validation.validation_passed ? '✅ Passed' : '❌ Failed'}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Evaluation Summary */}
            {reviewData.evaluation_summary && (
                <div className="card">
                    <h3 className="font-bold mb-4">Evaluation Summary</h3>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                        {reviewData.evaluation_summary}
                    </p>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
                <button 
                    onClick={() => navigate(`/next/${taskId}`)}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                    <Target size={20} />
                    View Next Task
                </button>
                <button 
                    onClick={() => navigate('/history')}
                    className="px-6 py-3 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg font-medium hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
                >
                    View All History
                </button>
            </div>
        </div>
    );
};

export default ReviewResult;