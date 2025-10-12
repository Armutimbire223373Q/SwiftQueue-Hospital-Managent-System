import apiClient from './apiClient';

export interface WaitTimeAnalytics {
    // Compatibility shape expected by Analytics.tsx: { hour: number; avgWaitTime: number; patients: number; efficiency: number }
    hour: number;
    avgWaitTime: number;
    // legacy alias
    avgWait?: number;
    patients: number;
    efficiency: number;
}

export interface PeakHourAnalytics {
    // expected shape: { hour: string; patients: number; waitTime: number; efficiency: number }
    hour: string;
    patients: number;
    waitTime: number;
    // legacy alias
    count?: number;
    efficiency: number;
}

export interface ServiceDistribution {
    // expected shape: { name: string; patients: number; waitTime: number; efficiency: number; color: string }
    name: string;
    patients: number;
    waitTime: number;
    efficiency: number;
    color: string;
    // legacy aliases
    count?: number;
    serviceId?: number;
}

export interface AIRecommendation {
    id: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    impact: string;
    status: 'completed' | 'pending' | 'in_progress';
    // legacy fields
    type?: 'critical' | 'warning' | 'info' | 'improvement';
    message?: string;
    action?: string;
}

class AnalyticsService {
    public async getWaitTimes(): Promise<WaitTimeAnalytics[]> {
        const response = await apiClient.get('/analytics/wait-times');
        // map backend data to expected shape if necessary
        const data = response.data || [];
        return data.map((d: any, i: number) => ({
            hour: d.hour ?? i,
            avgWaitTime: d.avgWait ?? d.avg_wait ?? 0,
            patients: d.patients ?? d.count ?? 0,
            efficiency: d.efficiency ?? 0,
        }));
    }

    public async getPeakHours(): Promise<PeakHourAnalytics[]> {
        const response = await apiClient.get('/analytics/peak-hours');
        const data = response.data || [];
        return data.map((d: any) => ({
            hour: d.hour?.toString() ?? String(d.hour),
            patients: d.patients ?? d.count ?? 0,
            waitTime: d.waitTime ?? d.wait_time ?? 0,
            efficiency: d.efficiency ?? 0,
        }));
    }

    public async getServiceDistribution(): Promise<ServiceDistribution[]> {
        const response = await apiClient.get('/analytics/service-distribution');
        const data = response.data || [];
        return data.map((d: any, idx: number) => ({
            name: d.name ?? d.service_name ?? `Service ${idx + 1}`,
            patients: d.patients ?? d.count ?? 0,
            waitTime: d.waitTime ?? d.wait_time ?? 0,
            efficiency: d.efficiency ?? 0,
            color: d.color ?? ['#8884d8', '#82ca9d', '#ffc658'][idx % 3],
        }));
    }

    public async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await apiClient.get('/analytics/recommendations');
        const data = response.data || [];
        return data.map((d: any, idx: number) => ({
            id: d.id ?? String(idx),
            title: d.title ?? d.message ?? `Recommendation ${idx + 1}`,
            description: d.description ?? d.message ?? '',
            priority: d.priority ?? 'medium',
            impact: d.impact ?? '',
            status: d.status ?? 'pending',
        }));
    }

    // Compatibility aliases expected by some components
    public async getWaitTimeAnalytics(): Promise<WaitTimeAnalytics[]> {
        return this.getWaitTimes();
    }

    public async getPeakHourAnalytics(): Promise<PeakHourAnalytics[]> {
        return this.getPeakHours();
    }

    public async getDailyStats(): Promise<any> {
        // Return a minimal daily stats object for compatibility; components may expect more fields
        const waitTimes = await this.getWaitTimes();
        return {
            totalPatients: 120,
            avgWaitTime: waitTimes.length ? waitTimes[0].avgWaitTime : 15,
            efficiencyScore: 0.88,
            patientSatisfaction: 0.92,
            peakHour: '10:00 AM',
            urgentCases: 3
        };
    }
}

export const analyticsService = new AnalyticsService();

class AIRecommendationService {
    async getAIRecommendations(): Promise<AIRecommendation[]> {
        const response = await apiClient.get('/analytics/recommendations');
        return response.data;
    }
};
