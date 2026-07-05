import * as React from 'react';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Search, FileText, Settings, Clock, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router';
import { useSearch } from '@/features/search/api/search';
import { useDebounce } from '@/hooks/use-debounce';

export function CommandPalette() {
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState('');
  const debouncedQuery = useDebounce(query, 300);
  const navigate = useNavigate();

  const { data, isLoading } = useSearch(debouncedQuery);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const runCommand = React.useCallback((command: () => void) => {
    setOpen(false);
    command();
  }, []);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput 
        placeholder="Type a command or search memories..." 
        value={query} 
        onValueChange={setQuery} 
      />
      <CommandList>
        {isLoading && query.trim().length > 0 && (
          <div className="py-6 text-center text-sm text-muted-foreground flex items-center justify-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Searching memories...
          </div>
        )}
        
        {!isLoading && <CommandEmpty>No results found.</CommandEmpty>}
        
        {data?.results && data.results.length > 0 && (
          <CommandGroup heading="Memories">
            {data.results.map((result) => (
              <CommandItem
                key={result.id}
                onSelect={() => runCommand(() => navigate(`/search?q=${encodeURIComponent(query)}`))}
                className="flex items-start gap-3 py-3"
              >
                <Clock className="h-4 w-4 shrink-0 mt-0.5 text-muted-foreground" />
                <div className="flex flex-col overflow-hidden">
                  <span className="text-sm truncate">{result.content}</span>
                  {result.score && (
                    <span className="text-[10px] text-muted-foreground mt-0.5 font-medium">
                      Match: {Math.round(result.score * 100)}%
                    </span>
                  )}
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        {(!query || query.trim().length === 0) && (
          <>
            <CommandGroup heading="Suggestions">
              <CommandItem onSelect={() => runCommand(() => navigate('/'))}>
                <Clock className="mr-2 h-4 w-4" />
                <span>Go to Timeline</span>
              </CommandItem>
              <CommandItem onSelect={() => runCommand(() => navigate('/chat'))}>
                <FileText className="mr-2 h-4 w-4" />
                <span>New Chat</span>
              </CommandItem>
              <CommandItem onSelect={() => runCommand(() => navigate('/search'))}>
                <Search className="mr-2 h-4 w-4" />
                <span>Search Memories</span>
              </CommandItem>
            </CommandGroup>
            <CommandGroup heading="Settings">
              <CommandItem onSelect={() => runCommand(() => navigate('/settings'))}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  );
}
