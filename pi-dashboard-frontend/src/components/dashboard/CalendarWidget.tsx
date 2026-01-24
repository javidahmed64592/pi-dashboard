"use client";

import { useState } from "react";

export default function CalendarWidget() {
  const today = new Date();
  const [currentDate, setCurrentDate] = useState(today);

  const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const getMonthData = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();

    // Get first day of month (0 = Sunday, 1 = Monday, etc.)
    const firstDay = new Date(year, month, 1).getDay();
    // Convert to Monday-based (0 = Monday, 6 = Sunday)
    const firstDayMondayBased = firstDay === 0 ? 6 : firstDay - 1;

    // Get last day of month
    const lastDate = new Date(year, month + 1, 0).getDate();

    return { firstDayMondayBased, lastDate };
  };

  const { firstDayMondayBased, lastDate } = getMonthData(currentDate);

  const monthName = currentDate.toLocaleString("en-US", {
    month: "long",
    year: "numeric",
  });

  const goToPreviousMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1)
    );
  };

  const goToNextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1)
    );
  };

  const goToCurrentMonth = () => {
    setCurrentDate(new Date());
  };

  const isToday = (day: number) => {
    const checkDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      day
    );
    return (
      checkDate.getDate() === today.getDate() &&
      checkDate.getMonth() === today.getMonth() &&
      checkDate.getFullYear() === today.getFullYear()
    );
  };

  const days = Array.from({ length: lastDate }, (_, i) => i + 1);

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-purple font-mono">
          CALENDAR
        </h2>
        <div className="flex items-center gap-1">
          <button
            onClick={goToPreviousMonth}
            className="px-2 py-1 text-sm font-mono text-text-primary hover:text-neon-purple transition-colors"
          >
            ←
          </button>
          <button
            onClick={goToCurrentMonth}
            className="text-sm font-mono text-text-primary hover:text-neon-purple transition-colors min-w-[120px] text-center"
          >
            {monthName}
          </button>
          <button
            onClick={goToNextMonth}
            className="px-2 py-1 text-sm font-mono text-text-primary hover:text-neon-purple transition-colors"
          >
            →
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {daysOfWeek.map(day => (
          <div
            key={day}
            className="text-center text-xs font-mono text-text-muted py-1"
          >
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {/* Empty cells for start of month */}
        {Array.from({ length: firstDayMondayBased }).map((_, i) => (
          <div key={`empty-${i}`} />
        ))}
        {days.map(day => (
          <div
            key={day}
            className={`text-center text-xs font-mono py-2 rounded cursor-pointer transition-all ${
              isToday(day)
                ? "bg-neon-purple text-background font-bold"
                : "text-text-primary hover:bg-background-tertiary"
            }`}
          >
            {day}
          </div>
        ))}
      </div>
    </div>
  );
}
