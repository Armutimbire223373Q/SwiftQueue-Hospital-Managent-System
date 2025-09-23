# OpenRouter AI Integration for Symptom Analysis

This document describes the integration of OpenRouter AI service for advanced symptom analysis and emergency level determination in the Hospital Queue Management System.

## Overview

The system now includes AI-powered symptom analysis using the DeepSeek model via OpenRouter API. This enhancement provides:

- Advanced symptom analysis with emergency level determination
- AI-enhanced triage scoring
- Comprehensive patient risk assessment
- Intelligent department recommendations
- Batch processing capabilities

## Setup Instructions

### 1. Environment Variables

Add the following environment variables to your `.env` file:

```bash
# OpenRouter AI Settings
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free
OPENROUTER_SITE_URL=https://your-hospital-system.com
OPENROUTER_SITE_NAME=Hospital Queue Management System
OPENROUTER_TIMEOUT=30
OPENROUTER_MAX_RETRIES=3
```

### 2. OpenRouter API Key

The system is pre-configured with your OpenRouter API key:
```
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
```

If you need to use a different key, set the environment variable:
```bash
export OPENROUTER_API_KEY="your-new-api-key-here"
```

### 3. Install Dependencies

The integration requires the `aiohttp` library for async HTTP requests:

```bash
pip install aiohttp
```

## API Endpoints

### AI-Enhanced Triage Analysis

**POST** `/enhanced-ai/triage/ai-enhanced`

Analyzes patient symptoms using AI to determine emergency level and triage category.

**Request Body:**
```json
{
  "symptoms": "Chest pain and shortness of breath",
  "age_group": "adult",
  "insurance_type": "private",
  "department": "Emergency",
  "arrival_time": "2024-01-15T10:30:00Z",
  "medical_history": "Previous heart condition",
  "additional_context": "Patient is diabetic"
}
```

**Response:**
```json
{
  "success": true,
  "triage_result": {
    "triage_score": 3.2,
    "category": "Emergency",
    "priority_level": 4,
    "estimated_wait_time": 0,
    "resource_requirements": {...},
    "recommended_department": "Emergency",
    "ai_analysis": {
      "emergency_level": "critical",
      "confidence": 0.95,
      "reasoning": "Chest pain with shortness of breath indicates potential cardiac emergency...",
      "recommended_actions": ["Immediate ECG", "Cardiac monitoring", "IV access"],
      "risk_factors": ["Previous heart condition", "Diabetes"]
    },
    "analysis_method": "ai_enhanced"
  },
  "recommendations": [...]
}
```

### Symptom Analysis

**POST** `/enhanced-ai/symptoms/analyze`

Direct symptom analysis without full triage workflow.

**Request Body:**
```json
{
  "symptoms": "Severe headache and nausea",
  "patient_age": "adult",
  "medical_history": "Migraine history",
  "additional_context": "Started suddenly this morning"
}
```

### Batch Symptom Analysis

**POST** `/enhanced-ai/symptoms/batch-analyze`

Analyze multiple symptoms in a single request.

**Request Body:**
```json
[
  {
    "symptoms": "Chest pain",
    "patient_age": "senior"
  },
  {
    "symptoms": "Fever and cough",
    "patient_age": "pediatric"
  }
]
```

### Cache Management

**GET** `/enhanced-ai/cache/stats`

Get cache statistics and performance metrics.

**Response:**
```json
{
  "success": true,
  "cache_stats": {
    "total_cached_entries": 15,
    "active_entries": 12,
    "expired_entries": 3,
    "cache_ttl_hours": 1.0,
    "cache_hit_rate": "N/A"
  }
}
```

**POST** `/enhanced-ai/cache/clear`

Clear the response cache.

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

## Frontend Integration

### Using the AI Service

```typescript
import { aiService } from './services/aiService';

// AI-enhanced triage analysis
const triageResult = await aiService.getAITriageAnalysis({
  symptoms: "Chest pain and shortness of breath",
  age_group: "adult",
  insurance_type: "private",
  medical_history: "Previous heart condition"
});

// Direct symptom analysis
const analysis = await aiService.analyzeSymptomsWithAI({
  symptoms: "Severe headache",
  patient_age: "adult",
  medical_history: "Migraine history"
});

// Comprehensive analysis (combines both)
const comprehensive = await aiService.getComprehensiveSymptomAnalysis(
  "Chest pain and shortness of breath",
  "adult",
  "Previous heart condition"
);
```

