# **Product Requirements Document: Readwise Reader RSS Feed Cleaner**

## **1\. Introduction**

This document outlines the requirements for a Python 3 script designed to automatically clean a user's Readwise Reader RSS feed. The script will identify and delete documents from the feed that match specific, user-defined filter criteria. This tool aims to help users manage their RSS feed more efficiently by removing unwanted or irrelevant content programmatically.

## **2\. Goals**

* Enable users to automatically delete documents from their Readwise Reader RSS feed based on configurable criteria.  
* Provide a simple, command-line interface for running the script.  
* Adhere to Readwise API rate limits.

## **3\. Features**

* Fetch all documents from the Readwise Reader RSS feed.  
* Apply user-defined filters to identify documents for deletion.  
* Delete identified documents using the Readwise API.  
* Provide feedback on the number of documents found, matched, and deleted.

## **4\. Technical Requirements**

* **Language:** Python 3  
* **Dependencies:** Standard libraries for making HTTP requests (e.g., requests) and potentially handling JSON.  
* **API Interaction:** The script will interact with the Readwise Reader API using the user's API token. The API token should be securely handled (e.g., read from an environment variable or configuration file, not hardcoded).  
* **Filtering Logic:** The filtering logic should be flexible enough to accommodate various criteria (see Section 5).  
* **Rate Limiting:** The script must respect the Readwise API rate limit of 20 requests per minute. Appropriate delays should be implemented between delete requests.

## **5\. Filter Criteria (Examples)**

The script should allow users to define filters based on document metadata. Examples of potential filter criteria include:

* **Title Contains:** Delete documents where the title contains a specific word or phrase (case-insensitive option desirable).  
* **Summary Contains:** Delete documents where the summary contains a specific word or phrase (case-insensitive option desirable).  
* **URL Contains:** Delete documents where the URL contains a specific string.  
* **Combined Criteria:** Support combining multiple filter criteria (e.g., title contains X *AND* URL contains Y).

The exact mechanism for defining filters (e.g., command-line arguments, a configuration file) can be determined during implementation, but the core filtering logic needs to be robust.

## **6\. API Endpoints**

The script will utilize the following Readwise Reader API endpoints:

* **Fetch Documents:** https://readwise.io/api/v3/list/  
  * Method: GET  
  * Parameters: location="feed"  
  * Authentication: API token in the Authorization header (Token YOUR\_TOKEN)  
* **Delete Document:** https://readwise.io/api/v3/delete/\<document\_id\>/  
  * Method: POST  
  * Authentication: API token in the Authorization header (Token YOUR\_TOKEN)

## **7\. Rate Limiting**

As per the Readwise API documentation, the rate limit is 20 requests per minute. The script must implement a delay between consecutive DELETE requests to avoid exceeding this limit. A simple approach is to wait for 3 seconds between each delete call.

## **8\. Future**

The following features might be implemented in the future but are not necessary right now:

* Combined criterias: E.g. URL contains AND title contains  
* LLM filtering: Using a LLM to get the general gist of the topic and filtering based on that