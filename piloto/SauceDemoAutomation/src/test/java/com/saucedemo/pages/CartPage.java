package com.saucedemo.pages;

import com.saucedemo.base.BasePage;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;

import java.util.List;

public class CartPage extends BasePage {

    @FindBy(className = "cart_item")
    private List<WebElement> cartItems;

    @FindBy(css = "button[class*='cart_button']")
    private List<WebElement> removeButtons;

    @FindBy(id = "checkout")
    private WebElement checkoutButton;

    public CartPage(WebDriver driver) {
        super(driver);
    }

    public void removeAllItems() {
        while (!removeButtons.isEmpty()) {
            removeButtons.get(0).click();
        }
    }

    public int getCartItemsCount() {
        return cartItems.size();
    }

    public CheckoutStepOnePage checkout() {
        checkoutButton.click();
        return new CheckoutStepOnePage(driver);
    }
}
