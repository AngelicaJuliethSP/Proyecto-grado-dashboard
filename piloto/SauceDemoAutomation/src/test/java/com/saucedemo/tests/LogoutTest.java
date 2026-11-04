package com.saucedemo.tests;

import com.saucedemo.base.BaseTest;
import com.saucedemo.pages.InventoryPage;
import com.saucedemo.pages.LoginPage;
import org.testng.Assert;
import org.testng.annotations.Test;
import org.testng.annotations.Listeners;

@Listeners(com.saucedemo.listeners.ScreenshotListener.class)

public class LogoutTest extends BaseTest{

    @Test
    public void logoutRedirectsToLoginPage() {
        LoginPage loginPage = new LoginPage(driver);
        InventoryPage inventoryPage = loginPage.login("standard_user", "secret_sauce");

        loginPage = inventoryPage.logout();

        Assert.assertTrue(driver.getCurrentUrl().equals("https://www.saucedemo.com/"),
                "User was not redirected to the login page after logout.");
    }

}
