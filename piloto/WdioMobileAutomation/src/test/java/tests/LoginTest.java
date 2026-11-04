package tests;

import base.BaseTest;
import org.testng.Assert;
import org.testng.annotations.Test;
import screens.HomeScreen;
import screens.LoginScreen;
import utils.DataGenerator;

public class LoginTest extends BaseTest {

    @Test
    public void successfulLogin() {
        HomeScreen homeScreen = new HomeScreen(driver);
        homeScreen.tapLoginIcon();

        LoginScreen loginScreen = new LoginScreen(driver);
        String email = DataGenerator.generateRandomEmail();
        String password = "Test1234!";

        loginScreen.submitSignUp(email, password);
        loginScreen.tapDialogOk();

        loginScreen.submitLogin(email, password);

        String actualMessage = loginScreen.getDialogMessage();
        Assert.assertEquals(actualMessage, "You are logged in!",
                "El mensaje de login exitoso no coincide");

        loginScreen.tapDialogOk();
    }
}