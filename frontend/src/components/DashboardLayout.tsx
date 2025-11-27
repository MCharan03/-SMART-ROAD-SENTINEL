import React from 'react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar - Placeholder */}
      <aside className="w-64 bg-card p-4 shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Sentinel Dashboard</h2>
        <nav>
          <ul>
            <li className="mb-2">
              <a href="#" className="block py-2 px-4 rounded hover:bg-primary hover:text-primary-foreground">Dashboard</a>
            </li>
            <li className="mb-2">
              <a href="#" className="block py-2 px-4 rounded hover:bg-primary hover:text-primary-foreground">Analytics</a>
            </li>
            <li className="mb-2">
              <a href="#" className="block py-2 px-4 rounded hover:bg-primary hover:text-primary-foreground">Settings</a>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main content area */}
      <div className="flex-1 p-6">
        {children}
      </div>
    </div>
  );
};

export default DashboardLayout;