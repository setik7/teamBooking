const STATE = {
  BOOKED: 'booked',
  FULL: 'full',
  AVAILABLE: 'available',
};

function getState(slot) {
  if (slot.is_booked_by_user) return STATE.BOOKED;
  if (slot.participants_count >= slot.max_participants) return STATE.FULL;
  return STATE.AVAILABLE;
}

const cardBase = {
  borderRadius: '6px',
  padding: '8px 10px',
  fontSize: '13px',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
  border: '1px solid transparent',
};

const stateStyles = {
  [STATE.BOOKED]: {
    card: { ...cardBase, background: '#d1fae5', border: '1px solid #6ee7b7' },
    label: { color: '#065f46', fontWeight: '600' },
    count: { color: '#047857' },
  },
  [STATE.FULL]: {
    card: { ...cardBase, background: '#f3f4f6', border: '1px solid #d1d5db' },
    label: { color: '#6b7280', fontWeight: '600' },
    count: { color: '#9ca3af' },
  },
  [STATE.AVAILABLE]: {
    card: { ...cardBase, background: '#fff', border: '1px solid #e5e7eb' },
    label: { color: '#111827', fontWeight: '600' },
    count: { color: '#374151' },
  },
};

const styles = {
  activityRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
  },
  icon: {
    fontSize: '14px',
    lineHeight: '1',
  },
  name: {
    fontSize: '13px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  time: {
    fontSize: '12px',
    color: '#6b7280',
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: '2px',
  },
  count: {
    fontSize: '12px',
  },
  btnBook: {
    padding: '3px 10px',
    fontSize: '12px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    background: '#3b82f6',
    color: '#fff',
  },
  btnCancel: {
    padding: '3px 10px',
    fontSize: '12px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    background: '#10b981',
    color: '#fff',
  },
  btnDisabled: {
    padding: '3px 10px',
    fontSize: '12px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '4px',
    cursor: 'not-allowed',
    background: '#d1d5db',
    color: '#9ca3af',
  },
};

export default function SlotCard({ slot, onBook, onCancel, isBooking }) {
  const state = getState(slot);
  const theme = stateStyles[state];

  const timeRange = `${slot.start_time.slice(0, 5)} \u2013 ${slot.end_time.slice(0, 5)}`;
  const participantsLabel = `${slot.participants_count}/${slot.max_participants}`;

  return (
    <div style={theme.card}>
      <div style={styles.activityRow}>
        {slot.activity?.icon && (
          <span style={styles.icon}>{slot.activity.icon}</span>
        )}
        <span style={{ ...styles.name, ...theme.label }}>
          {slot.activity?.name ?? 'Session'}
        </span>
      </div>

      <div style={styles.time}>{timeRange}</div>

      <div style={styles.footer}>
        <span style={{ ...styles.count, ...theme.count }}>
          {participantsLabel}
        </span>

        {state === STATE.BOOKED && (
          <button
            style={styles.btnCancel}
            disabled={isBooking}
            onClick={() => onCancel(slot.booking_id)}
          >
            Cancel
          </button>
        )}

        {state === STATE.FULL && (
          <button style={styles.btnDisabled} disabled>
            Full
          </button>
        )}

        {state === STATE.AVAILABLE && (
          <button
            style={styles.btnBook}
            disabled={isBooking}
            onClick={() => onBook(slot.slot_id, slot.date)}
          >
            Book
          </button>
        )}
      </div>
    </div>
  );
}
