import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

const HARDCODED_PLANS = [
  { id: 1, name: 'Starter', trainings_per_month: 8, price_eur: 49 },
  { id: 2, name: 'Standard', trainings_per_month: 12, price_eur: 69 },
  { id: 3, name: 'Unlimited', trainings_per_month: 999, price_eur: 99 },
];

export function usePlans() {
  const queryClient = useQueryClient();

  const {
    data: plans,
    isLoading: plansLoading,
  } = useQuery({
    queryKey: ['plans'],
    queryFn: () => Promise.resolve(HARDCODED_PLANS),
  });

  const subscribeMutation = useMutation({
    mutationFn: (planId) =>
      api.post(`/checkout/subscribe?plan_id=${planId}`).then((r) => r.data),
    onSuccess: (data) => {
      if (data?.checkout_url) {
        window.location.href = data.checkout_url;
      }
    },
  });

  const buyTokensMutation = useMutation({
    mutationFn: (amount) =>
      api.post(`/checkout/tokens?amount=${amount}`).then((r) => r.data),
    onSuccess: (data) => {
      if (data?.checkout_url) {
        window.location.href = data.checkout_url;
      }
    },
  });

  const fulfillMutation = useMutation({
    mutationFn: (sessionId) =>
      api.post(`/checkout/fulfill?session_id=${sessionId}`).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      queryClient.invalidateQueries({ queryKey: ['tokens'] });
    },
  });

  return {
    plans: plans ?? HARDCODED_PLANS,
    isLoading: plansLoading,
    subscribeMutation,
    buyTokensMutation,
    fulfillMutation,
  };
}
