package com.saucedemo.tests;

import com.saucedemo.base.BaseTest;
import com.saucedemo.pages.*;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Listeners;
import org.testng.annotations.Test;

@Listeners(com.saucedemo.listeners.ScreenshotListener.class)

public class PurchaseTest extends BaseTest {

    @DataProvider(name = "validUsers")
    public Object[][] validUsers() {
        return new Object[][] {
                { "standard_user", "secret_sauce" },
                { "performance_glitch_user", "secret_sauce" }
        };
    }

    @Test(dataProvider = "validUsers")
    public void purchaseProductSuccessfully(String username, String password) {
        LoginPage loginPage = new LoginPage(driver);
        InventoryPage inventoryPage = loginPage.login(username, password);

        inventoryPage.addRandomProductToCart();
        CartPage cartPage = inventoryPage.goToCart();

        CheckoutStepOnePage stepOnePage = cartPage.checkout();
        CheckoutStepTwoPage stepTwoPage = stepOnePage.fillPersonalInfo("Angelica", "Silva", "110110");
        CheckoutCompletePage completePage = stepTwoPage.finish();

        Assert.assertEquals(completePage.getThankYouMessage(), "Thank you for your order!",
                "The confirmation message was not displayed correctly for user: " + username);
    }
}
