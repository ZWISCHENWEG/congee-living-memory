import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { searchResponseSchema } from '../types';

export const useSearch = (query: string) => {
  return useQuery({
    queryKey: ['search', query],
    queryFn: async () => {
      if (!query.trim()) return { results: [] };
      const response = await apiClient.get('/search', { params: { q: query } });
      return searchResponseSchema.parse(response.data);
    },
    enabled: query.trim().length > 0,
  });
};
