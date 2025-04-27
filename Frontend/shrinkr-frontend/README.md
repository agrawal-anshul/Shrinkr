# Shrinkr - URL Shortener

Shrinkr is a modern URL shortening application built with Angular and FastAPI. This README covers how to set up and run the frontend application.

## Features

- **URL Shortening**: Create shortened URLs with custom settings
- **Analytics Dashboard**: Track clicks, geographic data, devices, and browsers
- **QR Code Generation**: Generate and download QR codes for your shortened URLs
- **User Authentication**: Secure user registration and login
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Prerequisites

- Node.js (v14+)
- npm (v6+)
- Angular CLI (v17+)
- FastAPI backend running (Docker container)

## Setup

1. Clone the repository (if you haven't already):
```bash
git clone <repository-url>
cd Frontend/shrinkr-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Ensure the backend API is running:
Make sure your FastAPI backend is running on `http://localhost:8000`

## Development Server

Run the development server:
```bash
npm run start
```

Navigate to `http://localhost:4200/` in your browser. The application will automatically reload if you change any of the source files.

## API Configuration

The application is configured to communicate with a backend API. 
- For development: `http://localhost:8000/api`
- For production: Configure in `src/environments/environment.prod.ts`

## Building for Production

To build the project for production:
```bash
npm run build -- --configuration production
```

The build artifacts will be stored in the `dist/` directory.

## Testing

Run unit tests:
```bash
npm run test
```

Run end-to-end tests:
```bash
npm run e2e
```

## Troubleshooting

### CORS Issues
If you experience CORS issues:
1. Ensure your backend server is properly configured to allow requests from the frontend origin
2. Check the CORS interceptor in the Angular application

### Authentication Issues
If you experience authentication problems:
1. Check that your backend API is running and accessible
2. Verify that login/register endpoints are responding correctly
3. Check the browser console for specific error messages

## API Reference

### Authentication API
- **Register User**
  - **Endpoint**: `POST /auth/register`
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string",
      "email": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "string"
    }
    ```

- **Login User**
  - **Endpoint**: `POST /auth/login`
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "string"
    }
    ```

### URL Management API
- **Create URL**
  - **Endpoint**: `POST /urls/create`
  - **Request Body**:
    ```json
    {
      "original_url": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "short_code": "string",
      "original_url": "string",
      "click_count": 0,
      "created_at": "date"
    }
    ```

- **List URLs**
  - **Endpoint**: `GET /urls/list`
  - **Query Parameters**:
    - `skip`: number of URLs to skip (default: 0)
    - `limit`: number of URLs to return (default: 100)

### Analytics API
- **Get URL Stats**
  - **Endpoint**: `GET /urls/{shortCode}/stats`
  - **Response**:
    ```json
    {
      "short_code": "string",
      "click_count": 0,
      "created_at": "date",
      "analytics": [
        {
          "date": "date",
          "clicks": 0
        }
      ]
    }
    ```

## Frontend Components
The frontend is built using Angular and includes various components for managing URLs, displaying analytics, and handling user authentication.

## Styling
The application uses Angular Material for UI components and custom SCSS for styling.

## Deployment
For deployment instructions, refer to the deployment section of your project.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
