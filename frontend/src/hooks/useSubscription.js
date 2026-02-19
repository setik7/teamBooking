import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

export function useSubscription() {
  const {
    data: subscription,
    isLoading: subLoading,
    error: subError,
  } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => api.get('/subscriptions/me').then((r) => r.data),
    retry: 1,
  });

  const {
    data: tokens,
    isLoading: tokensLoading,
    error: tokensError,
  } = useQuery({
    queryKey: ['tokens'],
    queryFn: () => api.get('/subscriptions/tokens/history').then((r) => r.data),
    retry: 1,
  });

  return {
    subscription: subscription ?? null,
    tokens: tokens ?? null,
    isLoading: subLoading || tokensLoading,
    subError,
    tokensError,
  };
}
