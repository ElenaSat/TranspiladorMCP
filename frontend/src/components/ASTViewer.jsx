import React, { useEffect, useState, useMemo } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const ASTViewer = ({ astData, semanticTree }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [activeTab, setActiveTab] = useState('ast');

  // Convert AST to ReactFlow nodes and edges
  const convertASTToFlow = (ast, parentId = null, x = 0, y = 0, level = 0) => {
    if (!ast) return { nodes: [], edges: [] };

    const nodes = [];
    const edges = [];
    const nodeId = ast.id || `node-${Math.random()}`;

    // Create node
    nodes.push({
      id: nodeId,
      type: 'default',
      data: {
        label: (
          <div className="text-xs">
            <div className="font-semibold text-blue-400">{ast.type}</div>
            {ast.text && (
              <div className="text-gray-400 mt-1 max-w-[150px] truncate">
                {ast.text.substring(0, 30)}
              </div>
            )}
            <div className="text-gray-500 text-[10px] mt-1">
              Line {ast.start_line}
            </div>
          </div>
        ),
      },
      position: { x, y },
      style: {
        background: '#18181b',
        border: '1px solid #27272a',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '12px',
        color: '#fafafa',
        width: 180,
      },
    });

    // Create edge from parent
    if (parentId) {
      edges.push({
        id: `edge-${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      });
    }

    // Process children
    if (ast.children && ast.children.length > 0) {
      const childrenPerRow = Math.min(ast.children.length, 5);
      const spacing = 220;
      const startX = x - ((childrenPerRow - 1) * spacing) / 2;

      ast.children.forEach((child, idx) => {
        const childX = startX + (idx % childrenPerRow) * spacing;
        const childY = y + 150 + Math.floor(idx / childrenPerRow) * 150;
        const childResult = convertASTToFlow(child, nodeId, childX, childY, level + 1);
        nodes.push(...childResult.nodes);
        edges.push(...childResult.edges);
      });
    }

    return { nodes, edges };
  };

  // Convert semantic tree to flow
  const convertSemanticToFlow = (semantic) => {
    if (!semantic) return { nodes: [], edges: [] };

    const nodes = [];
    const edges = [];
    let yOffset = 0;

    // Create root node
    const rootId = 'semantic-root';
    nodes.push({
      id: rootId,
      type: 'default',
      data: {
        label: (
          <div className="text-xs font-bold text-green-400">Árbol Semántico</div>
        ),
      },
      position: { x: 400, y: 0 },
      style: {
        background: '#18181b',
        border: '2px solid #22c55e',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '12px',
        color: '#fafafa',
      },
    });

    yOffset += 100;

    // Add classes
    if (semantic.classes && semantic.classes.length > 0) {
      const classesNodeId = 'semantic-classes';
      nodes.push({
        id: classesNodeId,
        data: {
          label: (
            <div className="text-xs">
              <div className="font-semibold text-blue-400">Clases</div>
              <div className="text-gray-400 text-[10px] mt-1">
                {semantic.classes.length} encontrada(s)
              </div>
            </div>
          ),
        },
        position: { x: 100, y: yOffset },
        style: {
          background: '#18181b',
          border: '1px solid #3b82f6',
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          color: '#fafafa',
        },
      });
      edges.push({
        id: `edge-${rootId}-${classesNodeId}`,
        source: rootId,
        target: classesNodeId,
        type: 'smoothstep',
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      });

      semantic.classes.forEach((cls, idx) => {
        const clsId = `class-${idx}`;
        nodes.push({
          id: clsId,
          data: {
            label: (
              <div className="text-xs">
                <div className="text-gray-300">{cls.name}</div>
                <div className="text-gray-500 text-[10px]">Línea {cls.line}</div>
              </div>
            ),
          },
          position: { x: 100, y: yOffset + 100 + idx * 80 },
          style: {
            background: '#18181b',
            border: '1px solid #27272a',
            borderRadius: '6px',
            padding: '8px',
            fontSize: '11px',
            color: '#fafafa',
          },
        });
        edges.push({
          id: `edge-${classesNodeId}-${clsId}`,
          source: classesNodeId,
          target: clsId,
          type: 'smoothstep',
          style: { stroke: '#52525b', strokeWidth: 1 },
        });
      });
    }

    // Add methods
    if (semantic.methods && semantic.methods.length > 0) {
      const methodsNodeId = 'semantic-methods';
      nodes.push({
        id: methodsNodeId,
        data: {
          label: (
            <div className="text-xs">
              <div className="font-semibold text-purple-400">Métodos</div>
              <div className="text-gray-400 text-[10px] mt-1">
                {semantic.methods.length} encontrado(s)
              </div>
            </div>
          ),
        },
        position: { x: 400, y: yOffset },
        style: {
          background: '#18181b',
          border: '1px solid #a855f7',
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          color: '#fafafa',
        },
      });
      edges.push({
        id: `edge-${rootId}-${methodsNodeId}`,
        source: rootId,
        target: methodsNodeId,
        type: 'smoothstep',
        style: { stroke: '#a855f7', strokeWidth: 2 },
      });

      semantic.methods.forEach((method, idx) => {
        const methodId = `method-${idx}`;
        nodes.push({
          id: methodId,
          data: {
            label: (
              <div className="text-xs">
                <div className="text-gray-300">{method.name}</div>
                <div className="text-gray-500 text-[10px]">Línea {method.line}</div>
              </div>
            ),
          },
          position: { x: 400, y: yOffset + 100 + idx * 80 },
          style: {
            background: '#18181b',
            border: '1px solid #27272a',
            borderRadius: '6px',
            padding: '8px',
            fontSize: '11px',
            color: '#fafafa',
          },
        });
        edges.push({
          id: `edge-${methodsNodeId}-${methodId}`,
          source: methodsNodeId,
          target: methodId,
          type: 'smoothstep',
          style: { stroke: '#52525b', strokeWidth: 1 },
        });
      });
    }

    // Add properties
    if (semantic.properties && semantic.properties.length > 0) {
      const propsNodeId = 'semantic-properties';
      nodes.push({
        id: propsNodeId,
        data: {
          label: (
            <div className="text-xs">
              <div className="font-semibold text-yellow-400">Propiedades</div>
              <div className="text-gray-400 text-[10px] mt-1">
                {semantic.properties.length} encontrada(s)
              </div>
            </div>
          ),
        },
        position: { x: 700, y: yOffset },
        style: {
          background: '#18181b',
          border: '1px solid #eab308',
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          color: '#fafafa',
        },
      });
      edges.push({
        id: `edge-${rootId}-${propsNodeId}`,
        source: rootId,
        target: propsNodeId,
        type: 'smoothstep',
        style: { stroke: '#eab308', strokeWidth: 2 },
      });

      semantic.properties.forEach((prop, idx) => {
        const propId = `prop-${idx}`;
        nodes.push({
          id: propId,
          data: {
            label: (
              <div className="text-xs">
                <div className="text-gray-300">{prop.name}</div>
                <div className="text-gray-500 text-[10px]">Línea {prop.line}</div>
              </div>
            ),
          },
          position: { x: 700, y: yOffset + 100 + idx * 80 },
          style: {
            background: '#18181b',
            border: '1px solid #27272a',
            borderRadius: '6px',
            padding: '8px',
            fontSize: '11px',
            color: '#fafafa',
          },
        });
        edges.push({
          id: `edge-${propsNodeId}-${propId}`,
          source: propsNodeId,
          target: propId,
          type: 'smoothstep',
          style: { stroke: '#52525b', strokeWidth: 1 },
        });
      });
    }

    return { nodes, edges };
  };

  useEffect(() => {
    if (activeTab === 'ast' && astData) {
      const { nodes: newNodes, edges: newEdges } = convertASTToFlow(astData, null, 400, 50);
      setNodes(newNodes);
      setEdges(newEdges);
    } else if (activeTab === 'semantic' && semanticTree) {
      const { nodes: newNodes, edges: newEdges } = convertSemanticToFlow(semanticTree);
      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [astData, semanticTree, activeTab]);

  return (
    <div className="h-full w-full bg-background">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <TabsList className="mx-4 mt-2 w-auto">
          <TabsTrigger value="ast" data-testid="ast-tab">Árbol Sintáctico (AST)</TabsTrigger>
          <TabsTrigger value="semantic" data-testid="semantic-tab">Árbol Semántico</TabsTrigger>
        </TabsList>
        <TabsContent value="ast" className="flex-1 mt-0">
          {astData ? (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="#27272a" gap={16} />
              <Controls />
              <MiniMap
                nodeColor="#3b82f6"
                maskColor="rgba(0, 0, 0, 0.5)"
                style={{ background: '#18181b', border: '1px solid #27272a' }}
              />
            </ReactFlow>
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <p>Transpila código para ver el AST</p>
            </div>
          )}
        </TabsContent>
        <TabsContent value="semantic" className="flex-1 mt-0">
          {semanticTree ? (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="#27272a" gap={16} />
              <Controls />
              <MiniMap
                nodeColor="#22c55e"
                maskColor="rgba(0, 0, 0, 0.5)"
                style={{ background: '#18181b', border: '1px solid #27272a' }}
              />
            </ReactFlow>
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <p>Transpila código para ver el árbol semántico</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ASTViewer;