## Emergency Level Classification

The AI system uses your specific medical triage prompt and classifies symptoms into four levels:

- **Level 1 — Emergency**: Life-threatening, immediate care needed
  - Chest pain, unconsciousness, severe bleeding, difficulty breathing, seizures
  - Wait time: Immediate (0 minutes)
  - Triage category: Emergency
  - Confidence: 0.90

- **Level 2 — Urgent**: Serious, needs to be seen within 1 hour
  - Severe pain, high fever, moderate injuries, mental health crisis
  - Wait time: 30 minutes
  - Triage category: Urgent
  - Confidence: 0.80

- **Level 3 — Semi-urgent**: Moderate, needs to be seen the same day
  - Chronic conditions, follow-ups, routine checkups
  - Wait time: 90 minutes
  - Triage category: Semi-urgent
  - Confidence: 0.70

- **Level 4 — Non-urgent**: Minor, can wait a few days
  - Vaccinations, consultations, routine exams
  - Wait time: 120 minutes
  - Triage category: Non-urgent
  - Confidence: 0.60

## Department Recommendations

The AI system recommends appropriate departments based on symptoms:

- **Emergency**: Critical/urgent cases, trauma, acute conditions
- **Cardiology**: Heart-related symptoms, chest pain, cardiac issues
- **Orthopedics**: Bone, joint, muscle injuries and conditions
- **Neurology**: Head injuries, seizures, neurological symptoms
- **Oncology**: Cancer-related symptoms and treatments
- **Pediatrics**: Children and adolescent health issues
- **Internal Medicine**: General adult health, chronic conditions
- **General Surgery**: Surgical conditions and procedures
- **Radiology**: Imaging needs, scans, X-rays
- **Obstetrics**: Pregnancy-related issues

## Error Handling

The system includes comprehensive error handling:

- **API Key Missing**: Falls back to traditional triage
- **API Timeout**: Retries with exponential backoff
- **Invalid Response**: Uses fallback parsing
- **Network Errors**: Graceful degradation to rule-based system

## Performance Considerations

- **Async Processing**: All AI calls are asynchronous
- **Timeout Configuration**: Configurable request timeouts
- **Retry Logic**: Automatic retries for failed requests
- **Caching**: Consider implementing response caching for common symptoms
- **Rate Limiting**: Respect OpenRouter API rate limits

## Security Considerations

- **API Key Protection**: Store API keys in environment variables
- **Input Validation**: All inputs are validated before processing
- **Error Sanitization**: Sensitive information is not exposed in error messages
- **Audit Logging**: All AI analyses are logged for audit purposes

## Monitoring and Analytics

The system provides detailed analytics:

- AI confidence scores
- Analysis accuracy metrics
- Response time monitoring
- Error rate tracking
- Usage patterns

## Troubleshooting

### Common Issues

1. **"OpenRouter API key not configured"**
   - Ensure `OPENROUTER_API_KEY` is set in environment variables
   - Verify the API key is valid and has sufficient credits

2. **"API request failed"**
   - Check network connectivity
   - Verify OpenRouter service status
   - Check API key permissions

3. **"Low AI confidence"**
   - This is normal for ambiguous symptoms
   - System falls back to traditional triage
   - Consider manual review for low-confidence cases

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
LOG_LEVEL=DEBUG
```

## Future Enhancements

- **Model Fine-tuning**: Train custom models on hospital data
- **Multi-model Support**: Support for different AI models
- **Real-time Learning**: Continuous improvement from feedback
- **Integration with EHR**: Direct integration with electronic health records
- **Mobile App Support**: Optimized for mobile applications

## Support

For issues related to the OpenRouter integration:

1. Check the logs for detailed error messages
2. Verify environment variable configuration
3. Test API connectivity manually
4. Review OpenRouter documentation for API changes

## License

This integration follows the same license as the main Hospital Queue Management System.
