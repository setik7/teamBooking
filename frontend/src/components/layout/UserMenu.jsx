function getInitials(user) {
  if (!user) return '?';
  if (user.full_name) {
    return user.full_name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
  if (user.email) return user.email[0].toUpperCase();
  return '?';
}

export default function UserMenu({ user, onLogout }) {
  const wrapperStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const avatarStyle = {
    width: 36,
    height: 36,
    borderRadius: '50%',
    overflow: 'hidden',
    background: '#2563eb',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    fontWeight: 700,
    fontSize: '14px',
    flexShrink: 0,
  };

  const nameStyle = {
    fontSize: '14px',
    fontWeight: 500,
    color: '#374151',
    maxWidth: '140px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  };

  const logoutBtnStyle = {
    padding: '6px 14px',
    borderRadius: '7px',
    border: '1px solid #e5e7eb',
    background: '#fff',
    color: '#6b7280',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background 0.15s',
    whiteSpace: 'nowrap',
  };

  const displayName = user?.full_name || user?.email || 'User';

  return (
    <div style={wrapperStyle}>
      <div style={avatarStyle} title={displayName}>
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={displayName}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          getInitials(user)
        )}
      </div>
      <span style={nameStyle} title={displayName}>
        {displayName}
      </span>
      <button
        style={logoutBtnStyle}
        onClick={onLogout}
        onMouseEnter={(e) => (e.currentTarget.style.background = '#f9fafb')}
        onMouseLeave={(e) => (e.currentTarget.style.background = '#fff')}
      >
        Logout
      </button>
    </div>
  );
}
