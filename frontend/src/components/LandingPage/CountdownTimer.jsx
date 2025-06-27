import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

const CountdownTimer = () => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });
  
  useEffect(() => {
    // Set end date to July 31, 2025
    const endDate = new Date('2025-07-31T23:59:59');
    
    const calculateTimeLeft = () => {
      const now = new Date();
      const difference = endDate - now;
      
      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
          minutes: Math.floor((difference / 1000 / 60) % 60),
          seconds: Math.floor((difference / 1000) % 60)
        });
      }
    };
    
    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div className="fixed bottom-8 right-8 bg-white rounded-xl shadow-2xl border border-gray-200 p-6 z-40">
      <div className="flex items-center mb-3">
        <Clock className="w-5 h-5 text-red-500 mr-2" />
        <p className="text-sm font-semibold text-gray-900">Early Bird Ends In:</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        <div>
          <div className="text-2xl font-bold text-blue-600">{timeLeft.days}</div>
          <div className="text-xs text-gray-500">Days</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{timeLeft.hours}</div>
          <div className="text-xs text-gray-500">Hours</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{timeLeft.minutes}</div>
          <div className="text-xs text-gray-500">Min</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{timeLeft.seconds}</div>
          <div className="text-xs text-gray-500">Sec</div>
        </div>
      </div>
    </div>
  );
};

export default CountdownTimer;