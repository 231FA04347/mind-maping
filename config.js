// Configuration file for API keys and endpoints
const CONFIG = {
    // OpenAI API configuration
    OPENAI_API_KEY: "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",
    OPENAI_API_ENDPOINT: "https://openrouter.ai/api/v1",
    
    // YouTube Data API configuration
    YOUTUBE_API_KEY: "your-youtube-api-key",
    
    // Custom backend API configuration
    API_ENDPOINT: "https://your-backend-api.com",
    
    // Feature flags
    ENABLE_FILE_UPLOAD: true,
    ENABLE_YOUTUBE: true,
    ENABLE_DIRECT_LINKS: true,
    
    // Processing limits
    MAX_VIDEO_DURATION: 3600, // in seconds
    MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB in bytes
    
    // Mind map configuration
    DEFAULT_MIND_MAP_DEPTH: 3,
    MAX_NODES_PER_LEVEL: 10
};