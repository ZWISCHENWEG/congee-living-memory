import { AnimatePresence } from 'framer-motion';
import { useMemories } from '@/features/memories/api/memories';
import { MemoryCard } from '@/features/memories/components/MemoryCard';
import { MemorySkeleton } from '@/features/memories/components/MemorySkeleton';
import { MemoryInput } from '@/features/memories/components/MemoryInput';
import { Inbox } from 'lucide-react';

export default function Dashboard() {
  const { data, isLoading, isError } = useMemories();

  return (
    <div className="h-full w-full max-w-3xl mx-auto px-6 py-8 md:px-8 md:py-10 flex flex-col">
      <MemoryInput />
      
      <div className="flex-1 min-h-0 overflow-y-auto hide-scrollbar pb-12">
        {isLoading && <MemorySkeleton />}
        
        {isError && (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-muted-foreground text-sm">Failed to load memories. Please check your connection.</p>
          </div>
        )}

        {!isLoading && !isError && data?.data.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="h-16 w-16 rounded-2xl bg-secondary/50 flex items-center justify-center mb-6 text-muted-foreground ring-1 ring-border/50">
              <Inbox className="h-8 w-8 opacity-50" />
            </div>
            <h3 className="text-lg font-medium text-foreground tracking-tight">No memories yet</h3>
            <p className="text-sm text-muted-foreground mt-2 max-w-[250px]">
              Your mind is clear. Start capturing your thoughts, meetings, and ideas above.
            </p>
          </div>
        )}

        <div className="flex flex-col space-y-4">
          <AnimatePresence mode="popLayout">
            {data?.data.map((memory) => (
              <MemoryCard key={memory.id} memory={memory} />
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
