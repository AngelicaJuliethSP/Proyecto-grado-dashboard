package tests;

import base.BaseTest;
import org.testng.Assert;
import org.testng.annotations.Test;
import screens.*;

public class NavigationTest extends BaseTest {

    @Test
    public void navigateThroughBottomMenu() {
        HomeScreen homeScreen = new HomeScreen(driver);
        Assert.assertTrue(homeScreen.isHomeScreenDisplayed(), "Home screen no se muestra");

        homeScreen.tapWebIcon();
        WebScreen webScreen = new WebScreen(driver);
        Assert.assertTrue(webScreen.isScreenDisplayed(), "Web screen no se muestra");
        Assert.assertTrue(webScreen.isWebdriverIOTextDisplayed(), "Texto WebdriverIO no visible");

        homeScreen.tapFormsIcon();
        FormsScreen formsScreen = new FormsScreen(driver);
        Assert.assertTrue(formsScreen.isScreenDisplayed(), "Forms screen no se muestra");
        Assert.assertEquals(formsScreen.getInputPlaceholder(), "Type something",
                "El placeholder del input no coincide");

        homeScreen.tapSwipeIcon();
        SwipeScreen swipeScreen = new SwipeScreen(driver);
        Assert.assertTrue(swipeScreen.isScreenDisplayed(), "Swipe screen no se muestra");

        homeScreen.tapDragIcon();
        DragScreen dragScreen = new DragScreen(driver);
        Assert.assertTrue(dragScreen.isScreenDisplayed(), "Drag screen no se muestra");

        homeScreen.tapMenuIcon();
        MenuScreen menuScreen = new MenuScreen(driver);
        Assert.assertTrue(menuScreen.isScreenDisplayed(), "Menu screen no se muestra");
    }
}