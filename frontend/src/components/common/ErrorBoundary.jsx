import { Component } from 'react';

const containerStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '300px',
  padding: '40px 24px',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  textAlign: 'center',
};

const iconStyle = {
  fontSize: '48px',
  marginBottom: '16px',
  color: '#ef4444',
};

const headingStyle = {
  fontSize: '20px',
  fontWeight: 700,
  color: '#111827',
  margin: '0 0 8px 0',
};

const subStyle = {
  fontSize: '14px',
  color: '#6b7280',
  margin: '0 0 24px 0',
};

const retryBtnStyle = {
  padding: '10px 24px',
  borderRadius: '8px',
  border: 'none',
  background: '#2563eb',
  color: '#fff',
  fontSize: '14px',
  fontWeight: 600,
  cursor: 'pointer',
};

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={containerStyle}>
          <div style={iconStyle}>⚠</div>
          <h2 style={headingStyle}>Something went wrong</h2>
          <p style={subStyle}>
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <button style={retryBtnStyle} onClick={this.handleRetry}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
