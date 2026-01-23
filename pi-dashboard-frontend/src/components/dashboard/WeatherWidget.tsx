export default function WeatherWidget() {
  return (
    <div className="bg-background-secondary border border-border rounded-lg p-4 shadow-neon">
      <h2 className="text-lg font-bold text-neon-blue font-mono mb-4">
        WEATHER
      </h2>

      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-4xl font-bold text-text-primary font-mono">
            22°C
          </div>
          <div className="text-sm text-text-muted font-mono">Partly Cloudy</div>
        </div>
        <div className="text-6xl">☁️</div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-xs font-mono">
          <span className="text-text-muted">High:</span>{" "}
          <span className="text-text-primary">25°C</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Low:</span>{" "}
          <span className="text-text-primary">18°C</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Humidity:</span>{" "}
          <span className="text-text-primary">65%</span>
        </div>
        <div className="text-xs font-mono">
          <span className="text-text-muted">Wind:</span>{" "}
          <span className="text-text-primary">12 km/h</span>
        </div>
      </div>

      <div className="border-t border-border pt-3">
        <div className="text-xs text-text-muted font-mono mb-2">
          12-HOUR FORECAST
        </div>
        <div className="flex justify-between">
          {["12PM", "3PM", "6PM", "9PM"].map(time => (
            <div key={time} className="text-center">
              <div className="text-xs text-text-muted font-mono">{time}</div>
              <div className="text-2xl my-1">🌤️</div>
              <div className="text-xs text-text-primary font-mono">23°</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
