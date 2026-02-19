import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useSubscription } from '../hooks/useSubscription';
import { usePlans } from '../hooks/usePlans';
import { useToast } from '../hooks/useToast';
import Toast from '../components/common/Toast';
import LoadingSpinner from '../components/common/LoadingSpinner';

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function ProgressBar({ value, max, label }) {
  const isUnlimited = max >= 999;
  const pct = isUnlimited ? 100 : Math.min(100, Math.round((value / max) * 100));
  const remaining = isUnlimited ? 'Unlimited' : `${max - value} remaining`;

  const barTrackStyle = {
    height: '10px',
    borderRadius: '99px',
    background: '#e5e7eb',
    overflow: 'hidden',
    margin: '8px 0 4px',
  };

  const barFillStyle = {
    height: '100%',
    width: isUnlimited ? '100%' : `${pct}%`,
    background: isUnlimited ? '#22c55e' : pct > 80 ? '#ef4444' : '#2563eb',
    borderRadius: '99px',
    transition: 'width 0.4s ease',
  };

  const labelRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
    color: '#6b7280',
  };

  return (
    <div>
      <div style={labelRowStyle}>
        <span>{label}</span>
        <span>{remaining}</span>
      </div>
      <div style={barTrackStyle}>
        <div style={barFillStyle} />
      </div>
      <div style={{ fontSize: '12px', color: '#9ca3af' }}>
        {isUnlimited ? 'Unlimited trainings' : `${value} used of ${max}`}
      </div>
    </div>
  );
}

