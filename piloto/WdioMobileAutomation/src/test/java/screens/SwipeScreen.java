package screens;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

import java.util.List;

public class SwipeScreen extends BaseScreen {

    private final By screenContainer = AppiumBy.accessibilityId("Swipe-screen");
    private final By card = AppiumBy.accessibilityId("card");
    private final By foundMeText = By.xpath("//*[@text='You found me!!!' or @content-desc='You found me!!!']");

    public SwipeScreen(AndroidDriver driver) {
        super(driver);
    }

    public boolean isScreenDisplayed() {
        return isDisplayed(screenContainer);
    }

    private By cardAtIndex(int index) {
        return By.xpath("//android.view.ViewGroup[@resource-id='__CAROUSEL_ITEM_" + index + "__']/android.view.ViewGroup[@content-desc='card']");
    }

    public boolean isCardIndexVisible(int index) {
        return isPresent(cardAtIndex(index));
    }

    public void waitUntilCardHidden(int index) {
        wait.until(driver -> !isCardIndexVisible(index));
    }

    public void swipeForwardAndWait(int currentIndex) {
        int attempts = 0;
        int maxAttempts = 3;

        while (isCardIndexVisible(currentIndex) && attempts < maxAttempts) {
            swipeCarouselForward();
            try {
                wait.until(driver -> !isCardIndexVisible(currentIndex));
                return;
            } catch (org.openqa.selenium.TimeoutException e) {
                attempts++;
            }
        }
    }

    public void swipeCarouselForward() {
        List<WebElement> cards = driver.findElements(card);
        if (!cards.isEmpty()) {
            // Deslizar de derecha a izquierda avanza el carrusel a la
            // siguiente carta (hacia la derecha no hacía nada porque
            // ya estábamos en la primera carta, no había hacia dónde retroceder).
            swipeElementHorizontally(cards.get(0), false);
        }
    }

    public void scrollUntilFoundMeVisible(int maxAttempts) {
        try {
            // Usa el motor nativo de Android para hacer scroll hasta que el texto sea visible
            driver.findElement(AppiumBy.androidUIAutomator(
                    "new UiScrollable(new UiSelector().scrollable(true))" +
                            ".scrollIntoView(new UiSelector().text(\"You found me!!!\"))"
            ));
        } catch (Exception e) {
            // En caso de que falle UiScrollable, intentamos con swipe de respaldo
            int attempts = 0;
            while (!isDisplayed(foundMeText) && attempts < maxAttempts) {
                swipeScreenUp();
                attempts++;
            }
        }
    }

    public boolean isCardOnScreen(int index) {
        return isPartiallyOnScreen(cardAtIndex(index));
    }

    public boolean isFoundMeTextDisplayed() {
        return isDisplayed(foundMeText);
    }
}