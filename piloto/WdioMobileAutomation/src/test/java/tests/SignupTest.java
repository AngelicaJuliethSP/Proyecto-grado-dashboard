package tests;

import base.BaseTest;
import org.testng.Assert;
import org.testng.annotations.Test;
import screens.HomeScreen;
import screens.LoginScreen;
import utils.DataGenerator;

public class SignupTest extends BaseTest {

    @Test
    public void successfulSignUp() {
        HomeScreen homeScreen = new HomeScreen(driver);
        homeScreen.tapLoginIcon();

        LoginScreen loginScreen = new LoginScreen(driver);
        String randomEmail = DataGenerator.generateRandomEmail();
        loginScreen.submitSignUp(randomEmail, "Test1234!");

        String actualMessage = loginScreen.getDialogMessage();
        Assert.assertEquals(actualMessage, "You successfully signed up!",
                "El mensaje de éxito del signup no coincide");

        loginScreen.tapDialogOk();
    }
}