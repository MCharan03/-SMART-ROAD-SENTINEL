import React from 'react';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface Defect {
  id: string;
  type: string;
  confidence: number;
  latitude: number;
  longitude: number;
  timestamp: string; // Will format date later
}

const placeholderDefects: Defect[] = [
  {
    id: "d1",
    type: "Pothole",
    confidence: 0.95,
    latitude: 34.0522,
    longitude: -118.2437,
    timestamp: "2025-11-27 10:00:00",
  },
  {
    id: "d2",
    type: "Crack",
    confidence: 0.88,
    latitude: 34.0550,
    longitude: -118.2500,
    timestamp: "2025-11-27 10:05:30",
  },
  {
    id: "d3",
    type: "Manhole Issue",
    confidence: 0.72,
    latitude: 34.0480,
    longitude: -118.2400,
    timestamp: "2025-11-27 10:10:15",
  },
  {
    id: "d4",
    type: "Pothole",
    confidence: 0.91,
    latitude: 34.0580,
    longitude: -118.2600,
    timestamp: "2025-11-27 10:15:00",
  },
];

const DefectTable: React.FC = () => {
  return (
    <div className="bg-card p-4 rounded-lg shadow h-96 overflow-auto">
      <h2 className="text-xl font-bold mb-4">Recent Defects</h2>
      <Table>
        <TableCaption>A list of recent road defects detected.</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Type</TableHead>
            <TableHead>Confidence</TableHead>
            <TableHead>Location (Lat, Lon)</TableHead>
            <TableHead>Timestamp</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {placeholderDefects.map((defect) => (
            <TableRow key={defect.id}>
              <TableCell className="font-medium">{defect.type}</TableCell>
              <TableCell>{(defect.confidence * 100).toFixed(1)}%</TableCell>
              <TableCell>{defect.latitude.toFixed(4)}, {defect.longitude.toFixed(4)}</TableCell>
              <TableCell>{defect.timestamp}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default DefectTable;