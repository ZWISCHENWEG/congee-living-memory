/**
 * Global Logger Utility
 * Centralizes logging to allow easy future integration with Sentry, LogRocket, or DataDog.
 */
type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
  private log(level: LogLevel, message: string, data?: unknown) {
    const timestamp = new Date().toISOString();
    
    // In production, we could send this to Sentry or LogRocket here.
    if (import.meta.env.DEV) {
      if (data !== undefined) {
        console[level](`[${timestamp}] [${level.toUpperCase()}] ${message}`, data);
      } else {
        console[level](`[${timestamp}] [${level.toUpperCase()}] ${message}`);
      }
    } else {
      // Production logging logic
      if (level === 'error') {
        // Send to error tracking service
      }
    }
  }

  info(message: string, data?: unknown) { this.log('info', message, data); }
  warn(message: string, data?: unknown) { this.log('warn', message, data); }
  error(message: string, data?: unknown) { this.log('error', message, data); }
  debug(message: string, data?: unknown) { this.log('debug', message, data); }
}

export const logger = new Logger();
