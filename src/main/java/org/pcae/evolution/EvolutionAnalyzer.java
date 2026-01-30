package org.pcae.evolution;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import org.pcae.log.LogManager;

/**
 * EvolutionAnalyzer - 专门用于分析程序演化实验结果的工具类
 * 功能：统计平均对话轮数 (Avg Rounds) 和代码继承率分布 (LPR Distribution / Fig.3)
 */
public class EvolutionAnalyzer {

    private static final String[] CATEGORIES = {"BorderConditionMove", "EXCHANGE_D", "MERGE_TD"};
    private static final String MODEL_NAME = "gpt-5.2";

    public static void analyzeExperiment(String experimentRoot) {
        System.out.println("========== 实验分析报告 (Fig. 3 分布数据) ==========");
        System.out.println("实验根目录: " + experimentRoot);

        for (String category : CATEGORIES) {
            String categoryPath = experimentRoot + File.separator + category;
            File categoryDir = new File(categoryPath);
            if (!categoryDir.exists()) continue;

            System.out.println("\n------------------------------------------------");
            System.out.println("正在处理分类: " + category);

            // 1. 自动探测日志路径（处理嵌套目录情况）
            String logBase = categoryPath + File.separator + "openai" + File.separator + MODEL_NAME;
            File logDirFile = new File(logBase);
            String finalLogPath = logBase;
            if (logDirFile.exists()) {
                File subDir = new File(logDirFile, MODEL_NAME);
                if (subDir.exists() && subDir.isDirectory()) {
                    finalLogPath = subDir.getAbsolutePath();
                }
            }

            // 2. 执行核心统计
            processLPSWithDistribution(categoryPath, finalLogPath);

            // 3. 统计平均对话轮数
            double avgRounds = calculateAvgRounds(finalLogPath);
            System.out.printf(">>> [%s] 最终统计 - 平均对话轮数: %.2f\n", category, avgRounds);
        }
    }

    /**
     * 以 succDataset 为基准，统计 LPR 分布
     */
    private static void processLPSWithDistribution(String categoryPath, String finalLogPath) {
        String succDirPath = categoryPath + File.separator + "succDataset";
        File succDir = new File(succDirPath);
        File[] succFiles = succDir.listFiles((d, name) -> name.endsWith(".txt"));

        if (succFiles == null || succFiles.length == 0) {
            System.err.println("错误：找不到有效的 succDataset 目录或该目录下无文件！");
            return;
        }

        int totalExpected = succFiles.length;
        int[] bins = new int[5]; // [0,20), [20,40), [40,60), [60,80), [80,100]
        double totalRate = 0;
        int processedCount = 0;
        List<String> failedItems = new ArrayList<>();

        for (File file : succFiles) {
            String className = file.getName().replace(".txt", "");
            try {
                // A. 获取原始代码 (来自 succDataset)
                String originalCode = LogManager.getOriginalCodeFromEvoTaskFile(file.getAbsolutePath());

                // B. 获取修改后的代码 (来自对应的日志文件)
                String logFilePath = finalLogPath + File.separator + "log-" + className + ".txt";
                File logFile = new File(logFilePath);

                if (!logFile.exists()) {
                    failedItems.add(className + " (日志文件不存在)");
                    continue;
                }

                String modifiedCode = extractCodeFromCustomLog(logFilePath);

                if (originalCode != null && modifiedCode != null) {
                    double rate = calculateDerivedRate(originalCode, modifiedCode);
                    totalRate += rate;
                    processedCount++;

                    int binIndex = (int) (rate * 100 / 20);
                    if (binIndex >= 5) binIndex = 4;
                    bins[binIndex]++;
                } else {
                    failedItems.add(className + " (代码提取为空)");
                }
            } catch (Exception e) {
                failedItems.add(className + " (程序异常: " + e.getMessage() + ")");
            }
        }

        // 输出该分类的统计结果
        if (processedCount > 0) {
            System.out.printf("有效样本数: %d / 期望总数: %d\n", processedCount, totalExpected);
            if (!failedItems.isEmpty()) {
                System.out.println("未计入的任务列表: " + failedItems);
            }

            System.out.println("Fig. 3 分布数据 (Lineage Preservation Ratio):");
            String[] labels = {"[0, 20)", "[20, 40)", "[40, 60)", "[60, 80)", "[80, 100]"};
            for (int i = 0; i < 5; i++) {
                System.out.printf("  %-10s : %d 个 (%.2f%%)\n", labels[i], bins[i], (double)bins[i]/processedCount*100);
            }

            int over60 = bins[3] + bins[4];
            System.out.printf("  => LPR > 60%% 的任务占比: %.2f%% (%d/%d)\n",
                    (double)over60/processedCount*100, over60, processedCount);
            System.out.printf("  => 平均继承率 (LPR): %.2f%%\n", (totalRate / processedCount) * 100);
        }
    }

