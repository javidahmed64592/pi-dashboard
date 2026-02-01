"use client";

import CalendarWidget from "@/components/dashboard/CalendarWidget";
import ContainerWidget from "@/components/dashboard/ContainerWidget";
import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import NotesWidget from "@/components/dashboard/NotesWidget";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";
import WeatherWidget from "@/components/dashboard/WeatherWidget";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-11 gap-4">
      <div className="lg:col-span-4 space-y-4">
        <SystemInfoWidget />
        <MiniSystemSummary />
        <NotesWidget />
      </div>

      <div className="lg:col-span-4 space-y-4">
        <ContainerWidget />
      </div>

      <div className="lg:col-span-3 space-y-4">
        <WeatherWidget />
        <CalendarWidget />
      </div>
    </div>
  );
}
