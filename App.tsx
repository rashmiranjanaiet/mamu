import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './components/MessageBubble';
import { sendMessageToGemini } from './services/geminiService';
import { Message } from './types';
import { Send, BarChart2, Loader2, Sparkles } from 'lucide-react';

export default function App() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'model',
      content: "Hello! I'm ChartBot. \n\nI can help you visualize data. Try asking me something like:\n• \"Show me a bar chart of monthly sales for 2024\"\n• \"Visualize the population growth of top 5 cities\"\n• \"Plot a comparison of Revenue vs Expenses\"",
      timestamp: Date.now(),
    },
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessageToGemini(messages, userMessage.content);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: response.text,
        chart: response.chart,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: "Sorry, I encountered an error while processing your request. Please try again or check your API key.",
        isError: true,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Adjust textarea height automatically
  const handleInputCheck = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="flex flex-col h-screen bg-background text-gray-100 font-sans selection:bg-primary/30">
      {/* Header */}
      <header className="flex-none h-16 border-b border-gray-800 bg-surface/50 backdrop-blur-md flex items-center justify-between px-4 md:px-8 z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-primary to-accent p-2 rounded-lg shadow-lg shadow-primary/20">
            <BarChart2 className="text-white w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            ChartBot <span className="text-primary font-light">AI</span>
          </h1>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-gray-400 bg-surface px-3 py-1.5 rounded-full border border-gray-700">
           <Sparkles size={14} className="text-yellow-500" />
           <span>Powered by Gemini 3 Flash</span>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8 relative">
        <div className="max-w-4xl mx-auto flex flex-col min-h-full">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-6 animate-pulse">
               <div className="bg-surface rounded-2xl rounded-tl-none p-4 flex items-center gap-3 border border-gray-700/50">
                 <Loader2 className="w-5 h-5 animate-spin text-primary" />
                 <span className="text-sm text-gray-400">Analyzing data...</span>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </main>

      {/* Input Area */}
      <footer className="flex-none p-4 bg-background border-t border-gray-800">
        <div className="max-w-4xl mx-auto relative">
          <div className="relative flex items-end gap-2 bg-surface rounded-2xl border border-gray-700 p-2 focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary transition-all shadow-lg">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={handleInputCheck}
              onKeyDown={handleKeyDown}
              placeholder="Describe a chart to generate..."
              className="flex-1 bg-transparent text-white placeholder-gray-500 text-base p-3 resize-none focus:outline-none max-h-32"
              style={{ minHeight: '48px' }}
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="p-3 bg-primary hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-xl text-white transition-colors duration-200 mb-0.5 shadow-md"
            >
              {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
            </button>
          </div>
          <div className="text-center mt-2">
            <p className="text-[10px] text-gray-500">
              AI can make mistakes. Please verify important data.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
