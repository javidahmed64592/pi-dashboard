"use client";

import { useState } from "react";

import ContainerWidget from "@/components/dashboard/ContainerWidget";
import LogsPanel from "@/components/dashboard/LogsPanel";
import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";
import type { LogSource } from "@/lib/types";

export default function DashboardPage() {
  const [selectedLogSource, setSelectedLogSource] = useState<LogSource | null>(
    null
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
      <div className="lg:col-span-4 overflow-y-auto space-y-4 min-h-0">
        <SystemInfoWidget />
        <MiniSystemSummary />
      </div>
      <div className="lg:col-span-4 min-h-0">
        <ContainerWidget onViewLogs={setSelectedLogSource} />
      </div>
      <div className="lg:col-span-4 min-h-0">
        <LogsPanel source={selectedLogSource} />
      </div>
    </div>
  );
}
