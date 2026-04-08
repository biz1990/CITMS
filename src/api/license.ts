import apiClient from './client';

export interface SoftwareLicense {
  id: string;
  software_catalog_id: string;
  type: string;
  total_seats: number;
  used_seats: number;
  purchase_date?: string;
  expire_date?: string;
  vendor_id?: string;
  created_at: string;
  updated_at: string;
}

export const licenseApi = {
  list: async () => {
    const response = await apiClient.get<SoftwareLicense[]>('/licenses');
    return response.data;
  },
  get: async (id: string) => {
    const response = await apiClient.get<SoftwareLicense>(`/licenses/${id}`);
    return response.data;
  },
};
