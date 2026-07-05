import { z } from 'zod';

export const searchResultSchema = z.object({
  id: z.string(),
  content: z.string(),
  score: z.number().optional(),
});

export const searchResponseSchema = z.object({
  results: z.array(searchResultSchema),
});

export type SearchResult = z.infer<typeof searchResultSchema>;
export type SearchResponse = z.infer<typeof searchResponseSchema>;
