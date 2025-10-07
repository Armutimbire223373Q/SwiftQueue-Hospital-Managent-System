import apiClient from './apiClient';

export interface ServiceType {
    id: number;
    name: string;
    description: string;
    department: string;
    estimatedTime: number;
    currentWaitTime: number;
    queueLength: number;
    aiPredictedWait: number;
}

export interface QueueEntry {
    queueNumber: number;
    estimatedWait: number;
    aiPredictedWait: number;
}

export interface PatientDetails {
    name: string;
    email: string;
    phone: string;
    dateOfBirth: string;
    symptoms?: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
}

export const queueService = {
    async joinQueue(serviceId: number, patientDetails: PatientDetails): Promise<QueueEntry> {
        const response = await apiClient.post('/queue/join', {
            service_id: serviceId,
            patient_details: patientDetails,
        });

        return response.data;
    },

    async getQueueStatus(queueNumber: number): Promise<{
        status: string;
        position: number;
        estimatedWait: number;
    }> {
        const response = await apiClient.get(`/queue/status/${queueNumber}`);

        return response.data;
    }
};
