import { Outlet, useLocation } from 'react-router';
import { motion, AnimatePresence } from 'framer-motion';
import { CommandPalette } from '@/components/common/CommandPalette';
import { Toaster } from '@/components/ui/sonner';
import { Sidebar } from '@/components/common/Sidebar';
import { Header } from '@/components/common/Header';
import { fadeAnimation } from '@/styles/animations';

export const RootLayout = () => {
  const location = useLocation();

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground selection:bg-primary selection:text-primary-foreground font-sans antialiased">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Header />
        <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              variants={fadeAnimation}
              initial="initial"
              animate="animate"
              exit="exit"
              className="h-full w-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      
      <CommandPalette />
      <Toaster position="bottom-right" theme="system" className="backdrop-blur-xl" />
    </div>
  );
};
