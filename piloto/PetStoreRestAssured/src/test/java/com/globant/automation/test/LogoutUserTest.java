package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.ApiResponse;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import static org.testng.Assert.assertEquals;

public class LogoutUserTest extends TestRunner {

    @Test(testName = "Validate user logout")
    public void logoutUserTest() {
        // When
        Response response = RequestBuilder.get(getBaseUrl(), "/user/logout");
        ApiResponse apiResponse = response.as(ApiResponse.class);

        // Then
        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertEquals(apiResponse.getMessage(), "ok", "The logout message should be 'ok'.");
    }
}