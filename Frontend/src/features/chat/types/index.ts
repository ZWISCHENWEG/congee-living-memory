import { z } from 'zod';

export const chatRequestSchema = z.object({
  message: z.string(),
  conversation_id: z.string().optional(),
});

// Mirrors the backend `ChatResponse` (Backend/app/schemas/chat.py). The reply
// text is `response`; retrieved memories and the autonomous memory outcome are
// surfaced too. Fields are permissive so a partial payload never breaks chat.
export const usedMemorySchema = z.object({
  id: z.string(),
  content: z.string(),
  score: z.number().nullable().optional(),
});

export const memoryActionSchema = z.object({
  status: z.string(),
  memory: z.string().nullable().optional(),
  memory_id: z.string().nullable().optional(),
  type: z.string().nullable().optional(),
  importance: z.number().nullable().optional(),
  detail: z.string().nullable().optional(),
});

export const chatResponseSchema = z.object({
  response: z.string(),
  used_memories: z.array(usedMemorySchema).optional().default([]),
  conversation_id: z.string().nullable().optional(),
  memory_action: memoryActionSchema.nullable().optional(),
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
