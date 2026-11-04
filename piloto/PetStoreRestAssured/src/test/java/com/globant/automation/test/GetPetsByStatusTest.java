package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.Pet;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertFalse;

public class GetPetsByStatusTest extends TestRunner {

    @Test(testName = "Validate get pets by status")
    public void getPetsByStatusTest() {
        Map<String, String> queryParams = new HashMap<>();
        queryParams.put("status", "available");

        Response response = RequestBuilder.getWithParams(getBaseUrl(), "/pet/findByStatus", queryParams);
        Pet[] pets = response.as(Pet[].class);
        List<Pet> petList = List.of(pets);

        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertFalse(petList.isEmpty(), "The pet list should not be empty.");
        petList.forEach(pet ->
                assertEquals(pet.getStatus(), "available",
                        "Every pet returned should have status 'available'. Failed for pet id " + pet.getId())
        );
    }
}
