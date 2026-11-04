package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;

public class MenuScreen extends BaseScreen {

    private final By screenContainer = AppiumBy.accessibilityId("tab-side-menu-panel");

    public MenuScreen(AndroidDriver driver) {
        super(driver);
    }

    public boolean isScreenDisplayed() {
        return isDisplayed(screenContainer);
    }
}