package com.saucedemo.tests;

import com.saucedemo.base.BaseTest;
import com.saucedemo.pages.CartPage;
import com.saucedemo.pages.InventoryPage;
import com.saucedemo.pages.LoginPage;
import org.testng.Assert;
import org.testng.annotations.Test;
import org.testng.annotations.Listeners;

@Listeners(com.saucedemo.listeners.ScreenshotListener.class)

public class RemoveCartItemsTest extends BaseTest{

    @Test
    public void removeAllItemsFromCart() {
        LoginPage loginPage = new LoginPage(driver);
        InventoryPage inventoryPage = loginPage.login("standard_user", "secret_sauce");

        inventoryPage.addProductToCartByIndex(0);
        inventoryPage.addProductToCartByIndex(1);
        inventoryPage.addProductToCartByIndex(2);

        CartPage cartPage = inventoryPage.goToCart();
        Assert.assertEquals(cartPage.getCartItemsCount(), 3,
                "Expected 3 items in the cart before removal.");

        cartPage.removeAllItems();
        Assert.assertEquals(cartPage.getCartItemsCount(), 0,
                "The cart should be empty after removing all items.");
    }

}
