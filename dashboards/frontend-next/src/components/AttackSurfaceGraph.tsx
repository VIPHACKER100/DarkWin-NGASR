"use client";

import React, { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph3D as it's a client-side library
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });

interface Node {
  id: string;
  label: string;
  type: 'root' | 'target' | 'finding';
  severity?: string;
}

interface Edge {
  source: string;
  target: string;
}

interface GraphData {
  nodes: Node[];
  links: Edge[];
}

export default function AttackSurfaceGraph() {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const fgRef = useRef<any>();

  useEffect(() => {
    async function fetchGraph() {
      try {
        const response = await fetch('http://localhost:5000/api/v1/graph');
        const rawData = await response.json();
        
        // Transform edges to links for react-force-graph
        setData({
          nodes: rawData.nodes,
          links: rawData.edges
        });
      } catch (error) {
        console.error("Failed to fetch attack surface graph:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchGraph();
  }, []);

  const getNodeColor = (node: Node) => {
    switch (node.type) {
      case 'root': return '#06b6d4'; // Cyan
      case 'target': return '#a855f7'; // Purple
      case 'finding':
        if (node.severity === 'Critical') return '#ef4444';
        if (node.severity === 'High') return '#f97316';
        if (node.severity === 'Medium') return '#eab308';
        return '#22c55e';
      default: return '#94a3b8';
    }
  };

  const getNodeSize = (node: Node) => {
    switch (node.type) {
      case 'root': return 10;
      case 'target': return 6;
      case 'finding': return 4;
      default: return 3;
    }
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-950 rounded-2xl border border-white/5">
        <p className="text-zinc-500 animate-pulse">Initializing Neural Attack Surface...</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative bg-zinc-950 rounded-2xl overflow-hidden border border-white/5">
      <ForceGraph3D
        ref={fgRef}
        graphData={data}
        nodeLabel="label"
        nodeColor={getNodeColor}
        nodeVal={getNodeSize}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        backgroundColor="#09090b"
        linkColor={() => "#ffffff10"}
        onNodeClick={(node: any) => {
          // Aim at node from outside it
          const distance = 40;
          const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);

          fgRef.current.cameraPosition(
            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new pos
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
          );
        }}
      />
      <div className="absolute top-4 left-4 p-4 glass pointer-events-none">
        <h4 className="text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Attack Surface Map</h4>
        <div className="flex flex-col gap-1">
          <LegendItem color="#06b6d4" label="Mesh Core" />
          <LegendItem color="#a855f7" label="Target Host" />
          <LegendItem color="#ef4444" label="Critical Vuln" />
        </div>
      </div>
    </div>
  );
}

function LegendItem({ color, label }: { color: string, label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
      <span className="text-[10px] text-zinc-500 uppercase">{label}</span>
    </div>
  );
}
