"use client";

import CalendarWidget from "@/components/dashboard/CalendarWidget";
import ContainerWidget from "@/components/dashboard/ContainerWidget";
import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import NotesWidget from "@/components/dashboard/NotesWidget";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";
import WeatherWidget from "@/components/dashboard/WeatherWidget";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
      {/* Column 1: System Info, Summary and Notes - 5/12 width */}
      <div className="lg:col-span-5 space-y-4">
        <SystemInfoWidget />
        <MiniSystemSummary />
        <NotesWidget />
      </div>

      {/* Column 2: Weather and Calendar - 3/12 width */}
      <div className="lg:col-span-3 space-y-4">
        <WeatherWidget />
        <CalendarWidget />
      </div>

      {/* Column 3: Containers (full height) - 4/12 width */}
      <div className="lg:col-span-4">
        <ContainerWidget />
      </div>
    </div>
  );
}
