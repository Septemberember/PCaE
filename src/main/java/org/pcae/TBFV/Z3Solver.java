package org.pcae.TBFV;

import org.pcae.verification.FSFValidationUnit;
import org.pcae.verification.SpecUnit;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;

public class Z3Solver {
    public static TBFVResult callZ3Solver(SpecUnit su) throws IOException {
        TBFVResult res =null;
        String suJson = su.toJson();

        String threadId = String.valueOf(Thread.currentThread().getId());
        String filePath = "temp_" + threadId;

        try {
            String encodedJson = Base64.getEncoder().encodeToString(suJson.getBytes(StandardCharsets.UTF_8));
            Files.write(Paths.get(filePath), encodedJson.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
        ProcessBuilder pb = new ProcessBuilder("python3", "resources/z3_validation_runner.py", "--su",filePath);
        pb.environment().put("PYTHONIOENCODING", "UTF-8");
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder errorInfo = new StringBuilder();
        String line;
        while((line = reader.readLine()) != null){
            if(line.startsWith("result:")){
                String resultJson = line.substring("result:".length()).trim();
                res = new TBFVResult(resultJson);
            }
            System.out.println(line);
        }

        BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        while((line = errReader.readLine()) != null){
            System.err.println("Error: " + line);
            errorInfo.append(line).append("\n");
        }

        try {
            process.waitFor();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

        if(res == null && !errorInfo.toString().isEmpty()){
            System.out.println("no result form TBFV");
            res = new TBFVResult(-1,"Something wrong with z3 verifier：\n" + errorInfo, "");
        }
        return res;
    }

    public static TBFVResult callZ3Solver(FSFValidationUnit fu) throws IOException {
        TBFVResult res =null;
        String fuJson = fu.toJson();
        String threadId = String.valueOf(Thread.currentThread().getId());
        String filePath = "temp_" + threadId;
        try {
            String encodedJson = Base64.getEncoder().encodeToString(fuJson.getBytes(StandardCharsets.UTF_8));
            Files.write(Paths.get(filePath), encodedJson.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }

        ProcessBuilder pb = new ProcessBuilder("python3", "resources/z3_validation_runner.py", "--fu",filePath);
        pb.environment().put("PYTHONIOENCODING", "UTF-8");
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        while((line = reader.readLine()) != null){
            if(line.startsWith("FSF validation result:")){
                String resultJson = line.substring("FSF validation result:".length()).trim();
                res = new TBFVResult(resultJson);
            }
            System.out.println(line);
        }

        StringBuilder errorInfo = new StringBuilder();
        while((line = reader.readLine()) != null){
            if(line.startsWith("result:")){
                String resultJson = line.substring("result:".length()).trim();
                res = new TBFVResult(resultJson);
            }
            System.out.println(line);
        }
        BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        while((line = errReader.readLine()) != null){
            System.err.println("Error: " + line);
            errorInfo.append(line).append("\n");
        }

        try {
            process.waitFor();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

        if(res == null && !errorInfo.toString().isEmpty()){
            System.out.println("no result form TBFV");
            res = new TBFVResult(-1,"Something wrong with z3 verifier：\n" + errorInfo, "");
        }
        return res;
    }

    public static TBFVResult callZ3Solver2GenerateTestcase(SpecUnit gu) throws IOException {
        TBFVResult res =null;
        String guJson = gu.toJson();
        //System.out.println("guJson: " + guJson);
        String threadId = String.valueOf(Thread.currentThread().getId());
        String filePath = "temp_" + threadId;
        try {
            String encodedJson = Base64.getEncoder().encodeToString(guJson.getBytes(StandardCharsets.UTF_8));
            Files.write(Paths.get(filePath), encodedJson.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
        ProcessBuilder pb = new ProcessBuilder("python3", "resources/z3_validation_runner.py", "--gu",filePath);
        pb.environment().put("PYTHONIOENCODING", "UTF-8");
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder errorInfo = new StringBuilder();
        String line;
        while((line = reader.readLine()) != null){
            if(line.startsWith("Testcase generation result:")){
                String resultJson = line.substring("Testcase generation result:".length()).trim();
                res = new TBFVResult(resultJson);
            }
            System.out.println(line);
        }

        // 读取错误信息
        BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        while((line = errReader.readLine()) != null){
            System.err.println("Error: " + line);
            errorInfo.append(line).append("\n");
        }

        // 等待进程结束
        try {
            process.waitFor();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        if(res == null){
            System.out.println("no result form TBFV");
            res = new TBFVResult(-1,"Something wrong with z3 verifier：\n" + errorInfo, "");
        }
        return res;
    }

}
