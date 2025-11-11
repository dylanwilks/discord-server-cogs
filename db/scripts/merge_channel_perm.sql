MERGE ChannelServerPerms AS Target
USING 
    (
	SELECT  ? as ChannelID,
		? as ServerName,
		? as Permission
    ) AS Source
ON  (Target.ChannelID = Source.ChannelID) AND 
    (Target.ServerName = Source.ServerName)

WHEN MATCHED THEN
    UPDATE SET Target.Permission = Source.Permission

WHEN NOT MATCHED BY Target THEN
    INSERT VALUES (Source.ChannelID, Source.ServerName, Source.Permission)
