package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.ApiResponse;
import com.globant.automation.model.User;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertNotNull;

public class CreateUserTest extends TestRunner {

    @Test(testName = "Validate user creation")
    public void createUserTest() {
        // Given: se arma un usuario con datos unicos (timestamp) para no chocar
        // con usuarios ya existentes en el ambiente de demo.
        long uniqueId = System.currentTimeMillis();
        User newUser = User.builder()
                .id(uniqueId)
                .username("qa_user_" + uniqueId)
                .firstName("Angelica")
                .lastName("QA")
                .email("qa_user_" + uniqueId + "@perfdog.com")
                .password("Secure123!")
                .phone("3000000000")
                .userStatus(1)
                .build();

        // When: se envia la peticion de creacion
        Response response = RequestBuilder.post(getBaseUrl(), "/user", newUser);
        ApiResponse apiResponse = response.as(ApiResponse.class);

        // Then: la API responde 200 y el "message" trae el id del usuario creado
        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertEquals(apiResponse.getCode(), Integer.valueOf(200), "The response code doesn't match.");
        assertNotNull(apiResponse.getMessage(), "The response should contain the created user id.");
    }
}