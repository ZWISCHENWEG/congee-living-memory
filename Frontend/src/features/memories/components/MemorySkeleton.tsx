import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export const MemorySkeleton = () => {
  return (
    <div className="space-y-4 w-full">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="border-border/40 bg-card/50 shadow-none">
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <Skeleton className="h-3 w-24" />
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
