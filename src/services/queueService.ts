import { apiService, Service, QueueEntry as APIQueueEntry } from './apiService';

export interface ServiceType extends Service {
    estimatedTime: number;
    currentWaitTime: number;
    queueLength: number;
    aiPredictedWait?: number;
}

export interface QueueJoinResponse {
    queue_number: number;
    estimated_wait: number;
    ai_predicted_wait: number;
}

export interface PatientDetails {
    name: string;
    email: string;
    phone: string;
    dateOfBirth: string;
    symptoms?: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface QueueStatus {
    status: string;
    position: number;
    estimated_wait: number;
}

export interface QueueDashboardData {
    services: ServiceType[];
    totalPatients: number;
    avgWaitTime: number;
    activeCounters: number;
}

class QueueService {
    /**
     * Join a queue for a specific service
     */
    async joinQueue(serviceId: number, patientDetails: PatientDetails): Promise<QueueJoinResponse> {
        return apiService.post('/queue/join', {
            service_id: serviceId,
            patient_details: patientDetails,
        });
    }

    /**
     * Get the status of a specific queue entry
     */
    async getQueueStatus(queueNumber: number): Promise<QueueStatus> {
        return apiService.get(`/queue/status/${queueNumber}`);
    }

    /**
     * Get all available services
     */
    async getServices(): Promise<ServiceType[]> {
        return apiService.get('/services/');
    }

    /**
     * Get a specific service by ID
     */
    async getService(serviceId: number): Promise<ServiceType> {
        return apiService.get(`/services/${serviceId}`);
    }

    /**
     * Get service counters for a specific service
     */
    async getServiceCounters(serviceId: number) {
        return apiService.get(`/services/${serviceId}/counters`);
    }

    /**
     * Get dashboard data for queue management
     */
    async getDashboardData(): Promise<QueueDashboardData> {
        try {
            const services = await this.getServices();
            
            // Calculate totals
            const totalPatients = services.reduce((sum, service) => sum + service.queue_length, 0);
            const avgWaitTime = services.length > 0 
                ? services.reduce((sum, service) => sum + service.current_wait_time, 0) / services.length 
                : 0;
            
            // Count active counters (this would need a separate endpoint in a full implementation)
            const activeCounters = services.length * 2; // Assuming 2 counters per service on average

            return {
                services,
                totalPatients,
                avgWaitTime: Math.round(avgWaitTime),
                activeCounters
            };
        } catch (error) {
            console.error('Failed to get dashboard data:', error);
            throw error;
        }
    }

    /**
     * Get queue entries for a specific service
     */
    async getServiceQueue(serviceId: number): Promise<APIQueueEntry[]> {
        // This would need to be implemented as a backend endpoint
        // For now, return empty array
        return [];
    }

    /**
     * Update queue entry status (for staff use)
     */
    async updateQueueStatus(queueId: number, status: 'waiting' | 'called' | 'serving' | 'completed'): Promise<void> {
        // This would need to be implemented as a backend endpoint
        return apiService.put(`/queue/${queueId}/status`, { status });
    }

    /**
     * Call next patient in queue
     */
    async callNextPatient(serviceId: number, counterId: number): Promise<{
        queue_entry: APIQueueEntry;
        message: string;
    }> {
        // This would need to be implemented as a backend endpoint
        return apiService.post(`/queue/call-next`, {
            service_id: serviceId,
            counter_id: counterId
        });
    }

    /**
     * Get queue statistics
     */
    async getQueueStatistics(): Promise<{
        total_waiting: number;
        total_being_served: number;
        total_completed_today: number;
        avg_wait_time_today: number;
        busiest_service: string;
        efficiency_score: number;
    }> {
        // This would be implemented as a backend endpoint
        // For now, return mock data
        return {
            total_waiting: 12,
            total_being_served: 6,
            total_completed_today: 73,
            avg_wait_time_today: 18.5,
            busiest_service: "Emergency Care",
            efficiency_score: 0.92
        };
    }
}

// Export singleton instance
export const queueService = new QueueService();
export default queueService;