export default function SubscriptionPage() {
  const navigate = useNavigate();
  const { subscription, tokens, isLoading } = useSubscription();
  const { fulfillMutation } = usePlans();
  const { toast, showToast, hideToast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const fulfilledRef = useRef(false);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const success = searchParams.get('tokens_success') === '1';

    if (success && sessionId && !fulfilledRef.current) {
      fulfilledRef.current = true;
      fulfillMutation.mutate(sessionId, {
        onSuccess: (data) => {
          if (data?.type === 'tokens') {
            showToast(`${data.amount} tokens added!`, 'success');
          } else {
            showToast('Payment processed!', 'success');
          }
          setSearchParams({}, { replace: true });
        },
        onError: () => {
          showToast('Activation failed. Please contact support.', 'error');
        },
      });
    } else if (searchParams.get('cancelled') === '1') {
      showToast('Payment was cancelled.', 'info');
      setSearchParams({}, { replace: true });
    }
  }, [searchParams]);

  const pageStyle = {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const headingStyle = {
    fontSize: '26px',
    fontWeight: 800,
    color: '#111827',
    margin: '0 0 24px 0',
  };

  const cardStyle = {
    background: '#fff',
    borderRadius: '14px',
    border: '1px solid #e5e7eb',
    padding: '28px',
    marginBottom: '24px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
  };

  const cardTitleStyle = {
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    color: '#9ca3af',
    marginBottom: '16px',
  };

  const planNameStyle = {
    fontSize: '28px',
    fontWeight: 800,
    color: '#111827',
    marginBottom: '4px',
  };

  const priceStyle = {
    fontSize: '16px',
    color: '#6b7280',
    marginBottom: '20px',
  };

  const tokenBalanceStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  };

  const tokenNumberStyle = {
    fontSize: '40px',
    fontWeight: 800,
    color: '#2563eb',
    lineHeight: 1,
  };

  const tokenLabelStyle = {
    fontSize: '15px',
    color: '#6b7280',
    fontWeight: 500,
  };

  const buyBtnStyle = {
    display: 'inline-block',
    marginTop: '20px',
    padding: '10px 24px',
    borderRadius: '9px',
    border: 'none',
    background: '#2563eb',
    color: '#fff',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px',
  };

  const thStyle = {
    padding: '10px 14px',
    textAlign: 'left',
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: '#9ca3af',
    borderBottom: '1px solid #f3f4f6',
  };

  const tdStyle = {
    padding: '12px 14px',
    borderBottom: '1px solid #f9fafb',
    color: '#374151',
  };

  const emptyStyle = {
    textAlign: 'center',
    padding: '40px',
    color: '#9ca3af',
  };

  const noSubStyle = {
    textAlign: 'center',
    padding: '60px 24px',
    background: '#fff',
    borderRadius: '14px',
    border: '1px solid #e5e7eb',
  };

  const noSubHeadStyle = {
    fontSize: '20px',
    fontWeight: 700,
    color: '#111827',
    marginBottom: '10px',
  };

  const noSubTextStyle = {
    color: '#6b7280',
    fontSize: '15px',
    marginBottom: '20px',
  };

  const linkBtnStyle = {
    display: 'inline-block',
    padding: '10px 26px',
    borderRadius: '9px',
    border: 'none',
    background: '#2563eb',
    color: '#fff',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    textDecoration: 'none',
  };

  if (isLoading) {
    return (
      <div style={pageStyle}>
        <h1 style={headingStyle}>Subscription</h1>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!subscription) {
    return (
      <div style={pageStyle}>
        <h1 style={headingStyle}>Subscription</h1>
        <div style={noSubStyle}>
          <div style={noSubHeadStyle}>No active subscription</div>
          <p style={noSubTextStyle}>
            Get started with a plan to book trainings and manage your team.
          </p>
          <button style={linkBtnStyle} onClick={() => navigate('/plans')}>
            View Plans
          </button>
        </div>
      </div>
    );
  }

  const totalTrainings = subscription.plan?.trainings_per_month ?? 0;
  const remaining = subscription.trainings_remaining ?? 0;
  const usedTrainings = totalTrainings - remaining;
  const tokenBalance = subscription.tokens_balance ?? 0;
  const tokenHistory = Array.isArray(tokens) ? tokens : [];

  return (
    <div style={pageStyle}>
      <h1 style={headingStyle}>Subscription</h1>

      <div style={cardStyle}>
        <div style={cardTitleStyle}>Current Plan</div>
        <div style={planNameStyle}>{subscription.plan?.name ?? 'Unknown Plan'}</div>
        <div style={priceStyle}>
          €{subscription.plan?.price_eur ?? '—'} / month
          {subscription.period_end && (
            <span> &middot; Renews {formatDate(subscription.period_end)}</span>
          )}
        </div>
        <ProgressBar
          value={usedTrainings}
          max={totalTrainings}
          label="Trainings this month"
        />
      </div>

      <div style={cardStyle}>
        <div style={cardTitleStyle}>Token Balance</div>
        <div style={tokenBalanceStyle}>
          <div style={tokenNumberStyle}>{tokenBalance}</div>
          <div style={tokenLabelStyle}>tokens available</div>
        </div>
        <button style={buyBtnStyle} onClick={() => navigate('/plans')}>
          Buy Tokens
        </button>
      </div>

      <div style={cardStyle}>
        <div style={cardTitleStyle}>Token History</div>
        {tokenHistory.length === 0 ? (
          <div style={emptyStyle}>No token transactions yet.</div>
        ) : (
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Date</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Amount</th>
                <th style={thStyle}>Reason</th>
              </tr>
            </thead>
            <tbody>
              {tokenHistory.map((entry, idx) => {
                const isPositive = entry.amount > 0;
                const amountStyle = {
                  ...tdStyle,
                  textAlign: 'right',
                  fontWeight: 600,
                  color: isPositive ? '#16a34a' : '#dc2626',
                };
                return (
                  <tr key={entry.id ?? idx}>
                    <td style={tdStyle}>{formatDate(entry.created_at)}</td>
                    <td style={amountStyle}>
                      {isPositive ? '+' : ''}{entry.amount}
                    </td>
                    <td style={tdStyle}>{entry.reason ?? '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {toast.visible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
}
