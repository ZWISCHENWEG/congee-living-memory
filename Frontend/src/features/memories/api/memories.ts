import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { memoriesResponseSchema, memorySchema, Memory, MemoriesResponse } from '../types';

export const useMemories = (page = 1, limit = 20, search = '') => {
  return useQuery({
    queryKey: ['memories', page, limit, search],
    queryFn: async () => {
      const response = await apiClient.get('/memories', { params: { page, limit, search } });
      return memoriesResponseSchema.parse(response.data);
    },
  });
};

export const useCreateMemory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { content: string; tags?: string[] }) => {
      const response = await apiClient.post('/memory', data);
      return memorySchema.parse(response.data);
    },
    onMutate: async (newMemory) => {
      await queryClient.cancelQueries({ queryKey: ['memories'] });
      const previousMemories = queryClient.getQueryData<MemoriesResponse>(['memories', 1, 20, '']);
      
      if (previousMemories) {
        // Optimistic UI update
        const optimisticMemory: Memory = {
          id: `temp-${Date.now()}`,
          content: newMemory.content,
          created_at: new Date().toISOString(),
          tags: newMemory.tags || [],
        };
        queryClient.setQueryData<MemoriesResponse>(['memories', 1, 20, ''], {
          ...previousMemories,
          data: [optimisticMemory, ...previousMemories.data],
        });
      }
      return { previousMemories };
    },
    onError: (_err, _newMemory, context) => {
      if (context?.previousMemories) {
        queryClient.setQueryData(['memories', 1, 20, ''], context.previousMemories);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
    },
  });
};

export const useDeleteMemory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/memory/${id}`);
    },
    onMutate: async (deletedId) => {
      await queryClient.cancelQueries({ queryKey: ['memories'] });
      const previousMemories = queryClient.getQueryData<MemoriesResponse>(['memories', 1, 20, '']);
      if (previousMemories) {
        queryClient.setQueryData<MemoriesResponse>(['memories', 1, 20, ''], {
          ...previousMemories,
          data: previousMemories.data.filter(m => m.id !== deletedId),
        });
      }
      return { previousMemories };
    },
    onError: (_err, _deletedId, context) => {
      if (context?.previousMemories) {
        queryClient.setQueryData(['memories', 1, 20, ''], context.previousMemories);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
    },
  });
};
