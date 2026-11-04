package com.globant.automation.test;

import com.globant.automation.config.TestRunner;
import com.globant.automation.model.Order;
import com.globant.automation.model.Pet;
import com.globant.automation.request.RequestBuilder;
import io.restassured.response.Response;
import org.testng.annotations.Test;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertNotNull;
import static org.testng.Assert.assertTrue;

public class CreateOrderTest extends TestRunner {

    @Test(testName = "Validate order creation")
    public void createOrderTest() {
        // Given: petId valido + datos de la orden
        Map<String, String> queryParams = new HashMap<>();
        queryParams.put("status", "available");
        Pet[] availablePets = RequestBuilder
                .getWithParams(getBaseUrl(), "/pet/findByStatus", queryParams)
                .as(Pet[].class);
        Long petId = availablePets[0].getId();

        Order newOrder = Order.builder()
                .id(System.currentTimeMillis() % 100000) // la API espera un int32
                .petId(petId)
                .quantity(1)
                .shipDate(Instant.now().toString())
                .status("placed")
                .complete(true)
                .build();

        // When
        Response response = RequestBuilder.post(getBaseUrl(), "/store/order", newOrder);
        Order createdOrder = response.as(Order.class);

        // Then
        assertEquals(response.getStatusCode(), 200, "The status code doesn't match.");
        assertNotNull(createdOrder.getId(), "The created order should have an id.");
        assertEquals(createdOrder.getPetId(), petId, "The petId should match the requested pet.");
        assertTrue(createdOrder.getComplete(), "The order should be marked as complete.");
    }
}