# THYNK UNLIMITED

THYNK API is a Python-based web application designed for wholesale Amazon third-party sellers to manage their business, inventory, and gain product analysis information including profitability. This powerful API provides endpoints for authentication, user management, business management, todos, wholesale management, and more. This documentation is a comprehensive guide to understanding the project, including detailed information about the different packages and modules utilised in the application.

### Packages

The THYNK API project is divided into several packages that handle different aspects of the application. These packages are:

	Auth: The auth package provides endpoints for user authentication and authorization. It includes routes for user registration, login, logout, password reset, and email verification. This package utilizes FastAPI's built-in security features such as OAuth2 with JWT tokens for authentication.
	Business: The business package is responsible for handling the business management functionality of the application. It includes routes for creating and managing businesses, such as adding products, updating business information, and retrieving business details.
	Csvhandler: The csvhandler package provides routes for handling CSV files. It includes endpoints for uploading and parsing CSV files.
	Driver: The driver package provides endpoints for handling driver information. It includes routes for navigating to a website, logging in to the website, searching for a product, and scraping product data from the website. This package utilizes Selenium for web scraping.
	Todos: The todos package provides endpoints for handling todo tasks. It includes routes for user registration, email verification, resending email verification, retrieving user details, updating user details, deleting a user, uploading profile pictures, requesting password resets, and resetting passwords.
	User: The user package provides endpoints for managing user details. It includes routes for user registration, email verification, resending email verification, retrieving and updating user information, deleting a user, uploading a user's profile picture, requesting a password reset, and resetting a password.
	Wholesale: The wholesale package is responsible for handling wholesale product management. It includes routes for creating and managing wholesale products, such as adding products, updating product details, and retrieving product information.


##### Package Structure

Each package has its own structure, with files and folders specific to its requirements. These include: 

    router.py: This file contains all the endpoints specific to the package. 
    schemas.py: This file contains pydantic models for the package. 
    services.py: This file contains the module-specific business logic. 
    config.py: This file contains environment variables specific to the package. 
    utils.py: This file contains non-business logic functions such as response normalisation and data enrichment. 
    exceptions.py: This folder contains module-specific exceptions, such as PostNotFound and InvalidUserData.


### Modules

Apart from packages, the project also uses several modules to handle different tasks. Some of these modules are:

	Config: The config module provides a configuration file (config.py) that contains the necessary settings and environment variables required for the application to function. It uses Pydantic for type validation and provides settings for database connections, email configuration, and other necessary variables.
	Database: The database module handles the connection to the MongoDB database using the Motor library. It uses the settings from the config.py file to establish a connection to the database.
	Email_handler: The email_handler module provides a fastapi_mail library for sending email notifications to users. It includes functions for sending verification emails, registration successful emails, and password reset emails.
	Global_exceptions: The global_exceptions module provides custom exception classes for handling common errors that may occur in the application. These errors include UserNotFoundException, ProductNotFoundException, InvalidIdException, InvalidFileExtensionException, UnauthorizedUserException, and ServerErrorException.
	Main: The main module (main.py) is the main entry point for the application. It includes the FastAPI app and includes all the routers from the different packages. It also includes CORS middleware and mounts the static folder for serving static files.
	Models: The models module includes the different database models used by the application. These models include Business, Product, and ScrapedProduct. It uses the Tortoise ORM to define the models and their fields.
