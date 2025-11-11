DELETE FROM ChannelCogs
WHERE (ChannelID, CogName) IN
(
    SELECT ChannelCogs.ChannelID, ChannelCogs.CogName
    FROM ChannelCogs 
    LEFT JOIN ChannelCommands
    ON  (ChannelCogs.ChannelID = ChannelCommands.ChannelID) AND
	(ChannelCogs.CogName = ChannelCommands.CogName)
    WHERE   (ChannelCommands.ChannelID IS NULL) AND 
	    (ChannelCommands.CogName IS NULL)
);
