import React, { useState } from 'react';
import { 
  Calendar, Clock, MoreVertical, 
  ChevronLeft, ChevronRight, Plus
} from 'lucide-react';

const WeeklyCalendar = ({ 
  selectedDate, 
  appointments, 
  onDateChange, 
  onAppointmentClick,
  onAddAppointment 
}) => {
  const [timeRange, setTimeRange] = useState({ start: 8, end: 16 }); // Default 8 AM to 4 PM
  const [showCustomTimeModal, setShowCustomTimeModal] = useState(false);
  const [customTimeRange, setCustomTimeRange] = useState({ start: 8, end: 16 });
  
  // Get week dates
  const getWeekDates = () => {
    const dates = [];
    const startOfWeek = new Date(selectedDate);
    startOfWeek.setDate(selectedDate.getDate() - selectedDate.getDay());
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  // Get time slots based on selected range
  const timeSlots = Array.from({ length: timeRange.end - timeRange.start + 1 }, (_, i) => {
    const hour = i + timeRange.start;
    return {
      hour,
      label: `${hour === 12 ? 12 : hour % 12}:00 ${hour < 12 ? 'AM' : 'PM'}`
    };
  });

  const weekDates = getWeekDates();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Process appointments for display
  const processAppointmentsForDay = (date) => {
    const dayAppointments = appointments.filter(apt => {
      const aptDate = new Date(apt.date);
      return aptDate.toDateString() === date.toDateString();
    });

    // Sort by time and handle overlaps
    const sorted = dayAppointments.sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    const columns = [];
    sorted.forEach(apt => {
      const start = new Date(apt.date).getTime();
      const end = start + apt.duration * 60 * 1000;
      
      let placed = false;
      for (let i = 0; i < columns.length; i++) {
        if (columns[i].every(existing => {
          const existingEnd = new Date(existing.date).getTime() + existing.duration * 60 * 1000;
          return existingEnd <= start;
        })) {
          columns[i].push(apt);
          placed = true;
          break;
        }
      }
      
      if (!placed) {
        columns.push([apt]);
      }
    });

    return columns;
  };

  // Get appointment position and dimensions
  const getAppointmentStyle = (appointment, columnIndex, totalColumns) => {
    const date = new Date(appointment.date);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const top = ((hours - timeRange.start) * 60 + minutes) * (100 / 60); // 100px per hour
    const height = appointment.duration * (100 / 60) - 2;
    const width = `${100 / totalColumns}%`;
    const left = `${(columnIndex * 100) / totalColumns}%`;

    return {
      top: `${top}px`,
      height: `${height}px`,
      width: width,
      left: left,
      position: 'absolute'
    };
  };

  // Get status colors
  const getStatusColor = (status) => {
    const colors = {
      scheduled: 'bg-blue-500',
      confirmed: 'bg-green-500',
      completed: 'bg-gray-400',
      cancelled: 'bg-red-400 opacity-60'
    };
    return colors[status] || colors.scheduled;
  };

  // Navigate week
  const navigateWeek = (direction) => {
    const newDate = new Date(selectedDate);
    newDate.setDate(selectedDate.getDate() + (direction * 7));
    onDateChange(newDate);
  };

  return (
    <>
      {/* Calendar Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-t-2xl">
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigateWeek(-1)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-semibold">
              {weekDates[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {' '}
              {weekDates[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </h2>
            <button
              onClick={() => navigateWeek(1)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center gap-3">
            <select
              value={`${timeRange.start}-${timeRange.end}`}
              onChange={(e) => {
                if (e.target.value === 'custom') {
                  setShowCustomTimeModal(true);
                } else {
                  const [start, end] = e.target.value.split('-').map(Number);
                  setTimeRange({ start, end });
                }
              }}
              className="px-3 py-1.5 bg-white/20 text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-white/50 backdrop-blur-sm"
            >
              <option value="8-16" className="text-gray-900">8:00 AM - 4:00 PM</option>
              <option value="9-17" className="text-gray-900">9:00 AM - 5:00 PM</option>
              <option value="10-18" className="text-gray-900">10:00 AM - 6:00 PM</option>
              <option value="0-23" className="text-gray-900">All Day</option>
              <option value="custom" className="text-gray-900">Custom</option>
            </select>
            
            <button
              onClick={() => onDateChange(new Date())}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-sm font-medium"
            >
              Today
            </button>
            <button
              onClick={onAddAppointment}
              className="flex items-center gap-2 px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-b-2xl shadow-lg overflow-hidden">
        {/* Days Header */}
        <div className="grid border-b border-gray-200" style={{ gridTemplateColumns: '80px repeat(7, 1fr)' }}>
          <div className="p-2 text-center text-sm font-medium text-gray-500">
            {/* Empty cell for time column */}
          </div>
          {weekDates.map((date, index) => {
            const isToday = date.toDateString() === today.toDateString();
            const dayAppointments = appointments.filter(apt => 
              new Date(apt.date).toDateString() === date.toDateString()
            );
            
            return (
              <div
                key={index}
                className={`p-4 text-center border-l border-gray-200 ${
                  isToday ? 'bg-blue-50' : ''
                }`}
              >
                <div className={`text-sm font-medium ${
                  isToday ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {date.toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className={`text-2xl font-bold mt-1 ${
                  isToday ? 'text-blue-700' : 'text-gray-900'
                }`}>
                  {date.getDate()}
                </div>
                {dayAppointments.length > 0 && (
                  <div className="text-xs text-gray-500 mt-1">
                    {dayAppointments.length} appts
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Time Grid */}
        <div className="grid" style={{ gridTemplateColumns: '80px repeat(7, 1fr)' }}>
          {/* Time Labels */}
          <div>
            {timeSlots.map((slot) => (
              <div
                key={slot.hour}
                className="h-24 border-b border-gray-100 text-right pr-3 pt-2"
              >
                <span className="text-xs text-gray-500 font-medium">{slot.label}</span>
              </div>
            ))}
          </div>

          {/* Day Columns */}
          {weekDates.map((date, dayIndex) => {
            const isToday = date.toDateString() === today.toDateString();
            const columns = processAppointmentsForDay(date);
            
            return (
              <div
                key={dayIndex}
                className={`relative border-l border-gray-200 ${
                  isToday ? 'bg-blue-50/30' : ''
                }`}
              >
                {/* Hour Slots */}
                {timeSlots.map((_, hourIndex) => (
                  <div
                    key={hourIndex}
                    className="h-24 border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
                  />
                ))}

                {/* Appointments */}
                <div className="absolute inset-0">
                  {columns.map((column, columnIndex) => 
                    column.map(appointment => {
                      const aptHour = new Date(appointment.date).getHours();
                      // Only show appointments within the selected time range
                      if (aptHour < timeRange.start || aptHour >= timeRange.end) {
                        return null;
                      }
                      
                      const style = getAppointmentStyle(
                        appointment, 
                        columnIndex, 
                        columns.length
                      );
                      
                      // Extract height value for conditional rendering
                      const heightValue = parseInt(style.height);
                      
                      return (
                        <div
                          key={appointment.id}
                          onClick={() => onAppointmentClick(appointment)}
                          className={`absolute px-2 py-1.5 rounded-md cursor-pointer transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:z-20 ${
                            getStatusColor(appointment.status)
                          } text-white group animate-slideIn overflow-hidden`}
                          style={{
                            ...style,
                            left: `calc(${style.left} + 2px)`,
                            width: `calc(${style.width} - 4px)`
                          }}
                        >
                          <div className="flex flex-col h-full">
                            <div className="flex items-center justify-between mb-0.5">
                              <div className="font-bold text-xs truncate">
                                {appointment.time}
                              </div>
                              {appointment.episodeId && (
                                <div className="w-2 h-2 bg-white/60 rounded-full flex-shrink-0 ml-1" />
                              )}
                            </div>
                            <div className="text-[11px] font-semibold truncate">
                              {appointment.patientName.split(' ').slice(0, 2).join(' ')}
                            </div>
                            {heightValue > 35 && (
                              <div className="text-[10px] opacity-90 capitalize truncate mt-0.5">
                                {appointment.type}
                              </div>
                            )}
                            {heightValue > 70 && appointment.reason && (
                              <div className="text-[9px] opacity-75 truncate mt-auto">
                                {appointment.reason}
                              </div>
                            )}
                          </div>
                          
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              onAppointmentClick(appointment);
                            }}
                            className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-white/20 rounded"
                          >
                            <MoreVertical className="w-3 h-3" />
                          </button>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Current Time Indicator */}
                {isToday && (() => {
                  const now = new Date();
                  const currentHour = now.getHours();
                  const currentMinute = now.getMinutes();
                  
                  if (currentHour >= timeRange.start && currentHour < timeRange.end) {
                    const top = ((currentHour - timeRange.start) * 100 + (currentMinute / 60) * 100);
                    return (
                      <div
                        className="absolute left-0 right-0 border-t-2 border-red-500 pointer-events-none z-10"
                        style={{ top: `${top}px` }}
                      >
                        <div className="absolute -left-2 -top-2 w-4 h-4 bg-red-500 rounded-full" />
                      </div>
                    );
                  }
                  return null;
                })()}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Custom Time Modal */}
      {showCustomTimeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Custom Time Range</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                <select
                  value={customTimeRange.start}
                  onChange={(e) => setCustomTimeRange({ ...customTimeRange, start: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {Array.from({ length: 24 }, (_, i) => (
                    <option key={i} value={i}>
                      {i === 0 ? '12:00 AM' : i < 12 ? `${i}:00 AM` : i === 12 ? '12:00 PM' : `${i - 12}:00 PM`}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                <select
                  value={customTimeRange.end}
                  onChange={(e) => setCustomTimeRange({ ...customTimeRange, end: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {Array.from({ length: 24 }, (_, i) => (
                    <option key={i} value={i}>
                      {i === 0 ? '12:00 AM' : i < 12 ? `${i}:00 AM` : i === 12 ? '12:00 PM' : `${i - 12}:00 PM`}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => {
                    setTimeRange(customTimeRange);
                    setShowCustomTimeModal(false);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Apply
                </button>
                <button
                  onClick={() => setShowCustomTimeModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default WeeklyCalendar;