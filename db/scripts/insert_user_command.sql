INSERT INTO UserCommands 
VALUES (?, ?, ?)
ON CONFLICT (UserID, CommandName) DO NOTHING
