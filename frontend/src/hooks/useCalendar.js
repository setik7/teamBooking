import { useState } from 'react';
import { startOfWeek, addWeeks, format } from 'date-fns';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

export function useCalendar() {
  const queryClient = useQueryClient();

  const [weekStart, setWeekStart] = useState(() =>
    startOfWeek(new Date(), { weekStartsOn: 1 })
  );

  const prevWeek = () => setWeekStart((d) => addWeeks(d, -1));
  const nextWeek = () => setWeekStart((d) => addWeeks(d, 1));
  const goToday = () => setWeekStart(startOfWeek(new Date(), { weekStartsOn: 1 }));

  const { data: slots, isLoading, isError, error } = useQuery({
    queryKey: ['slots', weekStart],
    queryFn: () =>
      api
        .get('/slots/week', { params: { week_start: format(weekStart, 'yyyy-MM-dd') } })
        .then((res) => res.data),
  });

  const invalidateAfterBooking = () => {
    queryClient.invalidateQueries({ queryKey: ['slots'] });
    queryClient.invalidateQueries({ queryKey: ['subscription'] });
  };

  const bookMutation = useMutation({
    mutationFn: ({ training_slot_id, date }) =>
      api.post('/bookings', { training_slot_id, date }).then((res) => res.data),
    onSuccess: invalidateAfterBooking,
  });

  const cancelMutation = useMutation({
    mutationFn: (bookingId) =>
      api.delete(`/bookings/${bookingId}`).then((res) => res.data),
    onSuccess: invalidateAfterBooking,
  });

  return {
    weekStart,
    prevWeek,
    nextWeek,
    goToday,
    slots: slots ?? [],
    isLoading,
    isError,
    error,
    bookMutation,
    cancelMutation,
  };
}
