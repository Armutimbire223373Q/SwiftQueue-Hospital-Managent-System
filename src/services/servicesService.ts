import { ServiceType } from './queueService';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface ServiceCounter {
    id: number;
    name: string;
    serviceId: number;
    isActive: boolean;
    staffMember?: string;
    currentQueueEntry?: number;
}

export const servicesService = {
    async getAllServices(): Promise<ServiceType[]> {
        const response = await fetch(`${API_BASE_URL}/services`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch services');
        }

        return response.json();
    },

    async getService(serviceId: number): Promise<ServiceType> {
        const response = await fetch(`${API_BASE_URL}/services/${serviceId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch service');
        }

        return response.json();
    },

    async getServiceCounters(serviceId: number): Promise<ServiceCounter[]> {
        const response = await fetch(`${API_BASE_URL}/services/${serviceId}/counters`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch service counters');
        }

        return response.json();
    }
};
