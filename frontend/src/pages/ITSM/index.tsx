import React, { useState } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { Card, Typography, Tag, Row, Col, Space } from 'antd'

const { Title } = Typography

const initialTickets = {
  OPEN: [
    { id: 'ITSM-001', content: 'Lỗi VPN', priority: 'HIGH' },
    { id: 'ITSM-002', content: 'Cấp laptop mới', priority: 'MEDIUM' }
  ],
  PENDING: [
    { id: 'ITSM-003', content: 'Chờ license Visio', priority: 'LOW' }
  ],
  RESOLVED: [
    { id: 'ITSM-004', content: 'Fix máy chấm công', priority: 'CRITICAL' }
  ]
}

export default function ITSMKanban() {
  const [columns, setColumns] = useState<any>(initialTickets)

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return
    const { source, destination } = result
    
    // Simulate moving items across lanes
    const sourceCol = [...columns[source.droppableId]]
    const destCol = source.droppableId === destination.droppableId ? sourceCol : [...columns[destination.droppableId]]
    
    const [removed] = sourceCol.splice(source.index, 1)
    destCol.splice(destination.index, 0, removed)
    
    setColumns({ ...columns, [source.droppableId]: sourceCol, [destination.droppableId]: destCol })
  }

  const getBadgeColor = (p: string) => p === 'CRITICAL' ? 'magenta' : p === 'HIGH' ? 'red' : p === 'MEDIUM' ? 'blue' : 'default'

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3}>ITSM Service Board (SLA Flow)</Title>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <Row gutter={16}>
          {Object.entries(columns).map(([columnId, columnTasks]: any) => (
            <Col span={8} key={columnId}>
              <Card 
                title={<Space>{columnId} <Tag>{columnTasks.length}</Tag></Space>} 
                style={{ background: '#f5f5f5', minHeight: '60vh', borderRadius: 8 }} 
                headStyle={{ fontWeight: 'bold' }}>
                <Droppable droppableId={columnId}>
                  {(provided) => (
                    <div {...provided.droppableProps} ref={provided.innerRef} style={{ minHeight: 100 }}>
                      {columnTasks.map((item: any, index: number) => (
                        <Draggable key={item.id} draggableId={item.id} index={index}>
                          {(provided) => (
                            <div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={{ marginBottom: 12, ...provided.draggableProps.style }}>
                              <Card size="small" hoverable>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                  <b>{item.id}</b>
                                  <Tag color={getBadgeColor(item.priority)}>{item.priority}</Tag>
                                </div>
                                <Text type="secondary">{item.content}</Text>
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

function Text({ children, type }: any) {
  return <Typography.Text type={type}>{children}</Typography.Text>
}
