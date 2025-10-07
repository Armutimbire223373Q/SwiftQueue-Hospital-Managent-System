import apiClient from './apiClient';

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
        const response = await apiClient.get('/analytics/wait-times');
        return response.data;
    }

    public async getPeakHours(): Promise<PeakHourAnalytics[]> {
        const response = await apiClient.get('/analytics/peak-hours');
        return response.data;
    }

    public async getServiceDistribution(): Promise<ServiceDistribution[]> {
        const response = await apiClient.get('/analytics/service-distribution');
        return response.data;
    }

    public async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await apiClient.get('/analytics/recommendations');
        return response.data;
    }
}

export const analyticsService = new AnalyticsService();

class AIRecommendationService {
    async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await apiClient.get('/analytics/recommendations');
        return response.data;
    }
};
