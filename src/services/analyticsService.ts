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
    type: 'critical' | 'warning' | 'info' | 'improvement';
    message: string;
    action: string;
}

class AnalyticsService {
    public async getWaitTimes(): Promise<WaitTimeAnalytics[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/wait-times`);
        if (!response.ok) {
            throw new Error('Failed to fetch wait time analytics');
        }
        return await response.json();
    }

    public async getPeakHours(): Promise<PeakHourAnalytics[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/peak-hours`);
        if (!response.ok) {
            throw new Error('Failed to fetch peak hours');
        }
        return await response.json();
    }

    public async getServiceDistribution(): Promise<ServiceDistribution[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/service-distribution`);
        if (!response.ok) {
            throw new Error('Failed to fetch service distribution');
        }
        return await response.json();
    }

    public async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/recommendations`);
        if (!response.ok) {
            throw new Error('Failed to fetch AI recommendations');
        }
        return await response.json();
    }
}

export const analyticsService = new AnalyticsService();

class AIRecommendationService {
    async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await fetch(`${API_BASE_URL}/analytics/recommendations`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch AI recommendations');
        }

        return response.json();
    }
};
