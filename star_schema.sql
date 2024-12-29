USE Netflix_copy;

-- Dim_Search_History
CREATE TABLE Dim_Search_History (
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    query_typed TEXT,
    displayed_name TEXT,
    action TEXT,
    section TEXT,
    timestamp_utc DATETIME
);

INSERT INTO Dim_Search_History (query_typed, displayed_name, action, section, timestamp_utc)
SELECT DISTINCT
    sh.query_typed,
    sh.displayed_name,
    sh.action,
    sh.section,
    sh.timestamp_utc
FROM search_history sh;

-- Dim_Profiles
CREATE TABLE Dim_Profiles (
    profile_name VARCHAR(255) PRIMARY KEY,
    maturity_level VARCHAR(50),
    primary_language VARCHAR(50),
    auto_playback VARCHAR(10),
    country_iso_code VARCHAR(10), -- Added from search_history
    is_child TINYINT(1),          -- Added from search_history
    search_id INT,                -- Reference to Dim_Search_History
    FOREIGN KEY (search_id) REFERENCES Dim_Search_History(search_id)
);

INSERT INTO Dim_Profiles (profile_name, maturity_level, primary_language, auto_playback, country_iso_code, is_child)
SELECT 
    p.profile_name,
    p.maturity_level,
    p.primary_language,
    p.auto_playback,
    MAX(sh.country_iso_code) AS country_iso_code, -- Use MAX() to pick a value
    MAX(sh.is_child) AS is_child -- Use MAX() to pick a value
FROM profiles p
LEFT JOIN search_history sh ON p.profile_name = sh.profile_name
GROUP BY p.profile_name, p.maturity_level, p.primary_language, p.auto_playback;

-- Dim_Shows
CREATE TABLE Dim_Shows (
    show_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    genre VARCHAR(100),
    duration INT
);

INSERT INTO Dim_Shows (show_id, title, genre, duration)
SELECT DISTINCT
    va.title AS show_id,
    va.title,
    NULL AS genre, -- Genre data not provided; set as NULL or join with another table if available
    MAX(va.duration) AS duration -- Use MAX() to handle duplicates
FROM viewing_activity va
GROUP BY va.title;

-- Dim_Time
CREATE TABLE Dim_Time (
    start_time DATETIME PRIMARY KEY,
    date DATE,
    hour TINYINT,
    day_of_week VARCHAR(10),
    month TINYINT,
    year SMALLINT
);

INSERT INTO Dim_Time (start_time, date, hour, day_of_week, month, year)
SELECT DISTINCT
    start_time,
    DATE(start_time) AS date,
    HOUR(start_time) AS hour,
    DAYNAME(start_time) AS day_of_week,
    MONTH(start_time) AS month,
    YEAR(start_time) AS year
FROM viewing_activity;

-- Dim_Devices
CREATE TABLE Dim_Devices (
    device_id VARCHAR(255) PRIMARY KEY,
    device_type VARCHAR(100),
    country VARCHAR(100)
);

INSERT INTO Dim_Devices (device_id, device_type, country)
SELECT DISTINCT
    device_id,
    device_type,
    NULL AS country -- If country is not available in devices table
FROM devices;

-- Dim_Friends
CREATE TABLE Dim_Friends (
    friend_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_name VARCHAR(255),
    friend_profile_name VARCHAR(255),
    status VARCHAR(20),
    UNIQUE (profile_name, friend_profile_name)
);

INSERT INTO Dim_Friends (profile_name, friend_profile_name, status)
SELECT 
    p1.profile_name AS profile_name, 
    p2.profile_name AS friend_profile_name, 
    'accepted' AS status
FROM profiles p1
CROSS JOIN profiles p2
WHERE p1.profile_name != p2.profile_name;

-- Dim_charts
CREATE TABLE Dim_Chats (
    unique_id VARCHAR(250) PRIMARY KEY,
    message TEXT,
    author TEXT,
    timestamp DATETIME,
    user_id INT,
    show_id TEXT
);

INSERT INTO Dim_Chats (unique_id, message, author, timestamp, user_id, show_id)
SELECT
    unique_id,
    messages AS message,
    SUBSTRING_INDEX(all_authors, ',', 1) AS author, -- Extract the first author
    time AS timestamp,
    user_id,
    show_id
FROM chats
WHERE messages IS NOT NULL;

