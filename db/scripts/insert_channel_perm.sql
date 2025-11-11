INSERT INTO ChannelPerms
VALUES (?, ?, ?)
ON CONFLICT (ChannelID, CogName) DO
UPDATE SET Permission = excluded.Permission
