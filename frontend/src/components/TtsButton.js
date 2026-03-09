import React, { useState, useRef } from 'react';
import { Volume2, Square } from 'lucide-react';
import Button from './ui/Button';
import { taskService } from '../services/taskService';

const TtsButton = ({ text, lang = 'en', tone = 'educational', className = '' }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef(null);

    const handleToggle = () => {
        if (isPlaying) {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.currentTime = 0;
            }
            setIsPlaying(false);
        } else {
            const ttsUrl = taskService.getTtsStream(text, lang, tone);
            if (!audioRef.current) {
                audioRef.current = new Audio(ttsUrl);
                audioRef.current.onended = () => setIsPlaying(false);
            } else {
                audioRef.current.src = ttsUrl;
            }

            audioRef.current.play()
                .then(() => setIsPlaying(true))
                .catch(err => {
                    console.error("TTS Play Error:", err);
                    setIsPlaying(false);
                });
        }
    };

    return (
        <Button
            variant="ghost"
            size="sm"
            onClick={handleToggle}
            className={`flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 ${className}`}
        >
            {isPlaying ? <Square size={16} fill="currentColor" /> : <Volume2 size={16} />}
            <span className="text-xs font-bold uppercase tracking-wider">
                {isPlaying ? "Stop" : "Listen"}
            </span>
        </Button>
    );
};

export default TtsButton;
