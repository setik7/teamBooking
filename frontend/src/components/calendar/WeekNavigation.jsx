import { format, addDays } from 'date-fns';

const styles = {
  bar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 0',
    marginBottom: '16px',
    borderBottom: '2px solid #e5e7eb',
  },
  group: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  dateRange: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#111827',
    minWidth: '220px',
    textAlign: 'center',
  },
  btn: {
    padding: '8px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    background: '#fff',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#374151',
    fontWeight: '500',
    transition: 'background 0.15s',
  },
  todayBtn: {
    padding: '8px 16px',
    border: '1px solid #3b82f6',
    borderRadius: '6px',
    background: '#3b82f6',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#fff',
    fontWeight: '500',
  },
};

export default function WeekNavigation({ weekStart, onPrev, onNext, onToday }) {
  const weekEnd = addDays(weekStart, 6);

  const startMonth = format(weekStart, 'MMM');
  const endMonth = format(weekEnd, 'MMM');
  const year = format(weekEnd, 'yyyy');

  const dateRange =
    startMonth === endMonth
      ? `${format(weekStart, 'MMM d')} \u2013 ${format(weekEnd, 'd, yyyy')}`
      : `${format(weekStart, 'MMM d')} \u2013 ${format(weekEnd, 'MMM d, yyyy')}`;

  return (
    <div style={styles.bar}>
      <div style={styles.group}>
        <button style={styles.btn} onClick={onPrev}>&lsaquo; Prev</button>
      </div>

      <span style={styles.dateRange}>{dateRange}</span>

      <div style={styles.group}>
        <button style={styles.todayBtn} onClick={onToday}>Today</button>
        <button style={styles.btn} onClick={onNext}>Next &rsaquo;</button>
      </div>
    </div>
  );
}
