"use client";

import CalendarWidget from "@/components/dashboard/CalendarWidget";
import MiniSystemSummary from "@/components/dashboard/MiniSystemSummary";
import NotesWidget from "@/components/dashboard/NotesWidget";
import ServiceCard from "@/components/dashboard/ServiceCard";
import SystemInfoWidget from "@/components/dashboard/SystemInfoWidget";
import WeatherWidget from "@/components/dashboard/WeatherWidget";

export default function DashboardPage() {
  // Mock service data
  const services = [
    {
      name: "pi-dashboard.service",
      description: "Pi Dashboard",
      path: "/home/pi/pi-dashboard",
      status: "running" as const,
      port: 443,
    },
    {
      name: "homebridge.service",
      description: "Homebridge Server",
      path: "/home/pi/.homebridge",
      status: "running" as const,
      port: 8581,
    },
    {
      name: "plex.service",
      description: "Plex Media Server",
      path: "/var/lib/plexmediaserver",
      status: "stopped" as const,
      port: 32400,
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Column (2/3 width on large screens) */}
      <div className="lg:col-span-2 space-y-6">
        <SystemInfoWidget />
        <MiniSystemSummary />

        {/* Service Cards */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-neon-green font-mono">
            SERVICES
          </h2>
          {services.map(service => (
            <ServiceCard
              key={service.name}
              name={service.name}
              description={service.description}
              path={service.path}
              status={service.status}
              port={service.port}
            />
          ))}
        </div>
      </div>

      {/* Right Column (1/3 width on large screens) */}
      <div className="space-y-6">
        <WeatherWidget />
        <CalendarWidget />
        <NotesWidget />
      </div>
    </div>
  );
}
