DELETE FROM Channels
WHERE ChannelID IN 
(
    SELECT Channels.ChannelID
    FROM Channels
    LEFT JOIN ChannelCommands 
    ON Channels.ChannelID = ChannelCommands.ChannelID
    WHERE ChannelCommands.ChannelID IS NULL
);
