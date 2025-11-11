DELETE FROM Users
WHERE UserID IN 
(
    SELECT Users.UserID
    FROM Users
    LEFT JOIN UserCommands 
    ON Users.UserID = UserCommands.UserID
    WHERE UserCommands.UserID IS NULL
);
