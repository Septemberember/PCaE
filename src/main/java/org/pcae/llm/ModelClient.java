package org.pcae.llm;

import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class ModelClient {
    private final String url;
    private final String API_KEY;


    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(3, TimeUnit.MINUTES) // 核心修改：防止模型生成慢导致误判超时
            .writeTimeout(30, TimeUnit.SECONDS)
            .build();

    public ModelClient(ModelConfig mc) {
        this.url = mc.getUrl();
        this.API_KEY = mc.getApiKey();
    }
    public ModelClient(String url, String apiKey){
        this.url = url;
        this.API_KEY = apiKey;
    }

    public ModelResponse call(ModelPrompt prompt) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        String requestBody = objectMapper.writeValueAsString(prompt);

        RequestBody body = RequestBody.create(requestBody, MediaType.parse("application/json"));
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .addHeader("Authorization", "Bearer " + API_KEY)
                .addHeader("Content-Type", "application/json")
                // 可选：添加应用标识，有时能帮助 OpenRouter 更好地分配资源
                .addHeader("HTTP-Referer", "http://localhost:8080")
                .addHeader("X-Title", "MyCodingAgent")
                .build();

        int maxRetries = 10;
        int retryCount = 0;
        long backoffMs = 2000; // 初始退避 2 秒
        IOException lastException = null;

        while (retryCount < maxRetries) {
            // 关键：检测线程是否被外部 shutdownNow() 中断
            if (Thread.currentThread().isInterrupted()) {
                throw new IOException("Task interrupted, stopping retries.");
            }

            try (Response response = client.newCall(request).execute()) {
                // 1. 请求成功
                if (response.isSuccessful()) {
                    assert response.body() != null;
                    return parseRespFromJson(response.body().string());
                }

                // 2. 处理限速 (429) 或 服务器繁忙 (5xx)
                int code = response.code();
                if (code == 429 || code >= 500) {
                    // 读取错误详情（OpenRouter 经常在 body 里给出原因）
                    String errorMsg = response.body() != null ? response.body().string() : response.message();
                    System.err.println("OpenRouter 繁忙/限速 (Code: " + code + "): " + errorMsg);
                    throw new IOException("Retryable status code: " + code);
                }

                // 3. 其它不可恢复错误 (401 没钱了, 400 格式错等)
                throw new IOException("Unrecoverable error: " + code + " " + response.message());

            } catch (IOException e) {
                retryCount++;
                lastException = e;

                if (retryCount >= maxRetries) break;

                // 指数退避：32线程并发时，错开重试时间非常重要
                System.err.println("正在进行第 " + retryCount + " 次重试，等待 " + (backoffMs / 1000.0) + " 秒...");
                try {
                    Thread.sleep(backoffMs);
                    // 每次失败等待时间翻倍，最大不超过 30 秒
                    backoffMs = Math.min(backoffMs * 2, 30000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new IOException("Interrupted during backoff", ie);
                }
            }
        }
        throw new IOException("10次尝试后依然失败: " + lastException.getMessage());
    }

    public ModelResponse parseRespFromJson(String json) {
        return ModelResponse.fromJson(json);
    }

}
