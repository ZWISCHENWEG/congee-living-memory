import * as React from 'react';
import { NavLink, useLocation } from 'react-router';
import { motion } from 'framer-motion';
import { Home, MessageSquare, Settings, Search, Menu, PanelLeftClose } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useMediaQuery } from '@/hooks/use-media-query';
import { Sheet, SheetContent, SheetTrigger, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { fadeAnimation, slideUpAnimation } from '@/styles/animations';

const navItems = [
  { icon: Home, label: 'Timeline', href: '/' },
  { icon: MessageSquare, label: 'Chat', href: '/chat' },
  { icon: Search, label: 'Search', href: '/search' },
  { icon: Settings, label: 'Settings', href: '/settings' },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = React.useState(false);
  const isMobile = useMediaQuery('(max-width: 768px)');
  const location = useLocation();

  const SidebarContent = () => (
    <motion.div 
      initial="initial"
      animate="animate"
      exit="exit"
      variants={fadeAnimation}
      className={cn(
        "flex h-full flex-col justify-between bg-card/50 backdrop-blur-xl border-r border-border/40 transition-all duration-300",
        collapsed && !isMobile ? "w-20" : "w-64",
        isMobile && "w-full border-none bg-transparent"
      )}
    >
      <div className="flex flex-col space-y-6 p-4">
        <div className="flex items-center justify-between px-2 h-8">
          {(!collapsed || isMobile) && (
            <motion.span variants={slideUpAnimation} className="text-lg font-semibold tracking-tight">
              Congee
            </motion.span>
          )}
          {!isMobile && (
            <Button variant="ghost" size="icon" onClick={() => setCollapsed(!collapsed)} className="ml-auto text-muted-foreground hover:text-foreground">
              <PanelLeftClose className={cn("h-4 w-4 transition-transform duration-300", collapsed && "rotate-180")} />
            </Button>
          )}
        </div>
        
        <nav className="flex flex-col space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href || (location.pathname.startsWith(item.href) && item.href !== '/');
            return (
              <Tooltip key={item.label}>
                <TooltipTrigger render={
                  <NavLink
                    to={item.href}
                    className={cn(
                      "flex items-center space-x-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 outline-none focus-visible:ring-2 focus-visible:ring-ring",
                      isActive 
                        ? "bg-primary/10 text-primary shadow-[inset_2px_0_0_var(--color-primary)]" 
                        : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                      collapsed && !isMobile && "justify-center px-0"
                    )}
                  />
                }>
                  <item.icon className={cn("shrink-0", collapsed && !isMobile ? "h-5 w-5" : "h-4 w-4")} />
                  {(!collapsed || isMobile) && <span>{item.label}</span>}
                </TooltipTrigger>
                {collapsed && !isMobile && (
                  <TooltipContent side="right" className="ml-2">
                    {item.label}
                  </TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </nav>
      </div>
      
      <div className="p-4 border-t border-border/40">
        <div className={cn("flex items-center gap-3", collapsed && !isMobile && "justify-center")}>
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary/80 to-primary/20 shrink-0" />
          {(!collapsed || isMobile) && (
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium truncate">User Name</span>
              <span className="text-xs text-muted-foreground truncate">Free Plan</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  if (isMobile) {
    return (
      <Sheet>
        <SheetTrigger render={
          <Button variant="ghost" size="icon" className="fixed top-3 left-4 z-50 md:hidden glass" />
        }>
          <Menu className="h-5 w-5" />
        </SheetTrigger>
        <SheetContent side="left" className="w-[300px] p-0 border-r-border/40 bg-background/80 backdrop-blur-2xl">
          <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
          <SheetDescription className="sr-only">Main application navigation menu</SheetDescription>
          <SidebarContent />
        </SheetContent>
      </Sheet>
    );
  }

  return <SidebarContent />;
}
