CREATE DATABASE chat;
\c chat;
CREATE EXTENSION pgcrypto;

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--


--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS users (
  id serial,
  username varchar(12) NOT NULL,
  password varchar(126) NOT NULL,
  PRIMARY KEY (id)
)  ;

--
-- Dumping data for table `users`
--

CREATE TABLE IF NOT EXISTS messages (
  id serial,
  username int NOT NULL, 
  message varchar(200) NOT NULL,
  PRIMARY KEY (id)
)  ;


INSERT INTO users (username, password) VALUES 
('carlson', crypt('beale', gen_salt('bf'))),
('matt', crypt('colony', gen_salt('bf')));