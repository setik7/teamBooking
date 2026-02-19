import { addDays, format, isSameDay } from 'date-fns';
import DayColumn from './DayColumn';

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(7, 1fr)',
    gap: '8px',
    alignItems: 'start',
  },
};

export default function WeekCalendar({ slots, weekStart, onBook, onCancel, isBooking }) {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  return (
    <div style={styles.grid}>
      {days.map((day) => {
        const daySlots = slots.filter((slot) => isSameDay(new Date(slot.date), day));
        return (
          <DayColumn
            key={format(day, 'yyyy-MM-dd')}
            date={day}
            slots={daySlots}
            onBook={onBook}
            onCancel={onCancel}
            isBooking={isBooking}
          />
        );
      })}
    </div>
  );
}
