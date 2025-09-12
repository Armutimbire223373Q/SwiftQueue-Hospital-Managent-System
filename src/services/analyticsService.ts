const API_BASE_URL = 'http://localhost:8000/api';

export interface WaitTimeAnalytics {
    date: string;
    avgWait: number;
}

export interface PeakHourAnalytics {
    hour: number;
    count: number;
}

export interface ServiceDistribution {
    serviceId: number;
    count: number;
}

export interface AIRecommendation {
    title: string;
    description: string;
}

export const analyticsService = {
    async getWaitTimes(): Promise<WaitTimeAnalytics[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/wait-times`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch wait time analytics');
        }

        return response.json();
    },

    async getPeakHours(): Promise<PeakHourAnalytics[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/peak-hours`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch peak hours');
        }

        return response.json();
    },

    async getServiceDistribution(): Promise<ServiceDistribution[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/service-distribution`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch service distribution');
        }

        return response.json();
    },

    async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/recommendations`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch AI recommendations');
        }

        return response.json();
    }
};
