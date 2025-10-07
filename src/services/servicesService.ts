import { ServiceType } from './queueService';
import apiClient from './apiClient';

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
        const response = await apiClient.get('/services');
        return response.data;
    },

    async getService(serviceId: number): Promise<ServiceType> {
        const response = await apiClient.get(`/services/${serviceId}`);
        return response.data;
    },

    async getServiceCounters(serviceId: number): Promise<ServiceCounter[]> {
        const response = await apiClient.get(`/services/${serviceId}/counters`);
        return response.data;
    }
};
