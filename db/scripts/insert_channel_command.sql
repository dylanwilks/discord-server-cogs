INSERT INTO ChannelCommands 
VALUES (?, ?, ?)
ON CONFLICT (ChannelID, CommandName) DO NOTHING
