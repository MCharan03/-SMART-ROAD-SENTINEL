import AnalyticsWidgets from "./components/AnalyticsWidgets";
import DefectTable from "./components/DefectTable"; // Import DefectTable
import DashboardLayout from './components/DashboardLayout';
import { DefectsProvider, useDefects } from "./context/DefectsContext";

function AppContent() {
  const { loading, error } = useDefects();

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-2xl">Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-2xl text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 p-6">
      <AnalyticsWidgets />
      <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem] mt-6 mb-6">
          SMART ROAD SENTINEL
      </h1>
      <DefectTable /> {/* Render DefectTable */}
    </div>
  );
}

function App() {
  return (
    <DefectsProvider>
      <div className="dark bg-background text-foreground">
        <DashboardLayout>
          <AppContent />
        </DashboardLayout>
      </div>
    </DefectsProvider>
  );
}

export default App;
