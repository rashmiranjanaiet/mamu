import React from 'react';
import { Message } from '../types';
import { ChartRenderer } from './ChartRenderer';
import { User, Bot, AlertCircle } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}>
      <div className={`flex max-w-[95%] md:max-w-[85%] lg:max-w-[75%] gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-primary' : isError ? 'bg-red-500' : 'bg-accent'
          }`}>
          {isUser ? <User size={18} className="text-white" /> : isError ? <AlertCircle size={18} className="text-white"/> : <Bot size={18} className="text-white" />}
        </div>

        {/* Content Bubble */}
        <div className="flex flex-col w-full min-w-0">
          <div
            className={`px-5 py-3.5 rounded-2xl shadow-sm text-sm md:text-base leading-relaxed whitespace-pre-wrap break-words ${
              isUser
                ? 'bg-primary text-white rounded-tr-none'
                : isError
                ? 'bg-red-900/50 border border-red-500/30 text-red-200 rounded-tl-none'
                : 'bg-surface text-gray-200 border border-gray-700/50 rounded-tl-none'
            }`}
          >
            {message.content}
          </div>

          {/* Chart Rendering */}
          {message.chart && (
            <div className="mt-2 w-full min-w-0 overflow-hidden">
               <ChartRenderer config={message.chart} />
            </div>
          )}
          
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
};
