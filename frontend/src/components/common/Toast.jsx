import { useEffect } from 'react';

const TYPE_COLORS = {
  success: { bg: '#f0fdf4', border: '#86efac', text: '#166534', icon: '✓' },
  error:   { bg: '#fef2f2', border: '#fca5a5', text: '#991b1b', icon: '✕' },
  info:    { bg: '#eff6ff', border: '#93c5fd', text: '#1e40af', icon: 'i' },
};

export default function Toast({ message, type = 'info', onClose }) {
  const colors = TYPE_COLORS[type] ?? TYPE_COLORS.info;

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose?.();
    }, 3000);
    return () => clearTimeout(timer);
  }, [message, onClose]);

  const containerStyle = {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    zIndex: 9999,
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    padding: '14px 18px',
    background: colors.bg,
    border: `1px solid ${colors.border}`,
    borderRadius: '10px',
    boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
    maxWidth: '360px',
    minWidth: '240px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    animation: 'tb-toast-in 0.2s ease',
  };

  const iconStyle = {
    flexShrink: 0,
    width: 22,
    height: 22,
    borderRadius: '50%',
    background: colors.border,
    color: colors.text,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '13px',
    fontWeight: 700,
    marginTop: '1px',
  };

  const messageStyle = {
    flex: 1,
    color: colors.text,
    fontSize: '14px',
    lineHeight: '1.5',
    fontWeight: 500,
  };

  const closeStyle = {
    flexShrink: 0,
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: colors.text,
    fontSize: '18px',
    lineHeight: 1,
    padding: '0 0 0 4px',
    opacity: 0.7,
  };

  return (
    <div style={containerStyle} role="alert">
      <div style={iconStyle}>{colors.icon}</div>
      <span style={messageStyle}>{message}</span>
      <button style={closeStyle} onClick={onClose} aria-label="Close notification">
        ×
      </button>
    </div>
  );
}
