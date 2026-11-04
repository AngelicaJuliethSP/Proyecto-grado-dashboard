package screens;

import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.Pause;
import org.openqa.selenium.interactions.PointerInput;
import org.openqa.selenium.interactions.Sequence;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.Rectangle;

import java.time.Duration;
import java.util.List;
import java.util.HashMap;
import java.util.Map;


public abstract class BaseScreen {

    protected AndroidDriver driver;
    protected WebDriverWait wait;

    public BaseScreen(AndroidDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    protected WebElement waitForVisible(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    protected void tap(By locator) {
        waitForVisible(locator).click();
    }

    protected String getText(By locator) {
        return waitForVisible(locator).getText();
    }

    protected boolean isDisplayed(By locator) {
        try {
            List<WebElement> elements = driver.findElements(locator);
            return !elements.isEmpty() && elements.get(0).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    protected boolean isPresent(By locator) {
        return !driver.findElements(locator).isEmpty();
    }

    protected boolean isPartiallyOnScreen(By locator) {
        List<WebElement> elements = driver.findElements(locator);
        if (elements.isEmpty()) {
            return false;
        }
        Rectangle rect = elements.get(0).getRect();
        int screenWidth = driver.manage().window().getSize().getWidth();
        return (rect.getX() + rect.getWidth()) > 0 && rect.getX() < screenWidth;
    }

    protected void swipeElementHorizontally(WebElement webElement, boolean toRight) {
        int centerY = webElement.getRect().getY() + (webElement.getRect().getHeight() / 2);
        int screenWidth = driver.manage().window().getSize().getWidth();

        int startX = toRight ? (int) (screenWidth * 0.08) : (int) (screenWidth * 0.92);
        int endX = toRight ? (int) (screenWidth * 0.100) : (int) (screenWidth * 0.00);

        PointerInput dedito = new PointerInput(PointerInput.Kind.TOUCH, "dedito");
        Sequence sequence = new Sequence(dedito, 0)
                .addAction(dedito.createPointerMove(Duration.ofSeconds(0), PointerInput.Origin.viewport(), startX, centerY))
                .addAction(dedito.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
                .addAction(dedito.createPointerMove(Duration.ofMillis(600), PointerInput.Origin.viewport(), endX, centerY))
                .addAction(dedito.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

        driver.perform(List.of(sequence));
    }

    protected void swipeScreenUp() {
        int screenWidth = driver.manage().window().getSize().getWidth();
        int screenHeight = driver.manage().window().getSize().getHeight();

        // Centro horizontal y movimiento en la mitad inferior de la pantalla
        int startX = screenWidth / 2;
        int startY = (int) (screenHeight * 0.85); // Iniciar muy abajo
        int endY = (int) (screenHeight * 0.30);   // Subir hasta la parte media

        PointerInput dedito = new PointerInput(PointerInput.Kind.TOUCH, "dedito");
        Sequence sequence = new Sequence(dedito, 0)
                .addAction(dedito.createPointerMove(Duration.ZERO, PointerInput.Origin.viewport(), startX, startY))
                .addAction(dedito.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
                .addAction(dedito.createPointerMove(Duration.ofMillis(600), PointerInput.Origin.viewport(), startX, endY))
                .addAction(dedito.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

        driver.perform(List.of(sequence));
    }

}