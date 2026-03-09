import React from 'react';
import { Star, ArrowRight, AlertCircle, Lightbulb } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from './ui/Button';
import PdfAnalysisCard from './PdfAnalysisCard';
import TtsButton from './TtsButton';

const ReviewResultCard = ({ review, taskId }) => {
    const navigate = useNavigate();
    const score = review?.score || 0;

    const getScoreColor = (s) => {
        if (s >= 80) return 'text-emerald-500';
        if (s >= 50) return 'text-amber-500';
        return 'text-red-500';
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid md:grid-cols-3 gap-6">
                {/* Score Card */}
                <div className="card flex flex-col items-center justify-center text-center py-10 border-b-4 border-b-blue-500">
                    <span className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-2">Review Score</span>
                    <div className={`text-6xl font-black mb-2 ${getScoreColor(score)}`}>
                        {score}<span className="text-2xl text-slate-300">/100</span>
                    </div>
                    <div className="flex gap-1 text-amber-400 mb-6">
                        {[...Array(5)].map((_, i) => (
                            <Star key={i} size={16} fill={i < Math.round(score / 20) ? "currentColor" : "none"} />
                        ))}
                    </div>

                    <div className="w-full space-y-2 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                        <div className="flex justify-between text-[10px] font-black uppercase tracking-tighter text-slate-400">
                            <span>Requirement Match</span>
                            <span className="text-slate-600 dark:text-slate-300">{((review?.requirement_match || 0) * 100).toFixed(0)}%</span>
                        </div>
                        <div className="h-1 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: `${(review?.requirement_match || 0) * 100}%` }} />
                        </div>

                        <div className="flex justify-between text-[10px] font-black uppercase tracking-tighter text-slate-400 pt-2">
                            <span>Documentation</span>
                            <span className="text-slate-600 dark:text-slate-300">{review?.documentation_score || 0}/10</span>
                        </div>
                        <div className="h-1 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${((review?.documentation_score || 0) / 10) * 100}%` }} />
                        </div>
                    </div>
                </div>

                {/* Reasons Card */}
                <div className="md:col-span-2 card bg-gradient-to-br from-white to-slate-50 dark:from-slate-800/50 dark:to-slate-900 border-l-4 border-l-emerald-500">
                    <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold mb-4">
                        <AlertCircle size={20} />
                        Improvement Areas
                    </div>
                    <ul className="space-y-2">
                        {review?.failure_reasons?.length > 0 ? (
                            review.failure_reasons.map((reason, i) => (
                                <li key={i} className="flex items-start gap-2 text-slate-600 dark:text-slate-300 text-sm">
                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                                    {reason}
                                </li>
                            ))
                        ) : (
                            <li className="text-emerald-500 font-medium">No critical failures identified. Quality exceeds baseline thresholds.</li>
                        )}
                    </ul>
                </div>
            </div>

            {/* Evaluation Summary — with TTS Listen button */}
            {review?.evaluation_summary && (
                <div className="card bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                        <div className="text-xs font-black uppercase tracking-widest text-slate-400">Evaluation Summary</div>
                        <TtsButton text={review.evaluation_summary} lang="en" tone="neutral" />
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                        {review.evaluation_summary}
                    </p>
                </div>
            )}

            {/* PDF Analysis Card */}
            {review?.documentation_score > 0 && (
                <PdfAnalysisCard
                    analysis={review.analysis_pdf}
                    alignment={review.documentation_alignment}
                />
            )}

            {/* Hints Section — with TTS on each hint */}
            <div className="card bg-blue-50/50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900/30">
                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-bold mb-3">
                    <Lightbulb size={20} />
                    Strategic Hints
                </div>
                <ul className="grid md:grid-cols-2 gap-4">
                    {review?.improvement_hints?.length > 0 ? (
                        review.improvement_hints.map((hint, i) => (
                            <li key={i} className="p-3 bg-white dark:bg-slate-800 rounded-xl text-sm text-slate-600 dark:text-slate-400 border border-slate-100 dark:border-slate-800">
                                <div className="flex items-start justify-between gap-2">
                                    <span className="italic">{hint}</span>
                                    <TtsButton text={hint} lang="en" tone="educational" className="shrink-0" />
                                </div>
                            </li>
                        ))
                    ) : (
                        <li className="text-slate-400 italic text-sm">No specific improvement hints available.</li>
                    )}
                </ul>
            </div>

            <div className="flex justify-center pt-4">
                <Button
                    onClick={() => navigate(`/next/${taskId}`)}
                    className="px-10"
                    size="lg"
                >
                    View Next Task Assignment
                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Button>
            </div>
        </div>
    );
};

export default ReviewResultCard;
