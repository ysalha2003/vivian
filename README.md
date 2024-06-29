# Grocery Store Debt Manager

This project is a web-based application for managing customer debts in a grocery store. It allows for adding customers, recording purchases, processing payments, and generating statements.

## Project Structure

```
grocery-store-debt-manager/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   └── config.py
│
├── frontend/
│   └── index.html
│
├── README.md
└── docker-compose.yml
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/grocery-store-debt-manager.git
   cd grocery-store-debt-manager
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   - No setup required. The `index.html` file can be opened directly in a web browser.

## Running the Application

1. Start the backend server:
   ```
   cd backend
   python app.py
   ```
   The server will start running on `http://localhost:5000`.

2. Open the frontend:
   Open the `frontend/index.html` file in a web browser.

## Using Docker (Optional)

If you prefer to use Docker, you can use the provided `docker-compose.yml` file:

1. Make sure you have Docker and Docker Compose installed.

2. Run the following command in the project root directory:
   ```
   docker-compose up --build
   ```

3. Access the application at `http://localhost:8080`.

## Features

- Add, edit, and delete customers
- Record purchases and process payments
- Generate customer statements
- View dashboard with total customers, total debt, and recent transactions
- Toggle between light and dark themes
- Flush database (with confirmation)

## Technologies Used

- Backend: Flask, SQLAlchemy
- Frontend: HTML, CSS, JavaScript
- UI Framework: Pico CSS
- Date Picker: Flatpickr

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).