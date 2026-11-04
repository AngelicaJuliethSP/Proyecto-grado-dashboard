package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.Pet;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertNotNull;

public class GetPetByIdTest extends TestRunner {

    @Test(testName = "Validate get a specific pet by id")
    public void getPetByIdTest() {
        // Given: se obtiene un id de mascota valido y existente
        Map<String, String> queryParams = new HashMap<>();
        queryParams.put("status", "available");
        Pet[] availablePets = RequestBuilder
                .getWithParams(getBaseUrl(), "/pet/findByStatus", queryParams)
                .as(Pet[].class);
        Long petId = availablePets[0].getId();

        // When
        Response response = RequestBuilder.get(getBaseUrl(), "/pet/" + petId);
        Pet pet = response.as(Pet.class);

        // Then
        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertEquals(pet.getId(), petId, "The pet id in the response should match the requested id.");
        assertNotNull(pet.getName(), "The pet should have a name.");
    }
}
