import React from 'react';
import DashboardNav from './DashboardNav';

const DashboardLayout = ({ children, hideTopNav = false }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {!hideTopNav && <DashboardNav />}
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
