import { useLocation } from 'react-router';
import { motion } from 'framer-motion';
import { Bell, Command, Sun, Moon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from 'next-themes';
import { slideUpAnimation } from '@/styles/animations';

export function Header() {
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  
  const getPageTitle = () => {
    if (location.pathname === '/') return 'Timeline';
    if (location.pathname.startsWith('/chat')) return 'Chat';
    if (location.pathname.startsWith('/search')) return 'Search';
    if (location.pathname.startsWith('/settings')) return 'Settings';
    return 'Congee';
  };

  return (
    <motion.header 
      variants={slideUpAnimation}
      initial="initial"
      animate="animate"
      className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-border/40 bg-background/80 px-8 backdrop-blur-xl transition-all w-full"
    >
      <div className="flex items-center gap-4 ml-12 md:ml-0">
        <h1 className="text-lg font-semibold tracking-tight">{getPageTitle()}</h1>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" className="hidden md:flex gap-2 text-muted-foreground bg-background/50 h-8">
          <Command className="h-3 w-3" />
          <span className="text-xs">Search</span>
          <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100">
            <span className="text-xs">⌘</span>K
          </kbd>
        </Button>
        
        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
          <Bell className="h-4 w-4" />
        </Button>
        
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-8 w-8 rounded-full"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </motion.header>
  );
}
