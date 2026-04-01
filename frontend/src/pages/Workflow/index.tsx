import React, { useState } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { Card, Typography, Tag, Row, Col } from 'antd'

const { Title, Text } = Typography

const initialTasks = {
  OPEN: [{ id: 't1', content: 'Cấp nguồn Zebra', priority: 'CRITICAL' }],
  PENDING: [{ id: 't2', content: 'Thay mực in', priority: 'LOW' }],
  RESOLVED: [{ id: 't3', content: 'Reset PW LDAP', priority: 'HIGH' }]
}

export default function WorkflowKanban() {
  const [columns, setColumns] = useState<any>(initialTasks)

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return
    const { source, destination } = result
    
    // Simulate moving items
    const sourceCol = [...columns[source.droppableId]]
    const destCol = source.droppableId === destination.droppableId ? sourceCol : [...columns[destination.droppableId]]
    
    const [removed] = sourceCol.splice(source.index, 1)
    destCol.splice(destination.index, 0, removed)
    
    setColumns({ ...columns, [source.droppableId]: sourceCol, [destination.droppableId]: destCol })
  }

  const getPriorityColor = (p: string) => p === 'CRITICAL' ? 'red' : p === 'HIGH' ? 'orange' : 'blue'

  return (
    <div>
      <Title level={3}>Onboarding Workflow Kanban</Title>
      <Text type="secondary">Kéo thả để Auto-trigger Celery Service cấp phát / thu hồi Thiết bị & Form</Text>
      
      <DragDropContext onDragEnd={onDragEnd}>
        <Row gutter={16} style={{ marginTop: 24 }}>
          {Object.entries(columns).map(([columnId, columnTasks]: any) => (
            <Col span={8} key={columnId}>
              <Card title={columnId} style={{ background: '#f5f5f5', minHeight: '60vh' }} headStyle={{ fontWeight: 'bold' }}>
                <Droppable droppableId={columnId}>
                  {(provided) => (
                    <div {...provided.droppableProps} ref={provided.innerRef} style={{ minHeight: 100 }}>
                      {columnTasks.map((item: any, index: number) => (
                        <Draggable key={item.id} draggableId={item.id} index={index}>
                          {(provided) => (
                            <div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={{ marginBottom: 12, ...provided.draggableProps.style }}>
                              <Card size="small" hoverable>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <b>{item.id}</b>
                                  <Tag color={getPriorityColor(item.priority)}>{item.priority}</Tag>
                                </div>
                                <p style={{ margin: '8px 0 0 0' }}>{item.content}</p>
                              </Card>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </Card>
            </Col>
          ))}
        </Row>
      </DragDropContext>
    </div>
  )
}
