INSERT INTO UserPerms
VALUES (?, ?, ?)
ON CONFLICT (UserID, CogName) DO
UPDATE SET Permission = excluded.Permission
