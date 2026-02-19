import { format, isToday } from 'date-fns';
import SlotCard from './SlotCard';

const styles = {
  column: (today) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    borderRadius: '8px',
    padding: '8px',
    background: today ? '#eff6ff' : '#f9fafb',
    border: today ? '2px solid #3b82f6' : '1px solid #e5e7eb',
    minHeight: '120px',
  }),
  header: (today) => ({
    textAlign: 'center',
    paddingBottom: '8px',
    borderBottom: `1px solid ${today ? '#bfdbfe' : '#e5e7eb'}`,
  }),
  dayName: (today) => ({
    fontSize: '11px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: today ? '#2563eb' : '#6b7280',
  }),
  dayNumber: (today) => ({
    fontSize: '22px',
    fontWeight: '700',
    color: today ? '#1d4ed8' : '#111827',
    lineHeight: '1.2',
  }),
  empty: {
    fontSize: '12px',
    color: '#9ca3af',
    textAlign: 'center',
    paddingTop: '12px',
    fontStyle: 'italic',
  },
};

export default function DayColumn({ date, slots, onBook, onCancel, isBooking }) {
  const today = isToday(date);

  return (
    <div style={styles.column(today)}>
      <div style={styles.header(today)}>
        <div style={styles.dayName(today)}>{format(date, 'EEE')}</div>
        <div style={styles.dayNumber(today)}>{format(date, 'd')}</div>
      </div>

      {slots.length === 0 ? (
        <div style={styles.empty}>No sessions</div>
      ) : (
        slots.map((slot) => (
          <SlotCard
            key={slot.slot_id}
            slot={slot}
            onBook={onBook}
            onCancel={onCancel}
            isBooking={isBooking}
          />
        ))
      )}
    </div>
  );
}
