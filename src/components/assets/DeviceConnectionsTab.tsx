import React, { useEffect, useMemo } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState,
  MarkerType,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Network, Info, Monitor, Tag, Settings } from 'lucide-react';
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatDistanceToNow } from 'date-fns';

interface DeviceConnectionsTabProps {
  deviceId: string;
}

// Custom Node Component
const PeripheralNode = ({ data }: any) => {
  const isOnline = data.last_seen && (new Date().getTime() - new Date(data.last_seen).getTime() < 5 * 60 * 1000);
  const isNew = data.new_peripheral;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div 
            className={`px-4 py-2 rounded-lg border-2 shadow-lg transition-all duration-300 ${
              isNew ? 'border-orange-500 shadow-orange-500/20 animate-pulse' : 'border-slate-700'
            } ${isOnline ? 'bg-slate-900' : 'bg-slate-950 opacity-80'}`}
            style={{ background: data.bgColor, minWidth: '150px' }}
          >
            <Handle type="target" position={Position.Top} className="w-2 h-2 bg-slate-400" />
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${isOnline ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'}`} />
              <div className="flex-1">
                <p className="text-[10px] font-bold text-white truncate">{data.label}</p>
                <p className="text-[8px] text-slate-400 uppercase tracking-tighter">{data.device_type}</p>
              </div>
              {data.device_type === 'SCANNER' ? <Tag className="h-3 w-3 text-white/50" /> : <Settings className="h-3 w-3 text-white/50" />}
            </div>
            <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-slate-400" />
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="bg-slate-900 border-slate-700 text-white p-3 space-y-1">
          <p className="text-xs font-bold border-b border-white/10 pb-1 mb-1">{data.label}</p>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[10px]">
            <span className="text-slate-400">Status:</span>
            <span className={isOnline ? 'text-green-400' : 'text-red-400'}>{isOnline ? 'Online' : 'Offline'}</span>
            
            <span className="text-slate-400">Last Seen:</span>
            <span>{data.last_seen ? formatDistanceToNow(new Date(data.last_seen), { addSuffix: true }) : 'Never'}</span>
            
            {data.port_name && (
              <>
                <span className="text-slate-400">Port:</span>
                <span>{data.port_name}</span>
              </>
            )}
            
            {data.baud_rate && (
              <>
                <span className="text-slate-400">Baud Rate:</span>
                <span>{data.baud_rate} bps</span>
              </>
            )}
            
            <span className="text-slate-400">Connection:</span>
            <span>{data.connection_type}</span>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

const DeviceConnectionsTab: React.FC<DeviceConnectionsTabProps> = ({ deviceId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const nodeTypes = useMemo(() => ({
    peripheral: PeripheralNode,
  }), []);

  // Fetch Connections
  const { data: connections, isLoading } = useQuery({
    queryKey: ['device-connections', deviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/devices/${deviceId}/connections`);
      return response.data;
    },
  });

  useEffect(() => {
    if (connections) {
      const newNodes: any[] = [];
      const newEdges: any[] = [];

      // Add central device node
      newNodes.push({
        id: deviceId,
        data: { label: 'This Device', device_type: 'HOST' },
        position: { x: 250, y: 250 },
        style: { background: '#3b82f6', color: '#fff', borderRadius: '8px', padding: '10px', fontWeight: 'bold', border: '2px solid #2563eb' },
      });

      // Add connected nodes
      connections.forEach((conn: any, index: number) => {
        const other = conn.other_device;
        const angle = (index / connections.length) * 2 * Math.PI;
        const radius = 300;
        
        // Node styling based on type
        let bgColor = '#1e293b';
        if (other.device_type === 'SCANNER') bgColor = '#065f46';
        if (other.device_type === 'PRINTER') bgColor = '#5b21b6';
        if (other.device_type === 'DOCK') bgColor = '#92400e';
        
        newNodes.push({
          id: other.id,
          type: 'peripheral',
          data: { 
            label: other.hostname || `Device ${other.id.substring(0, 8)}`,
            device_type: other.device_type,
            status: other.status,
            last_seen: other.last_seen,
            new_peripheral: other.new_peripheral,
            baud_rate: other.baud_rate,
            port_name: conn.port_name,
            connection_type: conn.connection_type,
            bgColor
          },
          position: { 
            x: 250 + radius * Math.cos(angle), 
            y: 250 + radius * Math.sin(angle) 
          },
        });

        const label = conn.baud_rate ? `${conn.connection_type} (${conn.baud_rate} bps)` : conn.connection_type;

        newEdges.push({
          id: `e-${conn.id}`,
          source: conn.source_device_id,
          target: conn.target_device_id,
          label: label,
          labelStyle: { fill: '#94a3b8', fontSize: '8px', fontWeight: 'bold' },
          animated: conn.status === 'ACTIVE',
          style: { stroke: conn.connection_type === 'DOCK_PAIRING' ? '#f59e0b' : '#3b82f6', strokeWidth: 2 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: conn.connection_type === 'DOCK_PAIRING' ? '#f59e0b' : '#3b82f6',
          },
        });
      });

      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [connections, deviceId, setNodes, setEdges]);

  if (isLoading) return <div className="h-[500px] flex items-center justify-center">Loading topology...</div>;

  return (
    <Card className="h-[650px] border-none shadow-none bg-transparent">
      <CardHeader className="px-0">
        <CardTitle className="flex items-center gap-2">
          <Network className="h-5 w-5 text-primary" />
          Network Topology & CMDB Relationships
        </CardTitle>
      </CardHeader>
      <CardContent className="h-full p-0 border rounded-lg bg-slate-950/50 overflow-hidden relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          colorMode="dark"
        >
          <Background color="#334155" gap={20} />
          <Controls />
          <MiniMap nodeColor={(n: any) => n.data?.bgColor || '#334155'} />
        </ReactFlow>
      </CardContent>
    </Card>
  );
};

export default DeviceConnectionsTab;
