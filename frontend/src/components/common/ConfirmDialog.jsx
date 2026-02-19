const overlayStyle = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0,0,0,0.45)',
  zIndex: 10000,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '16px',
};

const dialogStyle = {
  background: '#fff',
  borderRadius: '12px',
  boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
  padding: '28px 32px',
  maxWidth: '440px',
  width: '100%',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const titleStyle = {
  margin: '0 0 10px 0',
  fontSize: '18px',
  fontWeight: 700,
  color: '#111827',
};

const messageStyle = {
  margin: '0 0 24px 0',
  fontSize: '15px',
  color: '#4b5563',
  lineHeight: 1.6,
};

const actionsStyle = {
  display: 'flex',
  justifyContent: 'flex-end',
  gap: '10px',
};

const cancelBtnStyle = {
  padding: '9px 20px',
  borderRadius: '8px',
  border: '1px solid #d1d5db',
  background: '#fff',
  color: '#374151',
  fontSize: '14px',
  fontWeight: 500,
  cursor: 'pointer',
};

const confirmBtnStyle = {
  padding: '9px 20px',
  borderRadius: '8px',
  border: 'none',
  background: '#2563eb',
  color: '#fff',
  fontSize: '14px',
  fontWeight: 600,
  cursor: 'pointer',
};

export default function ConfirmDialog({
  title = 'Are you sure?',
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Confirm',
}) {
  return (
    <div style={overlayStyle} onClick={onCancel} role="dialog" aria-modal="true">
      <div style={dialogStyle} onClick={(e) => e.stopPropagation()}>
        <h3 style={titleStyle}>{title}</h3>
        {message && <p style={messageStyle}>{message}</p>}
        <div style={actionsStyle}>
          <button style={cancelBtnStyle} onClick={onCancel}>
            Cancel
          </button>
          <button style={confirmBtnStyle} onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
