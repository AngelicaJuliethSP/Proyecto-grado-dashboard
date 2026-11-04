package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;

public class HomeScreen extends BaseScreen {

    private final By homeIcon = AppiumBy.accessibilityId("Home");
    private final By webIcon = AppiumBy.accessibilityId("Webview");
    private final By loginIcon = AppiumBy.accessibilityId("Login");
    private final By formsIcon = AppiumBy.accessibilityId("Forms");
    private final By swipeIcon = AppiumBy.accessibilityId("Swipe");
    private final By dragIcon = AppiumBy.accessibilityId("Drag");
    private final By menuIcon = AppiumBy.accessibilityId("Menu");
    private final By homeScreenContainer = AppiumBy.accessibilityId("Home-screen");

    public HomeScreen(AndroidDriver driver) {
        super(driver);
    }

    public void tapHomeIcon() {
        tap(homeIcon);
    }

    public void tapWebIcon() {
        tap(webIcon);
    }

    public void tapLoginIcon() {
        tap(loginIcon);
    }

    public void tapFormsIcon() {
        tap(formsIcon);
    }

    public void tapSwipeIcon() {
        tap(swipeIcon);
    }

    public void tapDragIcon() {
        tap(dragIcon);
    }

    public void tapMenuIcon() {
        tap(menuIcon);
    }

    public boolean isHomeScreenDisplayed() {
        return isDisplayed(homeScreenContainer);
    }

}