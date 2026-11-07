package drivers;

import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.android.options.UiAutomator2Options;

import java.net.MalformedURLException;
import java.net.URL;
import java.time.Duration;

/**
 * Proveedor del AndroidDriver.
 *
 * Los valores de configuración se resuelven en este orden:
 *   1. Propiedad del sistema (-Dappium.url=..., -Ddevice.name=..., -Dapp.path=...)
 *   2. Variable de entorno (APPIUM_URL, DEVICE_NAME, APP_PATH)
 *   3. Valor por defecto
 */
public class DriverManager {

    private static final String DEFAULT_APPIUM_URL = "http://127.0.0.1:4723";
    private static final String DEFAULT_DEVICE_NAME = "Pixel_6";
    private static final String DEFAULT_APP_PATH = "apps/android.wdio.native.app.v2.2.0.apk";

    private static AndroidDriver driver;

    public static AndroidDriver getDriver() {
        if (driver == null) {
            driver = createDriver();
        }
        return driver;
    }

    private static AndroidDriver createDriver() {
        String appPath = getConfig("app.path", "APP_PATH", DEFAULT_APP_PATH);
        java.nio.file.Path appFile = java.nio.file.Path.of(appPath);
        if (!appPath.contains(":") && !appPath.startsWith("/")) {
            // ruta relativa: resolverla contra el directorio del proyecto (CWD del proceso Java)
            appFile = java.nio.file.Path.of(System.getProperty("user.dir"), appPath);
        }
        if (!java.nio.file.Files.exists(appFile)) {
            throw new RuntimeException("APK no encontrado en: " + appPath
                    + " (resuelto: " + appFile.toAbsolutePath() + "). "
                    + "Configura -Dapp.path=... o la variable APP_PATH.");
        }

        UiAutomator2Options options = new UiAutomator2Options()
                .setDeviceName(getConfig("device.name", "DEVICE_NAME", DEFAULT_DEVICE_NAME))
                .setApp(appFile.toAbsolutePath().toString())
                .setUiautomator2ServerInstallTimeout(Duration.ofSeconds(60));

        try {
            return new AndroidDriver(new URL(getConfig("appium.url", "APPIUM_URL", DEFAULT_APPIUM_URL)), options);
        } catch (MalformedURLException e) {
            throw new RuntimeException("No se pudo crear el AndroidDriver", e);
        }
    }

    private static String getConfig(String systemProperty, String envVariable, String defaultValue) {
        String value = System.getProperty(systemProperty);
        if (value == null || value.isBlank()) {
            value = System.getenv(envVariable);
        }
        return (value == null || value.isBlank()) ? defaultValue : value;
    }

    public static void quitDriver() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
    }
}
