import React, { useState, useRef, useEffect } from 'react';
import { Volume2, Square, Loader } from 'lucide-react';
import { taskService } from '../services/taskService';

const TtsButton = ({ text, lang = 'en', tone = 'neutral', className = '' }) => {
    const [state, setState] = useState('idle'); // idle | loading | playing | error
    const audioRef = useRef(null);

    // Stop and clean up when text changes or component unmounts
    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.src = '';
                audioRef.current = null;
            }
        };
    }, [text]);

    const handleToggle = () => {
        if (state === 'playing') {
            audioRef.current?.pause();
            if (audioRef.current) audioRef.current.currentTime = 0;
            setState('idle');
            return;
        }

        if (!text?.trim()) return;

        setState('loading');
        const ttsUrl = taskService.getTtsStream(text, lang, tone);

        if (!audioRef.current) {
            audioRef.current = new Audio();
        }

        audioRef.current.src = ttsUrl;
        audioRef.current.oncanplaythrough = null;
        audioRef.current.onended = () => setState('idle');
        audioRef.current.onerror = () => setState('error');

        audioRef.current.play()
            .then(() => setState('playing'))
            .catch(() => setState('error'));
    };

    const icon = {
        idle:    <Volume2 size={15} />,
        loading: <Loader size={15} className="animate-spin" />,
        playing: <Square size={15} fill="currentColor" />,
        error:   <Volume2 size={15} className="opacity-40" />,
    }[state];

    const label = {
        idle:    'Listen',
        loading: 'Loading',
        playing: 'Stop',
        error:   'Unavailable',
    }[state];

    return (
        <button
            onClick={handleToggle}
            disabled={state === 'loading' || state === 'error' || !text?.trim()}
            title={state === 'error' ? 'TTS unavailable' : label}
            className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-semibold
                text-blue-600 dark:text-blue-400
                hover:bg-blue-50 dark:hover:bg-blue-900/20
                disabled:opacity-40 disabled:cursor-not-allowed
                transition-colors ${className}`}
        >
            {icon}
            <span>{label}</span>
        </button>
    );
};

export default TtsButton;
