-- Create Users Table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Trains Table
CREATE TABLE Trains (
    train_id INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    train_type VARCHAR(50), -- e.g., Express, Local, etc.
    total_seats INT NOT NULL
);

-- Create Stations Table
CREATE TABLE Stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    station_code VARCHAR(10) NOT NULL UNIQUE,
    city VARCHAR(100),
    state VARCHAR(100)
);

-- Create Routes Table
CREATE TABLE Routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT,
    source_station_id INT,
    destination_station_id INT,
    distance_km INT,
    FOREIGN KEY (train_id) REFERENCES Trains(train_id),
    FOREIGN KEY (source_station_id) REFERENCES Stations(station_id),
    FOREIGN KEY (destination_station_id) REFERENCES Stations(station_id)
);

-- Create Train Schedules Table
CREATE TABLE Train_Schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT,
    station_id INT,
    arrival_time TIME,
    departure_time TIME,
    FOREIGN KEY (train_id) REFERENCES Trains(train_id),
    FOREIGN KEY (station_id) REFERENCES Stations(station_id)
);

-- Create Bookings Table
CREATE TABLE Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    train_id INT,
    route_id INT,
    booking_date DATE,
    journey_date DATE,
    seat_number INT,
    booking_status VARCHAR(50), -- e.g., Confirmed, Pending, Cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (train_id) REFERENCES Trains(train_id)
);
