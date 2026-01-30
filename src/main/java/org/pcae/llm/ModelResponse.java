package org.pcae.llm;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;

/**
 * 针对 OpenRouter/OpenAI 接口设计的通用 POJO
 * 增加了对推理字段 (Reasoning) 和 成本字段 (Cost) 的支持
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class ModelResponse {
    private String id;
    private String object;
    private long created;
    private String model;
    private String provider;
    private List<Choice> choices;
    private Usage usage;

    // OpenRouter 特有字段
    private double cost;
    @JsonProperty("is_byok")
    private boolean isByok;

    @JsonProperty("system_fingerprint")
    private String systemFingerprint;
    @JsonProperty("service_tier")
    private String serviceTier;

    // 全局静态配置：忽略所有未知字段，防止反序列化失败
    private final static ObjectMapper objectMapper = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    public ModelResponse() {}

    /**
     * 安全的反序列化方法
     */
    public static ModelResponse fromJson(String json) {
        try {
            return objectMapper.readValue(json, ModelResponse.class);
        } catch (Exception e) {
            // 这里可以记录日志，防止静默失败
            System.err.println("JSON解析失败: " + e.getMessage());
            return null;
        }
    }

    // --- 内部类 Choice ---
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Choice {
        private int index;
        private ModelMessage message; // 假设你已有 ModelMessage 类
        private Object logprobs;

        @JsonProperty("finish_reason")
        private String finishReason;

        @JsonProperty("native_finish_reason")
        private String nativeFinishReason;

        // 针对 GPT-5 或深度思考模型可能返回的 reasoning_details
        @JsonProperty("reasoning_details")
        private Object reasoningDetails;

        // Getters and Setters...
        public ModelMessage getMessage() { return message; }
        public void setMessage(ModelMessage message) { this.message = message; }
        public String getFinishReason() { return finishReason; }
        public void setFinishReason(String finishReason) { this.finishReason = finishReason; }
    }

    // --- 内部类 Usage ---
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Usage {
        @JsonProperty("prompt_tokens")
        private int promptTokens;
        @JsonProperty("completion_tokens")
        private int completionTokens;
        @JsonProperty("total_tokens")
        private int totalTokens;

        @JsonProperty("completion_tokens_details")
        private CompletionTokensDetails completionTokensDetails;

        public int getPromptTokens() {
            return promptTokens;
        }

        public void setPromptTokens(int promptTokens) {
            this.promptTokens = promptTokens;
        }

        // Getters and Setters...
        public int getTotalTokens() { return totalTokens; }
        public void setTotalTokens(int totalTokens) { this.totalTokens = totalTokens; }
        public CompletionTokensDetails getCompletionTokensDetails() { return completionTokensDetails; }
        public void setCompletionTokensDetails(CompletionTokensDetails details) { this.completionTokensDetails = details; }
    }

    // --- 内部类 CompletionTokensDetails ---
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CompletionTokensDetails {
        @JsonProperty("reasoning_tokens")
        private int reasoningTokens = 0; // 设置默认值防止 null
        @JsonProperty("audio_tokens")
        private int audioTokens = 0;

        public int getReasoningTokens() { return reasoningTokens; }
        public void setReasoningTokens(int reasoningTokens) { this.reasoningTokens = reasoningTokens; }
    }

    // --- 此处省略其他 Getters 和 Setters (建议使用 Lombok @Data 简化) ---
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public List<Choice> getChoices() { return choices; }
    public void setChoices(List<Choice> choices) { this.choices = choices; }
    public Usage getUsage() { return usage; }
    public void setUsage(Usage usage) { this.usage = usage; }
}