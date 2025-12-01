import { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Server, Clock } from 'lucide-react';

export default function App() {
  const [metrics, setMetrics] = useState([]);
  const [currentStats, setCurrentStats] = useState({ qps: 0, avgLatency: 0 });
  const lastTotalCalls = useRef(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:5000/metrics/current');
        const data = await res.json();
        
        // Calculate QPS (Current Total - Last Total)
        const newCalls = data.total_calls - lastTotalCalls.current;
        const qps = lastTotalCalls.current === 0 ? 0 : newCalls; // Ignore first jump
        lastTotalCalls.current = data.total_calls;

        // Update Chart History (Keep last 20 points)
        const timestamp = new Date().toLocaleTimeString();
        setMetrics(prev => [...prev.slice(-19), { time: timestamp, qps: qps }]);
        
        setCurrentStats({ 
          qps: qps, 
          avgLatency: data.avg_query_time_ms 
        });

      } catch (err) {
        console.error("API Error", err);
      }
    };

    const interval = setInterval(fetchData, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1 style={{ color: '#333' }}>🚀 CloudMetrics Live Dashboard</h1>
      
      {/* Top Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '20px' }}>
        <Card title="Live QPS" value={currentStats.qps} icon={<Activity />} color="#2563eb" />
        <Card title="Avg Latency (ms)" value={currentStats.avgLatency} icon={<Clock />} color="#dc2626" />
        <Card title="Status" value="Online" icon={<Server />} color="#16a34a" />
      </div>

      {/* Main Chart */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>Traffic Spike (Queries per Second)</h3>
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="qps" stroke="#2563eb" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// Simple Sub-component for cards
function Card({ title, value, icon, color }) {
  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '15px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ color: color }}>{icon}</div>
      <div>
        <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>{title}</p>
        <h2 style={{ margin: 0, fontSize: '1.5rem' }}>{value}</h2>
      </div>
    </div>
  );
}