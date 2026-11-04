package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;

public class DragScreen extends BaseScreen {

    private final By screenContainer = AppiumBy.accessibilityId("Drag-drop-screen");

    public DragScreen(AndroidDriver driver) {
        super(driver);
    }

    public boolean isScreenDisplayed() {
        return isDisplayed(screenContainer);
    }
}