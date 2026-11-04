package com.saucedemo.pages;

import com.saucedemo.base.BasePage;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;

import java.util.List;
import java.util.Random;

public class InventoryPage extends BasePage {

    @FindBy(className = "shopping_cart_link")
    private WebElement cartIcon;

    @FindBy(css = "button[class*='btn_inventory']")
    private List<WebElement> addToCartButtons;

    public InventoryPage(WebDriver driver) {
            super(driver);
    }

    public void addRandomProductToCart() {
        int randomIndex = new Random().nextInt(addToCartButtons.size());
        addToCartButtons.get(randomIndex).click();
    }

    public void addProductToCartByIndex(int index) {
        addToCartButtons.get(index).click();
    }

    public CartPage goToCart() {
        cartIcon.click();
        return new CartPage(driver);
    }

}