    /**
     * 针对特定日志格式提取最后一次 Assistant 回复中的代码块
     */
    private static String extractCodeFromCustomLog(String filePath) {
        try {
            String content = Files.readString(Paths.get(filePath));

            // 1. 定位最后一个 assistant 角色回复区域
            // 兼容是否有星号的情况: start role assistant / *start* role assistant
            String patternStr = "(?:\\*?start\\*?\\s+role\\s+assistant)(.*?)(?:\\*?end\\*?\\s+role\\s+assistant)";
            Pattern pSection = Pattern.compile(patternStr, Pattern.DOTALL | Pattern.CASE_INSENSITIVE);
            Matcher mSection = pSection.matcher(content);

            String lastAssistantResponse = "";
            while (mSection.find()) {
                lastAssistantResponse = mSection.group(1);
            }

            if (lastAssistantResponse.isEmpty()) return null;

            // 2. 从助手回复中提取 Markdown 代码块
            Pattern pCode = Pattern.compile("```(?:[a-zA-Z]*)\\s*(.*?)\\s*```", Pattern.DOTALL);
            Matcher mCode = pCode.matcher(lastAssistantResponse);
            String code = null;
            while (mCode.find()) {
                code = mCode.group(1).trim();
            }
            return code;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 统计对话轮数 (以 start role user 出现次数为准)
     */
    private static double calculateAvgRounds(String logPath) {
        File folder = new File(logPath);
        File[] logs = folder.listFiles((d, name) -> name.endsWith(".txt"));
        if (logs == null) return 0.0;

        int totalRounds = 0, filesCount = 0;
        for (File log : logs) {
            try {
                String content = Files.readString(log.toPath());
                int rounds = 0;
                Matcher m = Pattern.compile("(?:\\*?start\\*?\\s+role\\s+user)", Pattern.CASE_INSENSITIVE).matcher(content);
                while (m.find()) rounds++;

                if (rounds > 0) {
                    totalRounds += rounds;
                    filesCount++;
                }
            } catch (Exception e) {}
        }
        return filesCount == 0 ? 0.0 : (double) totalRounds / filesCount;
    }

    /**
     * 计算派生行比例 (LPR)
     */
    private static double calculateDerivedRate(String before, String after) {
        // 预处理：只保留非空白、非注释行进行对比
        Set<String> beforeSet = new HashSet<>();
        for (String line : before.split("\\R")) {
            String t = line.trim();
            if (!t.isEmpty() && !t.startsWith("/") && !t.startsWith("*")) {
                beforeSet.add(t);
            }
        }

        long matched = 0, total = 0;
        for (String line : after.split("\\R")) {
            String t = line.trim();
            if (t.isEmpty() || t.startsWith("/") || t.startsWith("*")) continue;
            total++;
            if (beforeSet.contains(t)) matched++;
        }
        return total == 0 ? 0 : (double) matched / total;
    }

    public static void main(String[] args) {
        // 执行分析任务
        analyzeExperiment("resources/experiment/20260127-RQ3-Evo-Test");
    }
}