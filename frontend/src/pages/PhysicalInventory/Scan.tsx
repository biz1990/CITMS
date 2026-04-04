import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Input, Space, Alert, Typography, Spin, Select, message } from 'antd';
import { BrowserMultiFormatReader, Result } from '@zxing/library';
import { ArrowLeftOutlined, SearchOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import physicalInventoryService from '../../services/physicalInventory';

const { Title } = Typography;

const InventoryScan: React.FC = () => {
    const { surveyId } = useParams<{ surveyId: string }>();
    const navigate = useNavigate();
    const videoRef = useRef<HTMLVideoElement>(null);
    const codeReader = useRef(new BrowserMultiFormatReader());
    
    const [scannedTag, setScannedTag] = useState('');
    const [lastScanResult, setLastScanResult] = useState<any>(null);
    const [scanning, setScanning] = useState(true);
    const [loading, setLoading] = useState(false);
    const [selectedLocationId, setSelectedLocationId] = useState<string | null>(null);

    // Mock locations for demo - in production this would be fetched from API
    const locations = [
        { label: 'Hanoi Office - Floor 1', value: 'b2e9a5d1-...' },
        { label: 'HCM Warehouse', value: 'c3f0b6e2-...' }
    ];

    useEffect(() => {
        if (scanning) {
            startScanner();
        } else {
            codeReader.current.reset();
        }
        return () => codeReader.current.reset();
    }, [scanning]);

    const startScanner = async () => {
        try {
            const videoInputDevices = await BrowserMultiFormatReader.listVideoInputDevices();
            if (videoInputDevices.length === 0) {
                message.error('No camera found');
                return;
            }
            const selectedDeviceId = videoInputDevices[0].deviceId;
            
            codeReader.current.decodeFromVideoDevice(selectedDeviceId, videoRef.current!, (result: Result | null, err: any) => {
                if (result) {
                    handleScan(result.getText());
                }
            });
        } catch (error) {
            message.error('Camera access failed');
            setScanning(false);
        }
    };

    const handleScan = async (tag: string) => {
        if (!selectedLocationId) {
            message.warning('Please select current location first');
            return;
        }
        if (loading) return;
        
        setScannedTag(tag);
        setLoading(true);
        message.loading({ content: 'Processing scan...', key: 'scanning' });
        
        try {
            const result = await physicalInventoryService.submitScan(surveyId!, {
                asset_tag: tag,
                actual_location_id: selectedLocationId
            });
            setLastScanResult(result);
            message.success({ content: `Scanned: ${tag}`, key: 'scanning' });
            
            setTimeout(() => {
                setScannedTag('');
                // setLastScanResult(null); // Keep results visible for a while
            }, 3000);
            
        } catch (error) {
            message.error({ content: 'Scan failed', key: 'scanning' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto', padding: '16px' }}>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/physical-inventory')} style={{ marginBottom: '16px' }}>
                Back to Surveys
            </Button>
            
            <Card style={{ textAlign: 'center' }}>
                <Title level={4}>Inventory Scanner (PWA)</Title>
                
                <Space direction="vertical" style={{ width: '100%', marginBottom: '16px' }}>
                    <Text strong>Step 1: Select Your Current Location</Text>
                    <Select 
                        style={{ width: '100%' }} 
                        placeholder="Current Location Context" 
                        onChange={val => setSelectedLocationId(val)}
                        options={locations}
                    />
                </Space>

                <div style={{ position: 'relative', width: '100%', height: '300px', backgroundColor: '#000', marginBottom: '16px', overflow: 'hidden', borderRadius: '8px' }}>
                    <video ref={videoRef} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', border: '2px solid rgba(255,180,0,0.6)', width: '220px', height: '160px' }} />
                </div>

                <Space direction="vertical" style={{ width: '100%' }}>
                    <Input 
                        placeholder="Manual Asset Tag Entry" 
                        prefix={<SearchOutlined />} 
                        value={scannedTag}
                        onChange={e => setScannedTag(e.target.value)}
                        onPressEnter={() => handleScan(scannedTag)}
                        disabled={!selectedLocationId}
                    />
                    
                    {loading && <Spin tip="Processing..." />}
                    
                    {lastScanResult && (
                        <Alert
                            message={`Scan Result: ${lastScanResult.status}`}
                            description={`Tag: ${lastScanResult.asset_tag} | Status: ${lastScanResult.status}`}
                            type={lastScanResult.status === 'MATCHED' ? 'success' : 'warning'}
                            showIcon
                            icon={lastScanResult.status === 'MATCHED' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                        />
                    )}
                </Space>
            </Card>
        </div>
    );
};

export default InventoryScan;
