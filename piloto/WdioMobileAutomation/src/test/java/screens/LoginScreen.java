package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;

public class LoginScreen extends BaseScreen {

    private final By emailInput = AppiumBy.accessibilityId("input-email");
    private final By passwordInput = AppiumBy.accessibilityId("input-password");
    private final By confirmPasswordInput = AppiumBy.accessibilityId("input-repeat-password");
    private final By loginButton = AppiumBy.accessibilityId("button-LOGIN");

    private final By signUpTab = By.xpath("//android.widget.TextView[@text='Sign up']");
    private final By loginTab = By.xpath("//android.widget.TextView[@text='Login']");
    private final By signUpButton = AppiumBy.accessibilityId("button-SIGN UP");

    private final By dialogTitle = AppiumBy.id("com.wdiodemoapp:id/alert_title");
    private final By dialogMessage = AppiumBy.id("android:id/message");
    private final By dialogOkButton = AppiumBy.id("android:id/button1");

    public LoginScreen(AndroidDriver driver) {
        super(driver);
    }

    public void switchToLoginTab() {
        tap(loginTab);
    }

    public void switchToSignUpTab() {
        tap(signUpTab);
    }

    public void enterEmail(String email) {
        driver.findElement(emailInput).sendKeys(email);
    }

    public void enterPassword(String password) {
        driver.findElement(passwordInput).sendKeys(password);
    }

    public void enterConfirmPassword(String confirmPassword) {
        waitForVisible(confirmPasswordInput).sendKeys(confirmPassword);
    }

    public void tapLogin() {
        tap(loginButton);
    }

    public void tapSignUpSubmit() {
        tap(signUpButton);
    }

    public String getDialogTitle() {
        return getText(dialogTitle);
    }

    public String getDialogMessage() {
        return getText(dialogMessage);
    }

    public void tapDialogOk() {
        tap(dialogOkButton);
    }

    public boolean isEmailFieldDisplayed() {
        return isDisplayed(emailInput);
    }

    public void submitSignUp(String email, String password) {
        switchToSignUpTab();
        enterEmail(email);
        enterPassword(password);
        enterConfirmPassword(password);
        tapSignUpSubmit();
    }

    public void submitLogin(String email, String password) {
        switchToLoginTab();
        enterEmail(email);
        enterPassword(password);
        tapLogin();
    }

}