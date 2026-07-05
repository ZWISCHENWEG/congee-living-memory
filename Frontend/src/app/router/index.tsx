import { createBrowserRouter, RouterProvider } from 'react-router';
import { Suspense, lazy } from 'react';
import { RootLayout } from '../layouts/RootLayout';
import { Skeleton } from '@/components/ui/skeleton';

// Lazy loaded placeholders for future features
const Dashboard = lazy(() => import('@/features/dashboard/Dashboard').catch(() => ({ default: () => <div className="p-8">Dashboard Placeholder</div> })));
const Chat = lazy(() => import('@/features/chat/Chat').catch(() => ({ default: () => <div className="p-8">Chat Placeholder</div> })));
const SearchScreen = lazy(() => import('@/features/search/Search').catch(() => ({ default: () => <div className="p-8">Search Placeholder</div> })));
const Settings = lazy(() => import('@/features/settings/Settings').catch(() => ({ default: () => <div className="p-8">Settings Placeholder</div> })));

const LoadingFallback = () => (
  <div className="p-8 space-y-4">
    <Skeleton className="h-10 w-1/3" />
    <Skeleton className="h-[400px] w-full" />
  </div>
);

import { GlobalError } from '@/components/common/GlobalError';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <GlobalError />, // Global error boundary
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: 'chat',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Chat />
          </Suspense>
        ),
      },
      {
        path: 'search',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <SearchScreen />
          </Suspense>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<LoadingFallback />}>
            <Settings />
          </Suspense>
        ),
      }
    ],
  },
]);

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
