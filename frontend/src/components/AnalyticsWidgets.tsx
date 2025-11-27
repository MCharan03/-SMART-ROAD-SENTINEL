import React from 'react';

const AnalyticsWidgets: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Stat Card 1 */}
      <div className="bg-card p-4 rounded-lg shadow flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Total Defects</p>
          <h3 className="text-2xl font-bold">1,234</h3>
        </div>
        {/* Icon placeholder */}
        <span className="text-primary text-3xl">⚙️</span> 
      </div>

      {/* Stat Card 2 */}
      <div className="bg-card p-4 rounded-lg shadow flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Potholes</p>
          <h3 className="text-2xl font-bold">567</h3>
        </div>
        {/* Icon placeholder */}
        <span className="text-destructive text-3xl">🚧</span>
      </div>

      {/* Stat Card 3 */}
      <div className="bg-card p-4 rounded-lg shadow flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Cracks</p>
          <h3 className="text-2xl font-bold">412</h3>
        </div>
        {/* Icon placeholder */}
        <span className="text-secondary text-3xl">📏</span>
      </div>

      {/* Stat Card 4 */}
      <div className="bg-card p-4 rounded-lg shadow flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Recent Alerts</p>
          <h3 className="text-2xl font-bold">28</h3>
        </div>
        {/* Icon placeholder */}
        <span className="text-accent text-3xl">🔔</span>
      </div>
    </div>
  );
};

export default AnalyticsWidgets;