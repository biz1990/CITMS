import React, { useEffect, useState } from 'react';
import { Table, Button, Card, Tag, Space, Modal, Form, Input, Select, message } from 'antd';
import { QrcodeOutlined, PlusOutlined, InteractionOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import physicalInventoryService, { InventorySurvey } from '../../services/physicalInventory';

const PhysicalInventory: React.FC = () => {
    const [surveys, setSurveys] = useState<InventorySurvey[]>([]);
    const [loading, setLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [form] = Form.Form();
    const navigate = useNavigate();

    const fetchSurveys = async () => {
        setLoading(true);
        try {
            const data = await physicalInventoryService.getSurveys();
            setSurveys(data);
        } catch (error) {
            message.error('Failed to fetch surveys');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSurveys();
    }, []);

    const handleCreate = async (values: any) => {
        try {
            await physicalInventoryService.createSurvey(values.name, values.location_id);
            message.success('Survey created successfully');
            setIsModalOpen(false);
            fetchSurveys();
        } catch (error) {
            message.error('Failed to create survey');
        }
    };

    const handleReconcile = async (id: string) => {
        try {
            await physicalInventoryService.reconcileSurvey(id);
            message.success('Reconciliation completed and survey closed');
            fetchSurveys();
        } catch (error) {
            message.error('Reconciliation failed');
        }
    };

    const columns = [
        { label: 'Survey Name', dataIndex: 'name', key: 'name' },
        { 
            label: 'Status', 
            dataIndex: 'status', 
            key: 'status',
            render: (status: string) => (
                <Tag color={status === 'OPEN' ? 'green' : 'blue'}>{status}</Tag>
            )
        },
        { label: 'Created At', dataIndex: 'created_at', key: 'created_at', render: (val: string) => new Date(val).toLocaleString() },
        { label: 'Closed At', dataIndex: 'closed_at', key: 'closed_at', render: (val: string) => val ? new Date(val).toLocaleString() : '-' },
        {
            label: 'Actions',
            key: 'actions',
            render: (_: any, record: InventorySurvey) => (
                <Space>
                    {record.status === 'OPEN' && (
                        <>
                            <Button 
                                icon={<QrcodeOutlined />} 
                                type="primary"
                                onClick={() => navigate(`/physical-inventory/scan/${record.id}`)}
                            >
                                Start Scan
                            </Button>
                            <Button 
                                icon={<InteractionOutlined />} 
                                onClick={() => handleReconcile(record.id)}
                            >
                                Reconcile
                            </Button>
                        </>
                    )}
                </Space>
            )
        }
    ];

    return (
        <div style={{ padding: '24px' }}>
            <Card title="Physical Inventory (Module 11)" extra={
                <Button icon={<PlusOutlined />} type="primary" onClick={() => setIsModalOpen(true)}>
                    New Audit Survey
                </Button>
            }>
                <Table 
                    dataSource={surveys} 
                    columns={columns} 
                    rowKey="id" 
                    loading={loading}
                />
            </Card>

            <Modal title="Create Audit Survey" open={isModalOpen} onCancel={() => setIsModalOpen(false)} onOk={() => form.submit()}>
                <Form form={form} layout="vertical" onFinish={handleCreate}>
                    <Form.Item name="name" label="Survey Name" rules={[{ required: true }]}>
                        <Input placeholder="e.g., Annual Audit Q1 2026" />
                    </Form.Item>
                    <Form.Item name="location_id" label="Location (Optional)">
                        <Select placeholder="Select specific office/warehouse">
                            {/* In a real app, populate with locations from service */}
                        </Select>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default PhysicalInventory;
