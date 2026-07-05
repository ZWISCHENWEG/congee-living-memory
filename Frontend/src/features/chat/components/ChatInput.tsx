import * as React from 'react';
import { SendHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput = ({ onSend, isLoading }: ChatInputProps) => {
  const [value, setValue] = React.useState('');

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!value.trim() || isLoading) return;
    onSend(value);
    setValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-3xl mx-auto">
      <div className="relative rounded-3xl border border-border/40 bg-card/80 shadow-sm focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary/50 transition-all overflow-hidden flex items-end p-2 backdrop-blur-xl">
        <Textarea 
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Chronos about your memories..."
          className="min-h-[44px] max-h-[200px] w-full resize-none border-0 bg-transparent px-3 py-2.5 text-[15px] placeholder:text-muted-foreground focus-visible:ring-0 focus-visible:outline-none scrollbar-hide"
          rows={1}
        />
        <Button 
          type="submit" 
          size="icon" 
          disabled={isLoading || !value.trim()}
          className="h-10 w-10 shrink-0 rounded-2xl mb-0.5 shadow-sm transition-transform active:scale-95"
        >
          <SendHorizontal className="h-5 w-5" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
      <div className="text-center mt-2.5">
        <span className="text-[10px] text-muted-foreground/60 font-medium tracking-wide uppercase">
          Press Enter to send, Shift + Enter for new line.
        </span>
      </div>
    </form>
  );
};