-- Fact_Viewing_Activity
CREATE TABLE Fact_Viewing_Activity (
    fact_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_name VARCHAR(255),
    show_id VARCHAR(255),
    friend_id INT,
    start_time DATETIME,
    device_id VARCHAR(255),
    duration INT,
    messages_count INT,
    friend_watched BOOLEAN,
    chat_unique_id VARCHAR(255), -- Reference Dim_Chats unique_id
    FOREIGN KEY (profile_name) REFERENCES Dim_Profiles(profile_name),
    FOREIGN KEY (show_id) REFERENCES Dim_Shows(show_id),
    FOREIGN KEY (friend_id) REFERENCES Dim_Friends(friend_id),
    FOREIGN KEY (start_time) REFERENCES Dim_Time(start_time),
    FOREIGN KEY (device_id) REFERENCES Dim_Devices(device_id),
    FOREIGN KEY (chat_unique_id) REFERENCES Dim_Chats(unique_id)
);

CREATE TEMPORARY TABLE Temp_Friends_Watched AS
SELECT 
    ROW_NUMBER() OVER () AS row_num,
    df.profile_name,
    df.friend_profile_name,
    vaf.title AS watched_show
FROM Dim_Friends df
JOIN viewing_activity vaf ON df.friend_profile_name = vaf.profile_name;

CREATE TEMPORARY TABLE Temp_Chat_Unique_IDs AS
SELECT 
    ROW_NUMBER() OVER () AS row_num,
    show_id,
    unique_id
FROM chats;

CREATE TEMPORARY TABLE Temp_Viewing_Activity AS
SELECT 
    ROW_NUMBER() OVER () AS row_num,
    profile_name,
    title AS show_id,
    start_time,
    device_type,
    duration
FROM viewing_activity;

INSERT INTO Fact_Viewing_Activity (
    profile_name,
    show_id,
    start_time,
    device_id,
    duration,
    messages_count,
    friend_watched,
    chat_unique_id
)
SELECT 
    tva.profile_name,
    tva.show_id,
    tva.start_time,
    d.device_id,
    tva.duration,
    0 AS messages_count, 
    CASE WHEN tfw.friend_profile_name IS NOT NULL THEN TRUE ELSE FALSE END AS friend_watched,
    COALESCE(tcu.unique_id, CONCAT(tva.show_id, '-default')) AS chat_unique_id -- Assign default if NULL
FROM Temp_Viewing_Activity tva
LEFT JOIN devices d ON tva.device_type = d.device_type
LEFT JOIN Temp_Friends_Watched tfw ON tva.row_num = tfw.row_num -- Match by row number
LEFT JOIN Temp_Chat_Unique_IDs tcu ON tva.row_num = tcu.row_num -- Match by row number
WHERE d.profile_name IS NOT NULL;

## Querries
-- For a Specific User, How Many of His Friends Watched the Same Show?
SELECT
    fva.profile_name AS user_profile,
    fva.show_id,
    COUNT(DISTINCT df.friend_profile_name) AS friends_who_watched
FROM Fact_Viewing_Activity fva
JOIN Dim_Friends df ON fva.profile_name = df.profile_name
JOIN Fact_Viewing_Activity fva_friend ON df.friend_profile_name = fva_friend.profile_name
    AND fva.show_id = fva_friend.show_id -- Match show watched by user and friend
WHERE fva.profile_name = 'User 1' -- Replace with the actual user's profile name
GROUP BY fva.profile_name, fva.show_id;

-- Which Movie Has the Most Chats
SELECT 
    fva.show_id,
    COUNT(dc.unique_id) AS total_chats
FROM Fact_Viewing_Activity fva
JOIN Dim_Chats dc ON fva.chat_unique_id = dc.unique_id
GROUP BY fva.show_id
ORDER BY total_chats DESC
LIMIT 1;

-- How Many Chats does a Specific Movie have Every Ten Minutes?
SELECT 
    fva.show_id AS movie_name,
    CONCAT('min ', FLOOR(DATE_FORMAT(dc.timestamp, '%i') / 10) * 10) AS ten_minute_interval,
    COUNT(dc.unique_id) AS total_chats
FROM Fact_Viewing_Activity fva
JOIN Dim_Chats dc ON fva.chat_unique_id = dc.unique_id
WHERE fva.show_id = 'Minnal Murali' -- Replace with the specific movie name
GROUP BY movie_name, ten_minute_interval
ORDER BY ten_minute_interval;

-- How Many Chats Has a Certain User Made?
SELECT 
    fva.profile_name AS user_name,
    COUNT(dc.unique_id) AS total_chats
FROM Fact_Viewing_Activity fva
JOIN Dim_Chats dc ON fva.chat_unique_id = dc.unique_id
WHERE fva.profile_name = 'User 1'
GROUP BY fva.profile_name;
