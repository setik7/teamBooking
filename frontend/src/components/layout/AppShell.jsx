import NavBar from './NavBar';

export default function AppShell({ children }) {
  const shellStyle = {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
    background: '#f9fafb',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const mainStyle = {
    flex: 1,
    width: '100%',
  };

  const contentStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px 24px',
  };

  return (
    <div style={shellStyle}>
      <NavBar />
      <main style={mainStyle}>
        <div style={contentStyle}>{children}</div>
      </main>
    </div>
  );
}
