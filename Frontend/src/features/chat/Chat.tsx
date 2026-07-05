import * as React from 'react';
import { AnimatePresence } from 'framer-motion';
import { BotMessageSquare } from 'lucide-react';
import { ChatBubble } from '@/features/chat/components/ChatBubble';
import { ChatInput } from '@/features/chat/components/ChatInput';
import { useChat } from '@/features/chat/api/chat';
import { Message } from '@/features/chat/types';
import { toast } from 'sonner';

export default function Chat() {
  const chatMutation = useChat();
  const [messages, setMessages] = React.useState<Message[]>([]);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, chatMutation.isPending]);

  const handleSend = (content: string) => {
    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    
    chatMutation.mutate(
      { message: content },
      {
        onSuccess: (data) => {
          const aiMsg: Message = {
            // The backend does not return a message id; generate one client-side.
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: data.response,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, aiMsg]);
        },
        onError: () => {
          toast.error('Failed to get a response from Chronos.');
          setMessages((prev) => prev.filter(m => m.id !== userMsg.id)); // Rollback
        }
      }
    );
  };

  return (
    <div className="h-full w-full max-w-3xl mx-auto px-6 py-4 md:px-8 flex flex-col">
      <div 
        ref={scrollRef}
        className="flex-1 min-h-0 overflow-y-auto hide-scrollbar pb-6 flex flex-col scroll-smooth"
      >
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 text-primary ring-1 ring-primary/20 shadow-inner">
              <BotMessageSquare className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-medium text-foreground tracking-tight">Chat with Chronos</h3>
            <p className="text-sm text-muted-foreground mt-3 max-w-sm leading-relaxed">
              Ask questions about your past memories, meetings, and ideas. Chronos remembers everything.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col justify-end">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <ChatBubble key={msg.id} message={msg} />
              ))}
              
              {chatMutation.isPending && (
                <ChatBubble 
                  key="typing" 
                  message={{ 
                    id: 'typing', 
                    role: 'assistant', 
                    content: 'Thinking...', 
                    timestamp: new Date().toISOString() 
                  }} 
                />
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
      
      <div className="shrink-0 pt-4 pb-4 z-10 sticky bottom-0">
        <ChatInput onSend={handleSend} isLoading={chatMutation.isPending} />
      </div>
    </div>
  );
}
