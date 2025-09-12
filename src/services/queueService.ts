const API_BASE_URL = 'http://localhost:8000/api';

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
        const response = await fetch(`${API_BASE_URL}/queue/join`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                service_id: serviceId,
                patient_details: patientDetails,
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to join queue');
        }

        return response.json();
    },

    async getQueueStatus(queueNumber: number): Promise<{
        status: string;
        position: number;
        estimatedWait: number;
    }> {
        const response = await fetch(`${API_BASE_URL}/queue/status/${queueNumber}`);
        
        if (!response.ok) {
            throw new Error('Failed to get queue status');
        }

        return response.json();
    }
};
