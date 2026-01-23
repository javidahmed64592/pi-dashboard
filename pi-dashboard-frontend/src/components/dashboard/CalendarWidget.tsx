"use client";

import { useState } from "react";

export default function CalendarWidget() {
  const [currentMonth, setCurrentMonth] = useState("January 2026");

  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const days = Array.from({ length: 31 }, (_, i) => i + 1);

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-neon-purple font-mono">
          CALENDAR
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentMonth("December 2025")}
            className="px-2 py-1 text-xs font-mono text-text-primary hover:text-neon-purple transition-colors"
          >
            ←
          </button>
          <span className="text-sm font-mono text-text-primary">
            {currentMonth}
          </span>
          <button
            onClick={() => setCurrentMonth("February 2026")}
            className="px-2 py-1 text-xs font-mono text-text-primary hover:text-neon-purple transition-colors"
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
        {[1, 2, 3].map(i => (
          <div key={`empty-${i}`} />
        ))}
        {days.map(day => (
          <div
            key={day}
            className={`text-center text-xs font-mono py-2 rounded cursor-pointer transition-all ${
              day === 23
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
