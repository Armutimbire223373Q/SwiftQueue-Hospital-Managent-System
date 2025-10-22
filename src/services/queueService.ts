import apiClient from './apiClient';

// API (snake_case) service type - matches backend responses
export interface ApiServiceType {
    id: number;
    name: string;
    description: string;
    department: string;
    estimated_time: number;
    current_wait_time: number;
    queue_length: number;
    staff_count: number;
    service_rate: number;
    ai_predicted_wait?: number;
}

// Frontend (camelCase) service type used across components
export interface ServiceType {
    id: number;
    name: string;
    description: string;
    department: string;
    // camelCase fields used across the UI (required for compatibility)
    estimatedTime: number;
    currentWaitTime: number;
    queueLength: number;
    staffCount: number;
    serviceRate: number;
    aiPredictedWait?: number;
    // snake_case aliases (required) to support components still using old names
    estimated_time: number;
    current_wait_time: number;
    queue_length: number;
    staff_count: number;
    service_rate: number;
    ai_predicted_wait?: number;
}

export interface QueueEntry {
    // camelCase
    queueNumber: number;
    estimatedWait: number;
    aiPredictedWait: number;
    // snake_case aliases for compatibility
    queue_number?: number;
    estimated_wait?: number;
    ai_predicted_wait?: number;
}

// API queue item shape (snake_case)
export interface ApiQueueItem {
    id: number;
    patient?: any;
    service?: any;
    queue_number?: number;
    estimated_wait_time?: number;
    ai_predicted_wait?: number;
    status?: string;
    priority?: string;
    created_at?: string;
}

export interface QueueItem {
    id: number;
    patient?: any;
    service?: any;
    // camelCase
    queueNumber?: number;
    estimatedWaitTime?: number;
    aiPredictedWait?: number;
    createdAt?: string;
    // snake_case aliases
    queue_number?: number;
    estimated_wait_time?: number;
    ai_predicted_wait?: number;
    created_at?: string;
    status?: string;
    priority?: string;
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

        const data = response.data || {};

        // backend returns snake_case; provide both shapes for compatibility
        const entry: QueueEntry = {
            queueNumber: data.queue_number ?? data.queueNumber,
            estimatedWait: data.estimated_wait ?? data.estimatedWait,
            aiPredictedWait: data.ai_predicted_wait ?? data.aiPredictedWait ?? 0,
            queue_number: data.queue_number ?? data.queueNumber,
            estimated_wait: data.estimated_wait ?? data.estimatedWait,
            ai_predicted_wait: data.ai_predicted_wait ?? data.aiPredictedWait,
        } as QueueEntry;

        return entry;
    },

    async getQueueStatus(queueNumber: number): Promise<{
        status: string;
        position: number;
        estimatedWait: number;
    }> {
        const response = await apiClient.get(`/queue/status/${queueNumber}`);

        return response.data;
    },

    // Fetch services from API and map snake_case -> camelCase
    async getAllQueues(): Promise<QueueItem[]> {
        const response = await apiClient.get('/queue');
        const apiItems: ApiQueueItem[] = response.data || [];

        return apiItems.map((it) => ({
            id: it.id,
            patient: it.patient,
            service: it.service,
            queueNumber: it.queue_number,
            estimatedWaitTime: it.estimated_wait_time,
            aiPredictedWait: it.ai_predicted_wait,
            createdAt: it.created_at,
            // snake_case aliases
            queue_number: it.queue_number,
            estimated_wait_time: it.estimated_wait_time,
            ai_predicted_wait: it.ai_predicted_wait,
            created_at: it.created_at,
            status: it.status,
            priority: it.priority,
        }));
    },

    async getQueueStatistics(): Promise<any> {
        console.log('queueService: getQueueStatistics called');
        try {
            console.log('queueService: Attempting to fetch from /queue/statistics');
            const response = await apiClient.get('/queue/statistics');
            console.log('queueService: Successfully fetched statistics:', response.data);
            return response.data;
        } catch (error) {
            console.error('queueService: Failed to fetch real statistics, using mock data:', error);
            console.log('queueService: Returning mock data');
            return {
                total_waiting: 8,
                total_being_served: 3,
                avg_wait_time_today: 15,
                efficiency_score: 0.89
            };
        }
    }
};

// Helper: transform API response (snake_case) to frontend ServiceType (camelCase)
export function mapApiServiceToServiceType(api: ApiServiceType): ServiceType {
    return {
        id: api.id,
        name: api.name,
        description: api.description,
        department: api.department,
        estimatedTime: api.estimated_time,
        currentWaitTime: api.current_wait_time,
        queueLength: api.queue_length,
        staffCount: api.staff_count,
        serviceRate: api.service_rate,
        aiPredictedWait: api.ai_predicted_wait,
        // snake_case aliases
        estimated_time: api.estimated_time,
        current_wait_time: api.current_wait_time,
        queue_length: api.queue_length,
        staff_count: api.staff_count,
        service_rate: api.service_rate,
        ai_predicted_wait: api.ai_predicted_wait,
    };
}
