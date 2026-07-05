import axios from 'axios';
import { memoriesResponseSchema, memorySchema } from './src/features/memories/types';

async function test() {
  try {
    const res1 = await axios.get('http://127.0.0.1:8000/memories');
    console.log('GET /memories raw:', JSON.stringify(res1.data).substring(0, 100) + '...');
    const parsed1 = memoriesResponseSchema.parse(res1.data);
    console.log('GET /memories Zod parsed successfully! count:', parsed1.data.length);

    const res2 = await axios.post('http://127.0.0.1:8000/memory', { content: "Test memory" }, { headers: { 'Content-Type': 'application/json' } });
    console.log('POST /memory raw:', JSON.stringify(res2.data).substring(0, 100) + '...');
    const parsed2 = memorySchema.parse(res2.data);
    console.log('POST /memory Zod parsed successfully! id:', parsed2.id);

    const res3 = await axios.delete(`http://127.0.0.1:8000/memory/${parsed2.id}`);
    console.log('DELETE /memory status:', res3.status);
  } catch (e: any) {
    console.error('Error:', e.message, e.errors || e.response?.data);
  }
}
test();
