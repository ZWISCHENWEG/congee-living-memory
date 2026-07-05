import { motion } from 'framer-motion';
import { Trash2, Clock, Tag } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Memory } from '../types';
import { formatRelativeTime } from '@/lib/formatters';
import { useDeleteMemory } from '../api/memories';
import { toast } from 'sonner';

export const MemoryCard = ({ memory }: { memory: Memory }) => {
  const deleteMutation = useDeleteMemory();

  const handleDelete = () => {
    deleteMutation.mutate(memory.id, {
      onSuccess: () => toast.success('Memory deleted'),
      onError: () => toast.error('Failed to delete memory'),
    });
  };

  return (
    <motion.div layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }}>
      <Card className="group relative overflow-hidden transition-all hover:shadow-md hover:border-primary/20 border-border/40 bg-card/50 backdrop-blur-sm">
        <CardHeader className="p-4 pb-2 flex flex-row items-start justify-between space-y-0">
          <div className="flex items-center text-xs text-muted-foreground space-x-1.5">
            <Clock className="h-3.5 w-3.5" />
            <span>{formatRelativeTime(memory.created_at)}</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive hover:bg-destructive/10 -mt-1 -mr-1"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span className="sr-only">Delete</span>
          </Button>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
            {memory.content}
          </p>
        </CardContent>
        {memory.tags && memory.tags.length > 0 && (
          <CardFooter className="p-4 pt-0 flex gap-2 flex-wrap">
            {memory.tags.map(tag => (
              <span key={tag} className="inline-flex items-center gap-1 rounded-md bg-secondary/50 px-2 py-0.5 text-xs font-medium text-secondary-foreground border border-secondary">
                <Tag className="h-3 w-3 opacity-70" />
                {tag}
              </span>
            ))}
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
};
