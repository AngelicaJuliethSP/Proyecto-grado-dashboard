package com.saucedemo.pages;

import com.saucedemo.base.BasePage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;

public class CheckoutCompletePage extends BasePage {

    @FindBy(css = "[data-test='complete-header']")
    private WebElement thankYouMessage;

    public CheckoutCompletePage(WebDriver driver) {
        super(driver);
    }

    public String getThankYouMessage() {
        return thankYouMessage.getText();
    }
}
