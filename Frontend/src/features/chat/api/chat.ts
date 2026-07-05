import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { ChatRequest, chatResponseSchema } from '../types';

export const useChat = () => {
  return useMutation({
    mutationFn: async (data: ChatRequest) => {
      const response = await apiClient.post('/chat', data);
      return chatResponseSchema.parse(response.data);
    },
  });
};
