package utils;

import java.util.UUID;

public class DataGenerator {

    public static String generateRandomEmail() {
        String uniqueId = UUID.randomUUID().toString().substring(0, 8);
        return "testuser_" + uniqueId + "@mailtest.com";
    }
}