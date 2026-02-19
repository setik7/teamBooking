import { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { usePlans } from '../hooks/usePlans';
import { useToast } from '../hooks/useToast';
import Toast from '../components/common/Toast';
import LoadingSpinner from '../components/common/LoadingSpinner';

const TOKEN_PACK = { amount: 5, price_eur: 25 };

export default function PlansPage() {
  const { plans, isLoading, subscribeMutation, buyTokensMutation, fulfillMutation } = usePlans();
  const { toast, showToast, hideToast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const fulfilledRef = useRef(false);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const success = searchParams.get('success') === '1';

    if (success && sessionId && !fulfilledRef.current) {
      fulfilledRef.current = true;
      fulfillMutation.mutate(sessionId, {
        onSuccess: (data) => {
          if (data?.status === 'already_fulfilled') {
            showToast('Payment already processed.', 'info');
          } else if (data?.type === 'subscription') {
            showToast(`Subscription activated: ${data.plan}!`, 'success');
          } else if (data?.type === 'tokens') {
            showToast(`${data.amount} tokens added to your account!`, 'success');
          } else {
            showToast('Payment successful!', 'success');
          }
          setSearchParams({}, { replace: true });
        },
        onError: () => {
          showToast('Payment received but activation failed. Please contact support.', 'error');
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
    margin: '0 0 6px 0',
    textAlign: 'center',
  };

  const subHeadStyle = {
    fontSize: '16px',
    color: '#6b7280',
    textAlign: 'center',
    margin: '0 0 40px 0',
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '20px',
    marginBottom: '48px',
  };

  const sectionTitleStyle = {
    fontSize: '20px',
    fontWeight: 700,
    color: '#111827',
    marginBottom: '16px',
  };

  const tokenCardStyle = {
    background: '#fff',
    borderRadius: '14px',
    border: '1px solid #e5e7eb',
    padding: '28px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '16px',
    flexWrap: 'wrap',
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
  };

  const tokenInfoStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  };

  const tokenTitleStyle = {
    fontSize: '17px',
    fontWeight: 700,
    color: '#111827',
  };

  const tokenSubStyle = {
    fontSize: '14px',
    color: '#6b7280',
  };

  const buyBtnStyle = {
    padding: '11px 28px',
    borderRadius: '9px',
    border: 'none',
    background: '#16a34a',
    color: '#fff',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    opacity: buyTokensMutation.isPending ? 0.7 : 1,
  };

  if (isLoading) {
    return (
      <div style={pageStyle}>
        <h1 style={headingStyle}>Choose a Plan</h1>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div style={pageStyle}>
      <h1 style={headingStyle}>Choose a Plan</h1>
      <p style={subHeadStyle}>
        Flexible monthly plans for teams of any size.
      </p>

      <div style={gridStyle}>
        {plans.map((plan) => {
          const isPopular = plan.name === 'Standard';
          const isUnlimited = plan.trainings_per_month >= 999;

          const cardStyle = {
            background: '#fff',
            borderRadius: '16px',
            border: isPopular ? '2px solid #2563eb' : '1px solid #e5e7eb',
            padding: '28px 24px',
            position: 'relative',
            boxShadow: isPopular
              ? '0 4px 20px rgba(37,99,235,0.15)'
              : '0 1px 4px rgba(0,0,0,0.06)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          };

          const badgeStyle = {
            position: 'absolute',
            top: '-13px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#2563eb',
            color: '#fff',
            fontSize: '12px',
            fontWeight: 700,
            padding: '4px 14px',
            borderRadius: '20px',
            letterSpacing: '0.04em',
            whiteSpace: 'nowrap',
          };

          const planNameStyle = {
            fontSize: '20px',
            fontWeight: 800,
            color: '#111827',
            marginTop: isPopular ? '8px' : 0,
          };

          const priceStyle = {
            fontSize: '36px',
            fontWeight: 800,
            color: isPopular ? '#2563eb' : '#111827',
            lineHeight: 1,
          };

          const priceSubStyle = {
            fontSize: '14px',
            color: '#6b7280',
            fontWeight: 400,
          };

          const featureStyle = {
            fontSize: '15px',
            color: '#374151',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          };

          const checkStyle = {
            color: '#22c55e',
            fontWeight: 700,
            fontSize: '16px',
          };

          const subscribeBtnStyle = {
            marginTop: 'auto',
            padding: '12px',
            borderRadius: '9px',
            border: 'none',
            background: isPopular ? '#2563eb' : '#f3f4f6',
            color: isPopular ? '#fff' : '#374151',
            fontSize: '15px',
            fontWeight: 700,
            cursor: 'pointer',
            opacity: subscribeMutation.isPending ? 0.7 : 1,
            width: '100%',
          };

          return (
            <div key={plan.id} style={cardStyle}>
              {isPopular && <div style={badgeStyle}>Most Popular</div>}
              <div style={planNameStyle}>{plan.name}</div>
              <div>
                <span style={priceStyle}>€{plan.price_eur}</span>
                <span style={priceSubStyle}> / month</span>
              </div>
              <div style={featureStyle}>
                <span style={checkStyle}>✓</span>
                {isUnlimited
                  ? 'Unlimited trainings per month'
                  : `${plan.trainings_per_month} trainings per month`}
              </div>
              <div style={featureStyle}>
                <span style={checkStyle}>✓</span>
                Full calendar access
              </div>
              <div style={featureStyle}>
                <span style={checkStyle}>✓</span>
                Token top-ups available
              </div>
              <button
                style={subscribeBtnStyle}
                onClick={() => subscribeMutation.mutate(plan.id)}
                disabled={subscribeMutation.isPending}
              >
                {subscribeMutation.isPending ? 'Processing...' : 'Subscribe'}
              </button>
            </div>
          );
        })}
      </div>

      <div>
        <h2 style={sectionTitleStyle}>Need extra trainings?</h2>
        <div style={tokenCardStyle}>
          <div style={tokenInfoStyle}>
            <div style={tokenTitleStyle}>Token Pack &mdash; {TOKEN_PACK.amount} tokens</div>
            <div style={tokenSubStyle}>
              Use tokens to book trainings beyond your monthly limit.
              Each token = 1 training session.
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
            <span style={{ fontSize: '22px', fontWeight: 800, color: '#111827' }}>
              €{TOKEN_PACK.price_eur}
            </span>
            <button
              style={buyBtnStyle}
              onClick={() => buyTokensMutation.mutate(TOKEN_PACK.amount)}
              disabled={buyTokensMutation.isPending}
            >
              {buyTokensMutation.isPending
                ? 'Processing...'
                : `Buy ${TOKEN_PACK.amount} tokens`}
            </button>
          </div>
        </div>
      </div>

      {toast.visible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
}
