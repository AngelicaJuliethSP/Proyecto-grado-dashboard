package com.globant.automation.config;

import org.testng.annotations.BeforeSuite;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class TestRunner {

    public static final String PROPERTIES_FILE = "src/test/resources/config.properties";
    public static final Properties PROPERTIES = new Properties();

    private static String baseUrl;

    @BeforeSuite
    public void setUpEnvironment() {
        loadProperties();
        baseUrl = getConfigVariable("url.base");
    }

    private void loadProperties() {
        try (FileInputStream fileInputStream = new FileInputStream(PROPERTIES_FILE)) {
            PROPERTIES.load(fileInputStream);
        } catch (IOException e) {
            System.out.println(String.format("Error loading the properties file: %s", e.getMessage()));
        }
    }

    private String getConfigVariable(String key) {
        return PROPERTIES.getProperty(key);
    }

    public static String getBaseUrl() {
        return baseUrl;
    }
}
