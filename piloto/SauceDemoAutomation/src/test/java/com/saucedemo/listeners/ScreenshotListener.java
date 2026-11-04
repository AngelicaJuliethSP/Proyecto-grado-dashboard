package com.saucedemo.listeners;

import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.ITestListener;
import org.testng.ITestResult;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.nio.file.Path;

public class ScreenshotListener implements  ITestListener {

    @Override
    public void onTestFailure(ITestResult result) {
        Object testClassInstance = result.getInstance();
        WebDriver driver = getDriverFromTestClass(testClassInstance);

        if (driver != null) {
            takeScreenshot(driver, result.getName());
        }
    }

    private WebDriver getDriverFromTestClass(Object testClassInstance) {
        try {
            var field = testClassInstance.getClass().getSuperclass().getDeclaredField("driver");
            field.setAccessible(true);
            return (WebDriver) field.get(testClassInstance);
        } catch (Exception e) {
            System.out.println("Could not retrieve WebDriver instance for screenshot: " + e.getMessage());
            return null;
        }
    }

    private void takeScreenshot(WebDriver driver, String testName) {
        try {
            File source = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String fileName = testName + "_" + timestamp + ".png";

            Files.createDirectories(Paths.get("screenshots"));
            Path destination = Paths.get("screenshots", fileName);
            Files.copy(source.toPath(), destination);

            System.out.println("Screenshot saved: " + destination);
        } catch (IOException e) {
            System.out.println("Failed to save screenshot: " + e.getMessage());
        }
    }
}
