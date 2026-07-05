import { useRouteError, isRouteErrorResponse } from 'react-router';
import { Button } from '@/components/ui/button';

export function GlobalError() {
  const error = useRouteError();
  
  let title = "Something went wrong";
  let message = "An unexpected error occurred. Please try again.";

  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      title = "404";
      message = "We couldn't find that memory.";
    }
  } else if (error instanceof Error) {
    message = error.message;
  }

  return (
    <div className="flex h-[80vh] flex-col items-center justify-center space-y-6 text-center bg-background text-foreground p-8">
      <div className="space-y-2">
        <h1 className="text-6xl font-bold tracking-tight">{title}</h1>
        <p className="text-xl text-muted-foreground max-w-md mx-auto">{message}</p>
      </div>
      <Button onClick={() => window.location.href = '/'} variant="default" size="lg">
        Return to Timeline
      </Button>
    </div>
  );
}
