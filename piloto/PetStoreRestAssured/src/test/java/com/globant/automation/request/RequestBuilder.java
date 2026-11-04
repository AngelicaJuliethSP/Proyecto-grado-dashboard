package com.globant.automation.request;

import io.restassured.RestAssured;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;

import java.util.Map;

public class RequestBuilder {

    private static RequestSpecification baseSpec(String baseUrl) {
        return RestAssured.given()
                .baseUri(baseUrl)
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .filter(new RequestLoggingFilter())
                .filter(new ResponseLoggingFilter());
    }

    public static Response get(String baseUrl, String path) {
        return baseSpec(baseUrl).get(path);
    }

    public static Response getWithParams(String baseUrl, String path, Map<String, String> queryParams) {
        return baseSpec(baseUrl)
                .queryParams(queryParams)
                .get(path);
    }

    public static Response post(String baseUrl, String path, Object body) {
        return baseSpec(baseUrl)
                .body(body)
                .post(path);
    }

    public static Response delete(String baseUrl, String path) {
        return baseSpec(baseUrl).delete(path);
    }
}