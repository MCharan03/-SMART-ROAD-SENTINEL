import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import axios from 'axios';

// --- INTERFACES to match FastAPI Backend for Road Defects ---
export interface Telemetry {
    cpuUsage: number;
    gpuUsage: number;
    fps: number;
    temperature: number;
    isScanning: boolean;
}

export interface Defect {
    id: string; // Document ID
    type: string;
    confidence: number;
    timestamp: number; // Unix timestamp
    latitude: number;
    longitude: number;
    image_url: string;
}

const initialTelemetry: Telemetry = {
    cpuUsage: 0,
    gpuUsage: 0,
    fps: 0,
    temperature: 0,
    isScanning: false,
};

// --- CONTEXT SHAPE ---
interface DefectsContextType {
  defects: Defect[];
  telemetry: Telemetry;
  loading: boolean;
  error: string | null;
  selectedDefect: Defect | null;
  selectDefect: (id: string | null) => void;
}

// --- CONTEXT ---
const DefectsContext = createContext<DefectsContextType | undefined>(undefined);

// --- PROVIDER ---
export const DefectsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [telemetry, setTelemetry] = useState<Telemetry>(initialTelemetry);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);

  const BACKEND_URL = 'http://localhost:8000/api/status';

  const fetchData = async () => {
    try {
      const response = await axios.get<{ telemetry: Telemetry, defects: Defect[] }>(BACKEND_URL);
      
      setTelemetry(response.data.telemetry);
      setDefects(response.data.defects);

      if (loading) setLoading(false);
      if (error) setError(null);
    } catch (err) {
      const message = axios.isAxiosError(err) ? err.message : 'An unexpected error occurred';
      setError(message);
      console.error('Failed to fetch data:', err);
    }
  };

  const selectDefect = (id: string | null) => {
    if (id === null) {
      setSelectedDefect(null);
      return;
    }
    const defect = defects.find(d => d.id === id) || null;
    setSelectedDefect(defect);
  };

  useEffect(() => {
    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 2000); // Poll every 2 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <DefectsContext.Provider value={{ 
      defects, 
      telemetry, 
      loading, 
      error, 
      selectedDefect, 
      selectDefect
    }}>
      {children}
    </DefectsContext.Provider>
  );
};

// --- CUSTOM HOOK ---
export const useDefects = () => {
  const context = useContext(DefectsContext);
  if (context === undefined) {
    throw new Error('useDefects must be used within a DefectsProvider');
  }
  return context;
};
