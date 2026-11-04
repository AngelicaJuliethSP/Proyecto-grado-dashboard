# SauceDemo Automation Framework

Test automation framework for [SauceDemo](https://www.saucedemo.com/) built with Selenium WebDriver, Java, and TestNG, following the Page Object Model (POM) design pattern with Page Factory.

## Overview

This project automates three core user flows on the SauceDemo web application:

- **Purchase flow**: Complete end-to-end checkout, from login to order confirmation, selecting a random product.
- **Cart management**: Add three different products to the cart, remove them, and verify the cart is empty.
- **Logout**: Verify the user is correctly redirected to the login page after logging out.

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Java | 17 | Programming language |
| Maven | 3.x | Build and dependency management |
| Selenium WebDriver | 4.47.0 | Browser automation |
| TestNG | 7.5 | Test runner and annotations |
| Chrome | Latest | Target browser |

## Project Structure

```
SauceDemoAutomation/
├── src/
│ ├── main/java/ # Application-level code (currently unused)
│ └── test/java/com/saucedemo/
│ ├── base/
│ │ ├── BaseTest.java # WebDriver setup/teardown (@BeforeMethod/@AfterMethod)
│ │ └── BasePage.java # Page Factory initialization, shared logout logic
│ ├── pages/
│ │ ├── LoginPage.java
│ │ ├── InventoryPage.java
│ │ ├── CartPage.java
│ │ ├── CheckoutStepOnePage.java
│ │ ├── CheckoutStepTwoPage.java
│ │ └── CheckoutCompletePage.java
│ ├── listeners/
│ │ └── ScreenshotListener.java # Auto screenshot capture on test failure
│ └── tests/
│ ├── PurchaseTest.java # Uses @DataProvider for multiple users
│ ├── RemoveCartItemsTest.java
│ └── LogoutTest.java
├── screenshots/ # Auto-generated on test failures
├── pom.xml
├── .gitignore
└── README.md
```

## Design Decisions

- **Page Object Model with Page Factory**: Each page is represented by a class using `@FindBy` annotations. Locators live exclusively in page classes; test classes never interact with `WebElement` directly.
- **Method chaining across pages**: Any method that triggers navigation returns the next page's Page Object (e.g. `login()` returns `InventoryPage`), keeping tests fluent and decoupled from implementation details.
- **Shared base classes**: `BaseTest` centralizes WebDriver lifecycle management; `BasePage` centralizes Page Factory initialization and cross-page functionality (logout menu, available from any logged-in page).
- **Explicit waits**: Applied at specific points in the checkout flow where page transitions proved unreliable with certain SauceDemo test users, using `WebDriverWait` with `ExpectedConditions`.
- **Chrome preferences**: Password leak detection and the password manager are disabled via `ChromeOptions` to prevent native browser dialogs from interfering with test execution.

## Advanced TestNG Features

- **`@DataProvider`** in `PurchaseTest`: runs the purchase flow against multiple SauceDemo users (`standard_user`, `performance_glitch_user`) to validate the flow across different simulated user behaviors.
- **Custom `ITestListener`** (`ScreenshotListener`): automatically captures a screenshot whenever a test fails, saved to the `screenshots/` directory with a timestamped filename for traceability.

## How to Run

Clone the repository and run:

```bash
mvn clean test
```

Or, from IntelliJ IDEA: right-click the `tests` package → **Run 'Tests in com.saucedemo.tests'**.

### Prerequisites

- JDK 17 or higher
- Maven 3.6+
- Google Chrome installed (ChromeDriver is resolved automatically via Selenium Manager)

## Test Evidence

A screenshot confirming successful execution of all test scenarios (`Tests run: 4, Failures: 0`) is available at `screenshots/test-execution-success.png`.

## Author

Angélica Julieth Silva Pérez — College Trainee, Globant