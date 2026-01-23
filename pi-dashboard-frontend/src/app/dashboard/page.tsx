"use client";

import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Column (2/3 width on large screens) */}
      <div className="lg:col-span-2 space-y-6">
        <SystemInfoWidget />
        <MiniSystemSummary />
        {/* Service Cards will go here */}
      </div>

      {/* Right Column (1/3 width on large screens) */}
      <div className="space-y-6">
        {/* Weather widget will go here */}
        {/* Calendar widget will go here */}
        {/* Notes widget will go here */}
      </div>
    </div>
  );
}
