import { useSystem } from "@/contexts/SystemContext";

export default function SystemInfoWidget() {
  const { systemInfo } = useSystem();

  if (!systemInfo) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
        <h2 className="text-lg font-bold text-neon-green font-mono mb-3">
          SYSTEM INFO
        </h2>
        <div className="text-text-muted font-mono text-sm">
          Loading system information...
        </div>
      </div>
    );
  }

  const systemFields = [
    { label: "System", value: systemInfo.system },
    { label: "Release", value: systemInfo.release },
    { label: "Version", value: systemInfo.version },
    { label: "Machine", value: systemInfo.machine },
  ];

  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <h2 className="text-lg font-bold text-neon-green font-mono mb-3">
        SYSTEM INFO
      </h2>
      <div className="space-y-2">
        {systemFields.map(field => (
          <div
            key={field.label}
            className="flex justify-between font-mono text-sm"
          >
            <span className="text-text-muted">{field.label}:</span>
            <span className="text-text-primary">{field.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
