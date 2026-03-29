CREATE DATABASE IF NOT EXISTS movie_booking;
USE movie_booking;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    movie_id INT,
    seat_number VARCHAR(10),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(movie_id, seat_number)
);

CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    duration VARCHAR(20) NOT NULL,
    poster VARCHAR(255)
);