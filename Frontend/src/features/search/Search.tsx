import * as React from 'react';
import { useSearchParams } from 'react-router';
import { AnimatePresence, motion } from 'framer-motion';
import { Search as SearchIcon, SearchX, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useSearch } from '@/features/search/api/search';
import { useDebounce } from '@/hooks/use-debounce';

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = React.useState(searchParams.get('q') ?? '');
  const debouncedQuery = useDebounce(query, 300);

  const { data, isLoading, isError } = useSearch(debouncedQuery);
  const hasQuery = debouncedQuery.trim().length > 0;

  // Keep the URL in sync so results are shareable / deep-linkable.
  // Guarded so it navigates at most once per distinct query (no render loop).
  const lastSynced = React.useRef<string | null>(null);
  React.useEffect(() => {
    const trimmed = debouncedQuery.trim();
    if (lastSynced.current === trimmed) return;
    lastSynced.current = trimmed;
    setSearchParams(trimmed ? { q: trimmed } : {}, { replace: true });
  }, [debouncedQuery, setSearchParams]);

  return (
    <div className="h-full w-full max-w-3xl mx-auto px-6 py-8 md:px-8 md:py-10 flex flex-col">
      <div className="relative w-full mb-8">
        <SearchIcon className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search across all your memories..."
          aria-label="Search memories"
          className="h-12 w-full rounded-2xl border-border/40 bg-card pl-11 pr-4 text-sm shadow-sm focus-visible:ring-2 focus-visible:ring-primary/50"
        />
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto hide-scrollbar pb-12">
        {/* Idle: no query yet */}
        {!hasQuery && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="h-16 w-16 rounded-2xl bg-secondary/50 flex items-center justify-center mb-6 text-muted-foreground ring-1 ring-border/50">
              <Sparkles className="h-8 w-8 opacity-50" />
            </div>
            <h3 className="text-lg font-medium text-foreground tracking-tight">Semantic search</h3>
            <p className="text-sm text-muted-foreground mt-2 max-w-[280px]">
              Find memories by meaning, not just keywords. Start typing to search.
            </p>
          </div>
        )}

        {/* Loading */}
        {hasQuery && isLoading && (
          <div className="space-y-4 w-full">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-border/40 bg-card/50 shadow-none">
                <CardContent className="p-4 space-y-3">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/5" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Error */}
        {hasQuery && isError && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-muted-foreground text-sm">
              Search failed. Please check your connection and try again.
            </p>
          </div>
        )}

        {/* Empty results */}
        {hasQuery && !isLoading && !isError && data?.results.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="h-16 w-16 rounded-2xl bg-secondary/50 flex items-center justify-center mb-6 text-muted-foreground ring-1 ring-border/50">
              <SearchX className="h-8 w-8 opacity-50" />
            </div>
            <h3 className="text-lg font-medium text-foreground tracking-tight">No results found</h3>
            <p className="text-sm text-muted-foreground mt-2 max-w-[280px]">
              We couldn't find any memories matching "{debouncedQuery.trim()}".
            </p>
          </div>
        )}

        {/* Results */}
        {hasQuery && !isLoading && !isError && data && data.results.length > 0 && (
          <div className="flex flex-col space-y-4">
            <AnimatePresence mode="popLayout">
              {data.results.map((result) => (
                <motion.div
                  key={result.id}
                  layout
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                >
                  <Card className="group border-border/40 bg-card/50 backdrop-blur-sm transition-all hover:border-primary/20 hover:shadow-md">
                    <CardContent className="p-4 flex items-start justify-between gap-4">
                      <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                        {result.content}
                      </p>
                      {typeof result.score === 'number' && (
                        <span className="shrink-0 rounded-md bg-secondary/50 px-2 py-0.5 text-[10px] font-medium text-secondary-foreground border border-secondary">
                          {Math.round(result.score * 100)}% match
                        </span>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
