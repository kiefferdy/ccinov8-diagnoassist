import React from 'react';
import DashboardNav from './DashboardNav';

const DashboardLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNav />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
