import { NavLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import UserMenu from './UserMenu';
import api from '../../services/api';

const NAV_LINKS = [
  { to: '/calendar', label: 'Calendar' },
  { to: '/subscription', label: 'Subscription' },
  { to: '/plans', label: 'Plans' },
];

export default function NavBar() {
  const { user, logout } = useAuth();

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => api.get('/subscriptions/me').then((r) => r.data),
    enabled: !!user,
    staleTime: 30_000,
  });

  const headerStyle = {
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    background: '#ffffff',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
    borderBottom: '1px solid #f3f4f6',
  };

  const innerStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 24px',
    height: '60px',
    display: 'flex',
    alignItems: 'center',
    gap: '24px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const logoStyle = {
    fontSize: '18px',
    fontWeight: 800,
    color: '#2563eb',
    textDecoration: 'none',
    letterSpacing: '-0.5px',
    flexShrink: 0,
  };

  const navStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    flex: 1,
  };

  const getLinkStyle = ({ isActive }) => ({
    display: 'inline-block',
    padding: '6px 14px',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: isActive ? 600 : 500,
    color: isActive ? '#2563eb' : '#6b7280',
    background: isActive ? '#eff6ff' : 'transparent',
    textDecoration: 'none',
    transition: 'background 0.15s, color 0.15s',
  });

  const rightStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginLeft: 'auto',
    flexShrink: 0,
  };

  const tokenBadgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '5px',
    padding: '4px 12px',
    borderRadius: '20px',
    background: '#f0fdf4',
    border: '1px solid #86efac',
    color: '#166534',
    fontSize: '13px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  };

  const tokenBalance = subscription?.tokens_balance ?? 0;
  const trainingsLeft = subscription?.trainings_remaining ?? 0;

  const trainingBadgeStyle = {
    ...tokenBadgeStyle,
    background: '#eff6ff',
    border: '1px solid #93c5fd',
    color: '#1e40af',
  };

  return (
    <header style={headerStyle}>
      <div style={innerStyle}>
        <NavLink to="/" style={logoStyle}>
          TeamBooking
        </NavLink>

        <nav style={navStyle}>
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink key={to} to={to} style={getLinkStyle}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={rightStyle}>
          {subscription && (
            <div style={trainingBadgeStyle}>
              <span>&#128170;</span>
              <span>{trainingsLeft} trainings</span>
            </div>
          )}
          <div style={tokenBadgeStyle}>
            <span>&#9733;</span>
            <span>{tokenBalance} tokens</span>
          </div>
          {user && <UserMenu user={user} onLogout={logout} />}
        </div>
      </div>
    </header>
  );
}
