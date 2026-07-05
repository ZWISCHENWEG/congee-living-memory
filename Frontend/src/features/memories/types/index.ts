import { z } from 'zod';

export const memorySchema = z.object({
  id: z.string(),
  content: z.string(),
  created_at: z.string().datetime({ offset: true }),
  tags: z.array(z.string()).optional(),
});

export const memoriesResponseSchema = z.object({
  data: z.array(memorySchema),
  meta: z.object({
    total: z.number(),
    page: z.number(),
    limit: z.number(),
  }),
});

export type Memory = z.infer<typeof memorySchema>;
export type MemoriesResponse = z.infer<typeof memoriesResponseSchema>;
