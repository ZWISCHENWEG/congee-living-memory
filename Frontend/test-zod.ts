import { z } from 'zod';
const memorySchema = z.object({
  id: z.string(),
  content: z.string(),
  created_at: z.string().datetime({ offset: true }),
  tags: z.array(z.string()).optional(),
});
try {
  memorySchema.parse({
    id: "mem_123",
    content: "hi",
    created_at: "2026-07-05T06:46:22.579377+00:00",
    tags: []
  });
  console.log("Success");
} catch(e: any) {
  console.log("Error:", JSON.stringify(e, null, 2));
}
