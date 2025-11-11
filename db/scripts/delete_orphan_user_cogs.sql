DELETE FROM UserCogs
WHERE (UserID, CogName) IN
(
    SELECT UserCogs.UserID, UserCogs.CogName
    FROM UserCogs 
    LEFT JOIN UserCommands
    ON  (UserCogs.UserID = UserCommands.UserID) AND
	(UserCogs.CogName = UserCommands.CogName)
    WHERE (UserCommands.UserID IS NULL) AND (UserCommands.CogName IS NULL)
);
