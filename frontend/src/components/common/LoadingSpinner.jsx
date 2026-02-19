const sizeMap = {
  sm: 24,
  md: 40,
  lg: 64,
};

const keyframes = `
@keyframes tb-spin {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

if (typeof document !== 'undefined' && !document.getElementById('tb-spinner-styles')) {
  const style = document.createElement('style');
  style.id = 'tb-spinner-styles';
  style.textContent = keyframes;
  document.head.appendChild(style);
}

export default function LoadingSpinner({ size = 'md' }) {
  const px = sizeMap[size] ?? sizeMap.md;

  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    padding: '24px 0',
  };

  const spinnerStyle = {
    width: px,
    height: px,
    border: `${Math.max(2, Math.round(px / 10))}px solid #e5e7eb`,
    borderTop: `${Math.max(2, Math.round(px / 10))}px solid #2563eb`,
    borderRadius: '50%',
    animation: 'tb-spin 0.75s linear infinite',
  };

  return (
    <div style={containerStyle}>
      <div style={spinnerStyle} aria-label="Loading" role="status" />
    </div>
  );
}
