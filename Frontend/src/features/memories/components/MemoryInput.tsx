import * as React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { SendHorizontal, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCreateMemory } from '../api/memories';
import { toast } from 'sonner';
import { Textarea } from '@/components/ui/textarea';

const formSchema = z.object({
  content: z.string().min(1, 'Cannot save an empty memory').max(2000),
});

export const MemoryInput = () => {
  const createMutation = useCreateMemory();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { content: '' },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createMutation.mutate(values, {
      onSuccess: () => {
        form.reset();
        toast.success('Memory saved');
      },
      onError: () => toast.error('Failed to save memory'),
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      form.handleSubmit(onSubmit)();
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="relative w-full mb-8">
      <div className="relative rounded-2xl border border-border/40 bg-card shadow-sm focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary/50 transition-all overflow-hidden group">
        <Textarea 
          {...form.register('content')}
          onKeyDown={handleKeyDown}
          placeholder="What's on your mind? (⌘ + Enter to save)"
          className="min-h-[120px] w-full resize-none border-0 bg-transparent p-4 pb-12 text-sm placeholder:text-muted-foreground focus-visible:ring-0 focus-visible:outline-none scrollbar-hide"
        />
        <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
          <Button type="button" variant="ghost" size="sm" className="text-muted-foreground hover:text-primary h-8 px-2">
            <Sparkles className="h-4 w-4 mr-2" />
            <span className="text-xs font-medium">Auto-tag</span>
          </Button>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground hidden sm:inline-block mr-2 opacity-0 group-focus-within:opacity-100 transition-opacity">
              ⌘ + Enter
            </span>
            <Button 
              type="submit" 
              size="sm" 
              disabled={createMutation.isPending || !form.formState.isValid}
              className="h-8 px-4 rounded-lg shadow-sm"
            >
              <SendHorizontal className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
      </div>
    </form>
  );
};
