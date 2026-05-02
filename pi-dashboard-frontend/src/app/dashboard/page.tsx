"use client";

import ContainerWidget from "@/components/dashboard/ContainerWidget";
import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-10 gap-4">
      <div className="lg:col-span-4 space-y-4">
        <SystemInfoWidget />
        <MiniSystemSummary />
      </div>

      <div className="lg:col-span-4 space-y-4">
        <ContainerWidget />
      </div>

      <div className="lg:col-span-2 space-y-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-2">Placeholder Widget</h2>
          <p className="text-gray-600">
            This is a placeholder for future widgets or features.
          </p>
        </div>
      </div>
    </div>
  );
}
