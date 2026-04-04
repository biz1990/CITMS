import apiClient from './apiClient';

export interface SurveyItem {
    id: string;
    asset_tag: string;
    status: 'MATCHED' | 'MISPLACED' | 'MISSING' | 'UNKNOWN';
    expected_location_id: string | null;
    actual_location_id: string;
    scanned_at: string;
}

export interface InventorySurvey {
    id: string;
    name: string;
    status: 'OPEN' | 'CLOSED' | 'RECONCILED';
    location_id: string | null;
    created_at: string;
    closed_at: string | null;
    items?: SurveyItem[];
}

export interface ScanSubmitData {
    asset_tag: string;
    actual_location_id: string;
}

const physicalInventoryService = {
    getSurveys: async (): Promise<InventorySurvey[]> => {
        const response = await apiClient.get('/physical-inventory/');
        return response.data;
    },

    createSurvey: async (name: string, locationId?: string): Promise<InventorySurvey> => {
        const response = await apiClient.post('/physical-inventory/', { name, location_id: locationId });
        return response.data;
    },

    submitScan: async (surveyId: string, data: ScanSubmitData): Promise<SurveyItem> => {
        const response = await apiClient.post(`/physical-inventory/${surveyId}/scan`, data);
        return response.data;
    },

    reconcileSurvey: async (surveyId: string): Promise<{ status: string; message: string }> => {
        const response = await apiClient.post(`/physical-inventory/${surveyId}/reconcile`);
        return response.data;
    }
};

export default physicalInventoryService;
