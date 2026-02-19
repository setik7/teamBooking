import { useCalendar } from '../hooks/useCalendar';
import { useToast } from '../hooks/useToast';
import WeekNavigation from '../components/calendar/WeekNavigation';
import WeekCalendar from '../components/calendar/WeekCalendar';
import Toast from '../components/common/Toast';

const styles = {
  page: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px 16px',
    fontFamily: 'system-ui, sans-serif',
  },
  spinner: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '200px',
    fontSize: '16px',
    color: '#666',
  },
  error: {
    padding: '16px',
    background: '#fff0f0',
    border: '1px solid #ffcccc',
    borderRadius: '6px',
    color: '#cc0000',
    marginTop: '16px',
  },
};

export default function CalendarPage() {
  const {
    weekStart,
    prevWeek,
    nextWeek,
    goToday,
    slots,
    isLoading,
    isError,
    error,
    bookMutation,
    cancelMutation,
  } = useCalendar();
  const { toast, showToast, hideToast } = useToast();

  const isBooking =
    bookMutation.isPending || cancelMutation.isPending;

  const handleBook = (training_slot_id, date) => {
    bookMutation.mutate({ training_slot_id, date }, {
      onSuccess: () => showToast('Training booked!', 'success'),
      onError: (err) => {
        const msg = err.response?.data?.detail || 'Failed to book training';
        showToast(msg, 'error');
      },
    });
  };

  const handleCancel = (bookingId) => {
    cancelMutation.mutate(bookingId, {
      onSuccess: () => showToast('Booking cancelled', 'info'),
      onError: (err) => {
        const msg = err.response?.data?.detail || 'Failed to cancel booking';
        showToast(msg, 'error');
      },
    });
  };

  return (
    <div style={styles.page}>
      <WeekNavigation
        weekStart={weekStart}
        onPrev={prevWeek}
        onNext={nextWeek}
        onToday={goToday}
      />

      {isLoading && (
        <div style={styles.spinner}>Loading schedule...</div>
      )}

      {isError && (
        <div style={styles.error}>
          Failed to load slots: {error?.message ?? 'Unknown error'}
        </div>
      )}

      {!isLoading && !isError && (
        <WeekCalendar
          slots={slots}
          weekStart={weekStart}
          onBook={handleBook}
          onCancel={handleCancel}
          isBooking={isBooking}
        />
      )}

      {toast.visible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
}
