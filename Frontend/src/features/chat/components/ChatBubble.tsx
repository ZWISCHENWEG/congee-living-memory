import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Message } from '../types';
import { formatRelativeTime } from '@/lib/formatters';

export const ChatBubble = ({ message }: { message: Message }) => {
  const isUser = message.role === 'user';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10, scale: 0.95 }} 
      animate={{ opacity: 1, y: 0, scale: 1 }} 
      className={cn("flex w-full mb-6", isUser ? "justify-end" : "justify-start")}
    >
      <div className={cn(
        "max-w-[85%] rounded-3xl px-5 py-3.5 shadow-sm",
        isUser 
          ? "bg-primary text-primary-foreground rounded-tr-sm" 
          : "bg-card border border-border/50 text-card-foreground rounded-tl-sm backdrop-blur-sm"
      )}>
        <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
        <div className={cn(
          "text-[10px] mt-2 font-medium opacity-60",
          isUser ? "text-primary-foreground text-right" : "text-muted-foreground text-left"
        )}>
          {formatRelativeTime(message.timestamp)}
        </div>
      </div>
    </motion.div>
  );
};
