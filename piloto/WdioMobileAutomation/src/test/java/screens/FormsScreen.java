package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;

public class FormsScreen extends BaseScreen {

    private final By screenContainer = AppiumBy.accessibilityId("Forms-screen");
    private final By inputField = AppiumBy.accessibilityId("text-input");

    public FormsScreen(AndroidDriver driver) {
        super(driver);
    }

    public boolean isScreenDisplayed() {
        return isDisplayed(screenContainer);
    }

    public String getInputPlaceholder() {
        return getText(inputField);
    }
}
