package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.ApiResponse;
import com.globant.automation.model.User;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

public class LoginUserTest extends TestRunner {

    private String username;
    private String password;

    @BeforeClass
    public void createUserForLogin() {
        long uniqueId = System.currentTimeMillis();
        username = "qa_login_" + uniqueId;
        password = "Secure123!";

        User newUser = User.builder()
                .id(uniqueId)
                .username(username)
                .firstName("Angelica")
                .lastName("QA")
                .email(username + "@perfdog.com")
                .password(password)
                .phone("3000000000")
                .userStatus(1)
                .build();

        RequestBuilder.post(getBaseUrl(), "/user", newUser);
    }

    @Test(testName = "Validate user login")
    public void loginUserTest() {
        Map<String, String> queryParams = new HashMap<>();
        queryParams.put("username", username);
        queryParams.put("password", password);

        Response response = RequestBuilder.getWithParams(getBaseUrl(), "/user/login", queryParams);
        ApiResponse apiResponse = response.as(ApiResponse.class);

        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertTrue(apiResponse.getMessage().contains("logged in user session"),
                "The message should confirm a logged in session.");
    }
}