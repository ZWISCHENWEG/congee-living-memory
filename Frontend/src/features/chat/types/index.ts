import { z } from 'zod';

export const chatRequestSchema = z.object({
  message: z.string(),
  conversation_id: z.string().optional(),
});

export const chatResponseSchema = z.object({
  id: z.string(),
  reply: z.string(),
  conversation_id: z.string().optional(),
  referenced_memories: z.array(z.string()).optional(),
});

export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;

// Internal state type for messages
export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};
