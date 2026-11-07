package com.saucedemo.base;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;

import java.util.HashMap;
import java.util.Map;

/**
 * Base de los tests web.
 *
 * Configuración (en orden de prioridad):
 *   1. Propiedad del sistema: -Dbase.url=..., -Dheadless=true
 *   2. Variable de entorno: BASE_URL, HEADLESS
 *   3. Valor por defecto
 */
public class BaseTest {

    private static final String DEFAULT_BASE_URL = "https://www.saucedemo.com/";

    protected WebDriver driver;

    @BeforeMethod
    public void setUp() {
        ChromeOptions options = new ChromeOptions();

        Map<String, Object> prefs = new HashMap<>();
        prefs.put("credentials_enable_service", false);
        prefs.put("profile.password_manager_leak_detection", false);
        options.setExperimentalOption("prefs", prefs);
        options.addArguments("--disable-features=PasswordLeakDetection,PasswordManagerOnboarding");

        if (isHeadless()) {
            options.addArguments("--headless=new", "--window-size=1920,1080");
        }

        driver = new ChromeDriver(options);
        driver.manage().window().maximize();
        driver.get(getBaseUrl());
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    protected static String getBaseUrl() {
        return getConfig("base.url", "BASE_URL", DEFAULT_BASE_URL);
    }

    protected static boolean isHeadless() {
        return Boolean.parseBoolean(getConfig("headless", "HEADLESS", "false"));
    }

    private static String getConfig(String systemProperty, String envVariable, String defaultValue) {
        String value = System.getProperty(systemProperty);
        if (value == null || value.isBlank()) {
            value = System.getenv(envVariable);
        }
        return (value == null || value.isBlank()) ? defaultValue : value;
    }
}
